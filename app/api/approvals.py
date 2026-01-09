from fastapi import APIRouter, Depends, HTTPException, status
from procguard.store.repository import Repository
from procguard.api.deps import get_repo, REQUIRE_APPROVER, get_identity_claims
from procguard.services.approve_step import approve_step, BatchSealedError, PolicyVersionMismatch
from procguard.core.errors import DomainError, AuthorizationError
from procguard.schemas.approval import ApprovalRequest, ApprovalResponse

router = APIRouter()

@router.post(
    "/batches/{batch_id}/approve",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Step 2: Provide an Approval",
    description="Adds an approval to a batch, binding the action to the approver's verified identity.",
    tags=["Approvals"],
)
async def approve_batch_endpoint(
    batch_id: str,
    request: ApprovalRequest,
    repo: Repository = Depends(get_repo),
    identity: dict = Depends(REQUIRE_APPROVER), # RBAC Enforced
):
    """
    Endpoint for submitting an approval for a specific batch.

    The approver's identity is taken from the JWT, not the request body,
    ensuring that the approval is non-repudiable.
    """
    try:
        # The service layer now receives the full identity claims dictionary
        approval = await approve_step(
            repo=repo,
            identity=identity,
            batch_id=batch_id,
            policy_version=request.policy_version,
            requested_role=request.role,
        )
        return ApprovalResponse(
            batch_id=approval.batch_id,
            approver=approval.approver,
            role=approval.role,
            policy_version=approval.policy_version,
            approved_at=approval.approved_at,
        )
    except BatchSealedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="BATCH_ALREADY_SEALED: This batch has been sealed and cannot be modified."
        )
    except PolicyVersionMismatch as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"POLICY_VERSION_MISMATCH: {e}"
        )
    except DomainError as e:
        if "batch_not_found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Batch with id '{batch_id}' not found.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"INSUFFICIENT_AUTHORITY: {e}"
        )