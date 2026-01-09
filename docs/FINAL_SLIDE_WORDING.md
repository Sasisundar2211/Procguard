# Slide: Frontend Integrity Model

## Architecture: Dumb Pipe, Sovereign Core

*   **Untrusted Client**: The browser is treated as a compromised environment by default.
*   **Intent-Only Network Traffic**: REST payloads contain *commands* (`approve_step`), never *state assertions* (`status: APPROVED`).
*   **Single Mutation Choke-Point**: All writes flow through `POST /batches/{id}/event`. No backdoor APIs.
*   **Backend Determinism**: All Roles, Sequence Logic, and AI outputs are computed server-side and immutable.
*   **Visual Transparency**: The UI displays blocking states (`403 FORBIDDEN`) verbatim, enforcing clarity over convenience.

**Verdict**: The frontend cannot weaken enforcement because it has no authority to do so.
