def test_invalid_transition_creates_violation(db_session, batch):
    from app.core.transitions import execute_transition
    from app.core.fsm import Event

    with pytest.raises(RuntimeError):
        execute_transition(
            db=db_session,
            batch=batch,
            event=Event.APPROVE_STEP,
            actor="user",
            occurred_at=datetime.utcnow(),
        )

    violations = db_session.query(Violation).all()
    assert len(violations) == 1
