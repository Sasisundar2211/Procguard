from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.batch import Batch
from app.models.procedure import Procedure
from app.models.audit import AuditLog
from app.schemas import BatchTimelineResponse, StageTimeline, Marker

def generate_batch_timeline(db: Session, batch: Batch) -> BatchTimelineResponse:
    # 1. Fetch Procedure and its steps
    proc = db.query(Procedure).filter(Procedure.procedure_id == batch.procedure_id).first()
    if not proc:
        # Fallback for demo
        steps = []
    else:
        steps = proc.steps

    # 2. Fetch Audit Logs for this batch
    logs = db.query(AuditLog).filter(AuditLog.batch_id == batch.batch_id).order_by(AuditLog.timestamp.asc()).all()

    # Determine base time
    base_time = batch.created_at or datetime.now(timezone.utc)
    if base_time.tzinfo is None:
        base_time = base_time.replace(tzinfo=timezone.utc)

    # 3. Build Stages from Steps
    stages_out = []
    legend_counts = {"ON_TIME": 0, "OVER_TIME": 0, "AT_RISK": 0, "DEVIATION": 0}

    for step in steps:
        # Find when this step was progressed or approved in the logs
        # This is simplified for the MVP
        step_logs = [l for l in logs if l.payload.get("step_id") == str(step.step_id)]
        
        act_start = None
        act_end = None
        
        if step_logs:
            act_start = (step_logs[0].timestamp - base_time).days
            # If we see a result that implies completion
            completion_logs = [l for l in step_logs if l.action == "progress_step" and l.result == "SUCCESS"]
            if completion_logs:
                act_end = (completion_logs[-1].timestamp - base_time).days

        # Status logic
        expected_start = step.step_order * 5 # Dummy window
        expected_end = expected_start + 5
        
        status = "NOT_STARTED"
        if act_start is not None:
            status = "ON_TIME"
        
        stages_out.append(StageTimeline(
            stage_id=str(step.step_id),
            label=step.step_name,
            expected_window=(expected_start, expected_end),
            actual_window=(act_start, act_end),
            status=status,
            markers=[]
        ))

    # If no stages (empty proc), provide something for the UI
    if not stages_out:
        # Create default stages matching the UI image roughly for demo
        default_names = ["USP BMR Review", "DSP BMR Review", "QA BMR Review", "QP BMR Review", "QC Testing", "Lot Release QA"]
        for i, name in enumerate(default_names):
            stages_out.append(StageTimeline(
                stage_id=f"S{i}",
                label=name,
                expected_window=(i*10, i*10+10),
                actual_window=(None, None),
                status="NOT_STARTED",
                markers=[]
            ))

    return BatchTimelineResponse(
        batch_id=batch.batch_id,
        procedure_id=batch.procedure_id,
        procedure_version=batch.procedure_version,
        time_axis={"unit": "days", "range": [0, 70]},
        stages=stages_out,
        legend_counts=legend_counts,
        delay_buckets=[],
        delayed_batches=[]
    )
