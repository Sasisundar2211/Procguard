"use client";

import { useState } from "react";

type Props = {
    onApply: (from: string, to: string) => void;
    onCancel?: () => void;
};

export function CustomDateRangePicker({ onApply, onCancel }: Props) {
    const [from, setFrom] = useState("");
    const [to, setTo] = useState("");

    function apply() {
        if (!from || !to) {
            alert("Please select both From and To dates");
            return;
        }

        const fromDate = new Date(from);
        const toDate = new Date(to);

        const fromISO = fromDate.toISOString();
        const toISO = toDate.toISOString();

        if (fromISO >= toISO) {
            alert("Invalid date range: 'From' must be earlier than 'To'");
            return;
        }

        onApply(fromISO, toISO);
    }

    return (
        <div className="p-4 border border-slate-200 rounded-lg bg-slate-50 space-y-4 animate-slideDown shadow-sm">
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex flex-col flex-1">
                    <label className="text-[10px] uppercase tracking-wider font-bold text-slate-400 mb-1 ml-1">From (Local)</label>
                    <input
                        type="datetime-local"
                        value={from}
                        onChange={e => setFrom(e.target.value)}
                        className="border border-slate-200 rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-medium text-slate-700"
                    />
                </div>

                <div className="flex flex-col flex-1">
                    <label className="text-[10px] uppercase tracking-wider font-bold text-slate-400 mb-1 ml-1">To (Local)</label>
                    <input
                        type="datetime-local"
                        value={to}
                        onChange={e => setTo(e.target.value)}
                        className="border border-slate-200 rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-medium text-slate-700"
                    />
                </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
                {onCancel && (
                    <button
                        onClick={onCancel}
                        className="text-slate-500 text-xs font-bold uppercase hover:text-slate-700 transition-colors"
                    >
                        Cancel
                    </button>
                )}
                <button
                    onClick={apply}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-md text-xs font-bold uppercase shadow-md shadow-emerald-200 transition-all active:scale-95"
                >
                    Apply Custom Range
                </button>
            </div>

            <p className="text-[10px] text-slate-400 italic text-center">
                Dates are selected in your local time and will be normalized to UTC for auditing.
            </p>
        </div>
    );
}
