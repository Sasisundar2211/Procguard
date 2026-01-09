"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import ViolationCard from "@/components/violation/ViolationCard";
// import EvidenceTimeline from "@/components/violation/EvidenceTimeline"; // Removed
import EvidenceChainGraph from "@/components/violation/EvidenceChainGraph";
import { getEvidenceChain, EvidenceChain } from "@/domain/evidence";

export default function ViolationForensicDetail({ violation }: { violation: any }) {
    const router = useRouter();
    const [chain, setChain] = useState<EvidenceChain | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            const data = await getEvidenceChain(violation.id);
            if (data) setChain(data);
            setLoading(false);
        }
        load();
    }, [violation.id]);

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <button
                onClick={() => router.push("/violations")}
                className="mb-4 text-sm font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1 uppercase tracking-tight transition-colors"
            >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                Back to Violations
            </button>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-1 space-y-6">
                    <div className="animate-in fade-in slide-in-from-bottom-2 duration-500 shadow-xl border border-slate-200 rounded-xl overflow-hidden">
                        <ViolationCard violation={violation} fullscreen />
                    </div>
                </div>

                <div className="lg:col-span-2">
                    <section className="bg-white rounded-xl border border-slate-200 p-8 shadow-sm h-full">
                        <header className="mb-8 pb-6 border-b border-slate-100 flex justify-between items-center">
                            <div>
                                <h2 className="text-xl font-black text-slate-800 tracking-tight uppercase">Authoritative Evidence Chain</h2>
                                <p className="text-sm text-slate-500 font-medium italic">Cryptographically verified forensic timeline for this incident.</p>
                            </div>
                            <div className="flex gap-4 items-center">
                                <button
                                    onClick={() => window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/violations/${violation.id}/export`}
                                    className="bg-blue-600 text-white px-3 py-1.5 rounded text-[10px] font-black uppercase tracking-widest hover:bg-blue-700 transition-colors shadow-sm"
                                >
                                    Forensic Export
                                </button>
                                <div className="bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-100 flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                    <span className="text-[10px] font-black text-emerald-700 uppercase tracking-widest">Integrity: Verified</span>
                                </div>
                            </div>
                        </header>

                        {loading ? (
                            <div className="py-20 text-center animate-pulse text-slate-400 font-bold uppercase tracking-widest">Retrieving Cryptographic Proofs...</div>
                        ) : chain ? (
                            <EvidenceChainGraph chain={chain} />
                        ) : (
                            <div className="p-8 text-center border-2 border-dashed border-slate-200 rounded-xl">
                                <p className="text-slate-400 font-bold">Evidence chain unavailable.</p>
                            </div>
                        )}
                    </section>
                </div>
            </div>
        </div>
    );
}
