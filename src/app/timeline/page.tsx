"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function TimelineRedirect() {
    const router = useRouter();
    const defaultBatchId = "f1989a15-15ab-4981-9914-72ee6ba3addf";

    useEffect(() => {
        // Redirecting to the authoritative dynamic route
        router.push(`/batches/${defaultBatchId}/timeline`);
    }, [router]);

    return (
        <div className="flex items-center justify-center min-h-[400px]">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-slate-500 italic">Redirecting to Authoritative Timeline...</span>
        </div>
    );
}
