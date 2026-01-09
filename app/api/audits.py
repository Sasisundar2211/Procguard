from fastapi import APIRouter, Depends, HTTPException, status
from procguard.store.repository import Repository
from procguard.api.deps import get_repo, REQUIRE_AUDITOR
from procguard.services.get_execution_replay import (
    get_execution_replay,
    GetExecutionReplaySuccess,
    BatchNotFound,
    DataCorruptionDetected,
)
from procguard.schemas.execution_replay import ExecutionReplayResponse

router = APIRouter()

@router.get(
    "/batches/{batch_id}/execution-replay",
    response_model=ExecutionReplayResponse,
    summary="Step 5: Forensic Proof of Record",
    tags=["Forensics"],
    dependencies=[Depends(REQUIRE_AUDITOR)] # RBAC Matrix: auditor only
)
async def get_replay_endpoint(
    batch_id: str,
    repo: Repository = Depends(get_repo),
):
    result = await get_execution_replay(repo=repo, batch_id=batch_id)

    if isinstance(result, GetExecutionReplaySuccess):
        return result.replay
    
    elif isinstance(result, BatchNotFound):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id '{result.batch_id}' not found.",
        )
    
    elif isinstance(result, DataCorruptionDetected):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "FORENSIC_INTEGRITY_COMPROMISED",
                "reason": result.reason,
                "batch": result.batch_id
            }
        )
