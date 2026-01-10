"use client";

import { useState, useRef, useEffect } from "react";
import { TIME_RANGES, TimeRangeOption } from "@/constants/timeRanges";

type Props = {
    selected: TimeRangeOption;
    onChange: (range: TimeRangeOption) => void;
};

export function TimeRangeDropdown({ selected, onChange }: Props) {
    const [open, setOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    // Close when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                setOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        <div className="relative" ref={containerRef}>
            {/* Trigger */}
            <div className="flex flex-col">
                <span className="text-[10px] text-slate-400 font-semibold mb-0.5 ml-1">Time Range</span>
                <button
                    onClick={() => setOpen(o => !o)}
                    className="flex items-center gap-2 text-emerald-500 font-bold text-sm hover:text-emerald-600 transition"
                >
                    {selected.label}
                    <span className={`transition-transform duration-200 text-[10px] ${open ? "rotate-180" : ""}`}>▼</span>
                </button>
            </div>

            {/* Dropdown */}
            {open && (
                <div
                    className="absolute z-50 mt-1 w-56 bg-white border border-slate-200 rounded-lg shadow-xl py-1 animate-slideDown overflow-hidden"
                >
                    {TIME_RANGES.map(range => (
                        <button
                            key={range.value}
                            onClick={() => {
                                onChange(range);
                                setOpen(false);
                            }}
                            className={`w-full text-left px-4 py-2.5 text-xs hover:bg-slate-50 transition-colors ${selected.value === range.value
                                    ? "bg-emerald-50/50 text-emerald-600 font-bold border-l-4 border-emerald-500"
                                    : "text-slate-600 font-medium"
                                }`}
                        >
                            {range.label}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}
