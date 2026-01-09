"use client";

import React, { useState } from "react";
import { EvidenceChain, EvidenceNode } from "@/domain/evidence";

interface EvidenceChainGraphProps {
    chain: EvidenceChain;
}

const TYPE_COLORS: Record<string, string> = {
    "VIOLATION": "bg-rose-100 text-rose-700 border-rose-200",
    "OPA_DECISION": "bg-indigo-100 text-indigo-700 border-indigo-200",
    "SOP": "bg-slate-100 text-slate-700 border-slate-200",
    "ENFORCEMENT": "bg-amber-100 text-amber-700 border-amber-200",
    "EVIDENCE": "bg-blue-100 text-blue-700 border-blue-200",
    "AUDIT_EVENT": "bg-emerald-100 text-emerald-700 border-emerald-200",
};

export default function EvidenceChainGraph({ chain }: EvidenceChainGraphProps) {
    const [selectedNode, setSelectedNode] = useState<EvidenceNode | null>(null);

    return (
        <div className="flex flex-col gap-4">
            {/* Authoritative Header (Part 5.2.A) */}
            <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Evidence Status:</span>
                        {chain.verification_level === "FULL" ? (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">
                                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                🟢 VERIFIED
                            </span>
                        ) : chain.verification_level === "PARTIAL" ? (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200">
                                <div className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                🟡 PARTIALLY VERIFIED
                            </span>
                        ) : (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-200">
                                <div className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                                ⚪ UNVERIFIED
                            </span>
                        )}
                    </div>

                    {chain.snapshot_anchor && (
                        <div className="flex items-center gap-2 border-l border-slate-100 pl-4">
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Snapshot:</span>
                            <span className="text-[10px] font-mono text-slate-600 bg-slate-50 px-2 py-0.5 rounded border border-slate-200">
                                #SNP-{chain.snapshot_anchor.snapshot_id.slice(0, 8)}
                            </span>
                            <span className="text-[10px] text-slate-400 italic">
                                Sealed {new Date(chain.snapshot_anchor.sealed_at).toLocaleTimeString()} UTC
                            </span>
                        </div>
                    )}
                </div>

                <div className="text-[10px] font-mono text-slate-400 select-all cursor-help" title="Merkle Root of entire forensic chain">
                    ROOT: {chain.chain_hash.slice(0, 24)}...
                </div>
            </div>

            <div className="flex gap-6 h-full min-h-[500px]">
                {/* Graph Column */}
                <div className="flex-1 flex flex-col items-center py-8 relative">
                    {/* Central Line */}
                    <div className="absolute top-8 bottom-8 left-1/2 w-0.5 bg-slate-200 -z-10" />

                    {chain.nodes.map((node, index) => (
                        <div key={node.id} className="relative flex flex-col items-center mb-12 last:mb-0 w-full group">
                            {/* Node Card */}
                            <button
                                onClick={() => setSelectedNode(node)}
                                className={`w-64 bg-white border-2 rounded-xl p-4 shadow-sm hover:shadow-md transition-all text-left relative z-10 ${selectedNode?.id === node.id ? "border-blue-500 ring-2 ring-blue-100" : "border-slate-200 hover:border-slate-300"
                                    }`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex items-center gap-2">
                                        <span className={`text-[10px] font-black px-2 py-0.5 rounded uppercase ${TYPE_COLORS[node.type] || "bg-gray-100 text-gray-700"}`}>
                                            {node.type.replace("_", " ")}
                                        </span>
                                        {node.verified ? (
                                            <div className="w-3 h-3 text-emerald-500" title="Cryptographically Verified">
                                                <svg fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                                            </div>
                                        ) : (
                                            <div className="w-3 h-3 text-slate-300" title="Integrity Check Pending">
                                                <svg fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" /></svg>
                                            </div>
                                        )}
                                    </div>
                                    <span className="text-[10px] font-mono text-slate-400">
                                        {new Date(node.created_at).toLocaleTimeString()}
                                    </span>
                                </div>
                                <div className="font-mono text-xs text-slate-600 truncate mb-1">
                                    {node.id.slice(0, 12)}...
                                </div>
                                <div className="flex items-center gap-1 text-[9px] text-slate-400 font-mono">
                                    <div className="w-2 h-2 rounded-full bg-slate-300" />
                                    {node.hash.slice(0, 12)}...
                                </div>
                            </button>

                            {/* Connection Arrow (except last) */}
                            {index !== chain.nodes.length - 1 && (
                                <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-slate-300">
                                    ↓
                                </div>
                            )}
                        </div>
                    ))}

                    {/* Chain Hash Footer */}
                    <div className="mt-8 pt-4 border-t border-slate-200 font-mono text-[10px] text-slate-400 text-center bg-slate-50 px-4 py-2 rounded-full">
                        CHAIN MERKLE ROOT: {chain.chain_hash.slice(0, 16)}...
                    </div>
                </div>

                {/* Details Panel */}
                <div className="w-96 border-l border-slate-200 bg-slate-50/50 p-6 overflow-y-auto rounded-r-xl">
                    {selectedNode ? (
                        <div className="animate-fade-in">
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide">Node Inspection</h3>
                                <button onClick={() => setSelectedNode(null)} className="text-slate-400 hover:text-slate-600">×</button>
                            </div>

                            <div className="space-y-6">
                                <div>
                                    <label className="text-[10px] font-bold text-slate-400 uppercase block mb-1">Identity</label>
                                    <div className="font-mono text-xs bg-white border border-slate-200 rounded p-2 text-slate-700 break-all">
                                        {selectedNode.id}
                                    </div>
                                </div>

                                <div>
                                    <label className="text-[10px] font-bold text-slate-400 uppercase block mb-1">Cryptographic Hash</label>
                                    <div className="font-mono text-[10px] bg-slate-100 border border-slate-200 rounded p-2 text-slate-600 break-all">
                                        {selectedNode.hash}
                                    </div>
                                </div>

                                {selectedNode.parent_hash && (
                                    <div>
                                        <label className="text-[10px] font-bold text-slate-400 uppercase block mb-1">Parent Anchor</label>
                                        <div className="font-mono text-[10px] bg-slate-100 border border-slate-200 rounded p-2 text-slate-400 break-all">
                                            {selectedNode.parent_hash}
                                        </div>
                                    </div>
                                )}

                                <div>
                                    <label className="text-[10px] font-bold text-slate-400 uppercase block mb-1">Data Payload</label>
                                    <pre className="font-mono text-[10px] bg-white border border-slate-200 rounded p-3 text-slate-600 overflow-x-auto whitespace-pre-wrap">
                                        {JSON.stringify(selectedNode.payload, null, 2)}
                                    </pre>
                                </div>

                                <div className="pt-4 border-t border-slate-200">
                                    {selectedNode.verified ? (
                                        <div className="flex items-center gap-2 text-emerald-600 text-xs font-bold uppercase tracking-wider">
                                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                                            Cryptographically Valid Artifact
                                        </div>
                                    ) : (
                                        <div className="flex items-center gap-2 text-amber-600 text-xs font-bold uppercase tracking-wider">
                                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                                            Verification Pending / Degraded
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-slate-400">
                            <svg className="w-12 h-12 mb-4 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                            <p className="text-xs font-medium uppercase tracking-widest text-center">Select an artifact to verify<br />chain of custody</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
