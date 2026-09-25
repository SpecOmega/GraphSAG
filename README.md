# GraphSAG

[简体中文文档](README.zh-CN.md)

Graph-based Security Assurance and Governance for autonomous-agent systems.

Current version: **1.0.0**.

GraphSAG treats security as a contract over evidence, provenance, policy, decision, audit and enforcement rather than as a single prompt filter.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
pytest -q
```

The project intentionally keeps the LLM provider behind an adapter. A DeepSeek V4-compatible integration must not bypass the deterministic security kernel.

## Status

GraphSAG 1.0.0 is a reference security-governance kernel. It is not universal certification, a zero-vulnerability claim, or a substitute for deployment-specific security review.
