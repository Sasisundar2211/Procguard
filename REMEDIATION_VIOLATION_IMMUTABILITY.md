# PROCGUARD: VIOLATION IMMUTABILITY & ARCHITECTURE REMEDIATION
**Document ID:** REM-2026-VIOL-001  
**Date:** 2026-01-09  
**Status:** REMEDIATED (Backend Hotfix Applied)  
**Classification:** ENTERPRISE AUDIT RECORD  

---

# EXECUTIVE SUMMARY

The system correctly rejected an attempt to modify an immutable **Violation** record.  
This event confirms that **Database-Level Integrity Protection** is active and authorized.

The application error (`Violation record unavailable`) was caused by a read-path operation attempting to "lazy-link" contextual data to the immutable record. This has been remediated by shifting to a **Derived Read Model**, ensuring the database remains append-only while the UI receives the necessary context.

---

# 1. DEFENSIBLE ROOT-CAUSE ANALYSIS

### Incident Trigger
The User Interface requested a specific violation record with `attach_context=True`.

### Illegal Operation
The Backend API (`app/api/violations.py`) attempted to:
1.  Query the violation.
2.  Identify recent `FilterAuditLog` activity.
3.  **UPDATE** the `violation.triggering_filter_event_id` field in the database.
4.  **COMMIT** the transaction.

### Failure Mechanism
PostgreSQL Interceptor (`forbid_violation_mutation`) blocked the `UPDATE` operation, raising a `ProgrammingError`.  
This is the **correct and intended behavior** of a forensic system.

### Root Cause
**Design Flaw in "Context Hydration":** The application conflated "Viewing Context" (mutable/transient) with "Violation Facts" (immutable). It attempted to write transient context into the immutable fact ledger.

---

# 2. IDENTIFIED ILLEGAL MUTATION PATH

**File:** `app/api/violations.py`  
**Endpoint:** `GET /violations/{violation_id}`  
**Lines:** 85-87 (Original)

```python
# ILLEGAL MUTATION BLOCK
if attach_context and not violation.triggering_filter_event_id:
    violation.triggering_filter_event_id = latest_filter.id # <--- Write to Immutable Model
    db.commit() # <--- Illegal Commit
    db.refresh(violation)
```

This path violated the **Append-Only Architecture** by attempting an in-place update during a READ operation.

---

# 3. CORRECTED BACKEND-AUTHORITATIVE DESIGN

### Architectural Decision: "Derived Read Models"

Instead of persisting the "Context Link" in the `violations` table (which locks after creation), the system now **dynamically hydrates** this link at query time.

1.  **Read:** Fetch immutable Violation from DB.
2.  **Hydrate:** Fetch relevant Filter Context from DB.
3.  **Merge:** combine into a transient `ViolationResponse` object in memory.
4.  **Return:** Send enriched object to Client.

**Database Result:** Zero writes. Immutability preserved.  
**Client Result:** Full context available.

### Remediation Code (Applied)

```python
# Enterprise Pattern: Derived Read Model (Immutable)
response = ViolationResponse.model_validate(violation)

if attach_context and not response.triggering_filter_event_id:
    latest_filter = db.query(FilterAuditLog)...first()
    if latest_filter:
        # Safe: Modifying the transient response object, NOT the database record.
        response.triggering_filter_event_id = latest_filter.id
        response.filter_context = FilterContextSchema.model_validate(latest_filter)

return response
```

---

# 4. SECURE RETRY & RE-HYDRATION FLOW

With the fix applied:
1.  **Retry Synchronization:** The UI can retry the request safely.
2.  **No Side Effects:** The request is now essentially idempotent and read-only.
3.  **Consistency:** The context returned is strictly based on the authoritative `FilterAuditLog` table, ensuring the "link" is based on proven audit data, not arbitrary updates.

---

# 5. COURT-READY AUDIT ARCHITECTURE EXPLANATION

### "Why couldn't we just update the record?"

In a forensic system, a **Violation** is a digital witness statement. It records exactly what happened at a specific moment in time.

If we allowed the system to go back and "add context" or "link events" inside the original record, we would be **rewriting history**. A defense attorney could argue: *"If the system can update the 'context' field today, how do we know it didn't update the 'severity' or 'payload' field yesterday?"*

### The "Immutable Ledger" Defense

To prevent this argument, ProcGuard enforces **strict database-level immutability**. Once a Violation is written, **no power in the universe** (not even the System Administrator) can alter a single byte of that row without triggering a tamper alert or being rejected by the database engine.

The error observed ("Violations are immutable") is proof that this defense is **working**. It protected the integrity of the evidence against a flawed software instruction.

The remediation adopted (Dynamic Hydration) allows us to **view** the connections between events (the Violation and the Filter) without **alterting** the evidence itself. This preserves the Chain of Custody while ensuring the court (and the user) sees the full picture.

---

# 6. ENTERPRISE RISK & CONTROL SUMMARY

| Control Area | Status | Notes |
| :--- | :--- | :--- |
| **Integrity** | **ENFORCED** | DB rejected illegal update. |
| **Availability** | **RESTORED** | Fix removes the blocking write operation. |
| **Confidentiality** | **UNCHANGED** | Access controls remain active. |
| **Auditability** | **PRESERVED** | No historical traces were altered. |
| **Code Quality** | **IMPROVED** | Removed side-effects from GET endpoint. |

---
**Signed by:**
*ProcGuard Enterprise Architect*
*2026-01-09*
