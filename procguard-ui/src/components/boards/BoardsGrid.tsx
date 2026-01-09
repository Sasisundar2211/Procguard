"use client";

import React, { useState, useEffect } from "react"
import Link from "next/link"
import { DashboardSummary } from "@/domain/dashboard"
import { Board, getBoards, createBoard, deleteBoard } from "@/domain/boards"

interface BoardsGridProps {
    stats: DashboardSummary;
}

export default function BoardsGrid({ stats }: BoardsGridProps) {
    const [boards, setBoards] = useState<Board[]>([])
    const [loading, setLoading] = useState(true)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [lastError, setLastError] = useState<string | null>(null)
    const [isCreating, setIsCreating] = useState(false)
    const [newBoardTitle, setNewBoardTitle] = useState("")

    useEffect(() => {
        async function loadBoards() {
            setLoading(true)
            const data = await getBoards()
            if (Array.isArray(data)) {
                setBoards(data)
            } else {
                console.error("Failed to load boards: Invalid response")
            }
            setLoading(false)
        }
        loadBoards()
    }, [])

    const handleStartCreate = () => {
        setIsCreating(true)
        setNewBoardTitle("")
    }

    const handleCancelCreate = () => {
        setIsCreating(false)
        setNewBoardTitle("")
        setLastError(null)
    }

    const handleSubmitCreate = async (e?: React.FormEvent) => {
        e?.preventDefault()
        if (!newBoardTitle.trim()) return

        setIsSubmitting(true)
        setLastError(null)

        const mutationId = crypto.randomUUID()
        const result = await createBoard({
            title: newBoardTitle.trim(),
            color: "bg-slate-600",
            // href is assigned canonically by the backend
            clientMutationId: mutationId
        })

        if (result.status === "ok") {
            const updatedBoards = await getBoards()
            if (Array.isArray(updatedBoards)) {
                setBoards(updatedBoards)
                setIsCreating(false)
                setNewBoardTitle("")
            } else {
                setLastError("Board created but failed to sync (Network Error)")
            }
        } else {
            setLastError(`Command Failed: ${result.reason}`)
        }
        setIsSubmitting(false)
    }

    const handleDeleteBoard = async (e: React.MouseEvent, boardId: string, title: string) => {
        e.preventDefault()
        e.stopPropagation()
        if (!window.confirm(`Are you sure you want to remove the "${title}" board? This action is auditable.`)) return

        setIsSubmitting(true)
        const result = await deleteBoard(boardId)
        if (result.status === "ok") {
            // Authoritative re-fetch after soft-delete
            const updatedBoards = await getBoards()
            if (Array.isArray(updatedBoards)) {
                setBoards(updatedBoards)
            }
        } else {
            alert(`Deletion Failed: ${result.reason}`)
        }
        setIsSubmitting(false)
    }

    // Map Backend stats to Board instances (Command Architecture)
    const displayBoards = boards.map(b => {
        if (!b.isSystem) return { ...b, primaryCount: 0, secondaryCount: 0 };

        // System Board Mapping Logic
        switch (b.title) {
            case "Procedure":
                return { ...b, primaryLabel: "Active", primaryCount: stats.totalProcedures, secondaryLabel: "Pending", secondaryCount: 0 };
            case "Batch State":
                return { ...b, primaryLabel: "Total", primaryCount: stats.totalBatches, secondaryLabel: "Completed", secondaryCount: stats.completedBatches };
            case "Violation":
                return { ...b, primaryLabel: "Violated", primaryCount: stats.violatedBatches, secondaryLabel: "Resolved", secondaryCount: 0 };
            case "Audit Evidence":
                return { ...b, primaryLabel: "Items", primaryCount: 0, secondaryLabel: "Reviews", secondaryCount: 0, locked: true };
            default:
                return { ...b, primaryCount: 0, secondaryCount: 0 };
        }
    });

    return (
        <div className="mb-8 bg-slate-50 p-6 rounded-xl border border-slate-200">
            {/* Header */}
            <div className="flex justify-between items-center mb-6 h-10">
                <h2 className="text-2xl font-bold text-[#1e293b]">Boards</h2>
                <div className="flex items-center gap-4">
                    {isCreating ? (
                        <form onSubmit={handleSubmitCreate} className="flex items-center gap-2 animate-in fade-in slide-in-from-right-4 duration-300">
                            <input
                                autoFocus
                                type="text"
                                value={newBoardTitle}
                                onChange={(e) => setNewBoardTitle(e.target.value)}
                                placeholder="Board Name..."
                                className="px-3 py-1.5 text-sm border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-slate-500 w-48 text-slate-800"
                                disabled={isSubmitting}
                            />
                            <button
                                type="submit"
                                disabled={isSubmitting || !newBoardTitle.trim()}
                                className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-md text-sm font-semibold shadow-sm transition-colors disabled:opacity-50"
                            >
                                {isSubmitting ? "..." : "Save"}
                            </button>
                            <button
                                type="button"
                                onClick={handleCancelCreate}
                                disabled={isSubmitting}
                                className="text-slate-500 hover:text-slate-800 px-2 py-1.5 text-sm font-medium transition-colors"
                            >
                                Cancel
                            </button>
                        </form>
                    ) : (
                        <>
                            <button className="flex items-center gap-2 text-slate-500 hover:text-slate-700 text-sm font-medium">
                                <InfoIcon />
                                Get help
                            </button>
                            <button
                                onClick={handleStartCreate}
                                className="bg-[#1e293b] hover:bg-slate-800 text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-md transition-all active:scale-95"
                            >
                                Create board
                            </button>
                        </>
                    )}
                </div>
            </div>

            {lastError && (
                <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    {lastError}
                </div>
            )}

            {/* Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {loading ? (
                    <div className="col-span-4 flex justify-center py-12">
                        <div className="animate-pulse text-slate-400 font-medium tracking-widest">LOADING COMMAND STATE...</div>
                    </div>
                ) : displayBoards.map((board) => (
                    <Link
                        key={board.title}
                        href={board.href}
                        className="block bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden hover:shadow-md transition-all group cursor-pointer hover:-translate-y-1"
                    >
                        {/* Color Card Header */}
                        <div className={`${board.color} h-28 p-4 flex flex-col justify-between relative`}>
                            <div className="flex justify-between items-start text-white/90">
                                <span className="font-medium tracking-wide"></span>
                                {!board.isSystem && (
                                    <button
                                        onClick={(e) => handleDeleteBoard(e, board.id, board.title)}
                                        className="p-1.5 hover:bg-red-500/20 rounded-lg transition-colors group/delete"
                                        title="Delete board"
                                    >
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-white opacity-60 group-hover/delete:opacity-100">
                                            <path d="M18 6L6 18M6 6l12 12" />
                                        </svg>
                                    </button>
                                )}
                            </div>
                            <h3 className="text-white text-lg font-bold tracking-wide">{board.title}</h3>

                            {board.locked && (
                                <div className="absolute bottom-3 right-3 text-white/90 bg-black/10 p-1.5 rounded-lg">
                                    <LockIcon />
                                </div>
                            )}
                        </div>

                        {/* Card Body */}
                        <div className="p-4 flex items-center justify-between min-h-[80px]">
                            <div className="flex gap-6">
                                <div>
                                    <div className="text-xl font-bold text-slate-800">{board.primaryCount}</div>
                                    <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{board.primaryLabel}</div>
                                </div>
                                <div>
                                    <div className="text-xl font-bold text-slate-800">{board.secondaryCount}</div>
                                    <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{board.secondaryLabel}</div>
                                </div>
                            </div>
                            <button className="text-slate-300 hover:text-slate-600">
                                <VerticalDotsIcon />
                            </button>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    )
}

// Icons
function InfoIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
    )
}

function DotsIcon() {
    return (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="12" cy="5" r="2"></circle>
            <circle cx="12" cy="12" r="2"></circle>
            <circle cx="12" cy="19" r="2"></circle>
        </svg>
    )
}

function LockIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
        </svg>
    )
}

function VerticalDotsIcon() {
    return (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" className="transform rotate-90">
            <circle cx="12" cy="5" r="2"></circle>
            <circle cx="12" cy="12" r="2"></circle>
            <circle cx="12" cy="19" r="2"></circle>
        </svg>
    )
}
