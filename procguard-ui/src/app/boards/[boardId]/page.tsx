
import Link from "next/link";

interface BoardPageProps {
    params: {
        boardId: string;
    };
}

export default function BoardPage({ params }: BoardPageProps) {
    return (
        <div className="p-8 max-w-7xl mx-auto">
            <div className="mb-6">
                <Link href="/dashboard" className="text-slate-500 hover:text-slate-800 text-sm font-medium flex items-center gap-2 mb-4">
                    ← Back to Dashboard
                </Link>
                <h1 className="text-3xl font-bold text-slate-900">Board View</h1>
                <p className="text-slate-500 mt-2 font-mono text-sm">ID: {params.boardId}</p>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-12 flex flex-col items-center justify-center text-center shadow-sm">
                <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                    <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                </div>
                <h3 className="text-lg font-medium text-slate-900">Board Content Placeholder</h3>
                <p className="text-slate-500 max-w-sm mt-2">
                    This board exists and is routable. Content widgets will be added here in future implementation phases.
                </p>
            </div>
        </div>
    );
}
