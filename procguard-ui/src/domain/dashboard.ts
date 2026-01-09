
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
    try {
        const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
        const res = await fetch(`${API_URL}/dashboard/summary`, {
            cache: "no-store",
            headers: {
                "Content-Type": "application/json",
            },
        })

        if (!res.ok) {
            return {
                status: "error",
                reason: `HTTP_${res.status}`,
                data: null,
            }
        }

        const rawData = await res.json()

        // Map backend snake_case to frontend camelCase
        const data: DashboardSummary = {
            totalProcedures: rawData.total_procedures,
            totalBatches: rawData.total_batches,
            completedBatches: rawData.completed_batches,
            violatedBatches: rawData.violated_batches,
            mode: rawData.mode,
        };

        return {
            status: "ok",
            data,
        }
    } catch (err) {
        console.error("Dashboard fetch failed", {
            error: err,
            service: "dashboard-summary",
            time: new Date().toISOString(),
        })

        return {
            status: "offline",
            reason: "network_failure",
            data: null,
        }
    }
}
