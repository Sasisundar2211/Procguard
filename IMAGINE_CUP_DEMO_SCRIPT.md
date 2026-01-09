# Imagine Cup 2026 - ProcGuard Audit Demo Script

## Setup
1. Ensure Backend is running: `uvicorn app.main:app --reload --port 8000`
2. Ensure Frontend is running: `npm run dev`
3. Open Browser to: `http://localhost:3000/batch-timeline/14`

## Scene 1: The Regulatory Surface (30 Seconds)

**Action**: maximizing the browser window. Mouse hover over the "Batch Timeline" header.

**Script**:
"Judges, what you are seeing is the ProcGuard Audit Surface. 
Unlike traditional manufacturing dashboards which allow operators to 'fudge' data, this view is a strictly read-only, cryptographic projection of the manufacturing state."

**Action**: Hover over the **Timeline Legend**.

**Script**:
"Every pixel here is derived from immutable event sourcing. The green 'On Time' blocks and red 'Over Time' blocks are not drawn by a UI designer—they are computed from the backend's finite state machine logic, compliant with 21 CFR Part 11."

## Scene 2: Evidence of Deviation (45 Seconds)

**Action**: Scroll slightly to the **Grid**. Point to the red "22" or "21" markers.

**Script**:
"Notice these Deviation Markers—numbers 22, 21, 20. In a typical system, an operator might suppress these warnings to rush a batch.
In ProcGuard, these are baked into the timeline. The grid structure itself enforces transparency. We can see exactly where the USP BMR Review went overtime (the red block at the start) versus where the DSP Review remained on track."

**Action**: Scroll down to **Distribution Bars** (The red bars: 100-150, 200+).

**Script**:
"This distribution summary highlights systemic risk. We instantly see 22 batches have exceeded the 200-hour lead time threshold. This isn't just a metric; it's a liability indicator that our AI has flagged for immediate QA review."

## Scene 3: The Audit Trail (45 Seconds)

**Action**: Scroll to the **Delayed Batches Table**.

**Script**:
"Finally, the 'Delayed Batches' ledger. 
Look at Batch 14. We see the exact start date, the estimated end date in red, and the 'EOS' (EndOfShift) deviation flag. 
This table is immutable. I cannot edit the lead time. I cannot delete the comments. 
(Attempt to click 'Export PDF' or a table row - demonstrate no reaction)"

**Action**: Click 'Export PDF'.

**Script**:
"The interface is locked. The only way to change this data is to execute a validated procedure in the cleanroom. 
This is how ProcGuard guarantees integrity from the factory floor to the FDA auditor's laptop."

## Closing

"ProcGuard: Mathematically defensible manufacturing compliance."
