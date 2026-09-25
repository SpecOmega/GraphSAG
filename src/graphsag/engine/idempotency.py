from __future__ import annotations
from threading import RLock
class IdempotencyStore:
    def __init__(self): self._seen={}; self._lock=RLock()
    def reserve(self,key:str)->bool:
        with self._lock:
            if key in self._seen: return False
            self._seen[key]=True; return True
    def contains(self,key): return key in self._seen
