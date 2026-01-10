import "@/styles/globals.css"
import Sidebar from "@/components/layout/Sidebar"
import Topbar from "@/components/layout/Topbar"
import { ApiHealthProvider } from "@/context/ApiHealthContext"
// import { AuthProvider } from "@/context/AuthContext" // Example if exists
import { SafeProvider } from "@/components/SafeProvider"

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body className="bg-slate-50 text-slate-800 font-sans">
                <SafeProvider>
                    <ApiHealthProvider>
                        <div className="flex h-screen">
                            <Sidebar />
                            <div className="flex flex-col flex-1">
                                <Topbar />
                                <main className="p-6 overflow-auto">{children}</main>
                            </div>
                        </div>
                    </ApiHealthProvider>
                </SafeProvider>
            </body>
        </html>
    )
}
