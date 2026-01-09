let failureCount = 0;
let openUntil = 0;

export function isCircuitOpen() {
    return Date.now() < openUntil;
}

export function recordFailure() {
    failureCount++;
    if (failureCount >= 3) {
        openUntil = Date.now() + 30_000; // 30 seconds
        failureCount = 0;
    }
}

export function recordSuccess() {
    failureCount = 0;
}
