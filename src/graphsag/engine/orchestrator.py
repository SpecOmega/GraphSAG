from __future__ import annotations
import asyncio
from graphsag.domain.models import Observation,ProviderStatus
class Orchestrator:
    def __init__(self,providers): self.providers=providers
    async def collect(self,request):
        async def one(p):
            try:
                o=await asyncio.wait_for(p.observe(request),timeout=p.timeout_ms/1000)
                return o
            except asyncio.TimeoutError:
                return Observation(p.provider_id,p.version,p.registry_version,request.request_id,request.generation,request.principal_id,p.purpose,p.requirement,ProviderStatus.TIMEOUT)
            except Exception:
                return Observation(p.provider_id,p.version,p.registry_version,request.request_id,request.generation,request.principal_id,p.purpose,p.requirement,ProviderStatus.ERROR)
        return await asyncio.gather(*(one(p) for p in self.providers))
