# G3 / 1.0 Production Engineering Implementation

## Implemented in 1.0.0
- version-bound Provider Registry with monotonic semantic versions
- evidence request/generation/principal/provider/registry/policy binding
- duplicate, expiry, future-skew and integrity rejection
- optional Ed25519 evidence provenance verification
- replay protection (memory + SQLite)
- required/optional provider semantics
- fail-closed required-provider handling
- durable SQLite audit reference implementation
- high-risk audit pre-commit
- hash-chained audit verification
- decision expiry and execution revalidation
- capability-bound execution authorization
- DeepSeek V4 adapter boundary
- provenance graph reconstruction
- constitution-constrained adaptive governance
- workload-identity integration seam
- telemetry integration seam
- deterministic unit/security regression tests

## Deployment-specific controls
- OIDC/mTLS/workload identity implementation
- KMS/HSM key custody and rotation
- HA database/storage topology and backup
- network policy and service-to-service authorization
- signed image/SBOM/attestation enforcement
- external OpenTelemetry collector/exporter
- independent security review and penetration testing

These are explicit deployment gates, not hidden assumptions.
