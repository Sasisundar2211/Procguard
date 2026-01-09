from datetime import datetime, timezone


def test_enforcement_works_with_ai_disabled(
    db_session,
    batch,
    monkeypatch,
):
    monkeypatch.setenv("AI_ENABLED", "false")

    from app.core.transitions import execute_transition
    from app.core.fsm import Event, State

    execute_transition(
        db=db_session,
        batch=batch,
        event=Event.START_BATCH,
        actor="tester",
        actor_role="OPERATOR",
        occurred_at=datetime.now(timezone.utc),
    )

    db_session.refresh(batch)
    assert batch.current_state == State.IN_PROGRESS.value
