from graphsag.domain.models import *
from graphsag.engine.registry import ProviderRegistry
from graphsag.engine.audit import MemoryAuditSink
from graphsag.engine.decision import DecisionEngine

def setup(req=Requirement.REQUIRED):
 r=ProviderRegistry('reg-1','pol-1',{'p':ProviderSpec('p','1','security',req)})
 return r

def test_required_allow():
 r=setup(); req=Request('q',1,'u',SecurityProfile('high',RiskLevel.HIGH), 'read')
 o=Observation('p','1','reg-1','q',1,'u','security',Requirement.REQUIRED,ProviderStatus.ALLOW)
 d=DecisionEngine(r,MemoryAuditSink()).decide(req,[o]); assert d.outcome==DecisionOutcome.ALLOW

def test_missing_required_fail_closed():
 r=setup(); req=Request('q',1,'u',SecurityProfile('high',RiskLevel.HIGH), 'read')
 d=DecisionEngine(r,MemoryAuditSink()).decide(req,[]); assert d.outcome==DecisionOutcome.FAIL_CLOSED

def test_mismatched_generation_rejected():
 r=setup(); req=Request('q',2,'u',SecurityProfile('low',RiskLevel.LOW), 'read')
 o=Observation('p','1','reg-1','q',1,'u','security',Requirement.REQUIRED,ProviderStatus.ALLOW)
 d=DecisionEngine(r,MemoryAuditSink()).decide(req,[o]); assert d.outcome==DecisionOutcome.FAIL_CLOSED

def test_registry_change_blocks_enforcement():
 r=setup(); req=Request('q',1,'u',SecurityProfile('low',RiskLevel.LOW), 'read')
 o=Observation('p','1','reg-1','q',1,'u','security',Requirement.REQUIRED,ProviderStatus.ALLOW)
 d=DecisionEngine(r,MemoryAuditSink()).decide(req,[o]); from graphsag.engine.enforcement import EnforcementGuard
 r2=ProviderRegistry('reg-2','pol-1',r.providers); assert not EnforcementGuard(r2).authorize(d,'read','x','u',1)[0]
