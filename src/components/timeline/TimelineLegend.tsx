"use client";

import React from "react";
import { TimelineStatus } from "@/domain/timeline";

interface TimelineLegendProps {
    enabledStatuses: TimelineStatus[];
    onChange: (status: TimelineStatus, enabled: boolean) => void;
}

export const STATUS_COLOR: Record<TimelineStatus, string> = {
    [TimelineStatus.ON_TIME]: "#00C781",
    [TimelineStatus.OVER_TIME]: "#FF6B81",
    [TimelineStatus.DEVIATION]: "#FF9F43",
    [TimelineStatus.LIR]: "#4C6FFF",
    [TimelineStatus.AT_RISK]: "#FFC048",
    [TimelineStatus.RESOLVED_DELAY]: "#A4B0BE",
    [TimelineStatus.EMPTY]: "#F8FAFC",
    [TimelineStatus.GRAY_GHOST]: "#E2E8F0"
};

export default function TimelineLegend({ enabledStatuses, onChange }: TimelineLegendProps) {
    const items: { label: string; status: TimelineStatus; type: "box" | "dot" | "check" }[] = [
        { label: "On Time", status: TimelineStatus.ON_TIME, type: "box" },
        { label: "Over Time", status: TimelineStatus.OVER_TIME, type: "box" },
        { label: "Deviation", status: TimelineStatus.DEVIATION, type: "dot" },
        { label: "LIR", status: TimelineStatus.LIR, type: "dot" },
        { label: "At Risk of Delay", status: TimelineStatus.AT_RISK, type: "box" },
        { label: "Resolved Delay", status: TimelineStatus.RESOLVED_DELAY, type: "check" },
    ];

    return (
        <div className="flex items-center gap-6 text-xs mb-4 p-4 bg-slate-50/50 rounded-xl border border-slate-100/50 shadow-sm flex-wrap">
            {items.map((item) => (
                <div
                    key={item.status}
                    className="flex items-center gap-2 cursor-pointer group"
                    onClick={() => onChange(item.status, !enabledStatuses.includes(item.status))}
                >
                    <input
                        type="checkbox"
                        className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-3.5 h-3.5 cursor-pointer"
                        checked={enabledStatuses.includes(item.status)}
                        onChange={(e) => {
                            e.stopPropagation();
                            onChange(item.status, e.target.checked);
                        }}
                    />
                    <div className="flex items-center gap-1.5 opacity-80 group-hover:opacity-100 transition-opacity">
                        {item.type === "box" && (
                            <div
                                className="w-3.5 h-3.5 rounded-[3px] shadow-sm border border-black/5"
                                style={{ backgroundColor: STATUS_COLOR[item.status] }}
                            />
                        )}
                        {item.type === "dot" && (
                            <div
                                className="w-3 h-3 rounded-full border-2 border-white shadow-sm ring-1 ring-slate-100"
                                style={{ backgroundColor: STATUS_COLOR[item.status] }}
                            />
                        )}
                        {item.type === "check" && (
                            <div
                                className="w-3.5 h-3.5 rounded-[3px] border flex items-center justify-center shadow-sm"
                                style={{ backgroundColor: STATUS_COLOR[item.status] }}
                            >
                                <div className="w-2.5 h-2.5 bg-slate-800 rounded-full text-[6px] text-white flex items-center justify-center">!</div>
                            </div>
                        )}
                        <span className="font-medium text-slate-600 group-hover:text-slate-900 transition-colors uppercase tracking-tight text-[10px]">
                            {item.label}
                        </span>
                    </div>
                </div>
            ))}

            <button className="ml-auto bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 shadow-sm transition-colors">
                <FilterIcon />
                Show/Hide Filter
            </button>
        </div>
    );
}

function FilterIcon() {
    return (
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
        </svg>
    )
}
