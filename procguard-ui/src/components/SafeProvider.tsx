"use client";

import { ReactNode } from "react";

export function SafeProvider({ children }: { children: ReactNode }) {
    try {
        return <>{children}</>;
    } catch (e) {
        console.error("Provider crash:", e);
        return (
            <div className="p-6 text-red-600">
                System recovered from provider failure.
            </div>
        );
    }
}
