import { getViolation } from "@/domain/violations";
import ViolationForensicDetail from "@/components/violation/ViolationForensicDetail";
import ErrorState from "@/components/common/ErrorState";
import EmptyState from "@/components/common/EmptyState";

export default async function ViolationPage({
    params
}: {
    params: Promise<{ violationId: string }>
}) {
    // Next.js 15: params is now a Promise
    const { violationId } = await params;

    try {
        const violation = await getViolation(violationId);

        if (!violation) {
            // This case shouldn't happen with apiFetch throwing on !ok, but for safety:
            return (
                <EmptyState
                    title="Violation not found"
                    subtitle="This violation no longer exists or was archived."
                />
            );
        }

        return <ViolationForensicDetail violation={violation} />;
    } catch (error: any) {
        console.log("Forensic Retrieval Error:", error.status, error.message);

        // Handle 404 explicitly for "Enterprise UX"
        if (error.status === 404 || error.message?.includes("404")) {
            return (
                <EmptyState
                    title="Violation not found"
                    subtitle="This violation record could not be located in the forensic store."
                />
            );
        }

        // Return descriptive error state for 409 or 500
        return (
            <ErrorState
                title="Violation record unavailable"
                message={error.message || "A forensic synchronization error occurred while retrieving the violation record."}
            />
        );
    }
}
