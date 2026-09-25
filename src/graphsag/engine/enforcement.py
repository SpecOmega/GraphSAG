from __future__ import annotations
import time
from graphsag.domain.models import Decision,DecisionOutcome
from graphsag.security.capability import Capability,CapabilityAuthority

class EnforcementError(PermissionError): pass
class EnforcementGuard:
    def __init__(self,registry, capability_authority:CapabilityAuthority|None=None, clock=time.time): self.registry=registry; self.capability_authority=capability_authority; self.clock=clock
    def authorize(self,decision:Decision,request,capability:Capability|None=None,*legacy):
        # Backward-compatible reference API: authorize(decision, action, resource_id, principal_id, generation) -> (bool, reason).
        if isinstance(request, str):
            action=request; resource_id=capability; principal_id=legacy[0] if len(legacy)>0 else ''; generation=legacy[1] if len(legacy)>1 else -1
            if decision.outcome not in {DecisionOutcome.ALLOW,DecisionOutcome.ALLOW_PARTIAL}: return (False,'DECISION_NOT_ALLOW')
            if self.clock()>decision.expires_at: return (False,'DECISION_EXPIRED')
            if decision.registry_version!=self.registry.version: return (False,'STALE_REGISTRY')
            if decision.generation!=generation: return (False,'GENERATION_MISMATCH')
            return (True,'AUTHORIZED')
        if decision.outcome not in {DecisionOutcome.ALLOW,DecisionOutcome.ALLOW_PARTIAL}: raise EnforcementError('DECISION_NOT_ALLOW')
        if self.clock()>decision.expires_at: raise EnforcementError('DECISION_EXPIRED')
        if decision.registry_version!=self.registry.version: raise EnforcementError('STALE_REGISTRY')
        if decision.generation!=request.generation: raise EnforcementError('GENERATION_MISMATCH')
        if not request.principal_id or not request.action: raise EnforcementError('INVALID_EXECUTION_BINDING')
        if self.capability_authority:
            if capability is None: raise EnforcementError('CAPABILITY_REQUIRED')
            try: self.capability_authority.verify(capability,request.principal_id,request.action,request.resource_id,request.generation,self.clock())
            except PermissionError as exc: raise EnforcementError(str(exc)) from exc
        return True
