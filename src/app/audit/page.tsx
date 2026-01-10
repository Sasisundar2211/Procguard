import AuditLogs from "@/components/audit/AuditLogs"

export const dynamic = "force-dynamic"

export default function AuditPage() {
    return (
        <div className="font-sans max-w-[1600px] mx-auto">
            <AuditLogs />
        </div>
    )
}
