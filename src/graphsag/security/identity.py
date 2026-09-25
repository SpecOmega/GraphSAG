from __future__ import annotations
from dataclasses import dataclass

class IdentityError(PermissionError): pass
@dataclass(frozen=True)
class Principal:
    principal_id:str; issuer:str; subject:str; claims:dict

class WorkloadIdentityVerifier:
    """Reference seam for OIDC/mTLS/workload identity. Never treat an unverified header as identity."""
    def verify(self, credential: str) -> Principal: raise NotImplementedError
