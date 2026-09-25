# Security boundaries

1. **Provider boundary:** untrusted provider output enters only through Observation validation.
2. **Decision boundary:** only the deterministic DecisionEngine creates authorization decisions.
3. **Audit boundary:** high-risk decisions require successful audit commit before execution.
4. **Enforcement boundary:** execution rechecks expiry, generation, registry version, identity and action.
5. **LLM boundary:** LLM output is advisory evidence; it cannot bypass the decision engine.
6. **Dynamic governance boundary:** adaptive response selects among pre-authorized modes and cannot mutate constitutional trust rules.
7. **Deployment boundary:** API authentication and workload identity must be supplied by the deployment; the reference static verifier is not a production identity provider.
