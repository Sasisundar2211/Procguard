"use client";

import React, { useState } from "react";

interface EmailModalProps {
    isOpen: boolean;
    onClose: () => void;
    batchId: string;
    onSend: (data: { to: string[], subject: string, message: string, attachments: any }) => Promise<void>;
}

export default function EmailModal({ isOpen, onClose, batchId, onSend }: EmailModalProps) {
    const [emails, setEmails] = useState("");
    const [subject, setSubject] = useState(`Batch Timeline Report – ${batchId.slice(0, 8)}`);
    const [message, setMessage] = useState("Please review the attached forensic timeline.");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [attachments, setAttachments] = useState({
        timeline_pdf: true,
        opa_decisions: true,
        violation_chain: true
    });

    if (!isOpen) return null;

    const validateEmailForm = (toEmails: string[]) => {
        if (toEmails.length === 0) {
            throw new Error("Recipient email is required");
        }
        toEmails.forEach(email => {
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                throw new Error(`Invalid email format: ${email}`);
            }
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        const toList = emails.split(",").map(e => e.trim()).filter(e => e !== "");

        try {
            validateEmailForm(toList);
            await onSend({
                to: toList,
                subject,
                message,
                attachments
            });
            onClose();
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-lg overflow-hidden animate-in fade-in zoom-in duration-200">
                <div className="bg-slate-50 px-6 py-4 border-b border-slate-100 flex justify-between items-center">
                    <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="text-blue-500"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                        Compose Forensic Report
                    </h2>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    {error && (
                        <div className="bg-rose-50 border border-rose-200 p-3 rounded-lg text-rose-600 text-xs font-bold uppercase tracking-tight flex items-center gap-2">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                            {error}
                        </div>
                    )}

                    <div>
                        <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1 ml-1">To (comma separated)</label>
                        <input
                            type="text"
                            placeholder="auditor@company.com, qa@company.com"
                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
                            value={emails}
                            onChange={(e) => setEmails(e.target.value)}
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1 ml-1">Subject</label>
                        <input
                            type="text"
                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
                            value={subject}
                            onChange={(e) => setSubject(e.target.value)}
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1 ml-1">Message (Optional)</label>
                        <textarea
                            rows={3}
                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                        />
                    </div>

                    <div>
                        <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Evidence Attachments</label>
                        <div className="grid grid-cols-1 gap-2">
                            <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                                <input
                                    type="checkbox"
                                    checked={attachments.timeline_pdf}
                                    onChange={(e) => setAttachments({ ...attachments, timeline_pdf: e.target.checked })}
                                    className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                                />
                                <div className="flex-1">
                                    <span className="text-xs font-bold text-slate-700 block">Batch Timeline PDF</span>
                                    <span className="text-[10px] text-slate-400">Authoritative visual history of the batch.</span>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                                <input
                                    type="checkbox"
                                    checked={attachments.opa_decisions}
                                    onChange={(e) => setAttachments({ ...attachments, opa_decisions: e.target.checked })}
                                    className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                                />
                                <div className="flex-1">
                                    <span className="text-xs font-bold text-slate-700 block">OPA Decisions</span>
                                    <span className="text-[10px] text-slate-400">Policy evaluation logs with cryptographic hashes.</span>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100 opacity-50 cursor-not-allowed">
                                <input type="checkbox" checked={true} disabled className="w-4 h-4" />
                                <div className="flex-1">
                                    <span className="text-xs font-bold text-slate-700 block">Forensic Chain Link</span>
                                    <span className="text-[10px] text-slate-400">Mandatory SHA-256 verification block.</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="pt-4 flex gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2.5 rounded-lg border border-slate-200 text-sm font-bold text-slate-600 hover:bg-slate-50 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-bold text-white shadow-lg shadow-blue-500/20 transition-all ${loading ? 'bg-slate-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
                        >
                            {loading ? 'Dispatching...' : 'Send Detailed Report'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
