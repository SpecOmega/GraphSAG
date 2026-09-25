from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from graphsag.domain.models import RiskLevel, SecurityProfile

class GovernanceMode(str, Enum): NORMAL='NORMAL'; RESTRICTED='RESTRICTED'; ISOLATED='ISOLATED'; EMERGENCY_STOP='EMERGENCY_STOP'

@dataclass(frozen=True)
class GovernanceState:
    mode: GovernanceMode; reason: str; generation: int; constitution_version: str

class AdaptiveGovernance:
    def __init__(self, constitution_version='1.0'):
        self.constitution_version=constitution_version
    def evaluate(self, profile: SecurityProfile, required_failures: int=0, integrity_failures: int=0) -> GovernanceState:
        if integrity_failures>0: mode=GovernanceMode.EMERGENCY_STOP; reason='INTEGRITY_FAILURE'
        elif profile.risk is RiskLevel.CRITICAL and required_failures>0: mode=GovernanceMode.ISOLATED; reason='CRITICAL_REQUIRED_PROVIDER_FAILURE'
        elif required_failures>0: mode=GovernanceMode.RESTRICTED; reason='REQUIRED_PROVIDER_FAILURE'
        else: mode=GovernanceMode.NORMAL; reason='BASELINE'
        return GovernanceState(mode,reason,0,self.constitution_version)
    def assert_constitution(self,state: GovernanceState, profile: SecurityProfile):
        if state.constitution_version != self.constitution_version: raise ValueError('CONSTITUTION_VERSION_MISMATCH')
        if state.mode is GovernanceMode.EMERGENCY_STOP: return False
        return True
