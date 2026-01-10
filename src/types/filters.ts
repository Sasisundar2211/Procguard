export type TimeFilter =
    | { mode: "preset"; value: string }
    | {
        mode: "custom";
        from: string; // ISO 8601 UTC
        to: string;   // ISO 8601 UTC
    };
