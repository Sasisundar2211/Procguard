from pathlib import Path


def test_ai_module_has_no_enforcement_access():
    ai_file = Path("app/ai/sop_interpreter.py")

    assert ai_file.exists(), "AI interpreter file missing"

    source = ai_file.read_text()

    forbidden_symbols = [
        "Session",
        "execute_transition",
        "Batch",
        "Violation",
        "AuditLog",
        "db",
        "sqlalchemy",
    ]

    for symbol in forbidden_symbols:
        assert symbol not in source, f"AI illegally references {symbol}"
