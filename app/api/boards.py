from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import uuid

from app.api.deps import get_db
from app.models.board import Board, BoardStatus
from app.schemas import BoardCreate, BoardResponse
from app.core.audit import write_audit_log

router = APIRouter(prefix="/boards", tags=["boards"])

@router.get("/", response_model=List[BoardResponse])
def list_boards(db: Session = Depends(get_db)):
    """
    List all Active boards.
    Ensures system boards are always present.
    """
    # Contract-aware filtering: Only show ACTIVE boards
    boards = db.query(Board).filter(Board.status == BoardStatus.ACTIVE).all()
    
    # If no active boards exist, seed the initial ones if DB is empty
    if not boards:
        total_count = db.query(Board).count()
        if total_count == 0:
            system_boards = [
                Board(title="Procedure", color="bg-[#2563eb]", href="/procedure", is_system=True, status=BoardStatus.ACTIVE),
                Board(title="Batch State", color="bg-[#3b82f6]", href="/timeline", is_system=True, status=BoardStatus.ACTIVE),
                Board(title="Violation", color="bg-[#1d4ed8]", href="/violations", is_system=True, status=BoardStatus.ACTIVE),
                Board(title="Audit Evidence", color="bg-[#0ea5e9]", href="/audit", is_system=True, status=BoardStatus.ACTIVE),
            ]
            db.add_all(system_boards)
            db.commit()
            boards = db.query(Board).filter(Board.status == BoardStatus.ACTIVE).all()
        
    return boards

@router.post("/", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
def create_board(board_in: BoardCreate, db: Session = Depends(get_db)):
    """
    Create a new custom board.
    Includes mandatory audit logging and Idempotency check.
    """
    # IDEMPOTENCY: Check if active board with same title exists
    existing = db.query(Board).filter(
        Board.title == board_in.title,
        Board.status == BoardStatus.ACTIVE
    ).first()
    
    if existing:
        return existing # Idempotent return

    board_id = uuid.uuid4()
    new_board = Board(
        id=board_id,
        title=board_in.title,
        description=board_in.description,
        color=board_in.color,
        # Canonical Navigation: Use ID-based routing
        href=f"/boards/{board_id}",
        is_system=False,
        status=BoardStatus.ACTIVE
    )
    
    try:
        db.add(new_board)
        db.flush()
        
        # AUDIT LOG: Board Creation
        write_audit_log(
            db=db,
            action="BOARD_CREATED",
            actor="SYSTEM_ADMIN",
            metadata={
                "board_id": str(new_board.id), 
                "title": new_board.title, 
                "idempotency_ref": str(board_in.client_mutation_id) if board_in.client_mutation_id else "none"
            }
        )
        
        db.commit()
        db.refresh(new_board)
        return new_board
    except IntegrityError:
        db.rollback()
        # Race Condition Handling:
        # A duplicate was inserted concurrently between our check and our insert.
        # We must return that existing board to maintain idempotency.
        existing_retry = db.query(Board).filter(
            Board.title == board_in.title,
            Board.status == BoardStatus.ACTIVE
        ).first()
        
        if existing_retry:
            # AUDIT LOG: Idempotent Recovery
            # Requirement: "No silent success". Must record the attempt.
            write_audit_log(
                db=db,
                action="BOARD_CREATED",
                actor="SYSTEM_ADMIN",
                metadata={
                    "board_id": str(existing_retry.id),
                    "title": existing_retry.title,
                    "outcome": "IDEMPOTENT_RECOVERY",
                    "idempotency_ref": str(board_in.client_mutation_id) if board_in.client_mutation_id else "none"
                }
            )
            db.commit()
            return existing_retry
            
        # If we still can't find it, something else caused IntegrityError
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Board creation conflict. Please try again."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create board: {str(e)}"
        )

@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(board_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Safely Eliminate a custom board (Soft-Delete).
    System boards are protected.
    """
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    if board.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System boards cannot be deleted"
        )
    
    try:
        # SOFT DELETE: Suppress artifact but preserve audit trail
        board.status = BoardStatus.DELETED
        
        # AUDIT LOG: Board Deletion
        write_audit_log(
            db=db,
            action="BOARD_DELETED",
            actor="SYSTEM_ADMIN",
            metadata={"board_id": str(board.id), "title": board.title, "mode": "soft_delete"}
        )
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete board: {str(e)}"
        )
