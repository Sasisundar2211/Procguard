import { apiFetch } from "@/lib/api";

export interface FilterContext {
    id: string;
    screen: string;
    filter_payload: any;
    user_id: string;
    hash: string;
    created_at: string;
}

export interface SOP {
    id: string;
    name: string;
    version: number;
    immutable_hash: string;
}

export interface Violation {
    id: string;
    batch_id: string;
    rule: string;
    detected_at: string;
    status: "OPEN" | "RESOLVED";
    triggering_filter_event_id?: string;
    filter_context?: FilterContext;
    sop?: SOP;
}


export type ViolationsResult =
    | { status: "ok"; data: Violation[] }
    | { status: "error"; httpStatus?: number; reason: string; data: null }
    | { status: "offline"; reason: string; data: null };

export async function getViolations(): Promise<ViolationsResult> {
    try {
        const { data, error, status } = await apiFetch("/violations/");

        if (error) {
            return {
                status: "error",
                httpStatus: status,
                reason: error,
                data: null,
            };
        }

        return {
            status: "ok",
            data: data as Violation[],
        };
    } catch (err) {
        return {
            status: "offline",
            reason: "network_failure",
            data: null,
        };
    }
}

export async function getViolation(violationId: string): Promise<Violation> {
    /**
     * Authoritative Forensic Fetch. 
     * Uses canonical UUID for record identity.
     * Attaches current filter context for cross-linking (Step 3).
     */
    const { data, error, status } = await apiFetch(`/violations/${violationId}?attach_context=true`);
    if (error) {
        const e: any = new Error(error);
        e.status = status;
        throw e;
    }
    return data;
}
