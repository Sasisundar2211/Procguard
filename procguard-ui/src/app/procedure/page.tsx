import ProcedurePanel from "@/components/procedure/ProcedurePanel"
import { getProcedures } from "@/domain/procedure"

export const dynamic = "force-dynamic"

export default async function ProcedurePage() {
    const procedures = await getProcedures()

    return (
        <div className="font-sans max-w-[1600px] mx-auto p-8">
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-slate-800">Compliance Procedures</h1>
                <p className="text-slate-500 text-sm">Authoritative immutable process definitions</p>
            </div>

            <div className="grid gap-8">
                {procedures.filter(p => p.steps && p.steps.length > 0).length > 0 ? (
                    procedures
                        .filter(p => p.steps && p.steps.length > 0)
                        .map(p => (
                            <ProcedurePanel key={`${p.procedure_id}-${p.version}`} procedure={p} />
                        ))
                ) : (
                    <div className="p-12 border-2 border-dashed border-slate-200 rounded-xl text-center">
                        <p className="text-slate-400 font-medium">No procedures loaded.</p>
                        <p className="text-xs text-slate-300 mt-1">Upload a signed schema to begin.</p>
                    </div>
                )}
            </div>
        </div>
    )
}
