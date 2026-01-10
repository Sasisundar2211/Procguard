import { getBatches } from "@/domain/batches";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function BatchesPage() {
    let batches: any[] = [];
    try {
        batches = await getBatches();
    } catch (err) {
        console.error("Batch fetch failure:", err);
    }

    return (
        <div className="p-8 max-w-[1200px] mx-auto font-sans">
            <h1 className="text-3xl font-bold text-slate-800 mb-8 tracking-tight">Authoritative Batch Ledger</h1>

            <div className="grid gap-4">
                {batches.length > 0 ? (
                    batches.map((batch, index) => (
                        <Link
                            key={`${batch.batch_id}-${index}`}
                            href={`/batches/${batch.batch_id}/timeline`}
                            className="p-6 bg-white border border-slate-200 rounded-xl shadow-sm hover:shadow-md hover:border-blue-300 transition-all flex justify-between items-center group text-decoration-none"
                        >
                            <div>
                                <div className="font-bold text-slate-800 group-hover:text-blue-600 transition-colors uppercase tracking-wide">
                                    Batch #{batch.batch_id.slice(0, 8)}
                                </div>
                                <div className="text-xs text-slate-400 font-mono mt-1">ID: {batch.batch_id}</div>
                                <div className="mt-2 text-[10px] font-black uppercase tracking-[0.2em] px-2 py-0.5 bg-slate-100 rounded inline-block">
                                    {batch.current_state}
                                </div>
                            </div>
                            <div className="text-blue-500 font-bold text-sm flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                View Timeline →
                            </div>
                        </Link>
                    ))
                ) : (
                    <div className="p-12 border-2 border-dashed border-slate-200 rounded-xl text-center bg-slate-50/50">
                        <p className="text-slate-400 font-medium italic">No batches found in the legislative ledger.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
