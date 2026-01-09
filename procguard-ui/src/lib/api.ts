import { isCircuitOpen, recordFailure, recordSuccess } from "./circuitBreaker";
import { correlationId } from "./correlation";

const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

/**
 * Enterprise-grade apiFetch (Step 4 & Phase 2/3)
 * - Circuit Breaker enforced
 * - Correlation IDs for audit
 * - 5s hard timeout
 * - NO THROWS
 */
export async function apiFetch(endpoint: string, options: RequestInit = {}) {
    if (isCircuitOpen()) {
        return { data: null, error: "circuit_open", status: 503 };
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    try {
        const res = await fetch(`${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : "/" + endpoint}`, {
            ...options,
            signal: controller.signal,
            cache: "no-store",
            headers: {
                "X-Correlation-ID": correlationId(),
                "Content-Type": "application/json",
                ...(options.headers || {}),
            },
        });

        clearTimeout(timeout);

        if (!res.ok) {
            recordFailure();
            const text = await res.text().catch(() => null);
            return {
                data: null,
                error: text || `HTTP_${res.status}`,
                status: res.status
            };
        }

        recordSuccess();
        const data = await res.json().catch(() => ({}));
        return {
            data,
            error: null,
            status: res.status
        };
    } catch (err) {
        recordFailure();
        return {
            data: null,
            error: "network_failure",
            status: 0
        };
    }
}

/**
 * Health check on startup (Step 4)
 */
export async function checkBackendHealth() {
    try {
        await apiFetch("/health");
        return true;
    } catch (err) {
        console.error("Health check failed", err);
        return false;
    }
}
