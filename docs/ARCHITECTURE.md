# GraphSAG architecture

GraphSAG is a security kernel around a graph/evidence-aware agent runtime. Evidence is treated as typed, version-bound, provenance-bearing input. The kernel validates evidence, aggregates required/optional provider results, creates an expiring Decision, commits durable audit for high-risk actions, and exposes a separate Enforcement boundary.

The design deliberately separates:

- **control plane:** registry, policy and trust configuration;
- **evidence plane:** provider observations and provenance;
- **decision plane:** deterministic contract evaluation;
- **execution plane:** identity/resource revalidation and side effects;
- **observability plane:** audit and telemetry.

A future adaptive governance layer may change response mode based on runtime risk, but only inside a pre-authorized policy envelope.
