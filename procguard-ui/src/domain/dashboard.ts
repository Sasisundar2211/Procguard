import { apiFetch } from "@/lib/api"

export type DashboardSummary = {
    totalProcedures: number;
    totalBatches: number;
    completedBatches: number;
    violatedBatches: number;
    mode?: "live" | "degraded";
};

export type DashboardResult =
    | { status: "ok"; data: DashboardSummary }
    | { status: "error"; reason: string; data: null }
    | { status: "offline"; reason: string; data: null };

export async function getDashboardSummary(): Promise<DashboardResult> {
    const { data, error, status } = await apiFetch("/dashboard/summary");

    if (status === 503 || error === "circuit_open" || error === "network_failure") {
        return {
            status: "offline",
            reason: "network_failure",
            data: null,
        }
    }

    if (error || !data) {
        return {
            status: "error",
            reason: error || `HTTP_${status}`,
            data: null,
        }
    }

    // Map backend snake_case to frontend camelCase
    const summary: DashboardSummary = {
        totalProcedures: data.total_procedures,
        totalBatches: data.total_batches,
        completedBatches: data.completed_batches,
        violatedBatches: data.violated_batches,
        mode: data.mode,
    };

    return {
        status: "ok",
        data: summary,
    }
}
