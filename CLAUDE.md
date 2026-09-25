# GraphSAG Constitution

## Non-negotiable invariants
1. LLMs are advisory evidence producers, never authorization authorities.
2. Required-provider failure is fail-closed.
3. Rejected evidence may be filtered and partial derived results may return only when the remaining contract permits it.
4. High/Critical actions require durable audit commit before execution; audit failure is fail-closed.
5. Evidence is bound to request_id, generation, principal_id, provider/version, registry_version and policy_version.
6. Enforcement revalidates decision expiry, generation, registry version, principal and action/resource identity; capability binding is available for execution-grade authorization.
7. Duplicate, stale, replayed or integrity-invalid evidence cannot increase authority.
8. Dynamic governance may choose among pre-authorized response modes; it cannot rewrite the constitution, trust root, or authorization semantics.
9. Provider Option B: required providers enforce security-critical checks; optional providers provide analysis and cannot independently authorize execution.
10. Multi-tenancy is not mandatory for the initial service but must be designed as an explicit boundary before enablement.

## Development rule
Do not claim production certification merely because tests pass. Security claims require threat model, independent review, operational evidence and deployment-specific validation.

## DeepSeek V4
Use the adapter boundary in `src/graphsag/adapters/llm.py`. Credentials and endpoints are configuration/secrets, never source code.
