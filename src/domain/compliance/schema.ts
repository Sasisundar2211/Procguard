export function normalizeComplianceReports(payload: any): any[] {
    if (Array.isArray(payload)) return payload;
    if (Array.isArray(payload?.reports)) return payload.reports;
    if (Array.isArray(payload?.data)) return payload.data;
    if (payload?.data && Array.isArray(payload.data.reports)) return payload.data.reports;
    return [];
}
