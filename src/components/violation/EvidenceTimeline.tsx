"use client";

import React, { useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";

import { EvidenceChain, EvidenceNode } from "@/domain/evidence";

export default function EvidenceTimeline({ violationId }: { violationId: string }) {
    const [chain, setChain] = useState<EvidenceChain | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadChain() {
            try {
                const { data, error } = await apiFetch(`/violations/${violationId}/evidence-chain`);
                if (data) setChain(data);
            } catch (e) {
                console.error("Failed to load evidence chain", e);
            } finally {
                setLoading(false);
            }
        }
        loadChain();
    }, [violationId]);

    if (loading) return <div className="p-8 text-center text-slate-400 animate-pulse font-bold uppercase tracking-widest text-xs">Assembling Forensic Chain...</div>;
    if (!chain || chain.nodes.length === 0) return (
        <div className="p-8 text-center bg-slate-50 rounded-xl border border-dashed border-slate-200">
            <p className="text-slate-400 text-sm italic font-medium">No verified evidence nodes found for this violation.</p>
        </div>
    );

    return (
        <div className="space-y-6">
            {chain.verification_level === "UNVERIFIED" && (
                <div className="bg-amber-600 text-white p-4 rounded-lg shadow-lg flex items-center gap-4 animate-pulse">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M10.29 1.5l8.83 15.17A2.3 2.3 0 0 1 17.11 21H6.89a2.3 2.3 0 0 1-2.01-3.33L13.71 1.5h-3.42z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                    <div>
                        <h4 className="font-black uppercase tracking-tighter">Chain Integrity Warning</h4>
                        <p className="text-xs font-bold opacity-90">Some nodes in the forensic chain could not be verified against the backend root of trust.</p>
                    </div>
                </div>
            )}

            <div className="relative pl-8 space-y-8 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-100">
                {chain.nodes.map((node, idx) => (
                    <div key={node.id} className="relative group">
                        {/* Status Circle */}
                        <div className={`absolute -left-[29px] top-1 w-4 h-4 rounded-full border-4 bg-white transition-all ${node.verified ? 'border-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.3)]' : 'border-amber-500'}`} />

                        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:border-blue-200 transition-all">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] block mb-1">Forensic Node {idx + 1}</span>
                                    <h5 className="text-sm font-black text-slate-800 uppercase tracking-tight">{node.type.replace(/_/g, ' ')}</h5>
                                </div>
                                <div className="text-right">
                                    <time className="text-[10px] text-slate-500 font-bold">{new Date(node.created_at).toLocaleString()}</time>
                                    <p className="text-[9px] text-slate-400 font-mono mt-0.5">{node.id.slice(0, 12)}...</p>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Created By</label>
                                    <p className="text-[10px] font-mono text-slate-600 bg-slate-50 px-2 py-1 rounded truncate border border-slate-100">{node.created_by}</p>
                                </div>
                                <div>
                                    <label className="block text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Verification</label>
                                    {node.verified ? (
                                        <p className="text-[10px] font-bold text-emerald-600 flex items-center gap-1">
                                            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4"><polyline points="20 6 9 17 4 12"></polyline></svg>
                                            HASH VALIDATED
                                        </p>
                                    ) : (
                                        <p className="text-[10px] font-bold text-amber-600 flex items-center gap-1">
                                            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                                            UNVERIFIED
                                        </p>
                                    )}
                                </div>
                            </div>

                            <div className="mt-4 pt-4 border-t border-slate-50">
                                <label className="block text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Cryptographic Fingerprint (SHA-256)</label>
                                <div className="bg-slate-900 text-emerald-400 p-3 rounded-lg font-mono text-[10px] leading-relaxed break-all shadow-inner border border-slate-800">
                                    {node.hash}
                                </div>
                                {node.parent_hash && (
                                    <div className="mt-2 flex items-center gap-2">
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" className="text-slate-300"><path d="M15 14l-3-3 3-3" /><path d="M9 10h7v4h-7z" /></svg>
                                        <span className="text-[9px] text-slate-400 font-bold uppercase tracking-tight">Chained to Parent: <span className="font-mono">{node.parent_hash.substring(0, 8)}...</span></span>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
