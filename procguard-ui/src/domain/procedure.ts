import { apiFetch } from "@/lib/api";

export interface ProcedureStep {
    step_id: string;
    step_order: number;
    step_name: string;
    requires_approval: boolean;
    approver_role: string | null;
}

export interface Procedure {
    procedure_id: string;
    version: number;
    name: string;
    description: string;
    steps: ProcedureStep[];
    created_at: string;
}

export interface ProcedureView {
    name: string;
    version: string;
    purpose: string;
    steps: {
        order: number;
        label: string;
        requiresApproval: boolean;
    }[];
}

export async function getProcedures(): Promise<Procedure[]> {
    const { data, error } = await apiFetch("/procedures/");
    if (error) throw new Error(error);
    return data;
}
