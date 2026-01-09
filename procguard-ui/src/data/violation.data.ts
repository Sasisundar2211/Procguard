import { ViolationView } from "@/domain/violation"

export const violationView: ViolationView = {
    severity: "HIGH",
    batchId: "BATCH-742",
    issue: "Assembly started before mandatory approval",
    detectedAt: "10:02 AM",
    approvedAt: "10:06 AM",
    procedure: "Battery Safety SOP v1.0",
    explanation:
        "Assembly began before supervisor approval, violating the required sequence.",
}
