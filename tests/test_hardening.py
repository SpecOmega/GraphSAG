import time
import pytest
from graphsag.domain.models import *
from graphsag.engine.registry import ProviderRegistry,RegistryError
from graphsag.engine.evidence import EvidenceValidator
from graphsag.engine.audit import MemoryAuditSink
from graphsag.engine.decision import DecisionEngine
from graphsag.engine.enforcement import EnforcementGuard,EnforcementError
from graphsag.security.crypto import Ed25519Signer,Ed25519Verifier,SignatureError
from graphsag.security.replay import MemoryReplayStore
from graphsag.security.capability import CapabilityAuthority
from graphsag.graph.builder import build_decision_graph
from graphsag.storage.audit_chain import ChainAuditSink

def setup():
    reg=ProviderRegistry('1.0.0','1.0.0',{'auth':ProviderSpec('auth','1.0.0','auth',Requirement.REQUIRED),'risk':ProviderSpec('risk','1.0.0','risk',Requirement.OPTIONAL)})
    req=Request('r1',1,'p1',SecurityProfile('p',RiskLevel.HIGH),'read','t','x',time.time(),time.time()+60)
    return reg,req

def obs(req,provider='auth',status=ProviderStatus.ALLOW,**kw):
    return Observation(provider,'1.0.0','1.0.0',req.request_id,req.generation,req.principal_id,'ok',Requirement.REQUIRED if provider=='auth' else Requirement.OPTIONAL,status,**kw)

def test_ed25519_and_replay():
    reg,req=setup(); signer=Ed25519Signer.generate('k1'); o=obs(req,nonce='n1',expires_at=time.time()+30); sig=signer.sign(o.digest().encode()); o=Observation(**{**o.__dict__,'signature':sig,'signing_key_id':'k1'})
    v=EvidenceValidator(reg,Ed25519Verifier({'k1':signer.public_key_bytes()}),MemoryReplayStore())
    assert v.validate(req,[o]).valid
    assert v.validate(req,[o]).rejected[0][1]=='REPLAY_DETECTED'

def test_bad_signature_rejected():
    reg,req=setup(); signer=Ed25519Signer.generate('k1'); o=obs(req,nonce='n2',expires_at=time.time()+30,signature='bad',signing_key_id='k1')
    v=EvidenceValidator(reg,Ed25519Verifier({'k1':signer.public_key_bytes()}))
    assert v.validate(req,[o]).rejected[0][1]=='SIGNATURE_INVALID'

def test_capability_is_execution_bound():
    reg,req=setup(); d=DecisionEngine(reg,MemoryAuditSink()).decide(req,[obs(req)])
    ca=CapabilityAuthority(b'secret'); cap=ca.issue('c1','p1','read','x',1,time.time()+30)
    assert EnforcementGuard(reg,ca).authorize(d,req,cap)
    with pytest.raises(EnforcementError):
        EnforcementGuard(reg,ca).authorize(d,Request('r1',2,'p1',req.profile,'read','t','x',time.time(),time.time()+60),cap)

def test_graph_and_audit_chain():
    reg,req=setup(); audit=MemoryAuditSink(); d=DecisionEngine(reg,audit).decide(req,[obs(req)]); g=build_decision_graph(req,[obs(req)],d)
    assert len(g.nodes)==3 and g.digest()
    chain=ChainAuditSink(); assert chain.commit(next(iter(audit.events.values()))); assert chain.verify()

def test_registry_versions_are_monotonic():
    reg,_=setup(); reg.evolve('1.1.0','1.1.0',reg.providers)
    with pytest.raises(RegistryError): reg.evolve('1.0.0','1.0.0',reg.providers)
