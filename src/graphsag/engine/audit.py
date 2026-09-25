from __future__ import annotations
from graphsag.domain.models import AuditEvent
class AuditSink:
    def commit(self,event:AuditEvent)->bool: raise NotImplementedError
class MemoryAuditSink(AuditSink):
    def __init__(self): self.events={}
    def commit(self,event): self.events[event.event_id]=event; return True
