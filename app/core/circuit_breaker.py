from datetime import datetime, timedelta
import threading
from typing import Dict, Literal, Optional, Any, Tuple
from pydantic import BaseModel
from enum import Enum

class CircuitType(str, Enum):
    AVAILABILITY = "AVAILABILITY" # Timeouts, network, DB lag
    INTEGRITY = "INTEGRITY"       # Hash mismatch, signature failure

class SubCircuitState(BaseModel):
    state: Literal["closed", "open", "half_open"] = "closed"
    failure_count: int = 0
    success_count: int = 0
    opened_at: Optional[datetime] = None
    last_failure_reason: Optional[str] = None

class EnterpriseCircuitState(BaseModel):
    endpoint: str
    availability: SubCircuitState = SubCircuitState()
    integrity: SubCircuitState = SubCircuitState()
    last_success_at: Optional[datetime] = None

class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=30, half_open_success=2):
        self.lock = threading.Lock()
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_success = half_open_success
        
        # Authoritative in-memory state
        self.circuits: Dict[str, EnterpriseCircuitState] = {}

    def get_state(self, endpoint: str) -> EnterpriseCircuitState:
        with self.lock:
            if endpoint not in self.circuits:
                self.circuits[endpoint] = EnterpriseCircuitState(endpoint=endpoint)
            
            state = self.circuits[endpoint]
            now = datetime.utcnow()

            # Check for Half-Open transitions for both tracks
            for track in [state.availability, state.integrity]:
                if track.state == "open" and track.opened_at:
                    if now - track.opened_at > timedelta(seconds=self.reset_timeout):
                        track.state = "half_open"
                        track.success_count = 0
                        print(f"[CIRCUIT] {endpoint} track transitioning to HALF_OPEN")

            return state

    def record_success(self, endpoint: str):
        with self.lock:
            if endpoint not in self.circuits:
                self.circuits[endpoint] = EnterpriseCircuitState(endpoint=endpoint)
            state = self.circuits[endpoint]
            state.last_success_at = datetime.utcnow()

            for track in [state.availability, state.integrity]:
                if track.state == "half_open":
                    track.success_count += 1
                    if track.success_count >= self.half_open_success:
                        track.state = "closed"
                        track.failure_count = 0
                        track.opened_at = None
                elif track.state == "closed":
                    track.failure_count = 0 

    def record_failure(self, endpoint: str, reason: str, failure_type: CircuitType = CircuitType.AVAILABILITY):
        with self.lock:
            if endpoint not in self.circuits:
                self.circuits[endpoint] = EnterpriseCircuitState(endpoint=endpoint)
            state = self.circuits[endpoint]
            
            track = state.integrity if failure_type == CircuitType.INTEGRITY else state.availability

            if track.state == "open":
                return 

            track.failure_count += 1
            track.last_failure_reason = reason
            
            if track.state == "half_open" or track.failure_count >= self.failure_threshold:
                track.state = "open"
                track.opened_at = datetime.utcnow()
                print(f"[CIRCUIT] {endpoint} {failure_type} track OPEN! Reason: {reason}")

    def is_integrity_compromised(self, endpoint: str) -> bool:
        state = self.get_state(endpoint)
        return state.integrity.state == "open"

    def is_degraded(self, endpoint: str) -> bool:
        state = self.get_state(endpoint)
        return state.availability.state == "open" or state.integrity.state == "open"

    def get_health_status(self) -> Dict[str, Any]:
        """Enterprise health status with split circuit visibility"""
        status = "healthy"
        services = {}
        
        with self.lock:
            for endpoint, state in self.circuits.items():
                if state.integrity.state == "open":
                    status = "critical" # Integrity compromised
                elif state.availability.state == "open" and status != "critical":
                    status = "degraded"
                
                services[endpoint] = {
                    "availability": state.availability.state,
                    "integrity": state.integrity.state,
                    "last_success": state.last_success_at.isoformat() if state.last_success_at else None,
                    "reason": state.integrity.last_failure_reason or state.availability.last_failure_reason,
                    "retry_after": self.reset_timeout if (state.availability.state == "open" or state.integrity.state == "open") else 0
                }
        
        return {
            "status": status,
            "services": services
        }

# Global instance
circuit_breaker = CircuitBreaker()
