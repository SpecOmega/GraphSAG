from __future__ import annotations
from contextlib import contextmanager
import time

class Telemetry:
    def __init__(self): self.events=[]
    @contextmanager
    def span(self,name,**attrs):
        start=time.time(); item={'name':name,'attributes':attrs}
        try: yield item
        except Exception as exc:
            item['error']=type(exc).__name__; raise
        finally:
            item['duration_ms']=(time.time()-start)*1000; self.events.append(item)
