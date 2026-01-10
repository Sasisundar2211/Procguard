"use client";

import { AuditDelayedBatch } from "@/domain/timeline";
import { useRouter } from "next/navigation";

interface DelayedBatchesTableProps {
    batches: AuditDelayedBatch[];
}

export default function DelayedBatchesTable({ batches }: DelayedBatchesTableProps) {
    const router = useRouter();

    const onEosClick = (batch: AuditDelayedBatch) => {
        // PHASE 2.2: Correct routing using canonical IDs
        if (batch.eos_status === "DEVIATION" && batch.deviation_id) {
            // For now, redirect to batch view or specific deviation if available
            router.push(`/batches/${batch.batch_id}/timeline`);
        } else if (batch.eos_status === "EOS" && batch.violation_id) {
            router.push(`/violations/${batch.violation_id}`);
        }
    };

    return (
        <div className="mt-8 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
            <div className="bg-slate-50/50 p-4 border-b border-slate-100 flex justify-between items-center cursor-pointer hover:bg-slate-50 transition-colors">
                <div className="flex items-center gap-2">
                    <div className="w-1 h-4 bg-rose-500 rounded-full" />
                    <h3 className="font-bold text-slate-800 text-sm">Delayed Batches</h3>
                </div>
                <ChevronDownIcon />
            </div>

            <table className="w-full text-xs text-left">
                <thead>
                    <tr className="border-b border-slate-100 text-slate-500 font-bold uppercase tracking-wider bg-slate-50/30 text-[10px]">
                        <th className="p-4 w-16">BATCH</th>
                        <th className="p-4 w-48 text-center">BATCH NUMBERS</th>
                        <th className="p-4">START DATE</th>
                        <th className="p-4">EST_END</th>
                        <th className="p-4">LEAD TIME</th>
                        <th className="p-4">EOS STATUS</th>
                        <th className="p-4 w-1/3">COMMENTS</th>
                    </tr>
                </thead>
                <tbody className="text-slate-700 font-medium">
                    {batches.map((batch, index) => (
                        <tr
                            key={`${batch.batch_id}-${index}`}
                            className="border-b border-slate-50 last:border-0 hover:bg-blue-50/30 transition-colors"
                        >
                            <td className="p-4">
                                <div className="flex items-center gap-2">
                                    <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 border border-blue-200 flex items-center justify-center font-bold text-[10px]">
                                        {batch.display_id}
                                    </div>
                                </div>
                            </td>
                            <td className="p-4">
                                <div className="flex flex-col items-center justify-center gap-1">
                                    <div className="flex items-center gap-2 bg-slate-100/50 px-2 py-0.5 rounded border border-slate-200 w-full max-w-[120px]">
                                        <span className="text-slate-400 w-4 text-[8px] uppercase font-bold">USP</span>
                                        <span className="font-mono text-slate-600 text-[10px]">{batch.usp}</span>
                                    </div>
                                    <div className="flex items-center gap-2 bg-slate-100/50 px-2 py-0.5 rounded border border-slate-200 w-full max-w-[120px]">
                                        <span className="text-slate-400 w-4 text-[8px] uppercase font-bold">DSP</span>
                                        <span className="font-mono text-slate-600 text-[10px]">{batch.dsp}</span>
                                    </div>
                                </div>
                            </td>
                            <td className="p-4 text-slate-500">{batch.start_date}</td>
                            <td className="p-4">
                                <span className="text-rose-600 font-semibold">
                                    {batch.estimated_end}
                                </span>
                            </td>
                            <td className="p-4">
                                <span className="font-bold text-slate-800">{batch.lead_time}</span>
                                <span className="text-slate-400"> days</span>
                            </td>
                            <td className="p-4">
                                <button
                                    onClick={() => onEosClick(batch)}
                                    title={batch.eos_status === "DEVIATION" ? "Delay covered by approved deviation" : "End-of-schedule breach without approval"}
                                    className="group flex items-center transition-transform hover:scale-105"
                                >
                                    {batch.eos_status === "DEVIATION" ? (
                                        <span className="bg-orange-100 text-orange-700 border border-orange-200 px-2 py-1 rounded-md font-bold text-[10px] uppercase shadow-sm">
                                            Deviation
                                        </span>
                                    ) : batch.eos_status === "EOS" ? (
                                        <span className="bg-rose-100 text-rose-700 border border-rose-200 px-2 py-1 rounded-md font-bold text-[10px] uppercase shadow-sm">
                                            EOS Breach
                                        </span>
                                    ) : (
                                        <span className="bg-emerald-100 text-emerald-700 border border-emerald-200 px-2 py-1 rounded-md font-bold text-[10px] uppercase shadow-sm">
                                            On Time
                                        </span>
                                    )}
                                </button>
                            </td>
                            <td className="p-4 text-slate-400 italic font-normal">{batch.comments}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

function ChevronDownIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
    )
}
