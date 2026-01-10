"use client";

import React from "react";
import Link from "next/link";

interface EmptyStateProps {
    title: string;
    subtitle: string;
}

export default function EmptyState({ title, subtitle }: EmptyStateProps) {
    return (
        <div className="flex items-center justify-center min-h-[400px] p-6">
            <div className="max-w-md w-full bg-slate-50 border border-slate-200 border-dashed rounded-xl p-8 text-center">
                <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 9.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <h2 className="text-xl font-bold text-slate-900 mb-2">{title}</h2>
                <p className="text-slate-500 mb-6">{subtitle}</p>
                <Link
                    href="/violations"
                    className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-700 transition-colors shadow-sm"
                >
                    Back to Registry
                </Link>
            </div>
        </div>
    );
}
