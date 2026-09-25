from __future__ import annotations
from dataclasses import dataclass
from graphsag.domain.models import ProviderSpec
from graphsag.engine.versioning import require_monotonic

class RegistryError(Exception): pass

@dataclass(frozen=True)
class ProviderRegistry:
    version:str; policy_version:str; providers:dict[str,ProviderSpec]
    def validate(self, obs):
        spec=self.providers.get(obs.provider_id)
        if not spec: raise RegistryError('UNKNOWN_PROVIDER')
        if spec.version != obs.provider_version: raise RegistryError('PROVIDER_VERSION_MISMATCH')
        if obs.registry_version != self.version: raise RegistryError('REGISTRY_VERSION_MISMATCH')
        if spec.requirement != obs.requirement: raise RegistryError('REQUIREMENT_MISMATCH')
        return spec
    def evolve(self, version:str, policy_version:str, providers:dict[str,ProviderSpec]):
        try: require_monotonic(self.version,version); require_monotonic(self.policy_version,policy_version)
        except ValueError as exc: raise RegistryError(str(exc)) from exc
        return ProviderRegistry(version,policy_version,dict(providers))
