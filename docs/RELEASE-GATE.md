# Release Gate

## GraphSAG 1.0.0 kernel gate

The repository must pass:

- `python -m compileall -q src`
- complete pytest suite
- security regression corpus
- package build/import smoke test
- CI execution on supported Python version

## Deployment gate

A deployment may call itself production only after validating its identity provider, key custody, storage durability, network controls, image/SBOM provenance, observability, backup/recovery, capacity limits, fault injection, and independent security review.

Passing repository tests alone is not sufficient evidence for those deployment claims.
