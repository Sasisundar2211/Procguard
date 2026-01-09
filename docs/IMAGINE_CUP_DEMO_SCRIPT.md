# Imagine Cup 2026 - Final Demo Script
## ProcGuard: Deterministic Compliance Enforcement

**Time Allocation:** 7-8 Minutes
**Speakers:** 1 or 2 (Narrator + Operator)

---

### 1️⃣ Opening (30 Seconds)
**Visual:** Slide with "ProcGuard" logo and "Code-Based Enforcement".
**Narrator:**
"ProcGuard is a deterministic compliance enforcement engine. In high-stakes manufacturing, 'trust but verify' is not enough. We enforce **Process-as-Code**.
Our system guarantees that no physical step can proceed without cryptographic proof of prior approval. It enforces this using code, database schemas, and mathematical state machines—not AI judgment, and not frontend logic."

---

### 2️⃣ The Frontend: Untrusted & Read-Only (1 Minute)
**Visual:** Navigate to ProcGuard Dashboard -> Click on "Active" Batch -> Show Timeline.
**Action:** Scroll through the timeline grid. Hover over a "Gray Ghost" (future) day.
**Narrator:**
"What you are seeing is the ProcGuard Dashboard.
I want to be clear: **This frontend is an untrusted client.**
It contains zero business logic. It does not calculate timelines, it does not infer status, and it cannot 'decide' anything.
It is a pure projection of the backend's immutable state. If we deleted this UI code right now, the enforcement in the backend would remain 100% intact."

---

### 3️⃣ Live Attack: Attempting to Skip Approval (1 Minute)
**Visual:** Locate the "Attempt Progress" button on the Batch Header.
**Context:** The current step requires approval (e.g., `qa_bmr_review`).
**Action:** **Operator clicks 'Attempt Progress' immediately.**
*UI shows loading spinner... then displays "BLOCKED: Approval Required" error message.*
**Narrator:**
"Watch closely. We just tried to force the batch forward without approval.
The frontend didn't stop us—the **Backend** did.
Ideally, the UI implies you can't do this, but we specifically allow the *attempt* to prove the underlying security.
The system rejected the transition, returned a 403 Forbidden, and... let's check the audit."

---

### 4️⃣ The Consequence: Immutable Violation (1 Minute)
**Visual:** Refresh the page or navigate to the "Audit/Violations" board.
**Action:** Show the newly created Audit Log entry.
**Narrator:**
"There are no warnings in ProcGuard. There are only facts.
by attempting that illegal move, we generated a permanent **Violation Record** in the database.
Here it is:
*   **Actor:** `demo_user`
*   **Action:** `progress_step`
*   **Result:** `VIOLATION`
*   **Timestamp:** [Current Time]
This log is immutable. An auditor one year from now will see that we tried to break the rules today."

---

### 5️⃣ The Happy Path: Deterministic Approval (1 Minute)
**Visual:** Go back to the Batch Timeline.
**Action:** Click "Approve qa_bmr_review" (Impersonating Supervisor).
*UI waits... then refreshes.*
**Action:** Now click "Attempt Progress".
*UI updates to the next step.*
**Narrator:**
"Now we follow the protocol. The Supervisor submits a cryptographic approval.
The backend validates the role, updates the state machine, and *only then* allows the progress event.
Notice the timeline updated instantly? That's not a frontend trick. That's a fresh fetch of the new server-side truth."

---

### 6️⃣ AI Discipline: Explanation, Not Decision (1 Minute)
**Visual:** Click on a Violation to see details (or hover).
**Action:** (If implemented) Show AI text explaining *why* it failed.
**Narrator:**
"We use AI in ProcGuard, but with extreme discipline.
AI **explains** violations. It never **decides** them.
If the AI hallucinates, it might give a confusing explanation, but it can never force a batch forward or bypass a safety check. The enforcement kernel is pure Python and SQL."

---

### 7️⃣ Deployment & Trust (1 Minute)
**Visual:** Show Azure Portal or "Deployment" Slide.
**Narrator:**
"ProcGuard is designed for the regulated enterprise.
It deploys entirely inside the customer's Azure tenant.
It has zero dependency on our servers.
It requires clear network isolation.
This isn't a SaaS wrapper; it's infrastructure code."

---

### 8️⃣ Closing (30 Seconds)
**Visual:** "ProcGuard: Enforcement Infrastructure" Slide.
**Narrator:**
"ProcGuard proves that compliance doesn't have to be a bureaucracy. It can be a computable guarantee.
This is not just a demo. This is enforcement infrastructure.
Thank you."
