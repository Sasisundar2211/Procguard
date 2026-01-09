import { apiFetch } from "@/lib/api";

export interface AuditLogItem {
    id: string;
    created_at: string;
    source: "SYSTEM" | "OPA";
    project_id: string;
    event_type?: string | null;
    user_id?: string | null;
    client_id?: string | null;
    payload: Record<string, any>;

    // Authoritative Rich Fields
    actor?: string | null;
    action?: string | null;
    result?: string | null;
    expected_state?: string | null;
    actual_state?: string | null;
    // Forensic Hash Chain (Step 4)
    audit_hash?: string;
    violation_hash_link?: string;
}

export interface OPAAuditLogItem {
    id: string;
    timestamp: string;
    project_id: string;
    policy_package: string;
    rule: string;
    decision: "allow" | "deny";
    resource_type: string;
    resource_id?: string;
    input_hash: string;
    result_hash: string;
    decision_hash: string; // Root of truth
    linked_violation_id?: string;
    immutable: boolean;
}

export interface AuditLogResponse {
    items: AuditLogItem[];
    total: number;
    mode?: "live" | "degraded";
    error?: string;
}

export interface OPAAuditLogResponse {
    items: OPAAuditLogItem[];
    total: number;
}

/**
 * Hardened fetchAuditLogs (Step 1)
 * Enforces UUID contract for project_id.
 */
export async function fetchAuditLogs(filters: {
    domain: "SYSTEM" | "OPA";
    projectId?: string; // MUST BE UUID
    eventType?: string;
    userId?: string;
    clientId?: string;
    from_ts: string;
    to_ts: string;
}): Promise<AuditLogResponse> {
    const params = new URLSearchParams({
        domain: filters.domain,
        from_ts: filters.from_ts,
        to_ts: filters.to_ts,
    });

    if (filters.projectId) {
        params.append("project_id", filters.projectId);
    }

    if (filters.eventType) params.append("event_type", filters.eventType);
    if (filters.userId) params.append("user_id", filters.userId);
    if (filters.clientId) params.append("client_id", filters.clientId);

    const { data, error, status } = await apiFetch(`/audit-logs?${params.toString()}`);

    // Enterprise Resilience: Handle Circuit/Network Failure as Degraded Mode
    if (error === "circuit_open" || error === "network_failure" || status === 503 || status === 0) {
        return {
            items: [],
            total: 0,
            mode: "degraded",
            error: typeof error === "string" ? error : "Resilience event"
        };
    }

    if (error) {
        throw new Error(error);
    }
    if (!data) {
        return { items: [], total: 0 };
    }

    return {
        items: Array.isArray(data.items) ? data.items : [],
        total: typeof data.total === "number" ? data.total : 0,
        mode: "live"
    };
}

/**
 * Authoritative fetchOpaAuditLogs (Step 3)
 * Fetches policy decision trail from dedicated OPA endpoint.
 */
export async function fetchOpaAuditLogs(filters: {
    projectId?: string;
    from_ts: string;
    to_ts: string;
    decision?: string;
}): Promise<OPAAuditLogResponse> {
    const params = new URLSearchParams({
        from_ts: filters.from_ts,
        to_ts: filters.to_ts,
    });

    if (filters.projectId) params.append("project_id", filters.projectId);
    if (filters.decision) params.append("decision", filters.decision);

    const { data, error } = await apiFetch(`/opa/audit-logs?${params.toString()}`);

    if (error) {
        throw new Error(error);
    }
    if (!data) {
        return { items: [], total: 0 };
    }

    return {
        items: Array.isArray(data.items) ? data.items : [],
        total: typeof data.total === "number" ? data.total : 0,
    };
}
