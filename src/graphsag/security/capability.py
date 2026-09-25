from __future__ import annotations
from dataclasses import dataclass
import hashlib,hmac,json,time

@dataclass(frozen=True)
class Capability:
    capability_id: str; principal_id: str; action: str; resource_id: str|None; generation: int; expires_at: float; mac: str

class CapabilityAuthority:
    def __init__(self, secret: bytes): self.secret=secret
    def issue(self, capability_id, principal_id, action, resource_id, generation, expires_at):
        body={'capability_id':capability_id,'principal_id':principal_id,'action':action,'resource_id':resource_id,'generation':generation,'expires_at':expires_at}
        mac=hmac.new(self.secret,json.dumps(body,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
        return Capability(**body,mac=mac)
    def verify(self, cap, principal_id, action, resource_id, generation, now=None):
        now=now or time.time()
        body={'capability_id':cap.capability_id,'principal_id':cap.principal_id,'action':cap.action,'resource_id':cap.resource_id,'generation':cap.generation,'expires_at':cap.expires_at}
        expected=hmac.new(self.secret,json.dumps(body,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected,cap.mac): raise PermissionError('CAPABILITY_INTEGRITY_FAILURE')
        if (cap.principal_id,cap.action,cap.resource_id,cap.generation)!=(principal_id,action,resource_id,generation): raise PermissionError('CAPABILITY_BINDING_MISMATCH')
        if now>cap.expires_at: raise PermissionError('CAPABILITY_EXPIRED')
        return True
