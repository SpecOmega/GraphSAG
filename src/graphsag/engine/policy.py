from __future__ import annotations
from dataclasses import dataclass
from threading import RLock
from graphsag.domain.models import RiskLevel
@dataclass(frozen=True)
class Policy:
    version:str
    max_risk_without_audit:RiskLevel=RiskLevel.MEDIUM
    decision_ttl_seconds:int=300
class PolicyStore:
    def __init__(self,initial:Policy): self._policy=initial; self._lock=RLock()
    def get(self):
        with self._lock: return self._policy
    def publish(self,policy:Policy):
        with self._lock:
            if policy.version <= self._policy.version: raise ValueError('POLICY_VERSION_MUST_INCREASE')
            self._policy=policy
