# Judge Verification & Binding Report

## 1. Source Code Verification
**Status**: ✅ FOUND
**Path**: `/Users/djtaylor/Desktop/procguard/procguard-ui`
**Contents**:
- `src/app` (App Router structure confirmed)
- `src/components` (UI Components confirmed)
- `src/domain` (Business logic)

The "no source" risk is **ELIMINATED**. We can proceed to binding verification.

## 2. Gap Analysis (The Brutal Truth)

| UI Component | Backend Endpoint | Status | Severity |
| :--- | :--- | :--- | :--- |
| `BoardsGrid` (Dashboard) | `GET /dashboard/summary` | 🔴 HARDCODED | CRITICAL |
| `AuditLogs` (Audit table) | `GET /audit-logs` | 🔴 HARDCODED | CRITICAL |
| `BatchTimeline` | `GET /api/batch-timeline` | ⚠️ PARTIAL | HIGH |

**Findings**:
- The UI is currently a "Vibecode" shell for the Dashboard and Audit Logs.
- Data values are hardcoded arrays (`BOARDS`, `LOGS`).
- This fails the "Traceability" requirement.

## 3. Mapping Table (The Fix)

### Screen: Dashboard (`/dashboard`)
| UI Element | Backend Service | Endpoint | Request Schema | Response Schema |
| :--- | :--- | :--- | :--- | :--- |
| **Procedures Card** | `dashboard.py` | `GET /dashboard/summary` | `None` | `{ procedures: { active: int, pending: int } }` |
| **Batch State Card** | `dashboard.py` | `GET /dashboard/summary` | `None` | `{ batches: { running: int, delayed: int } }` |
| **Violation Card** | `dashboard.py` | `GET /dashboard/summary` | `None` | `{ violations: { new: int, resolved: int } }` |
| **Audit Evidence Card** | `dashboard.py` | `GET /dashboard/summary` | `None` | `{ audit: { files: int, reviews: int } }` |

### Screen: Audit Logs (`/audit`)
| UI Element | Backend Service | Endpoint | Request Schema | Response Schema |
| :--- | :--- | :--- | :--- | :--- |
| **Audit Table** | `audit_logs.py` | `GET /audit-logs` | query params | `List[AuditLogResponse]` |
| **Filters** | `audit_logs.py` | `GET /audit-logs?project=...` | query params | `List[AuditLogResponse]` |

## 4. Binding Plan (Code-Level)

### B1. Client-Side Data Fetching Strategy
We will use a strictly typed API client (or `fetch` with strict types) to ensure contract validity.

**For `BoardsGrid.tsx`:**
1.  Convert to **Server Component** (preferred for Dashboard) OR use `useEffect` (if client-side interaction needed). 
    *   *Decision*: `BoardsGrid` is purely presentational summary. We will make `DashboardPage` fetch the data server-side and pass it to `BoardsGrid`, or make `BoardsGrid` fetch its own data.
    *   *Refinement*: Since `BoardsGrid` is currently a client component (hooks implicit in Next.js app directory usually, but `page.tsx` is server by default unless 'use client').
    *   We will introduce `async function getDashboardSummary()` in `src/domain/dashboard.ts` (new file).
    *   We will call this in `BoardsGrid` (or parent `page.tsx`).

**For `AuditLogs.tsx`:**
1.  Remove `const LOGS`.
2.  Introduce `useAuditLogs` hook or Server Component data fetching.
3.  Bind table rows to the API response.

## 5. Security & Failure Review
- **Auth**: The backend endpoint `GET /dashboard/summary` requires `db: Session = Depends(get_db)`. It does *not* currently enforce `get_current_user` in the code I saw (`dashboard.py` line 14). **SECURITY GAP DETECTED**. 
    - *Remediation*: Add `user = Depends(get_current_actor)` to `dashboard_summary`.
- **Error Handling**: Configuring `GlobalExceptionHandler` in `main.py` is good, but UI must handle 500s gracefully (e.g., Error Boundary).

---

**Next Steps**:
1.  Secure the backend dashboard endpoint.
2.  Implement `src/domain/api.ts` (or similar) for type-safe fetching.
3.  Rewrite `BoardsGrid.tsx` and `AuditLogs.tsx` to use live data.
