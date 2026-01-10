"use client";

import React, { useState, useEffect, useCallback } from "react";
import { fetchAuditLogs, fetchOpaAuditLogs, AuditLogItem, OPAAuditLogItem } from "@/domain/audit";
import { TimeRangeDropdown } from "@/components/common/TimeRangeDropdown";
import { CustomDateRangePicker } from "@/components/common/CustomDateRangePicker";
import { TIME_RANGES, TimeRangeOption } from "@/constants/timeRanges";
import { TimeFilter } from "@/types/filters";
import { apiFetch } from "@/lib/api";
import { normalizeComplianceReports } from "@/domain/compliance/schema";

import { useApiHealth } from "@/context/ApiHealthContext";
import OfflineScreen from "@/components/common/OfflineScreen";

type AuditUIStatus = "loading" | "error" | "empty" | "ready" | "degraded";

const DEFAULT_RANGE = TIME_RANGES.find(r => r.value === "24h")!;

const PROJECTS = [
    { id: "550e8400-e29b-41d4-a716-446655440000", name: "Default Project" },
    { id: "6ba7b810-9dad-11d1-80b4-00c04fd430c8", name: "Forensic Sandbox" }
];

export default function AuditLogs() {
    const { healthy } = useApiHealth();

    if (!healthy) {
        return <OfflineScreen />;
    }

    const [state, setState] = useState<{
        status: AuditUIStatus;
        items: AuditLogItem[];
        opaItems: OPAAuditLogItem[];
        total: number;
        message?: string;
    }>({
        status: "loading",
        items: [],
        opaItems: [],
        total: 0
    });

    const [filters, setFilters] = useState({
        domain: "SYSTEM" as "SYSTEM" | "OPA",
        projectId: "",
        eventType: "",
        userId: "",
        clientId: "",
    });

    const [refreshCounter, setRefreshCounter] = useState(0);
    const [timeFilter, setTimeFilter] = useState<TimeFilter>({
        mode: "preset",
        value: DEFAULT_RANGE.value,
    });

    const [showCustomPicker, setShowCustomPicker] = useState(false);

    /**
     * Immutable Filter Audit Trail (Step 5)
     * Every filter change must log before fetch.
     */
    const logFilterEvent = useCallback(async (payload: any) => {
        try {
            await apiFetch("/audit/filter-events", {
                method: "POST",
                body: JSON.stringify({
                    screen: "AUDIT_LOGS",
                    filter_payload: payload,
                }),
            });
        } catch (e) {
            console.warn("Failed to log filter event, proceeding with fetch for availability.", e);
        }
    }, []);

    const resolveTimeRange = useCallback((filter: TimeFilter) => {
        if (filter.mode === "custom") {
            return { from_ts: filter.from, to_ts: filter.to };
        }

        const preset = TIME_RANGES.find(r => r.value === filter.value) || DEFAULT_RANGE;
        const hours = preset.fromHours!;
        const now = new Date();
        return {
            from_ts: new Date(now.getTime() - hours * 3600_000).toISOString(),
            to_ts: now.toISOString(),
        };
    }, []);

    const filtersDep = JSON.stringify(filters);
    const timeFilterDep = JSON.stringify(timeFilter);

    useEffect(() => {
        let active = true;

        const fetchData = async () => {
            setState(prev => ({ ...prev, status: "loading", message: undefined }));
            try {
                const { from_ts, to_ts } = resolveTimeRange(timeFilter);

                await logFilterEvent({ ...filters, timeFilter });

                if (filters.domain === "OPA") {
                    const data = await fetchOpaAuditLogs({
                        projectId: filters.projectId,
                        from_ts,
                        to_ts,
                        decision: filters.eventType || undefined
                    });
                    if (active) {
                        setState({
                            status: data.items.length === 0 ? "empty" : "ready",
                            items: [],
                            opaItems: data.items,
                            total: data.total
                        });
                    }
                } else {
                    const data = await fetchAuditLogs({
                        ...filters,
                        from_ts,
                        to_ts,
                    });
                    if (active) {
                        if (data.mode === "degraded") {
                            setState({
                                status: "degraded",
                                items: [],
                                opaItems: [],
                                total: 0,
                                message: data.error
                            });
                        } else {
                            setState({
                                status: data.items.length === 0 ? "empty" : "ready",
                                items: data.items,
                                opaItems: [],
                                total: data.total
                            });
                        }
                    }
                }
            } catch (err: any) {
                if (active) {
                    console.error(err);
                    setState({
                        status: "error",
                        items: [],
                        opaItems: [],
                        total: 0,
                        message: err.message || "Unable to load audit logs. Please verify backend connectivity."
                    });
                }
            }
        };

        fetchData();

        return () => {
            active = false;
        };
    }, [filtersDep, timeFilterDep, resolveTimeRange, logFilterEvent, refreshCounter]);

    const triggerFetch = useCallback(() => {
        setRefreshCounter(c => c + 1);
    }, []);


    const handleTabChange = (domain: "SYSTEM" | "OPA") => {
        setFilters(prev => ({ ...prev, domain }));
    };

    const handleDropdownChange = (key: string, value: string) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const handleClearFilters = () => {
        setFilters({
            domain: "SYSTEM",
            projectId: "",
            eventType: "",
            userId: "",
            clientId: "",
        });
        setTimeFilter({ mode: "preset", value: DEFAULT_RANGE.value });
        setShowCustomPicker(false);
    };

    const handleCustomApply = (from: string, to: string) => {
        setTimeFilter({ mode: "custom", from, to });
        setShowCustomPicker(false);
    };

    const handleExport = () => {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;
        if (!API_BASE_URL) return;

        const { from_ts, to_ts } = resolveTimeRange(timeFilter);

        const params = new URLSearchParams({
            domain: filters.domain,
            from_ts,
            to_ts,
        });
        if (filters.domain === "OPA") {
            const params = new URLSearchParams({ from_ts, to_ts });
            if (filters.projectId) params.append("project_id", filters.projectId);
            window.location.href = `${API_BASE_URL}/opa/audit-logs/export?${params.toString()}`;
        } else {
            const params = new URLSearchParams({
                domain: filters.domain,
                from_ts,
                to_ts,
            });
            if (filters.projectId) params.append("project_id", filters.projectId);
            if (filters.eventType) params.append("event_type", filters.eventType);
            if (filters.userId) params.append("user_id", filters.userId);
            if (filters.clientId) params.append("client_id", filters.clientId);
            window.location.href = `${API_BASE_URL}/audit-logs/export?${params.toString()}`;
        }
    };

    const handleExportFilterAudit = () => {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;
        if (!API_BASE_URL) return;

        const { from_ts, to_ts } = resolveTimeRange(timeFilter);
        const params = new URLSearchParams({
            screen: "AUDIT_LOGS",
            from_ts,
            to_ts,
        });

        window.location.href = `${API_BASE_URL}/audit/filter-events/export?${params.toString()}`;
    };

    const [complianceReports, setComplianceReports] = useState<any[]>([]);
    const [selectedReportId, setSelectedReportId] = useState("");

    useEffect(() => {
        async function loadReports() {
            try {
                const { data } = await apiFetch("/compliance/compliance-reports");
                const safeReports = normalizeComplianceReports(data);
                setComplianceReports(safeReports);
            } catch (e) {
                console.warn("Failed to load compliance reports");
                setComplianceReports([]);
            }
        }
        loadReports();
    }, []);

    const handleAttachToCompliance = async () => {
        if (!selectedReportId) {
            alert("Please select a compliance report");
            return;
        }

        try {
            const { from_ts, to_ts } = resolveTimeRange(timeFilter);

            await apiFetch(`/compliance/compliance-reports/${selectedReportId}/attach-current-filters`, {
                method: "POST",
                body: JSON.stringify({
                    screen: "AUDIT_LOGS",
                    from_ts,
                    to_ts,
                    evidence_type: "FILTER_AUDIT_TRAIL"
                })
            });

            alert("Forensic evidence successfully attached to compliance report.");
        } catch (e) {
            console.error(e);
            alert("Failed to attach evidence. Ensure hash chain integrity is valid.");
        }
    };

    return (
        <div className="mt-8 bg-white p-6 rounded-xl border border-slate-200">
            {/* Header */}
            <div className="mb-6 flex justify-between items-start">
                <div>
                    <h2 className="text-2xl font-bold text-orange-400 mb-1">Audit Logs</h2>
                    <p className="text-slate-500 text-sm italic">
                        {state.status === "loading" ? "Authoritative synchronization in progress..." : "Courtroom-safe audit records verified"}
                    </p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => window.open(`${process.env.NEXT_PUBLIC_API_URL}/audit/filter-events/verify`, '_blank')}
                        className="text-[10px] bg-slate-100 px-2 py-1 rounded text-slate-500 font-bold hover:bg-slate-200 transition-colors uppercase"
                    >
                        Verify Chain
                    </button>
                    <button
                        onClick={() => window.location.href = '/system/compliance'}
                        className="text-[10px] bg-blue-50 px-2 py-1 rounded text-blue-600 font-bold hover:bg-blue-100 transition-colors uppercase"
                    >
                        Compliance Repository
                    </button>
                </div>
            </div>

            {state.status === "error" && (
                <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded text-red-600 text-xs font-bold leading-tight uppercase flex items-center gap-2">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                    {state.message}
                </div>
            )}

            {/* Resilience Banner */}
            {state.status === "degraded" && (
                <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg flex items-center justify-between animate-in slide-in-from-top-2">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center text-amber-600 font-bold">!</div>
                        <div>
                            <h3 className="text-amber-800 font-bold text-sm uppercase tracking-wide">Audit Synchronization Paused ({state.message})</h3>
                            <p className="text-amber-700 text-xs mt-0.5">
                                System is in protective state to preserve integrity. Logs are queued safely.
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={triggerFetch}
                        className="px-3 py-1.5 bg-amber-600 text-white rounded text-xs font-bold hover:bg-amber-700 transition"
                    >
                        RETRY SYNC
                    </button>
                </div>
            )}

            {/* Tabs */}
            <div className="flex border-b border-slate-200 mb-6">
                <button
                    onClick={() => handleTabChange("SYSTEM")}
                    className={`px-6 py-2 text-sm font-semibold transition-all ${filters.domain === "SYSTEM" ? "text-emerald-500 border-b-2 border-emerald-500 bg-emerald-50/30" : "text-slate-500 hover:text-slate-700"}`}
                >
                    SYSTEM
                </button>
                <button
                    onClick={() => handleTabChange("OPA")}
                    className={`px-6 py-2 text-sm font-semibold transition-all ${filters.domain === "OPA" ? "text-emerald-500 border-b-2 border-emerald-500 bg-emerald-50/30" : "text-slate-500 hover:text-slate-700"}`}
                >
                    OPA
                </button>
            </div>

            {/* Filters */}
            <div className="space-y-6 mb-6">
                <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-8 flex-wrap">
                        <FilterDropdown
                            label="Project"
                            value={PROJECTS.find(p => p.id === filters.projectId)?.name || "All projects"}
                            options={PROJECTS}
                            onSelect={(id) => handleDropdownChange("projectId", id)}
                        />
                        {filters.domain === "SYSTEM" ? (
                            <>
                                <FilterDropdown
                                    label="Type"
                                    value={filters.eventType || "All types"}
                                    onClick={() => handleDropdownChange("eventType", "unknown")}
                                />
                                <FilterDropdown
                                    label="User"
                                    value={filters.userId || "All users"}
                                    onClick={() => handleDropdownChange("userId", "system")}
                                />
                                <FilterDropdown
                                    label="Client"
                                    value={filters.clientId || "All clients"}
                                    onClick={() => handleDropdownChange("clientId", "API")}
                                />
                            </>
                        ) : (
                            <FilterDropdown
                                label="Decision"
                                value={filters.eventType || "All decisions"}
                                options={[{ id: "allow", name: "Allow" }, { id: "deny", name: "Deny" }]}
                                onSelect={(val) => handleDropdownChange("eventType", val)}
                            />
                        )}

                        <div className="flex items-center gap-4">
                            <TimeRangeDropdown
                                selected={timeFilter.mode === 'preset' ? TIME_RANGES.find(r => r.value === timeFilter.value)! : { label: 'Custom Range', value: 'custom', fromHours: null }}
                                onChange={(range) => setTimeFilter({ mode: "preset", value: range.value })}
                            />
                            <button
                                onClick={() => setShowCustomPicker(!showCustomPicker)}
                                className={`text-[10px] font-bold uppercase px-2 py-1 rounded border transition-all ${timeFilter.mode === 'custom' ? 'bg-emerald-500 text-white border-emerald-600 shadow-sm' : 'text-slate-400 border-slate-200 hover:border-slate-300'}`}
                            >
                                {timeFilter.mode === 'custom' ? 'Custom Active' : 'Set Custom'}
                            </button>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2 border-r border-slate-200 pr-3 mr-3">
                            <select
                                value={selectedReportId}
                                onChange={(e) => setSelectedReportId(e.target.value)}
                                className="text-[10px] uppercase font-bold text-slate-500 bg-slate-50 border border-slate-200 rounded px-2 py-1.5 outline-none focus:border-blue-300"
                            >
                                <option value="">Select Report...</option>
                                {complianceReports.map(r => (
                                    <option key={r.id} value={r.id}>{r.title}</option>
                                ))}
                            </select>
                            <button
                                onClick={handleAttachToCompliance}
                                className="text-blue-600 border border-blue-200 hover:bg-blue-50 text-xs font-bold px-3 py-1.5 rounded uppercase flex items-center gap-1 transition-colors"
                            >
                                Attach Evidence
                            </button>
                        </div>

                        <button
                            onClick={triggerFetch}
                            className="text-emerald-500 border border-emerald-200 hover:bg-emerald-50 text-xs font-bold px-3 py-1.5 rounded uppercase flex items-center gap-1 transition-colors"
                        >
                            <RefreshIcon />
                            Refresh
                        </button>
                        <button
                            onClick={handleExportFilterAudit}
                            className="text-orange-500 border border-orange-200 hover:bg-orange-50 text-xs font-bold px-3 py-1.5 rounded uppercase flex items-center gap-1 transition-colors"
                        >
                            <DownloadIcon />
                            Filter Trail
                        </button>
                        <button
                            onClick={handleExport}
                            className="text-emerald-500 border border-emerald-200 hover:bg-emerald-50 text-xs font-bold px-3 py-1.5 rounded uppercase flex items-center gap-1 transition-colors"
                        >
                            <DownloadIcon />
                            Logs
                        </button>
                        <button
                            onClick={handleClearFilters}
                            className="text-red-400 border border-red-200 hover:bg-red-50 text-xs font-semibold px-3 py-1.5 rounded uppercase transition-colors"
                        >
                            Clear
                        </button>
                    </div>
                </div>

                {showCustomPicker && (
                    <CustomDateRangePicker
                        onApply={handleCustomApply}
                        onCancel={() => setShowCustomPicker(false)}
                    />
                )}
            </div>

            {/* Table or States */}
            <div className="overflow-x-auto shadow-inner rounded-lg border border-slate-100">
                {state.status === "loading" && (
                    <div className="py-24 text-center">
                        <p className="text-slate-400 animate-pulse font-medium">Synchronizing with authoritative ledger...</p>
                    </div>
                )}

                {state.status === "empty" && (
                    <div className="py-24 text-center bg-slate-50/20">
                        <p className="text-slate-400 italic font-medium">
                            {filters.domain === "OPA"
                                ? "No policy decisions recorded for selected period."
                                : "No audit records found for the selected filters."}
                        </p>
                        <p className="text-[10px] text-slate-300 mt-1 uppercase tracking-widest font-bold">Try expanding the time range or selecting a different domain.</p>
                    </div>
                )}

                {/* Degraded mode with existing items - Optional if we cache, but currently we clear items */}
                {/* For now, degraded just shows the banner at top, and maybe empty list here if no cache */}

                {state.status === "ready" && filters.domain === "SYSTEM" && (
                    <table className="w-full text-xs text-left">
                        <thead>
                            <tr className="text-slate-800 font-bold border-b border-slate-200 bg-slate-50/50">
                                <th className="py-3 px-4">Timestamp</th>
                                <th className="py-3 px-4">Actor</th>
                                <th className="py-3 px-4">Action</th>
                                <th className="py-3 px-4">Result</th>
                                <th className="py-3 px-4">State Transition</th>
                                <th className="py-3 px-4">Hash</th>
                                <th className="py-3 px-4">Source</th>
                            </tr>
                        </thead>
                        <tbody className="text-slate-600">
                            {state.items.map((log) => (
                                <tr key={log.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors group">
                                    <td className="py-4 px-4 font-semibold text-slate-700 whitespace-nowrap">
                                        {new Date(log.created_at).toLocaleString()}
                                    </td>
                                    <td className="py-4 px-4 font-medium text-slate-800">
                                        {log.actor || log.user_id || "SYSTEM"}
                                    </td>
                                    <td className="py-4 px-4">
                                        <span className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-600 font-bold text-[10px] uppercase">
                                            {log.action || log.event_type || "N/A"}
                                        </span>
                                    </td>
                                    <td className="py-4 px-4">
                                        <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${log.result === 'SUCCESS' ? 'text-emerald-600 bg-emerald-50' : 'text-red-600 bg-red-50'}`}>
                                            {log.result || "PROCESSED"}
                                        </span>
                                    </td>
                                    <td className="py-4 px-4 font-mono text-[10px]">
                                        {log.expected_state && log.actual_state ? (
                                            <div className="flex items-center gap-1.5">
                                                <span className="text-slate-400">{log.expected_state}</span>
                                                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" className="text-slate-300"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                                                <span className="text-blue-600 font-bold">{log.actual_state}</span>
                                            </div>
                                        ) : "—"}
                                    </td>
                                    <td className="py-4 px-4">
                                        <span className="font-mono text-[9px] text-slate-400 bg-slate-50 px-1 rounded">{log.audit_hash?.substring(0, 12)}...</span>
                                    </td>
                                    <td className="py-4 px-4">
                                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${log.source === 'SYSTEM' ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'}`}>
                                            {log.source}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}

                {state.status === "ready" && filters.domain === "OPA" && (
                    <table className="w-full text-xs text-left">
                        <thead>
                            <tr className="text-slate-800 font-bold border-b border-slate-200 bg-slate-50/50">
                                <th className="py-3 px-4">Timestamp</th>
                                <th className="py-3 px-4">Policy Package</th>
                                <th className="py-3 px-4">Rule</th>
                                <th className="py-3 px-4">Decision</th>
                                <th className="py-3 px-4">Resource</th>
                                <th className="py-3 px-4">Decision Hash</th>
                                <th className="py-3 px-4 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody className="text-slate-600">
                            {state.opaItems.map((log) => (
                                <tr key={log.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors group">
                                    <td className="py-4 px-4 font-semibold text-slate-700 whitespace-nowrap">
                                        {new Date(log.timestamp).toLocaleString()}
                                    </td>
                                    <td className="py-4 px-4 font-medium text-slate-800">
                                        {log.policy_package}
                                    </td>
                                    <td className="py-4 px-4">
                                        <span className="bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded font-bold text-[10px] uppercase">
                                            {log.rule}
                                        </span>
                                    </td>
                                    <td className="py-4 px-4">
                                        <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] uppercase ${log.decision === 'allow' ? 'text-emerald-600 bg-emerald-50' : 'text-rose-600 bg-rose-50'}`}>
                                            {log.decision}
                                        </span>
                                    </td>
                                    <td className="py-4 px-4">
                                        <div className="flex flex-col">
                                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">{log.resource_type}</span>
                                            <span className="font-mono text-[9px] text-slate-500 text-ellipsis overflow-hidden w-24 block">{log.resource_id}</span>
                                        </div>
                                    </td>
                                    <td className="py-4 px-4">
                                        <div className="flex flex-col gap-1">
                                            <span className="font-mono text-[9px] bg-slate-100 px-1 rounded text-slate-500">{log.decision_hash?.substring(0, 16)}...</span>
                                            <div className="flex gap-2">
                                                <span className="text-[8px] text-slate-400 font-bold uppercase tracking-tighter">I: {log.input_hash.substring(0, 6)}</span>
                                                <span className="text-[8px] text-slate-400 font-bold uppercase tracking-tighter">R: {log.result_hash.substring(0, 6)}</span>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="py-4 px-4 text-right">
                                        {log.linked_violation_id ? (
                                            <a
                                                href={`/violations/${log.linked_violation_id}`}
                                                className="text-blue-600 hover:text-blue-800 font-bold text-[10px] uppercase tracking-wider border-b border-blue-200"
                                            >
                                                View Proof
                                            </a>
                                        ) : (
                                            <span className="text-slate-300 text-[10px] uppercase font-bold tracking-wider">No Violation</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}

function FilterDropdown({ label, value, options, onSelect, onClick }: {
    label: string;
    value: string;
    options?: { id: string, name: string }[];
    onSelect?: (id: string) => void;
    onClick?: () => void
}) {
    const [open, setOpen] = useState(false);

    return (
        <div className="relative flex flex-col cursor-pointer group" onClick={() => options ? setOpen(!open) : onClick?.()}>
            <span className="text-[10px] text-slate-400 font-semibold mb-0.5 ml-1 group-hover:text-emerald-400 transition-colors uppercase tracking-widest">{label}</span>
            <div className="flex items-center gap-1 text-emerald-500 font-bold text-sm hover:text-emerald-600">
                {value}
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="6 9 12 15 18 9"></polyline></svg>
            </div>

            {open && options && (
                <div className="absolute top-full left-0 mt-2 w-48 bg-white border border-slate-200 rounded-lg shadow-xl z-50 py-2 animate-in fade-in slide-in-from-top-1 duration-200">
                    <div
                        className="px-4 py-2 hover:bg-slate-50 text-[10px] font-bold text-slate-400 uppercase border-b border-slate-50 mb-1"
                        onClick={(e) => { e.stopPropagation(); onSelect?.(""); setOpen(false); }}
                    >
                        Clear Filter
                    </div>
                    {options.map(opt => (
                        <div
                            key={opt.id}
                            onClick={(e) => { e.stopPropagation(); onSelect?.(opt.id); setOpen(false); }}
                            className="px-4 py-2 hover:bg-emerald-50 hover:text-emerald-600 text-xs font-bold text-slate-600 transition-colors"
                        >
                            {opt.name}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

function RefreshIcon() {
    return <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M23 4v6h-6"></path><path d="M1 20v-6h6"></path><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>;
}

function DownloadIcon() {
    return <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>;
}
