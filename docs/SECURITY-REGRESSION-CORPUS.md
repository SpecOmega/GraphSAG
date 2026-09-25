# Security Regression Corpus

Every release must preserve these invariants:

- unknown provider is rejected;
- provider version mismatch is rejected;
- registry version mismatch is rejected;
- policy version mismatch is rejected;
- request/principal/generation mismatch is rejected;
- expired evidence is rejected;
- future-dated evidence beyond clock skew is rejected;
- invalid signatures are rejected when verification is enabled;
- duplicate nonce is rejected when replay protection is enabled;
- required provider DENY/ERROR/TIMEOUT cannot produce ALLOW;
- high/critical audit commit failure cannot produce ALLOW;
- stale registry cannot execute a decision;
- stale/expired capability cannot execute an action;
- capability principal/action/resource/generation mismatch is rejected;
- provenance graph cannot contain dangling edges;
- audit-chain tampering is detected;
- adaptive governance cannot change constitutional version or trust semantics.
