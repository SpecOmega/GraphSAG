from __future__ import annotations
try:
    from fastapi import FastAPI,HTTPException,Header
except ImportError:
    FastAPI=None
from graphsag.domain.models import *
from graphsag.engine.registry import ProviderRegistry
from graphsag.engine.audit import MemoryAuditSink
from graphsag.engine.decision import DecisionEngine
from graphsag.engine.enforcement import EnforcementGuard

def create_app(registry=None,audit=None,principal_verifier=None):
    if FastAPI is None: raise RuntimeError("Install graphsag[api]")
    registry=registry or ProviderRegistry('bootstrap','bootstrap',{})
    audit=audit or MemoryAuditSink(); engine=DecisionEngine(registry,audit); guard=EnforcementGuard(registry); app=FastAPI(title='GraphSAG',version='1.0.0')
    @app.get('/healthz')
    def health(): return {'status':'ok','registry_version':registry.version}
    @app.post('/v1/decisions')
    def decide(body:dict, x_principal_id:str|None=Header(default=None)):
        if principal_verifier is None: raise HTTPException(503,'workload identity verifier not configured')
        if not x_principal_id: raise HTTPException(401,'principal required')
        principal = principal_verifier.verify(x_principal_id)
        profile=SecurityProfile(body.get('profile','default'),RiskLevel(body.get('risk','LOW')),True,tuple(body.get('high_risk_actions',[])),bool(body.get('dynamic_governance',False)))
        req=Request(body['request_id'],int(body.get('generation',0)),principal.principal_id,profile,body['action'],body.get('tenant_id'),body.get('resource_id'))
        obs=[]
        for x in body.get('observations',[]): obs.append(Observation(x['provider_id'],x['provider_version'],x['registry_version'],x['request_id'],int(x['generation']),x['principal_id'],x['claim'],Requirement(x['requirement']),ProviderStatus(x['status']),x.get('payload',{}),x.get('source_uri'),x.get('evidence_hash'), x.get('issued_at', __import__('time').time()), x.get('expires_at'), x.get('nonce'), x.get('signing_key_id'), x.get('signature'), x.get('policy_version')))
        d=engine.decide(req,obs); return d.__dict__
    return app
