import { apiFetch } from "@/lib/api";

export type EvidenceNodeType = "VIOLATION" | "OPA_DECISION" | "SOP" | "ENFORCEMENT" | "EVIDENCE" | "AUDIT_EVENT";

export interface EvidenceNode {
    id: string;
    type: EvidenceNodeType;
    payload: Record<string, any>;
    hash: string;
    parent_hash?: string;
    created_at: string;
    created_by: string; // system / user / service
    verified: boolean;
}

export interface SnapshotAnchor {
    snapshot_id: string;
    snapshot_hash: string;
    sealed_at: string;
}

export interface EvidenceChain {
    chain_id: string;
    root_violation_id: string;
    nodes: EvidenceNode[];
    chain_hash: string;
    verified: boolean;
    verification_level: "FULL" | "PARTIAL" | "UNVERIFIED";
    snapshot_anchor?: SnapshotAnchor;
}

export async function getEvidenceChain(violationId: string): Promise<EvidenceChain | null> {
    const { data, error } = await apiFetch(`/violations/${violationId}/evidence-chain`);
    if (error) {
        console.error("Failed to fetch evidence chain:", error);
        return null;
    }
    return data;
}
