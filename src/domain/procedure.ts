import { apiFetch } from "@/lib/api";

export interface ProcedureStep {
    step_id: string;
    step_order: number;
    step_name: string;
    requires_approval: boolean;
    approver_role: string | null;
}

export interface Procedure {
    procedure_id: string;
    version: number;
    name: string;
    description: string;
    steps: ProcedureStep[];
    created_at: string;
}

export interface ProcedureView {
    name: string;
    version: string;
    purpose: string;
    steps: {
        order: number;
        label: string;
        requiresApproval: boolean;
    }[];
}

export type ProceduresResult =
    | { status: "ok"; data: Procedure[] }
    | { status: "error"; reason: string; data: null }
    | { status: "offline"; reason: string; data: null };

export async function getProcedures(): Promise<ProceduresResult> {
    try {
        const { data, error, status } = await apiFetch("/procedures/");

        if (status === 503 || error === "circuit_open" || error === "network_failure") {
            return {
                status: "offline",
                reason: "network_failure",
                data: null,
            };
        }

        if (error || !data) {
            return {
                status: "error",
                reason: error || `HTTP_${status}`,
                data: null,
            };
        }

        return {
            status: "ok",
            data: data as Procedure[],
        };
    } catch (err) {
        return {
            status: "offline",
            reason: "network_failure",
            data: null,
        };
    }
}
