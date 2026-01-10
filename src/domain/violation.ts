export interface ViolationView {
    severity: string;
    batchId: string;
    issue: string;
    detectedAt: string;
    approvedAt: string;
    procedure: string;
    explanation: string;
}
