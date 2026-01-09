import { getDashboardSummary } from "@/domain/dashboard"
import DashboardClientWrapper from "./DashboardClientWrapper"
import BackendOffline from "@/components/common/BackendOffline"

export const dynamic = "force-dynamic"

export default async function DashboardPage() {
    const summary = await getDashboardSummary()

    if (summary.status !== "ok") {
        return <BackendOffline reason={summary.reason} />
    }

    return (
        <DashboardClientWrapper summary={summary.data} />
    )
}
