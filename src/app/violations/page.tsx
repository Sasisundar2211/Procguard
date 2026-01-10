import ViolationCard from "@/components/violation/ViolationCard"
import { getViolations } from "@/domain/violations"
import Link from "next/link"

import BackendOffline from "@/components/common/BackendOffline"

export const dynamic = "force-dynamic"

export default async function ViolationsPage() {
    const result = await getViolations();

    if (result.status !== "ok") {
        return (
            <div className="font-sans max-w-[1200px] mx-auto p-8">
                <BackendOffline
                    reason={result.reason}
                />
            </div>
        );
    }

    const violations = result.data || [];

    return (
        <div className="font-sans max-w-[1200px] mx-auto p-8">
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Violation Management</h1>
                <p className="text-slate-500 text-sm font-medium">Real-time enforcement breach monitoring</p>
            </div>

            <div className="grid gap-6">
                {violations.length > 0 ? (
                    violations.map(v => (
                        <Link key={v.id} href={`/violations/${v.id}`} className="block transition-transform hover:scale-[1.01] active:scale-[0.99]">
                            <ViolationCard violation={v} />
                        </Link>
                    ))
                ) : (
                    <div className="p-12 border-2 border-dashed border-slate-200 rounded-xl text-center bg-slate-50/50">
                        <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <p className="text-slate-600 font-bold">No active violations detected.</p>
                        <p className="text-xs text-slate-400 mt-1 uppercase tracking-widest font-semibold">System integrity confirmed</p>
                    </div>
                )}
            </div>
        </div>
    )
}
