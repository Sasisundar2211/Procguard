export default function TimelineRanges({
    distribution,
}: {
    distribution: Record<string, number>
}) {
    // Default ranges to ensure layout consistency even if backend misses some
    const RANGES = [
        "70-75", "75-80", "80-85", "85-90", "90-95", "95-100", "100-150", "150-200", "200+"
    ]

    return (
        <div className="mt-6">
            <div className="flex border border-slate-300 rounded overflow-hidden text-xs">
                {RANGES.map((label, i) => {
                    const key = label.replace("-", "_").replace("+", "_plus")
                    const count = distribution[key] || 0

                    return (
                        <div key={label} className={`flex-1 flex flex-col ${i !== RANGES.length - 1 ? "border-r border-slate-300" : ""}`}>
                            <div className="bg-white p-2 font-bold text-slate-700 h-8 flex items-center">{label}</div>
                            <div className="bg-slate-50/50 p-2 border-t border-slate-100 h-10 flex items-center">
                                {count > 0 && (
                                    <span className={`px-4 py-1 rounded-full text-white font-semibold text-[10px] w-full text-center shadow-sm ${count > 10 ? "bg-rose-400" : "bg-rose-400"}`}>
                                        {count}{count > 20 ? `(${count})` : ""}
                                    </span>
                                )}
                            </div>
                        </div>
                    )
                })}
            </div>

            <div className="mt-4 text-xs text-slate-500 font-medium flex items-center gap-2">
                <span>View</span>
                <select className="border border-slate-300 rounded p-1 bg-white text-slate-700">
                    <option>10</option>
                    <option>20</option>
                    <option>50</option>
                </select>
                <span>records</span>
            </div>
        </div>
    )
}
