export type TimeRangeOption = {
    label: string;
    value: string;
    fromHours: number | null; // null = custom / all
};

export const TIME_RANGES: TimeRangeOption[] = [
    { label: "Last 15 minutes", value: "15m", fromHours: 0.25 },
    { label: "Last 1 hour", value: "1h", fromHours: 1 },
    { label: "Last 6 hours", value: "6h", fromHours: 6 },
    { label: "Last 12 hours", value: "12h", fromHours: 12 },
    { label: "Last 24 hours", value: "24h", fromHours: 24 },
    { label: "Last 7 days", value: "7d", fromHours: 168 },
    { label: "Last 30 days", value: "30d", fromHours: 720 },
];
