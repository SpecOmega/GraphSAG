from __future__ import annotations
import time,uuid
from graphsag.domain.models import *
from graphsag.engine.registry import ProviderRegistry
from graphsag.engine.evidence import EvidenceValidator
from graphsag.engine.audit import AuditSink
from graphsag.governance.adaptive import AdaptiveGovernance, GovernanceMode

class DecisionEngine:
    def __init__(self,registry:ProviderRegistry,audit:AuditSink,validator:EvidenceValidator|None=None,governance:AdaptiveGovernance|None=None):
        self.registry=registry; self.validator=validator or EvidenceValidator(registry); self.audit=audit; self.governance=governance or AdaptiveGovernance()
    def decide(self,request:Request,observations:list[Observation])->Decision:
        vr=self.validator.validate(request,observations); specs=self.registry.providers
        required={pid for pid,s in specs.items() if s.requirement is Requirement.REQUIRED}; observed={o.provider_id:o for o in vr.valid}
        missing=required-observed.keys(); errors={o.provider_id for o in observations if o.status in {ProviderStatus.ERROR,ProviderStatus.TIMEOUT}}; denied={o.provider_id for o in vr.valid if o.status is ProviderStatus.DENY}
        reasons=[]; outcome=DecisionOutcome.ALLOW
        if missing: reasons.append('REQUIRED_PROVIDER_MISSING'); outcome=DecisionOutcome.FAIL_CLOSED
        if errors & required: reasons.append('REQUIRED_PROVIDER_FAILURE'); outcome=DecisionOutcome.FAIL_CLOSED
        if denied & required: reasons.append('REQUIRED_PROVIDER_DENY'); outcome=DecisionOutcome.FAIL_CLOSED
        if not vr.valid and observations: reasons.append('NO_VALID_EVIDENCE'); outcome=DecisionOutcome.FAIL_CLOSED
        if outcome is DecisionOutcome.ALLOW and vr.rejected: reasons.append('SOME_EVIDENCE_REJECTED'); outcome=DecisionOutcome.ALLOW_PARTIAL
        gov=self.governance.evaluate(request.profile,len(missing | (errors & required)),len(vr.rejected))
        if gov.mode is GovernanceMode.EMERGENCY_STOP: reasons.append('DYNAMIC_EMERGENCY_STOP'); outcome=DecisionOutcome.FAIL_CLOSED
        elif gov.mode is GovernanceMode.ISOLATED and outcome is DecisionOutcome.ALLOW: reasons.append('DYNAMIC_ISOLATION'); outcome=DecisionOutcome.ALLOW_PARTIAL
        now=time.time(); exp=request.expires_at or now+300
        d=Decision(str(uuid.uuid4()),request.request_id,request.generation,self.registry.policy_version,self.registry.version,outcome,request.profile.risk,tuple(sorted(set(reasons))),tuple(sorted(o.digest() for o in vr.valid)),now,exp,request.profile.audit_required)
        if d.audit_required and d.risk.rank()>=RiskLevel.HIGH.rank():
            ev=AuditEvent(str(uuid.uuid4()),'DECISION_COMMIT',request.request_id,d.decision_id,{'outcome':d.outcome.value,'risk':d.risk.value,'evidence_hashes':d.evidence_hashes,'governance_mode':gov.mode.value})
            if not self.audit.commit(ev):
                return Decision(d.decision_id,d.request_id,d.generation,d.policy_version,d.registry_version,DecisionOutcome.FAIL_CLOSED,d.risk,d.reason_codes+('AUDIT_COMMIT_FAILURE',),d.evidence_hashes,d.created_at,d.expires_at,d.audit_required)
        return d
