"use client";

import React from 'react';

interface BackendOfflineProps {
    reason?: string;
}

export default function BackendOffline({ reason }: BackendOfflineProps) {
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] p-8 text-center animate-in fade-in duration-700">
            <div className="bg-red-50 p-6 rounded-full mb-6">
                <svg
                    className="w-16 h-16 text-red-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    ></path>
                </svg>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">System Unavailable</h1>
            <p className="text-gray-500 max-w-md mb-8">
                The dashboard service cannot be reached at this time.
            </p>
            {reason && (
                <div className="bg-gray-100 px-4 py-2 rounded text-xs font-mono text-gray-600 border border-gray-200">
                    Error Code: {reason}
                </div>
            )}
            <button
                onClick={() => window.location.reload()}
                className="mt-8 px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
            >
                Retry Connection
            </button>
        </div>
    );
}
