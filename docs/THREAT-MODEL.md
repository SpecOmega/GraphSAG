# GraphSAG Threat Model

## Assets
- Authorization decisions and their evidence.
- Principal/workload identity.
- Provider registry and policy versions.
- Audit history.
- Signing keys and capability secrets.
- Execution resources and action bindings.

## Trust boundaries
1. Agent/request boundary.
2. Provider boundary.
3. LLM boundary.
4. Decision kernel boundary.
5. Execution boundary.
6. Audit/storage boundary.
7. Control/deployment boundary.

## Primary threats and controls
| Threat | Kernel control |
|---|---|
| Forged evidence | Ed25519 verification seam |
| Replay | nonce replay store + expiry |
| Stale evidence | request/generation/registry/policy binding |
| Required-provider outage | fail-closed |
| Evidence corruption | canonical digest |
| Audit failure on high risk | pre-execution audit commit |
| TOCTOU between decision/execution | expiry + registry/generation + capability binding |
| Dynamic-policy escalation | constitution-constrained governance |
| LLM prompt injection / hallucination | LLM cannot authorize directly |
| Audit tampering | hash-chain verification |

## Residual risks
Key custody, workload identity implementation, network compromise, host compromise, malicious providers, database availability, and deployment configuration remain environment-specific risks. The reference kernel deliberately exposes seams instead of pretending to solve these at package level.
