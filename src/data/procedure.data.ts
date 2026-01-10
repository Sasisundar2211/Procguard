import { ProcedureView } from "@/domain/procedure"

export const procedureView: ProcedureView = {
    name: "Battery Assembly Safety Check",
    version: "v1.0",
    purpose:
        "Ensures supervisor approval is completed before assembly begins.",
    steps: [
        { order: 1, label: "Sensor Safety Check", requiresApproval: false },
        { order: 2, label: "Supervisor Approval", requiresApproval: true },
        { order: 3, label: "Assembly Start", requiresApproval: false },
    ],
}
