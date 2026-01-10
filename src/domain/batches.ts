import { apiFetch } from "@/lib/api";

export interface Batch {
    batch_id: string;
    procedure_id: string;
    procedure_version: number;
    current_state: string;
    created_at: string;
}

export async function getBatches(): Promise<Batch[]> {
    const { data, error } = await apiFetch("/batches/");
    if (error) {
        console.error("Failed to fetch batches:", error);
        return [];
    }
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.data)) return data.data; // Handle { data: [...] }
    return [];
}
