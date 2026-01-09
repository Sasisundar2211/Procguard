"use client";

import { AuditStage, TimelineStatus, Deviation } from "@/domain/timeline";
import { STATUS_COLOR } from "./TimelineLegend";

interface TimelineGridProps {
    stages: AuditStage[];
    leadTime: number[];
    enabledStatuses: TimelineStatus[];
    deviations: Deviation[];
}

export default function TimelineGrid({
    stages,
    leadTime,
    enabledStatuses,
    deviations,
}: TimelineGridProps) {

    const isMarkerVisible = (marker: any) => {
        // Forensic labels (numeric values) represent immutable audit identifiers
        // and must persist regardless of status toggling for audit transparency.
        if (marker.val) return true;

        // Functional indicators respect their respective canonical category visibility.
        if (marker.type === "lir") {
            return enabledStatuses.includes(TimelineStatus.LIR);
        }
        if (marker.type === "lir-warn") {
            return enabledStatuses.includes(TimelineStatus.DEVIATION);
        }
        if (marker.warn) {
            return enabledStatuses.includes(TimelineStatus.RESOLVED_DELAY);
        }

        return true;
    };

    const getTooltip = (status: TimelineStatus, cellIdx: number, stageName: string) => {
        if (status === TimelineStatus.DEVIATION) {
            const dev = deviations.find(d =>
                d.stage === stageName &&
                cellIdx >= d.valid_from_day &&
                cellIdx <= d.valid_until_day &&
                !d.resolved_at &&
                !d.superseded_by_lir
            );
            if (dev) {
                return `Deviation ID: ${dev.id.slice(0, 8)}...\nType: ${dev.deviation_type}\nApproved by: ${dev.approved_by}\nValid days: ${dev.valid_from_day}–${dev.valid_until_day}`;
            }
        }

        switch (status) {
            case TimelineStatus.DEVIATION:
                return `Deviation recorded @ Day ${cellIdx}`;
            case TimelineStatus.LIR:
                return `LIR issued @ Day ${cellIdx}`;
            case TimelineStatus.AT_RISK:
                return `At Risk: Risk score >= 0.7`;
            case TimelineStatus.RESOLVED_DELAY:
                return `Delay resolved @ Day ${cellIdx}`;
            case TimelineStatus.OVER_TIME:
                return `Exceeded planned schedule`;
            case TimelineStatus.ON_TIME:
                return "On schedule";
            default:
                return "";
        }
    };

    return (
        <div className="overflow-x-auto border border-slate-200 rounded-lg bg-white shadow-sm">
            {/* Header Row */}
            <div className="flex text-[10px] bg-slate-50/80 border-b border-slate-200">
                <div className="w-48 flex-shrink-0 p-3 font-bold text-slate-500 uppercase tracking-wider flex items-end">
                    STAGE
                </div>
                {leadTime.map(t => (
                    <div
                        key={t}
                        className="w-8 flex-shrink-0 text-center border-l border-slate-100/50 text-slate-400 pb-2 flex flex-col justify-end"
                    >
                        {t}
                    </div>
                ))}
            </div>

            {/* Stages */}
            {stages.map((stage, i) => (
                <div key={stage.name} className={`flex h-10 ${i !== stages.length - 1 ? "border-b border-slate-100" : ""}`}>
                    <div className="w-48 flex-shrink-0 px-3 text-xs font-semibold text-slate-700 bg-slate-50/30 flex items-center border-r border-slate-100 uppercase tracking-tight">
                        {stage.name}
                    </div>

                    {stage.cells.map((cellStatus, cellIdx) => {
                        const isVisible = enabledStatuses.includes(cellStatus) || cellStatus === TimelineStatus.EMPTY || cellStatus === TimelineStatus.GRAY_GHOST;
                        const bgColor = isVisible ? STATUS_COLOR[cellStatus] : STATUS_COLOR[TimelineStatus.EMPTY];

                        return (
                            <div
                                key={`${stage.name}-${cellIdx}`}
                                title={isVisible ? getTooltip(cellStatus, cellIdx, stage.name) : ""}
                                className="w-8 flex-shrink-0 border-r border-slate-50 relative transition-all duration-300 group"
                                style={{ backgroundColor: bgColor }}
                            >
                                {/* Marker check - Forensic Labels persist even if cell background is filtered */}
                                {stage.markers.some(m => m.day === cellIdx && isMarkerVisible(m)) && (
                                    <div className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none">
                                        {stage.markers.filter(m => m.day === cellIdx && isMarkerVisible(m)).map((marker, mIdx) => (
                                            <div
                                                key={`${cellIdx}-${marker.val}-${mIdx}`}
                                                className="relative bg-white border border-slate-200 rounded-[4px] w-5 h-5 flex items-center justify-center text-[10px] font-bold text-slate-600 shadow-sm transform group-hover:scale-110 transition-transform"
                                            >
                                                {marker.val}

                                                {/* Alert Badge - Only if Resolved Delay is enabled */}
                                                {marker.warn && enabledStatuses.includes(TimelineStatus.RESOLVED_DELAY) && (
                                                    <div className="absolute -top-1.5 -right-1.5 bg-slate-800 text-white w-3 h-3 rounded-full flex items-center justify-center text-[8px] z-20 shadow-md ring-1 ring-white">
                                                        !
                                                    </div>
                                                )}

                                                {/* Colored Dot Indicators - Deviation specific */}
                                                {marker.type === "lir-warn" && enabledStatuses.includes(TimelineStatus.DEVIATION) && (
                                                    <div className="absolute -bottom-1 -right-1 w-2.5 h-2.5 bg-orange-400 border-2 border-white rounded-full z-20 shadow-sm" />
                                                )}
                                                {marker.type === "lir" && enabledStatuses.includes(TimelineStatus.LIR) && (
                                                    <div className="absolute -bottom-1 -right-1 w-2.5 h-2.5 bg-blue-400 border-2 border-white rounded-full z-20 shadow-sm" />
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            ))}
        </div>
    )
}
