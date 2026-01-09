"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import TimelineLegend from "@/components/timeline/TimelineLegend";
import TimelineGrid from "@/components/timeline/TimelineGrid";
import TimelineRanges from "@/components/timeline/TimelineRanges";
import DelayedBatchesTable from "@/components/timeline/DelayedBatchesTable";
import { getBatchTimeline, AuditTimelineResponse, TimelineStatus } from "@/domain/timeline";
import { apiFetch } from "@/lib/api";
import EmailModal from "@/components/common/EmailModal";
import { useApiHealth } from "@/context/ApiHealthContext";
import OfflineScreen from "@/components/common/OfflineScreen";

export default function BatchTimelinePage() {
    const { healthy } = useApiHealth();

    if (!healthy) {
        return <OfflineScreen />;
    }
    const router = useRouter();
    const params = useParams();
    const batchId = params.batchId as string;

    const [data, setData] = useState<AuditTimelineResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [enabledStatuses, setEnabledStatuses] = useState<TimelineStatus[]>([
        TimelineStatus.ON_TIME,
        TimelineStatus.OVER_TIME,
        TimelineStatus.DEVIATION,
        TimelineStatus.LIR,
        TimelineStatus.AT_RISK,
        TimelineStatus.RESOLVED_DELAY
    ]);
    const [emailModalOpen, setEmailModalOpen] = useState(false);
    const [refreshCounter, setRefreshCounter] = useState(0);

    // Layer 4 Resilience State
    const [retrySeconds, setRetrySeconds] = useState<number | null>(null);
    const [failureReason, setFailureReason] = useState<string | null>(null);

    // Countdown Timer
    useEffect(() => {
        if (retrySeconds === null || retrySeconds <= 0) return;

        const timer = setInterval(() => {
            setRetrySeconds(prev => {
                if (prev === null || prev <= 1) return 0;
                return prev - 1;
            });
        }, 1000);
        return () => clearInterval(timer);
    }, [retrySeconds]);

    useEffect(() => {
        let active = true;

        const fetchDataInternal = async () => {
            setLoading(true);
            setError(null);

            try {
                if (!batchId || batchId.length < 5) return;

                const result = await getBatchTimeline(batchId);

                if (!active) return;

                // Layer 3: Degraded Mode Detection (Enterprise Audit Grade)
                if (result.mode === "degraded") {
                    console.log("[UI] System Degraded. Fetching Health...");
                    const { data: healthData } = await apiFetch("/system/health");
                    const serviceHealth = healthData?.services?.["/batches/" + batchId + "/timeline"];

                    if (serviceHealth) {
                        const isIntegrityOpen = serviceHealth.integrity === "open";
                        const isAvailOpen = serviceHealth.availability === "open";

                        setRetrySeconds(serviceHealth.retry_after || 30);
                        setFailureReason(
                            isIntegrityOpen ? `INTEGRITY BREACH: ${serviceHealth.reason}` :
                                isAvailOpen ? `AVAILABILITY ISSUE: ${serviceHealth.reason}` :
                                    "System Stabilizing"
                        );
                    } else {
                        setRetrySeconds(30);
                        setFailureReason("Backend Sync Interrupt");
                    }
                } else {
                    setRetrySeconds(null);
                    setFailureReason(null);
                }

                setData(result);
                setLoading(false);

            } catch (err: any) {
                if (active) {
                    try {
                        const { data: healthData } = await apiFetch("/system/health");
                        if (healthData?.status !== "healthy") {
                            const serviceHealth = healthData.services?.["/batches/" + batchId + "/timeline"];
                            setRetrySeconds(serviceHealth?.retry_after || 30);
                            setFailureReason(serviceHealth?.reason || "Connection Failure");
                            setLoading(false);
                            return;
                        }
                    } catch (hErr) { }

                    setError(err.message || "Unexpected failure in synchronization engine");
                    setLoading(false);
                }
            }
        };

        fetchDataInternal();

        return () => {
            active = false;
        };
    }, [batchId, refreshCounter]);

    const fetchData = () => {
        // Layer 4: Valid Retry Logic
        if (retrySeconds && retrySeconds > 0) return; // Prevent retry if blocked
        setRefreshCounter(c => c + 1);
    };

    const onBack = () => {
        router.push("/batches");
    };

    const onExportPdf = () => {
        const finalBatchId = data?.batch_id || batchId;
        const eosStatus = "ON_TIME";
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;
        window.location.href = `${API_BASE_URL}/batches/${finalBatchId}/timeline/pdf?eos_status=${eosStatus}`;
    };

    const handleSendEmail = async (payload: { to: string[], subject: string, message: string, attachments: any }) => {
        const finalBatchId = data?.batch_id || batchId;
        const { error } = await apiFetch(`/batches/${finalBatchId}/email`, {
            method: "POST",
            body: JSON.stringify(payload)
        });
        if (error) {
            alert("Failed to send email: " + error);
            return;
        }
        alert(`Forensic report successfully dispatched to: ${payload.to.join(", ")}`);
    };

    const onEmail = () => {
        setEmailModalOpen(true);
    };

    const handleStatusChange = (status: TimelineStatus, enabled: boolean) => {
        if (enabled) {
            setEnabledStatuses(prev => [...prev, status]);
        } else {
            setEnabledStatuses(prev => prev.filter(s => s !== status));
        }
    };

    // Authoritative Aggregation Layer (ARCH-2026-CHART-002)
    const filteredDistribution = React.useMemo(() => {
        const dist: Record<string, number> = {};
        const RANGES = [
            { min: 70, max: 74, key: "70_75" },
            { min: 75, max: 79, key: "75_80" },
            { min: 80, max: 84, key: "80_85" },
            { min: 85, max: 89, key: "85_90" },
            { min: 90, max: 94, key: "90_95" },
            { min: 95, max: 99, key: "95_100" },
            { min: 100, max: 149, key: "100_150" },
            { min: 150, max: 199, key: "150_200" },
            { min: 200, max: 9999, key: "200_plus" }
        ];

        // Initialize stable projection (Ensure IDEMPOTENCY)
        RANGES.forEach(r => dist[r.key] = 0);

        const batches = data?.delayed_batches || [];
        batches.forEach(b => {
            // Map forensic EOS status to UI TimelineStatus for authoritative filtering
            const statusMap: Record<string, TimelineStatus> = {
                "ON_TIME": TimelineStatus.ON_TIME,
                "DEVIATION": TimelineStatus.DEVIATION,
                "EOS": TimelineStatus.OVER_TIME,
                "RESOLVED": TimelineStatus.RESOLVED_DELAY
            };
            const status = statusMap[b.eos_status] || TimelineStatus.ON_TIME;

            if (enabledStatuses.includes(status)) {
                const range = RANGES.find(r => b.lead_time >= r.min && b.lead_time <= r.max);
                if (range) {
                    dist[range.key]++;
                }
            }
        });

        return dist;
    }, [data?.delayed_batches, enabledStatuses]);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <span className="ml-4 text-slate-500 font-medium tracking-tight">Synchronizing Batch State...</span>
            </div>
        );
    }

    // Resilience Banner logic
    const isDegraded = data?.mode === "degraded" || (retrySeconds !== null);

    // If we have NO data and NO degraded state, show error
    if (error && !data && !isDegraded) {
        return (
            <div className="p-12 text-center bg-white rounded-xl border border-slate-200 m-8">
                <h1 className="text-2xl font-bold text-rose-600">Timeline Synchronization Failure</h1>
                <p className="text-slate-500 mt-2">{error || "Data artifact is missing or corrupted."}</p>
                <button
                    onClick={fetchData}
                    className="mt-6 bg-blue-600 text-white px-4 py-2 rounded-lg font-bold shadow-md hover:bg-blue-700 transition"
                >
                    Retry Synchronization
                </button>
            </div>
        );
    }

    const leadTime = Array.from({ length: 70 }, (_, i) => i);
    // Safe data for degraded rendering
    const safeData = data || {
        batch_id: batchId,
        procedure_id: "UNKNOWN",
        stages: [],
        distribution: {},
        delayed_batches: [],
        deviations: [],
        lirs: []
    } as any;

    return (
        <div className="font-sans max-w-[1600px] mx-auto p-8">

            {/* Layer 4: Resilience Banner */}
            {isDegraded && (
                <div className={`${data?.sync_status === 'paused' ? 'bg-rose-50 border-rose-200' : 'bg-amber-50 border-amber-200'} p-6 rounded-xl mb-8 flex items-center justify-between animate-in slide-in-from-top-4 duration-500 shadow-sm transition-colors`}>
                    <div className="flex items-center gap-4">
                        <div className={`${data?.sync_status === 'paused' ? 'bg-rose-100 text-rose-600' : 'bg-amber-100 text-amber-600'} w-10 h-10 rounded-full flex items-center justify-center font-bold text-xl`}>
                            <span className="animate-pulse">!</span>
                        </div>
                        <div>
                            <h3 className={`${data?.sync_status === 'paused' ? 'text-rose-800' : 'text-amber-800'} font-bold uppercase tracking-tight`}>
                                {data?.sync_status === 'paused' ? 'Timeline Synchronization Paused (Integrity Lock)' : 'Timeline Synchronization Degraded'}
                            </h3>
                            <div className={`${data?.sync_status === 'paused' ? 'text-rose-700' : 'text-amber-700'} text-sm mt-1 space-y-1`}>
                                <p>Reason: <span className="font-semibold">{failureReason || "System Stabilizing"}</span></p>
                                <p>Last successful sync: <span className="font-mono">{data?.last_successful_sync ? new Date(data.last_successful_sync).toLocaleString() : "Sync Ledger Bootstrapping"}</span></p>
                            </div>
                        </div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                        <span className="text-amber-800 text-xs font-bold uppercase tracking-wider">
                            Automatic retry in: {retrySeconds}s
                        </span>
                        <button
                            onClick={fetchData}
                            disabled={!!(retrySeconds && retrySeconds > 0)}
                            className={`px-4 py-2 rounded-lg font-bold text-xs uppercase tracking-wider transition-all
                                ${retrySeconds && retrySeconds > 0
                                    ? "bg-amber-100 text-amber-300 cursor-not-allowed"
                                    : "bg-amber-600 text-white hover:bg-amber-700 shadow-md"
                                }`}
                        >
                            Retry Now
                        </button>
                    </div>
                </div>
            )}

            {/* Page Header */}
            <div className="mb-8 flex flex-col gap-4">
                <div className="flex items-center gap-4">
                    <button
                        onClick={onBack}
                        className="text-slate-400 hover:text-blue-600 transition-colors p-1 hover:bg-blue-50 rounded-full"
                    >
                        <DoubleChevronLeftIcon />
                    </button>
                    <h1 className="text-2xl font-bold text-slate-800 tracking-tight">
                        Batch Timeline <span className="text-slate-400 ml-2 font-normal">#{safeData.batch_id.slice(0, 8)}</span>
                    </h1>
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={onExportPdf}
                        className="bg-white hover:bg-blue-50 text-slate-700 border border-slate-200 hover:border-blue-200 px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 shadow-sm transition-all"
                    >
                        <FileTextIcon />
                        Export PDF
                    </button>
                    <button
                        onClick={onEmail}
                        className="bg-white hover:bg-blue-50 text-slate-700 border border-slate-200 hover:border-blue-200 px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 shadow-sm transition-all"
                    >
                        <MailIcon />
                        Email
                    </button>
                </div>
            </div>

            {/* Tracker Card */}
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden mb-8">
                <div className="bg-slate-50/50 p-4 border-b border-slate-100 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <div className="w-1 h-4 bg-blue-500 rounded-full" />
                        <h2 className="font-bold text-slate-800 text-sm italic">FORENSIC TIMELINE RECORD</h2>
                    </div>
                </div>

                <div className="p-6">
                    <TimelineLegend enabledStatuses={enabledStatuses} onChange={handleStatusChange} />

                    <div className="flex items-center gap-2 mb-4">
                        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Release Lead Time (Days)</span>
                    </div>

                    <TimelineGrid
                        stages={safeData.stages}
                        leadTime={leadTime}
                        enabledStatuses={enabledStatuses}
                        deviations={safeData.deviations}
                    />
                    <TimelineRanges distribution={filteredDistribution} />
                </div>
            </div>

            <DelayedBatchesTable batches={safeData.delayed_batches} />

            <EmailModal
                isOpen={emailModalOpen}
                onClose={() => setEmailModalOpen(false)}
                batchId={batchId}
                onSend={handleSendEmail}
            />
        </div>
    );
}

function DoubleChevronLeftIcon() {
    return (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="11 17 6 12 11 7"></polyline>
            <polyline points="18 17 13 12 18 7"></polyline>
        </svg>
    )
}

function FileTextIcon() {
    return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
    )
}

function MailIcon() {
    return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
            <polyline points="22,6 12,13 2,6"></polyline>
        </svg>
    )
}
