import { Violation } from "@/domain/violations"

export default function ViolationCard({
    violation,
    fullscreen = false
}: {
    violation: Violation;
    fullscreen?: boolean
}) {
    return (
        <div className={
            fullscreen
                ? "w-full max-w-none rounded-none shadow-none bg-white p-8"
                : "max-w-3xl border p-6 rounded-lg shadow bg-white hover:border-rose-300 transition-all cursor-pointer"
        }>
            <h1 className="text-lg font-bold text-rose-600 flex items-center gap-2">
                <span className="w-2 h-6 bg-rose-500 rounded-full" />
                Violation Detected
            </h1>

            <ul className="mt-6 space-y-3 text-sm">
                <li className="flex justify-between border-b border-slate-50 pb-2">
                    <span className="text-slate-500 font-medium tracking-tight">Violation ID</span>
                    <span className="font-mono text-slate-800 text-xs">{violation.id}</span>
                </li>
                <li className="flex justify-between border-b border-slate-50 pb-2">
                    <span className="text-slate-500 font-medium tracking-tight">Batch ID</span>
                    <span className="font-mono text-slate-800 text-xs">{violation.batch_id}</span>
                </li>
                <li className="flex justify-between border-b border-slate-50 pb-2">
                    <span className="text-slate-500 font-medium tracking-tight">Rule Violated</span>
                    <span className="text-slate-800 font-semibold">{violation.rule}</span>
                </li>
                <li className="flex justify-between border-b border-slate-50 pb-2">
                    <span className="text-slate-500 font-medium tracking-tight">Detected At</span>
                    <span className="text-slate-800 font-medium tracking-tighter">{new Date(violation.detected_at).toLocaleString()}</span>
                </li>
                <li className="flex justify-between border-b border-slate-50 pb-2">
                    <span className="text-slate-500 font-medium tracking-tight">Resolution Status</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${violation.status === "RESOLVED" ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700"}`}>
                        {violation.status}
                    </span>
                </li>
                {violation.sop && (
                    <li className="flex justify-between border-b border-slate-50 pb-2">
                        <span className="text-slate-500 font-medium tracking-tight">Invoked SOP</span>
                        <span className="text-blue-600 font-bold uppercase text-[10px] flex items-center gap-1">
                            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                            {violation.sop.name} v{violation.sop.version}
                        </span>
                    </li>
                )}
            </ul>

            {violation.filter_context && (
                <div className="mt-6 p-4 bg-emerald-50/50 rounded border border-emerald-100">
                    <h3 className="text-[10px] font-black text-emerald-600 uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"></path></svg>
                        Filter Context at Detection
                    </h3>
                    <div className="grid grid-cols-2 gap-4 text-xs">
                        <div>
                            <span className="block text-slate-400 font-bold uppercase text-[9px]">Time Range Mode</span>
                            <span className="text-slate-700 font-bold">{violation.filter_context.filter_payload.timeFilter?.mode || "PRESET"}</span>
                        </div>
                        <div>
                            <span className="block text-slate-400 font-bold uppercase text-[9px]">Domain Scope</span>
                            <span className="text-slate-700 font-bold text-blue-600">{violation.filter_context.filter_payload.domain || "SYSTEM"}</span>
                        </div>
                        <div>
                            <span className="block text-slate-400 font-bold uppercase text-[9px]">Reviewing User</span>
                            <span className="text-slate-700 font-bold">{violation.filter_context.user_id}</span>
                        </div>
                        <div>
                            <span className="block text-slate-400 font-bold uppercase text-[9px]">Filter Hash (Fingerprint)</span>
                            <span className="text-emerald-700 font-mono text-[10px] bg-white px-1 border border-emerald-100 rounded">{violation.filter_context.hash.substring(0, 16)}...</span>
                        </div>
                    </div>
                </div>
            )}

            {(violation as any).opa_decision_hash && (
                <div className="mt-6 p-4 bg-orange-50/50 rounded border border-orange-100">
                    <h3 className="text-[10px] font-black text-orange-600 uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg>
                        Forensic Chain of Custody
                    </h3>
                    <div className="space-y-3 text-xs">
                        <div>
                            <span className="block text-slate-400 font-bold uppercase text-[9px]">Root OPA Decision Hash</span>
                            <span className="text-orange-700 font-mono text-[10px] bg-white px-1 border border-orange-100 rounded block truncate">{(violation as any).opa_decision_hash}</span>
                        </div>
                        <div>
                            <span className="block text-slate-400 font-bold uppercase text-[9px]">Violation Record Hash</span>
                            <span className="text-slate-700 font-mono text-[10px] bg-white px-1 border border-slate-200 rounded block truncate">{(violation as any).violation_hash || "N/A"}</span>
                        </div>
                    </div>
                </div>
            )}

            <div className="mt-6 p-4 bg-slate-50 rounded border border-slate-100">
                <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2">Automated Enforcement Action</h3>
                <p className="text-sm text-slate-600 leading-relaxed font-medium tracking-tight">
                    Procedure has been <strong className="text-slate-900">automatically locked</strong>. No further transitions will be accepted until this violation is reviewed by a QA lead and resolved in the audit trail.
                </p>
            </div>
        </div>
    )
}
