def test_ai_output_can_be_garbage_and_system_survives():
    from app.core.procedure_validation import validate_parsed_procedure

    bad_ai_output = {
        "steps": [
            {"step_id": "x", "description": "bad", "requires_approval": True},
            {"step_id": "x", "description": "duplicate", "requires_approval": False},
        ]
    }

    try:
        validate_parsed_procedure(bad_ai_output)
        assert False, "Validation should fail"
    except ValueError:
        assert True
