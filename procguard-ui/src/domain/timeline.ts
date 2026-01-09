import { apiFetch } from "@/lib/api";

export interface TimelineCell {
    index: number;
    status: "ON_TIME" | "OVER_TIME" | "EMPTY";
    marker?: number;
    badge?: "ALERT";
    dot?: "ORANGE" | "BLUE";
}

export interface TimelineView {
    leadTime: number[];
    stages: {
        label: string;
        cells: TimelineCell[];
    }[];
    ranges: {
        label: string;
        count: number;
    }[];
}

export enum TimelineStatus {
    ON_TIME = "ON_TIME",
    OVER_TIME = "OVER_TIME",
    DEVIATION = "DEVIATION",
    LIR = "LIR",
    AT_RISK = "AT_RISK",
    RESOLVED_DELAY = "RESOLVED_DELAY",
    EMPTY = "EMPTY",
    GRAY_GHOST = "GRAY_GHOST"
}

export interface AuditMarker {
    val: string;
    type: string;
    day: number;
    warn?: boolean;
}

export interface AuditStage {
    name: string;
    cells: TimelineStatus[];
    markers: AuditMarker[];
}

export interface AuditDelayedBatch {
    batch_id: string;
    display_id: string;
    usp: string;
    dsp: string;
    start_date: string;
    estimated_end: string;
    lead_time: number;
    eos_status: string; // ON_TIME, DEVIATION, EOS
    deviation_id: string | null;
    violation_id: string | null;
    comments: string;
}

export interface Deviation {
    id: string;
    stage: string;
    deviation_type: string;
    approved_by: string;
    approved_at: string;
    valid_from_day: number;
    valid_until_day: number;
    resolved_at: string | null;
    superseded_by_lir: boolean;
}

export interface AuditTimelineResponse {
    batch_id: string;
    procedure_id: string;
    procedure_version: number;
    stages: AuditStage[];
    distribution: Record<string, number>;
    delayed_batches: AuditDelayedBatch[];
    deviations: Deviation[];
    lirs: any[];
    // Resilience & Authority Layer (ARCH-2026-SYNC-001)
    mode: "live" | "degraded";
    sync_status: "synchronized" | "bootstrapping" | "paused" | "degraded";
    last_successful_sync: string | null;
    error?: string;
}

// Reverting to throw-based logic (Pre-Resilience) -> Updating for Resilience Aware
// Enterprise Resilience Check: Never throw on circuit/network control signals
export async function getBatchTimeline(batchId: string): Promise<AuditTimelineResponse> {
    const { data, error, status } = await apiFetch(`/batches/${batchId}/timeline`);

    // Handle Circuit Breaker & Network Failures as Degraded State
    if (error === "circuit_open" || error === "network_failure" || status === 503 || status === 0) {
        console.warn(`[Resilience] Entering degraded mode due to: ${error}`);
        return {
            batch_id: batchId,
            procedure_id: "UNKNOWN",
            procedure_version: 0,
            stages: [],
            distribution: {},
            delayed_batches: [],
            deviations: [],
            lirs: [],
            mode: "degraded",
            sync_status: error === "circuit_open" ? "paused" : "degraded",
            last_successful_sync: null,
            error: typeof error === "string" ? error : "Unknown resilience event"
        };
    }

    if (error) {
        throw new Error(error);
    }

    if (!data) {
        throw new Error("No data received");
    }

    return data as AuditTimelineResponse;
}
