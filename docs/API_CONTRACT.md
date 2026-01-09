# API Contract for ProcGuard
**Status**: Frozen / Read-Only
**Last Verified**: 2026-01-07

## Overview
This document defines the strict, immutable contract between the ProcGuard Backend and UI.
Any UI deviation from this contract is a violation of audit integrity.

## 1. Batch Timeline (Audit View)
**Endpoint**: `GET /api/batch-timeline/{batch_id}`
**Access**: Read-Only
**Purpose**: Returns the authoritative, calculated snapshot of a batch's audit timeline. The UI MUST render this exactly as received.

### Response Schema
```json
{
  "batch_id": "string (uuid)",
  "procedure_id": "string (uuid)",
  "procedure_version": "integer",
  "stages": [
    {
      "name": "string (Stage Label)",
      "cells": [
        "string (Enum: ON_TIME | OVER_TIME | EMPTY | GRAY_GHOST)"
      ],
      "markers": [
        {
          "val": "string (e.g. '21')",
          "type": "string (e.g. 'box', 'lir', 'lir-warn')",
          "day": "integer (0-69)",
          "warn": "boolean (optional)"
        }
      ]
    }
  ],
  "distribution": {
    "100_150": "integer",
    "200_plus": "integer"
    // ... dynamic keys allowed for buckets
  },
  "delayed_batches": [
    {
      "batch": "integer (ID)",
      "usp": "string",
      "dsp": "string",
      "start_date": "string",
      "estimated_end": "string",
      "lead_time": "integer (days)",
      "eos": "boolean",
      "comments": "string"
    }
  ]
}
```

### Immutable Fields (UI Must Not Compute)
*   `cells`: The backend decides if a day is Green, Red, or Empty.
*   `markers`: The backend decides where approval stamps go.
*   `delayed_batches`: The backend decides which batches are "delayed".

## 2. Batches
**Endpoint**: `GET /batches/{id}`

### Response Schema
```json
{
  "batch_id": "uuid",
  "procedure_id": "uuid",
  "procedure_version": 1,
  "current_state": "string (e.g. 'CREATED', 'LOCKED')",
  "created_at": "timestamp"
}
```

## 3. Enforce Progress
**Endpoint**: `POST /batches/{id}/attempt-progress` or similar (TBD)

*Currently defined via `events` or state transitions.*

---
**Verification Rule**:
If the UI displays a state (e.g., "Step 3 Complete") that cannot be found in these JSON responses, the UI is lying.
