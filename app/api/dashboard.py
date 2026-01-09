from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.deps import get_db, get_current_actor
from app.models.batch import Batch
from app.models.procedure import Procedure
from app.models.violation import Violation
from app.core.fsm import State
from app.core.circuit_breaker import circuit_breaker
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Authoritative Dashboard Aggregator.
    PHASE 4: No fake data. Aggregate from real database records.
    Integrated with Enterprise Resilience Circuit Breaker.
    """
    endpoint = "/dashboard/summary"

    if circuit_breaker.is_degraded(endpoint):
        logger.warning(f"Circuit OPEN for {endpoint}. Returning degraded zero-state.")
        return {
            "total_procedures": 0,
            "total_batches": 0,
            "completed_batches": 0,
            "violated_batches": 0,
            "mode": "degraded"
        }

    try:
        data = {
            "total_procedures": db.query(Procedure).count(),
            "total_batches": db.query(Batch).count(),
            "completed_batches": db.query(Batch).filter(Batch.current_state == State.COMPLETED.value).count(),
            "violated_batches": db.query(Violation).filter(Violation.status == 'OPEN').count(),
            "mode": "live"
        }
        circuit_breaker.record_success(endpoint)
        return data
    except Exception as e:
        logger.exception("Dashboard aggregation failed")
        circuit_breaker.record_failure(endpoint, type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to aggregate dashboard metrics")
