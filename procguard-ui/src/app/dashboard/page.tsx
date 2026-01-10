import { getDashboardSummary } from "@/domain/dashboard"
import DashboardClientWrapper from "./DashboardClientWrapper"
import BackendOffline from "@/components/common/BackendOffline"

export const dynamic = "force-dynamic"

export default async function DashboardPage() {
    const summary = await getDashboardSummary()

    // Soft-Fail: If server-side fetch fails, pass null to client wrapper.
    // Client wrapper will use ApiHealthContext to manage the offline state dynamically.
    const safeSummary = summary.status === "ok" ? summary.data : null;

    return (
        <DashboardClientWrapper summary={safeSummary} />
    )
}
