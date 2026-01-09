import hashlib
import json
from typing import Optional

def compute_record_hash(record: dict, prev_hash: Optional[str]) -> str:
    """
    Computes a SHA-256 hash of the record, chained to the previous record's hash.
    Ensures a tamper-evident chain of custody.
    """
    # Canonicalize JSON to ensure deterministic hashing
    canonical = json.dumps(record, sort_keys=True, default=str)
    base = f"{prev_hash or ''}{canonical}"
    return hashlib.sha256(base.encode()).hexdigest()
