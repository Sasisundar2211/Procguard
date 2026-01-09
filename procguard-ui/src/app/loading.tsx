export default function Loading() {
    return (
        <div className="flex flex-col items-center justify-center min-h-[400px]">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-500"></div>
            <p className="mt-4 text-slate-500 font-medium italic">Synchronizing Authoritative Ledger...</p>
        </div>
    )
}
