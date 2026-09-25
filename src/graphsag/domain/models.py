from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import hashlib, json, time, uuid

class RiskLevel(str, Enum):
    LOW="LOW"; MEDIUM="MEDIUM"; HIGH="HIGH"; CRITICAL="CRITICAL"
    def rank(self): return {"LOW":0,"MEDIUM":1,"HIGH":2,"CRITICAL":3}[self.value]

class Requirement(str, Enum): REQUIRED="REQUIRED"; OPTIONAL="OPTIONAL"
class ProviderStatus(str, Enum): ALLOW="ALLOW"; DENY="DENY"; ERROR="ERROR"; TIMEOUT="TIMEOUT"
class DecisionOutcome(str, Enum): ALLOW="ALLOW"; ALLOW_PARTIAL="ALLOW_PARTIAL"; DENY="DENY"; FAIL_CLOSED="FAIL_CLOSED"

@dataclass(frozen=True)
class SecurityProfile:
    name:str; risk:RiskLevel; audit_required:bool=True; high_risk_actions:tuple[str,...]=(); dynamic_governance:bool=False

@dataclass(frozen=True)
class Request:
    request_id:str; generation:int; principal_id:str; profile:SecurityProfile; action:str
    tenant_id:str|None=None
    resource_id:str|None=None
    created_at:float=field(default_factory=time.time)
    expires_at:float|None=None

@dataclass(frozen=True)
class ProviderSpec:
    provider_id:str; version:str; purpose:str; requirement:Requirement; timeout_ms:int=3000
    risk_cap:RiskLevel=RiskLevel.CRITICAL

@dataclass(frozen=True)
class Observation:
    provider_id:str; provider_version:str; registry_version:str; request_id:str; generation:int
    principal_id:str; claim:str; requirement:Requirement; status:ProviderStatus
    payload:dict[str,Any]=field(default_factory=dict); source_uri:str|None=None
    evidence_hash:str|None=None; issued_at:float=field(default_factory=time.time); expires_at:float|None=None
    nonce:str|None=None; signing_key_id:str|None=None; signature:str|None=None; policy_version:str|None=None
    def canonical(self):
        return {"provider_id":self.provider_id,"provider_version":self.provider_version,"registry_version":self.registry_version,"request_id":self.request_id,"generation":self.generation,"principal_id":self.principal_id,"claim":self.claim,"requirement":self.requirement.value,"status":self.status.value,"payload":self.payload,"source_uri":self.source_uri,"issued_at":self.issued_at,"expires_at":self.expires_at,"nonce":self.nonce,"policy_version":self.policy_version}
    def digest(self): return hashlib.sha256(json.dumps(self.canonical(),sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

@dataclass(frozen=True)
class Decision:
    decision_id:str; request_id:str; generation:int; policy_version:str; registry_version:str
    outcome:DecisionOutcome; risk:RiskLevel; reason_codes:tuple[str,...]; evidence_hashes:tuple[str,...]
    created_at:float; expires_at:float; audit_required:bool

@dataclass(frozen=True)
class AuditEvent:
    event_id:str; event_type:str; request_id:str; decision_id:str|None; payload:dict[str,Any]; ts:float=field(default_factory=time.time)
    def canonical(self): return {"event_id":self.event_id,"event_type":self.event_type,"request_id":self.request_id,"decision_id":self.decision_id,"payload":self.payload,"ts":self.ts}
    def digest(self): return hashlib.sha256(json.dumps(self.canonical(),sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
