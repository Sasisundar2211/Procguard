from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.schemas import ProcedureResponse
from app.models.procedure import Procedure

router = APIRouter()

@router.get("/", response_model=List[ProcedureResponse])
def list_procedures(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    procedures = db.query(Procedure).offset(skip).limit(limit).all()
    return procedures

@router.get("/{procedure_id}", response_model=ProcedureResponse)
def get_procedure(
    procedure_id: str,
    db: Session = Depends(get_db),
):
    # Retrieve the latest version? Or specific?
    # For now, just finding one by ID.
    # Since ID+Version is PK, finding by ID returns potentially multiple.
    # We should probably return the latest version or require version in URL.
    # For MVP robustness, let's just return the latest version if only ID provided.
    
    procedure = db.query(Procedure).filter(Procedure.procedure_id == procedure_id).order_by(Procedure.version.desc()).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    return procedure
