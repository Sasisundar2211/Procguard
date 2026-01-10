import { TimelineView, TimelineCell } from "@/domain/timeline"

const TOTAL_COLS = 70

function createCells(
    startGreen: number,
    endGreen: number, // inclusive
    markers: Record<number, { display: number; badge?: "ALERT"; dot?: "ORANGE" | "BLUE" }> = {}
): TimelineCell[] {
    return Array.from({ length: TOTAL_COLS }, (_, i) => {
        let status: "ON_TIME" | "OVER_TIME" | "EMPTY" = "EMPTY"
        if (i >= startGreen && i <= endGreen) {
            status = "ON_TIME"
        } else if (i > endGreen) {
            status = "OVER_TIME"
        }

        // Special case: if we want to simulate lead-in empty cells
        if (i < startGreen) status = "EMPTY"

        const markerInfo = markers[i]

        return {
            index: i,
            status,
            marker: markerInfo?.display,
            badge: markerInfo?.badge,
            dot: markerInfo?.dot,
        }
    })
}

export const timelineView: TimelineView = {
    leadTime: Array.from({ length: TOTAL_COLS }, (_, i) => i),
    stages: [
        {
            label: "USP BMR Review",
            cells: createCells(0, 2, {}),
        },
        {
            label: "DSP BMR Review",
            cells: createCells(0, 8, {}),
        },
        {
            label: "QA BMR Review",
            cells: createCells(9, 23, {
                22: { display: 22 },
                21: { display: 21 },
                20: { display: 20 }, // Transition to red often happens after this
                29: { display: 19, badge: "ALERT" },
                41: { display: 17, badge: "ALERT" },
                51: { display: 16 },
            }),
        },
        {
            label: "QP BMR Review",
            cells: createCells(20, 29, {
                36: { display: 18 },
            }),
        },
        {
            label: "Prod Deviations Window",
            cells: createCells(24, 38, {
                56: { display: 15, badge: "ALERT" },
            }),
        },
        {
            label: "QC Testing",
            cells: createCells(0, 28, {
                15: { display: 21, dot: "BLUE" },
                20: { display: 20 },
                28: { display: 19, badge: "ALERT" },
                36: { display: 18 },
                41: { display: 17, badge: "ALERT", dot: "ORANGE" },
                50: { display: 16, dot: "BLUE" },
                56: { display: 15, badge: "ALERT", dot: "BLUE" },
            }),
        },
        {
            label: "QC DRS/Review",
            cells: createCells(51, 60, {}),
        },
        {
            label: "Lot Release QA",
            cells: createCells(61, 65, {}),
        },
        {
            label: "QP Release",
            cells: createCells(65, 68, {}),
        },
        {
            label: "Shippable Batch",
            cells: createCells(69, 70, {
                64: { display: 14 },
            }),
        },
    ],
    ranges: [
        { label: "70–75", count: 0 },
        { label: "75–80", count: 0 },
        { label: "80–85", count: 11 },
        { label: "85–90", count: 0 },
        { label: "90–95", count: 0 },
        { label: "95–100", count: 0 },
        { label: "100–150", count: 4 },
        { label: "150–200", count: 0 },
        { label: "200+", count: 22 }, // Showing 22(22) in design
    ],
}
