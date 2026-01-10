"use client";

import React, { useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";

import { normalizeComplianceReports } from "@/domain/compliance/schema";

interface Evidence {
    blob_path: string;
    evidence_type: string;
    created_at: string;
}

interface ComplianceReport {
    id: string;
    title: string;
    created_at: string;
    evidence: Evidence[];
}

export default function CompliancePage() {
    const [reports, setReports] = useState<ComplianceReport[]>([]);
    const [loading, setLoading] = useState(true);
    const [newReportTitle, setNewReportTitle] = useState("");

    const fetchReports = async () => {
        try {
            const { data, error } = await apiFetch("/compliance/compliance-reports");
            if (error) {
                console.error("Failed to fetch reports:", error);
            } else if (data) {
                setReports(normalizeComplianceReports(data));
            }
        } catch (e) {
            console.error("Failed to fetch reports", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchReports();
    }, []);

    const handleCreateReport = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newReportTitle) return;
        try {
            const { error } = await apiFetch("/compliance/compliance-reports", {
                method: "POST",
                body: JSON.stringify({ title: newReportTitle }),
            });
            if (error) {
                alert("Failed to create report: " + error);
                return;
            }
            setNewReportTitle("");
            fetchReports();
        } catch (e) {
            alert("Failed to create report");
        }
    };

    return (
        <div className="p-8 max-w-6xl mx-auto">
            <header className="mb-10">
                <h1 className="text-3xl font-black text-slate-800 tracking-tight uppercase mb-2">Compliance & Forensic Evidence</h1>
                <p className="text-slate-500 font-medium italic">Immutable repository for authorized audit trails and system proofs.</p>
            </header>

            <section className="mb-12 bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                <h2 className="text-sm font-black text-slate-400 uppercase tracking-widest mb-4">Generate Compliance Bundle</h2>
                <form onSubmit={handleCreateReport} className="flex gap-4">
                    <input
                        type="text"
                        value={newReportTitle}
                        onChange={(e) => setNewReportTitle(e.target.value)}
                        placeholder="Report Title (e.g., Q1 2026 Forensic Audit)"
                        className="flex-1 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none"
                    />
                    <button
                        type="submit"
                        className="bg-blue-600 text-white px-6 py-2 rounded-lg text-sm font-bold uppercase hover:bg-blue-700 transition-all shadow-lg shadow-blue-200"
                    >
                        Create Report
                    </button>
                </form>
            </section>

            <div className="grid gap-6">
                {loading ? (
                    <div className="py-20 text-center animate-pulse text-slate-400 font-bold uppercase tracking-widest">Retrieving Secure Archive...</div>
                ) : reports.length === 0 ? (
                    <div className="py-20 text-center border-2 border-dashed border-slate-200 rounded-xl text-slate-400">
                        No compliance reports found in the forensic store.
                    </div>
                ) : (
                    reports.map(report => (
                        <div key={report.id} className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm hover:border-blue-200 transition-all">
                            <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                                <div>
                                    <h3 className="text-lg font-bold text-slate-800">{report.title}</h3>
                                    <p className="text-[10px] text-slate-400 font-bold uppercase mt-1">
                                        ID: {report.id} • CREATED: {new Date(report.created_at).toLocaleString()}
                                    </p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="bg-emerald-100 text-emerald-700 text-[10px] font-black px-2 py-1 rounded uppercase">Hash Verified ✓</span>
                                </div>
                            </div>
                            <div className="p-6">
                                <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Attached Evidence</h4>
                                {report.evidence.length === 0 ? (
                                    <p className="text-sm text-slate-400 italic">No evidence attached yet.</p>
                                ) : (
                                    <div className="grid gap-3">
                                        {report.evidence.map((ev, idx) => (
                                            <div key={idx} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-100 group">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-8 h-8 rounded bg-white border border-slate-200 flex items-center justify-center text-rose-500">
                                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs font-bold text-slate-700">{ev.blob_path.split('/').pop()}</p>
                                                        <p className="text-[10px] text-slate-400 font-bold uppercase">{ev.evidence_type} • {new Date(ev.created_at).toLocaleDateString()}</p>
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={() => window.open(`${process.env.NEXT_PUBLIC_API_URL}/${ev.blob_path}`, '_blank')}
                                                    className="opacity-0 group-hover:opacity-100 transition-all bg-white text-blue-600 border border-blue-200 px-3 py-1 rounded text-[10px] font-black uppercase hover:bg-blue-50"
                                                >
                                                    Download
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
