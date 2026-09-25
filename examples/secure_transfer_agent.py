"""End-to-end GraphSAG example for a high-risk money transfer agent.

This example keeps the model and external providers untrusted. The only
authorization decision is created by ``DecisionEngine`` and execution is
revalidated by ``EnforcementGuard``.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import asdict

from graphsag.adapters.llm import DeepSeekV4Adapter
from graphsag.domain.models import (
    Observation,
    ProviderSpec,
    ProviderStatus,
    Request,
    Requirement,
    RiskLevel,
    SecurityProfile,
)
from graphsag.engine.decision import DecisionEngine
from graphsag.engine.evidence import EvidenceValidator
from graphsag.engine.orchestrator import Orchestrator
from graphsag.engine.registry import ProviderRegistry
from graphsag.graph.builder import build_decision_graph
from graphsag.governance.adaptive import AdaptiveGovernance
from graphsag.observability.telemetry import Telemetry
from graphsag.security.capability import CapabilityAuthority
from graphsag.security.crypto import Ed25519Signer, Ed25519Verifier
from graphsag.security.identity import Principal, WorkloadIdentityVerifier
from graphsag.security.replay import MemoryReplayStore
from graphsag.storage.audit_chain import ChainAuditSink


class DemoIdentityVerifier(WorkloadIdentityVerifier):
    """Deterministic stand-in for an OIDC or mTLS workload verifier."""

    def verify(self, credential: str) -> Principal:
        if credential != "demo-agent-credential":
            raise ValueError("INVALID_WORKLOAD_CREDENTIAL")
        return Principal(
            principal_id="agent:payments",
            issuer="demo-issuer",
            subject="payments-agent",
            claims={"scope": "transfer:execute"},
        )


class Provider:
    def __init__(
        self,
        provider_id: str,
        version: str,
        registry_version: str,
        purpose: str,
        requirement: Requirement,
        status: ProviderStatus = ProviderStatus.ALLOW,
    ) -> None:
        self.provider_id = provider_id
        self.version = version
        self.registry_version = registry_version
        self.purpose = purpose
        self.requirement = requirement
        self.timeout_ms = 500
        self.status = status

    async def observe(self, request: Request) -> Observation:
        return Observation(
            provider_id=self.provider_id,
            provider_version=self.version,
            registry_version=self.registry_version,
            request_id=request.request_id,
            generation=request.generation,
            principal_id=request.principal_id,
            claim=self.purpose,
            requirement=self.requirement,
            status=self.status,
            payload={"source": self.provider_id, "action": request.action},
            expires_at=time.time() + 60,
            nonce=f"{request.request_id}:{self.provider_id}",
            policy_version="policy-1.0.0",
        )


def sign_observation(observation: Observation, signer: Ed25519Signer) -> Observation:
    """Bind a provider observation to its digest without signing mutable fields."""

    return Observation(
        **{
            **asdict(observation),
            "signing_key_id": signer.key_id,
            "signature": signer.sign(observation.digest().encode()),
        }
    )


async def collect_signed_evidence(
    request: Request,
    providers: list[Provider],
    signer: Ed25519Signer,
) -> list[Observation]:
    observations = await Orchestrator(providers).collect(request)
    return [sign_observation(observation, signer) for observation in observations]


def build_registry() -> ProviderRegistry:
    return ProviderRegistry(
        version="registry-1.0.0",
        policy_version="policy-1.0.0",
        providers={
            "account-status": ProviderSpec(
                "account-status",
                "1.0.0",
                "account is eligible for transfer",
                Requirement.REQUIRED,
            ),
            "fraud-risk": ProviderSpec(
                "fraud-risk",
                "1.0.0",
                "fraud risk is within policy",
                Requirement.OPTIONAL,
            ),
        },
    )


async def authorize_transfer(
    request: Request,
    providers: list[Provider],
    registry: ProviderRegistry,
    signer: Ed25519Signer,
    audit: ChainAuditSink,
    telemetry: Telemetry,
):
    replay = MemoryReplayStore()
    validator = EvidenceValidator(
        registry,
        verifier=Ed25519Verifier({"provider-demo": signer.public_key_bytes()}),
        replay_store=replay,
    )
    engine = DecisionEngine(
        registry,
        audit,
        validator=validator,
        governance=AdaptiveGovernance("constitution-1.0"),
    )
    with telemetry.span("graphsag.decision", request_id=request.request_id):
        observations = await collect_signed_evidence(request, providers, signer)
        decision = engine.decide(request, observations)
    graph = build_decision_graph(request, observations, decision)
    return decision, observations, graph


async def run_demo() -> dict[str, object]:
    identity = DemoIdentityVerifier().verify("demo-agent-credential")
    registry = build_registry()
    signer = Ed25519Signer.generate("provider-demo")
    audit = ChainAuditSink()
    telemetry = Telemetry()
    capability_authority = CapabilityAuthority(b"demo-only-secret-not-for-production")
    request = Request(
        request_id="transfer-2026-0001",
        generation=7,
        principal_id=identity.principal_id,
        profile=SecurityProfile(
            name="payment-transfer",
            risk=RiskLevel.HIGH,
            audit_required=True,
            high_risk_actions=("transfer",),
            dynamic_governance=True,
        ),
        action="transfer",
        tenant_id="tenant-demo",
        resource_id="account-123",
        expires_at=time.time() + 60,
    )
    providers = [
        Provider(
            "account-status",
            "1.0.0",
            "registry-1.0.0",
            "account is eligible for transfer",
            Requirement.REQUIRED,
        ),
        Provider(
            "fraud-risk",
            "1.0.0",
            "registry-1.0.0",
            "fraud risk is within policy",
            Requirement.OPTIONAL,
        ),
    ]
    decision, observations, graph = await authorize_transfer(
        request, providers, registry, signer, audit, telemetry
    )
    capability = capability_authority.issue(
        "cap-transfer-0001",
        identity.principal_id,
        request.action,
        request.resource_id,
        request.generation,
        time.time() + 30,
    )

    # The adapter is intentionally instantiated but never treated as an
    # authorization source. A real deployment supplies its endpoint and secret.
    _llm = DeepSeekV4Adapter("https://approved.example.invalid", api_key=None)

    from graphsag.engine.enforcement import EnforcementGuard

    EnforcementGuard(registry, capability_authority).authorize(
        decision, request, capability
    )
    assert audit.verify()
    return {
        "principal_id": identity.principal_id,
        "decision": decision.outcome.value,
        "reasons": decision.reason_codes,
        "evidence_count": len(observations),
        "provenance_nodes": len(graph.nodes),
        "audit_chain_valid": audit.verify(),
        "telemetry_spans": len(telemetry.events),
        "execution": "authorized",
    }


def main() -> None:
    print(asyncio.run(run_demo()))


if __name__ == "__main__":
    main()
