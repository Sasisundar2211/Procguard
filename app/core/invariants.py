# app/core/invariants.py

from app.core.fsm import State

# Closed set of terminal states
TERMINAL_STATES = {
    State.COMPLETED,
    State.VIOLATED,
    State.REJECTED,
}


def is_terminal(state: State) -> bool:
    return state in TERMINAL_STATES
