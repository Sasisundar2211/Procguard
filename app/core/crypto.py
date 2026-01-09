import hashlib
import json

def sha256(data: str) -> str:
    """
    Standard SHA-256 hash primitive (Step 1).
    Deterministic, court-accepted, and verifiable offline.
    """
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def canonical_hash(payload: dict) -> str:
    """
    Computes a deterministic hash of a JSON payload.
    Ensures sort_keys=True for consistent verification.
    """
    # Use sort_keys=True to ensure deterministic JSON representation
    canonical_json = json.dumps(payload, sort_keys=True)
    return sha256(canonical_json)
