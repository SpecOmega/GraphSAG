from __future__ import annotations
from dataclasses import dataclass
class AuthenticationError(Exception): pass
@dataclass(frozen=True)
class Principal:
    principal_id:str; scopes:frozenset[str]
class StaticPrincipalVerifier:
    """Reference seam only; production deployments should replace with OIDC/mTLS/workload identity."""
    def __init__(self,principals): self.principals=principals
    def verify(self,principal_id,scope):
        p=self.principals.get(principal_id)
        if not p or scope not in p.scopes: raise AuthenticationError('UNAUTHORIZED')
        return p
