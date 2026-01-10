from typing import Optional, List, Dict, Any
from app.schemas import TimelineStatus

def is_deviation(stage_name: str, day: int, deviations: List[Any]) -> bool:
    """
    Checks if a cell is covered by an active, non-superseded deviation.
    """
    for dev in deviations:
        if isinstance(dev, dict):
            dev_stage = dev.get("stage")
            dev_from = dev.get("valid_from_day")
            dev_until = dev.get("valid_until_day")
            dev_resolved = dev.get("resolved_at")
            dev_superseded = dev.get("superseded_by_lir")
        else:
            dev_stage = getattr(dev, "stage", None)
            dev_from = getattr(dev, "valid_from_day", 0)
            dev_until = getattr(dev, "valid_until_day", 0)
            dev_resolved = getattr(dev, "resolved_at", None)
            dev_superseded = getattr(dev, "superseded_by_lir", False)

        if dev_stage == stage_name and dev_from <= day <= dev_until:
            if not dev_resolved and not dev_superseded:
                return True
    return False

def classify_timeline_cell(
    stage_name: str,
    day: int,
    planned_day: int,
    actual_day: Optional[int] = None,
    deviation_id: Optional[str] = None, # Legacy, kept for compat
    lir_id: Optional[str] = None,
    resolved_at: Optional[str] = None,
    risk_score: Optional[float] = None,
    deviations: List[Any] = None,
    lirs: List[Any] = None
) -> TimelineStatus:
    """
    Authoritative Classification Logic for Timeline Cells.
    PHASE 4: Precedence Order (Root Cause Fix).
    """
    # 1. Resolved (Gray/Blue)
    if resolved_at:
        return TimelineStatus.RESOLVED_DELAY
    
    # 2. LIR (Highest Operational Priority)
    if lir_id or (lirs and any(l.get("stage") == stage_name and l.get("day") == day for l in lirs)):
        return TimelineStatus.LIR
        
    # 3. Deviation (Authoritative lookup)
    if is_deviation(stage_name, day, deviations or []):
        return TimelineStatus.DEVIATION
        
    # 4. Risk (Predictive)
    if risk_score is not None and risk_score >= 0.7:
        return TimelineStatus.AT_RISK
        
    # 5. Over Time (Execution fact)
    if actual_day is not None and actual_day > planned_day:
        return TimelineStatus.OVER_TIME
        
    # 6. On Time (Steady State)
    return TimelineStatus.ON_TIME

def compute_eos_status(
    lead_time: int,
    stage_name: str,
    day_offset: int,
    deviations: List[Any]
) -> tuple[str, Optional[str]]:
    """
    PHASE 1.1: Authoritative EOS Status Computation.
    Returns (status, deviation_id)
    """
    if lead_time <= 0:
        return "ON_TIME", None

    # Check if any deviation covers the delay period
    for dev in deviations:
        dev_stage = getattr(dev, "stage", None) if not isinstance(dev, dict) else dev.get("stage")
        dev_from = getattr(dev, "valid_from_day", 0) if not isinstance(dev, dict) else dev.get("valid_from_day")
        dev_until = getattr(dev, "valid_until_day", 0) if not isinstance(dev, dict) else dev.get("valid_until_day")
        dev_resolved = getattr(dev, "resolved_at", None) if not isinstance(dev, dict) else dev.get("resolved_at")
        dev_superseded = getattr(dev, "superseded_by_lir", False) if not isinstance(dev, dict) else dev.get("superseded_by_lir")
        dev_id = getattr(dev, "id", None) if not isinstance(dev, dict) else dev.get("id")

        # If deviation covers the 'late' period
        if dev_stage == stage_name and dev_from <= day_offset <= dev_until:
            if not dev_resolved and not dev_superseded:
                return "DEVIATION", str(dev_id)
            if dev_resolved:
                return "EOS", None

    return "EOS", None
