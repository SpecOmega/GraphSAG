# GraphSAG 端到端示例：安全支付 Agent

本示例展示一个具有高风险转账能力的 Agent 如何通过 GraphSAG 内核完成一次受约束的执行。它不是把 LLM 输出当作授权结果，而是把模型和 Provider 都视为不可信的证据来源。

## 覆盖的架构能力

示例 [`secure_transfer_agent.py`](secure_transfer_agent.py) 覆盖：

1. **工作负载身份**：使用 `WorkloadIdentityVerifier` 的演示实现验证 Agent 凭据。
2. **控制平面**：`ProviderRegistry` 固定 Provider、Provider 版本、注册表版本和策略版本。
3. **证据平面**：两个 Provider 分别提供必需的账户状态证据和可选的欺诈风险证据。
4. **证据完整性**：使用 Ed25519 签名、摘要、过期时间和 nonce。
5. **决策平面**：`DecisionEngine` 聚合证据，并对必需 Provider 失败执行 fail-closed。
6. **动态治理**：使用 `AdaptiveGovernance`，其状态不能改变宪法或授权语义。
7. **审计边界**：High 风险决策先提交 `ChainAuditSink`，审计失败不能继续执行。
8. **执行边界**：`CapabilityAuthority` 将主体、动作、资源、代次和过期时间绑定到能力。
9. **溯源图**：`build_decision_graph` 关联 Request、Evidence 和 Decision。
10. **可观测性**：`Telemetry` 记录决策 span。
11. **LLM 边界**：实例化 DeepSeek V4 adapter 仅代表集成边界；LLM 不参与授权。

## 运行

从仓库根目录执行：

```bash
python examples/secure_transfer_agent.py
```

预期输出类似：

```text
{
  'principal_id': 'agent:payments',
  'decision': 'ALLOW',
  'reasons': (),
  'evidence_count': 2,
  'provenance_nodes': 4,
  'audit_chain_valid': True,
  'telemetry_spans': 1,
  'execution': 'authorized'
}
```

输出中的 UUID、时间戳和摘要可能不同。示例使用内存/临时审计存储和演示密钥，不能直接用于生产。

## 失败关闭演练

可以在交互式 Python 会话中复用示例构造器验证必需 Provider 的失败关闭语义：

```python
import asyncio
from examples.secure_transfer_agent import (
    DemoIdentityVerifier,
    Provider,
    build_registry,
)
from graphsag.domain.models import ProviderStatus, Requirement

identity = DemoIdentityVerifier().verify("demo-agent-credential")
registry = build_registry()
provider = Provider(
    "account-status",
    "1.0.0",
    "registry-1.0.0",
    "account is eligible for transfer",
    Requirement.REQUIRED,
    status=ProviderStatus.DENY,
)
```

实际应用中应让该 Provider 参与同一决策流程；当必需 Provider 返回 `DENY`、`ERROR`、`TIMEOUT`，或者证据缺失/无效时，决策不能产生可执行的 `ALLOW`。

## 安全流程

```text
credential
  -> workload identity
  -> Request
  -> ProviderRegistry
  -> signed Observation
  -> EvidenceValidator
  -> DecisionEngine
  -> durable audit commit
  -> capability-bound EnforcementGuard
  -> tool execution
```

生产接入时应替换：

- `DemoIdentityVerifier`：使用 OIDC、mTLS 或平台工作负载身份；
- `Ed25519Signer`：使用 KMS/HSM 管理的 Provider 密钥；
- `ChainAuditSink`：使用高可用、备份和访问控制的持久化存储；
- `Provider`：通过受保护网络调用真实 Provider；
- `DeepSeekV4Adapter`：使用配置/密钥管理系统提供 endpoint 和 credential；
- 示例中的转账函数：在 `authorize` 成功后再调用真实支付工具，并在工具层再次执行资源校验。

## 故障演练

将可选 `fraud-risk` Provider 的 `status` 改为 `ProviderStatus.TIMEOUT`，观察决策退化为允许部分结果或进入更严格治理；将必需 `account-status` Provider 改为 `DENY`、`ERROR` 或 `TIMEOUT`，决策必须为 `FAIL_CLOSED`，且不能执行。

不要通过删除签名、关闭验证器、复用 nonce、跳过审计或直接调用工具来“修复”失败。这些失败正是安全边界的一部分。
