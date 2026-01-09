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
        return (
             <div className="flex flex-col items-center justify-center min-h-[400px] p-8 bg-white rounded-xl border border-slate-200 shadow-sm">
                <h2 className="text-2xl font-bold text-slate-800 mb-2">Dashboard unavailable</h2>
                <p className="text-slate-500 italic">Please try again later. (API Connectivity Issue)</p>
            </div>
        )
    }

    return (
        <div className="font-sans max-w-[1600px] mx-auto">
            <BoardsGrid stats={summary} />
        </div>
    );
}
