export default function Topbar() {
    return (
        <header className="h-12 border-b flex items-center justify-between px-6 bg-white">
            <div /> {/* Spacer */}
            <div className="flex items-center gap-6 text-xs text-slate-600 font-medium">
                <div className="flex items-center gap-2 cursor-pointer">
                    <UserIcon />
                    <span className="text-slate-900">Admin</span>
                    <ChevronDownIcon />
                </div>

                <span>Session Timeout 25:00</span>

                <button className="text-sky-400 p-1 rounded hover:bg-slate-50">
                    <SunIcon />
                </button>
            </div>
        </header>
    )
}

function UserIcon() {
    return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" className="text-slate-800">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
        </svg>
    )
}

function ChevronDownIcon() {
    return (
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
    )
}

function SunIcon() {
    return (
        <div className="w-6 h-6 bg-sky-100 rounded-full flex items-center justify-center text-sky-500">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
        </div>
    )
}
