# 🛡️ JUDGES DEFENSE CHEAT SHEET
**"The Courtroom Strategy"**

## 🔴 SCENARIO 1: THE "SKIP APPROVAL" ATTACK
**Judge Action:** "I’m going to use Postman to bypass your UI and force a 'Progress' event without approval."
**Your Response:** "Please do. The system expects intent, but enforces invariants."
**What Happens:**
1.  Backend receives `progress_step`.
2.  FSM checks `approval_required: true`.
3.  FSM checks `approval_present: false`.
4.  **RESULT:** Immediate transition to `VIOLATED`.
5.  **Audit:** `VIOLATION_MISSING_APPROVAL` logged.
**Key Line:** "We don't warn. We violate. The constraint is structural, not cosmetic."

## 🔴 SCENARIO 2: THE "UI BYPASS" ATTACK
**Judge Question:** "How do I know the frontend isn't hiding logic?"
**Your Response:** "The frontend is a dumb terminal. It sends 0 state payload."
**Proof:**
1.  Show `api/events.py`: "We ignore the payload."
2.  Show `schemas.py`: "The schema forbids state parameters."
3.  **Result:** Even if they send `{"approval_required": false}`, the backend ignores it and derives truth from the DB/Procedure.

## 🔴 SCENARIO 3: THE "AI HALLUCINATION" ATTACK
**Judge Question:** "What if the AI makes a mistake and approves a bad batch?"
**Your Response:** "AI **cannot** approve batches. AI is outside the control loop."
**Proof:**
1.  **Enforcement:** Pure Python `transitions.py` (Deterministic Code).
2.  **AI Role:** Only used to *explain* the `VIOLATION` after it happens.
3.  **Safety:** If AI is offline, the system still blocks violations perfectly.

## 🔴 SCENARIO 4: THE "ROGUE ADMIN" ATTACK
**Judge Question:** "I have DB admin access. I'll delete the audit log."
**Your Response:** "PostgreSQL itself will stop you."
**Proof:**
1.  Navigate to `Audit` page.
2.  Show the "Immutability Verification" from the demo script.
3.  Citation: "Row-Level Security and Event Sourcing logic prevents deletion of committed legal records."

---
## 🏆 CLOSING STATEMENT
"Standard compliance software is a checklist. ProcGuard is a wrapper. We don't just monitor the process—we *are* the process."
