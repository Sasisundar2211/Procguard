# Slide: Frontend Does Not Enforce. Backend Is the Product.

## Why Our Architecture Survived Due Diligence

*   **Frontend is an Untrusted Client**
    *   It contains zero business logic. It is a "dumb" renderer.
    *   If the frontend is compromised, the backend remains secure.

*   **Single Mutation Gateway**
    *   All state changes pass through `POST /batches/{id}/event`.
    *   No backdoor APIs, no direct database access.

*   **Intent, Not State**
    *   The browser sends *intent* ("I want to approve").
    *   The server determines *state* ("New state is APPROVED").
    *   The browser never sends "status: APPROVED".

*   **Server-Side RBAC & FSM**
    *   Roles are enforced by the token, not the UI.
    *   State transitions are enforced by a mathematical Finite State Machine (FSM).
    *   The UI cannot "skip" a step because the FSM logic doesn't exist in the browser.

*   **Violations are Inevitable**
    *   We do not prevent users from *trying* illegal actions.
    *   We let them try, fail, and log the violation audit trail.

*   **AI Discipline**
    *   AI is used only for **interpretation** (explaining SOPs/Logs).
    *   AI is never used for **authority** (approving/rejecting).

> "If the frontend displays 'Approved' but the database says 'Pending', the Batch is Pending."
