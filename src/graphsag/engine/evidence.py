from __future__ import annotations
from dataclasses import dataclass
import time
from graphsag.domain.models import Observation
from graphsag.engine.registry import ProviderRegistry, RegistryError
from graphsag.security.crypto import Ed25519Verifier, SignatureError
from graphsag.security.replay import ReplayStore

@dataclass
class EvidenceResult:
    valid:list[Observation]; rejected:list[tuple[Observation,str]]

class EvidenceValidator:
    def __init__(self, registry:ProviderRegistry, verifier:Ed25519Verifier|None=None, replay_store:ReplayStore|None=None, clock=time.time):
        self.registry=registry; self.verifier=verifier; self.replay_store=replay_store; self.clock=clock
    def validate(self, request, observations):
        valid=[]; rejected=[]; seen=set(); now=self.clock()
        for o in observations:
            try:
                if o.request_id!=request.request_id: raise RegistryError('REQUEST_MISMATCH')
                if o.generation!=request.generation: raise RegistryError('GENERATION_MISMATCH')
                if o.principal_id!=request.principal_id: raise RegistryError('PRINCIPAL_MISMATCH')
                self.registry.validate(o)
                if o.policy_version is not None and o.policy_version != self.registry.policy_version: raise RegistryError('POLICY_VERSION_MISMATCH')
                digest=o.digest()
                if o.evidence_hash and o.evidence_hash!=digest: raise RegistryError('EVIDENCE_INTEGRITY_FAILURE')
                if digest in seen: raise RegistryError('DUPLICATE_EVIDENCE')
                if o.expires_at is not None and now>o.expires_at: raise RegistryError('EVIDENCE_EXPIRED')
                if o.issued_at>now+30: raise RegistryError('EVIDENCE_FROM_FUTURE')
                if self.verifier:
                    if not (o.signature and o.signing_key_id): raise SignatureError('SIGNATURE_REQUIRED')
                    self.verifier.verify(o.signing_key_id, digest.encode(), o.signature)
                if self.replay_store and o.nonce:
                    exp=o.expires_at or now+300
                    if not self.replay_store.reserve(o.nonce,exp): raise RegistryError('REPLAY_DETECTED')
                seen.add(digest); valid.append(o)
            except (RegistryError, SignatureError) as e: rejected.append((o,str(e)))
        return EvidenceResult(valid,rejected)
