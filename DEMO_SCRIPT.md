# 🏆 ProcGuard - Imagine Cup World Finals Demo Script

## **The Set Up (Before Judges Arrive)**
1.  **Backend Terminal**:
    ```bash
    cd procguard
    source .venv/bin/activate
    uvicorn app.main:app --reload --port 8000
    ```
2.  **Frontend Terminal**:
    ```bash
    cd procguard/procguard-ui
    npm run dev
    # Ensure .env.local has NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
    ```
3.  **Browser**: Open `http://localhost:3000/dashboard`.
4.  **Database**: Ensure clean state if possible, or have one "Perfect Batch" ready.

---

## **ACT 1: The "Unavoidable" Guarantee (1 Minute)**
**Voiceover**: "Judges, standard compliance software is a checklist. ProcGuard is a wrapper. We don't just 'monitor' the process—we *are* the process."

1.  **Navigate to `Procedures`**: Show the list of immutable SOPs.
    *   *Action*: Click on a Procedure.
    *   *Script*: "These steps aren't text. They are cryptographic constraints."

2.  **Navigate to `Dashboard`**: Show the real-time grid.
    *   *Script*: "Every square you see here isn't a database entry. It's an event stream derived from a Finite State Machine."

---

## **ACT 2: The Happy Path (Operator View) (2 Minutes)**
1.  **Create/Start Batch**:
    *   (Use Postman or a hidden 'Start' button if UI doesn't have create yet - *NOTE: Dashboard doesn't have create. Use API or assumed start.* **Correction: Use the `scripts/manual_transition.py` or API to start a batch in background to show it appearing live.**)
    *   *Alternative*: Go to `Batch Execution` page for an existing `IN_PROGRESS` batch.

2.  **Navigate to `Batch Execution`**:
    *   *Action*: Click `Progress Step` button.
    *   *Visual*: Loading spinner -> Page Refresh -> State remains `IN_PROGRESS` or moves to next step.
    *   *Script*: "I am the Operator. I signal intent. The backend validates my role, the time, and the procedure version. If I am 1ms off, it fails."

3.  **Request Approval**:
    *   *Action*: Click `Request Approval`.
    *   *Result*: state changes to `AWAITING_APPROVAL`.
    *   *Script*: "I cannot proceed. The physics of the system prevent it. The button to 'Approve' is visibly disabled for me (or leads to error) because I am an Operator, not a Supervisor."

---

## **ACT 3: The Attack (Auditor/Judge View) (2 Minutes)**
**Voiceover**: "Now, let's try to break it. This is what you are looking for."

1.  **The "Inspect Element" Attack**:
    *   *Action*: Open DevTools. Find the "Approve" button (if visible) or the "Progress" button.
    *   *Action*: Try to enable a disabled button or replay a request via Network tab with a modified payload (e.g. `"approval_required": false`).
    *   *Result*: Backend returns `409 Conflict` or `403 Forbidden`.
    *   *Script*: "The frontend is a dumb terminal. It sends intent. The backend State Machine rejects the invalid transition immediately."

2.  **The "Rogue Admin" Attack**:
    *   *Script*: "Even if I steal the Admin's JWT..."
    *   *Action*: Go to `Audit Evidence` page.
    *   *Action*: Click on a specific Batch ID.
    *   *Script*: "I cannot delete this log. PostgreSQL Row-Level Security and Event Sourcing mean the 'Delete' command does not exist in our schema for audit records."

---

## **ACT 4: The Violation (Ai Enforcement) (1 Minute)**
1.  **Trigger Violation** (Background script or specific "Bad Event"):
    *   *Action*: Submit a temperature reading that is out of bounds (if implemented) or skip a step.
    *   *Result*: State instantly flips to `VIOLATED`.
    *   *Visual*: Red badge appears on Dashboard.
    *   *Script*: "The AI detected a discrepancy. The batch is now dead. No human can unlock it. It requires a hard-fork or an external Auditor Reset (not available in MVP)."

---

## **CLOSING Statement**
"ProcGuard isn't just software. It is Digital Law. Thank you."
