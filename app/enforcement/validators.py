from collections import Counter
from typing import List, Dict, Optional

def validate_step_order(
    sop_steps: List[Dict],
    execution: List[Dict]
) -> Optional[Dict]:
    sop_order = [s["id"] for s in sop_steps]
    executed_order = [e["step_id"] for e in execution]

    filtered = [s for s in executed_order if s in sop_order]

    if filtered != sorted(filtered, key=lambda x: sop_order.index(x)):
        return {
            "code": "STEP_ORDER_MISMATCH",
            "details": "Steps executed out of approved order"
        }

    return None

def validate_missing_steps(
    sop_steps: List[Dict],
    execution: List[Dict]
) -> Optional[Dict]:
    sop_ids = {s["id"] for s in sop_steps}
    executed_ids = {e["step_id"] for e in execution}

    missing = sop_ids - executed_ids

    if missing:
        return {
            "code": "MISSING_REQUIRED_STEP",
            "details": f"Missing steps: {sorted(list(missing))}"
        }

    return None

def validate_actor_roles(
    sop_steps: List[Dict],
    execution: List[Dict],
    role_map: Dict[str, str]
) -> Optional[Dict]:
    sop_roles = {s["id"]: role_map.get(s["id"]) for s in sop_steps}

    for e in execution:
        required_role = sop_roles.get(e["step_id"])

        if required_role and e["actor"] != required_role:
            return {
                "code": "UNAUTHORIZED_ACTOR",
                "details": f"Step {e['step_id']} requires role {required_role}"
            }

    return None

def validate_unexpected_steps(
    sop_steps: List[Dict],
    execution: List[Dict]
) -> Optional[Dict]:
    sop_ids = {s["id"] for s in sop_steps}

    for e in execution:
        if e["step_id"] not in sop_ids:
            return {
                "code": "UNEXPECTED_STEP",
                "details": f"Step {e['step_id']} is not part of the SOP"
            }

    return None

def validate_duplicates(
    execution: List[Dict]
) -> Optional[Dict]:
    counts = Counter(e["step_id"] for e in execution)

    for step_id, count in counts.items():
        if count > 1:
            return {
                "code": "DUPLICATE_STEP_EXECUTION",
                "details": f"Step {step_id} executed {count} times"
            }

    return None
