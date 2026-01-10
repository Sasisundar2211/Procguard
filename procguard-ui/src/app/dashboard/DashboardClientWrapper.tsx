"use client";

import { useApiHealth } from "@/context/ApiHealthContext";
import OfflineScreen from "@/components/common/OfflineScreen";
import BoardsGrid from "@/components/boards/BoardsGrid";
import { DashboardSummary } from "@/domain/dashboard";

export default function DashboardClientWrapper({ summary }: { summary: DashboardSummary | null }) {
    const { healthy } = useApiHealth();

    if (!healthy) {
        return <OfflineScreen />;
    }

    if (!summary) {
        // Client-Side Recovery Mode:
        // If server-side fetch failed, we allow the client component to attempt
        // fetching the Boards list directly. This bypasses SSR failures.
        const fallbackStats: DashboardSummary = {
            totalProcedures: 0,
            totalBatches: 0,
            completedBatches: 0,
            violatedBatches: 0,
            mode: "degraded"
        };

        return (
            <div className="font-sans max-w-[1600px] mx-auto">
                <div className="mb-4 bg-amber-50 border border-amber-200 text-amber-800 px-4 py-2 rounded-lg text-sm flex items-center justify-between">
                    <span className="font-bold">Sync Mode: Client-Side Recovery</span>
                    <span className="text-xs opacity-75">Server artifact missing, using live client data.</span>
                </div>
                <BoardsGrid stats={fallbackStats} />
            </div>
        )
    }

    return (
        <div className="font-sans max-w-[1600px] mx-auto">
            <BoardsGrid stats={summary} />
        </div>
    );
}
