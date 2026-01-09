import { UUID } from "crypto";

export type Board = {
    id: string;
    title: string;
    description?: string;
    color: string;
    href: string;
    primaryLabel?: string;
    primaryCount?: number;
    secondaryLabel?: string;
    secondaryCount?: number;
    isSystem: boolean;
    locked?: boolean;
    status: "ACTIVE" | "DEPRECATED" | "DELETED";
};

export type BoardCreate = {
    title: string;
    description?: string;
    color?: string;
    href?: string;
    clientMutationId?: string;
};

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function getBoards(): Promise<Board[]> {
    try {
        const res = await fetch(`${API_URL}/boards/`, {
            cache: "no-store",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (!res.ok) {
            console.error("Failed to fetch boards", res.status);
            return [];
        }

        const data = await res.json();

        // Map backend snake_case to frontend camelCase
        return data.map((b: any) => ({
            id: b.id,
            title: b.title,
            description: b.description,
            color: b.color,
            href: b.href,
            primaryLabel: b.primary_label,
            secondaryLabel: b.secondary_label,
            isSystem: b.is_system,
            status: b.status,
        }));
    } catch (err) {
        console.error("Error fetching boards", err);
        return [];
    }
}

export async function createBoard(board: BoardCreate): Promise<{ status: "ok"; data: Board } | { status: "error"; reason: string }> {
    try {
        const res = await fetch(`${API_URL}/boards/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                ...board,
                client_mutation_id: board.clientMutationId
            }),
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            return { status: "error", reason: errData.detail || `HTTP_${res.status}` };
        }

        const b = await res.json();
        return {
            status: "ok",
            data: {
                id: b.id,
                title: b.title,
                description: b.description,
                color: b.color,
                href: b.href,
                primaryLabel: b.primary_label,
                secondaryLabel: b.secondary_label,
                isSystem: b.is_system,
                status: b.status,
            },
        };
    } catch (err) {
        return { status: "error", reason: "network_failure" };
    }
}

export async function deleteBoard(boardId: string): Promise<{ status: "ok" } | { status: "error"; reason: string }> {
    try {
        const res = await fetch(`${API_URL}/boards/${boardId}`, {
            method: "DELETE",
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            return { status: "error", reason: errData.detail || `HTTP_${res.status}` };
        }

        return { status: "ok" };
    } catch (err) {
        return { status: "error", reason: "network_failure" };
    }
}
