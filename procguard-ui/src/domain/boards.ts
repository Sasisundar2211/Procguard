import { apiFetch } from "@/lib/api";

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

export async function getBoards(): Promise<Board[]> {
    const { data, error } = await apiFetch("/boards/");

    if (error || !data) {
        console.error("Failed to fetch boards", error);
        return [];
    }

    if (!Array.isArray(data)) {
        console.error("Invalid boards response format");
        return [];
    }

    // Map backend snake_case to frontend camelCase
    return data.map((b: any) => ({
        id: b.id,
        title: b.title,
        description: b.description,
        color: b.color,
        href: b.href,
        primaryLabel: b.primary_label,
        primaryCount: b.primary_count,
        secondaryLabel: b.secondary_label,
        secondaryCount: b.secondary_count,
        isSystem: b.is_system,
        status: b.status,
    }));
}

export async function createBoard(board: BoardCreate): Promise<{ status: "ok"; data: Board } | { status: "error"; reason: string }> {
    const { data, error, status } = await apiFetch("/boards/", {
        method: "POST",
        body: JSON.stringify({
            ...board,
            client_mutation_id: board.clientMutationId
        }),
    });

    if (error || !data) {
        return { status: "error", reason: error || `HTTP_${status}` };
    }

    const b = data;
    return {
        status: "ok",
        data: {
            id: b.id,
            title: b.title,
            description: b.description,
            color: b.color,
            href: b.href,
            primaryLabel: b.primary_label,
            primaryCount: b.primary_count,
            secondaryLabel: b.secondary_label,
            secondaryCount: b.secondary_count,
            isSystem: b.is_system,
            status: b.status,
        },
    };
}

export async function deleteBoard(boardId: string): Promise<{ status: "ok" } | { status: "error"; reason: string }> {
    const { error, status } = await apiFetch(`/boards/${boardId}`, {
        method: "DELETE",
    });

    if (error) {
        return { status: "error", reason: error || `HTTP_${status}` };
    }

    return { status: "ok" };
}
