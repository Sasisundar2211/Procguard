import { Procedure } from "@/domain/procedure"

export default function ProcedurePanel({ procedure }: { procedure: Procedure }) {
    const steps = procedure.steps || []

    return (
        <div className="w-full max-w-none min-h-[420px] bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-100 bg-slate-50/50 flex justify-between items-start">
                <div>
                    <h1 className="text-xl font-bold text-slate-800 tracking-tight">
                        {procedure.name}
                    </h1>
                    <div className="flex items-center gap-3 mt-1 text-xs font-medium uppercase tracking-wider">
                        <span className="text-slate-400">Ver: {procedure.version}</span>
                        <span className="text-slate-300">|</span>
                        <span className="text-blue-600">ID: {procedure.procedure_id}</span>
                    </div>
                </div>
            </div>

            <div className="p-6">
                <p className="text-slate-600 text-sm mb-8 leading-relaxed italic">
                    {procedure.description}
                </p>

                <h3 className="font-bold text-slate-800 text-sm mb-4 flex items-center gap-2">
                    <span className="w-1.5 h-4 bg-blue-500 rounded-full" />
                    Enforcement Schema Definition
                </h3>

                <div className="space-y-3">
                    {steps.length > 0 ? (
                        steps.map((step, idx) => (
                            <div
                                key={step.step_id}
                                className="flex items-center justify-between border border-slate-100 p-4 rounded-lg bg-white hover:border-blue-100 transition-colors group"
                            >
                                <div className="flex items-center gap-4">
                                    <span className="w-8 h-8 rounded bg-slate-100 text-slate-500 flex items-center justify-center font-bold text-xs group-hover:bg-blue-50 group-hover:text-blue-600 transition-colors">
                                        {step.step_order}
                                    </span>
                                    <span className="text-sm font-semibold text-slate-700">{step.step_name}</span>
                                </div>
                                {step.requires_approval && (
                                    <span className="text-[10px] font-bold text-blue-700 bg-blue-50 px-2.5 py-1 rounded-md uppercase tracking-wide ring-1 ring-blue-100">
                                        Approval Required
                                    </span>
                                )}
                            </div>
                        ))
                    ) : (
                        <div className="p-8 border border-dashed border-slate-200 rounded-lg text-center text-slate-400 text-sm">
                            No step definitions found in schema.
                        </div>
                    )}
                </div>

                <div className="mt-8 pt-6 border-t border-slate-100 text-[10px] text-slate-400 font-mono">
                    Created at: {new Date(procedure.created_at).toISOString()}
                </div>
            </div>
        </div>
    )
}
