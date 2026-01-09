def validate_parsed_procedure(parsed) -> None:
    if not parsed["steps"]:
        raise ValueError("Procedure must contain at least one step")

    seen_ids = set()
    for step in parsed["steps"]:
        if step["step_id"] in seen_ids:
            raise ValueError("Duplicate step IDs")
        seen_ids.add(step["step_id"])
def validate_procedure_structure(structured_steps: dict):
    if "steps" not in structured_steps:
        raise ValueError("Invalid SOP structure")

    if not structured_steps["steps"]:
        raise ValueError("Procedure must contain steps")

    step_ids = [s["id"] for s in structured_steps["steps"]]

    if len(step_ids) != len(set(step_ids)):
        raise ValueError("Duplicate step IDs detected")