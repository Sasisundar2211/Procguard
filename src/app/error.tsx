"use client"

import { useEffect } from "react"

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    useEffect(() => {
        console.error("PAGE ERROR", error)
    }, [error])

    return (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-8 bg-white rounded-xl border border-rose-200 shadow-sm m-8">
            <h2 className="text-2xl font-bold text-rose-600 mb-2">Authoritative Synchronization Failure</h2>
            <p className="text-slate-500 italic mb-6">{error.message || "An unexpected error occurred while communicating with the ledger."}</p>
            <button
                onClick={() => reset()}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-bold shadow-md transition-all uppercase text-sm tracking-widest"
            >
                Retry Authorization
            </button>
        </div>
    )
}
