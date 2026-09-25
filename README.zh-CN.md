# GraphSAG

[English documentation](README.md)

### Graph-based Security, Assurance & Governance for Autonomous AI Agents
**GraphSAG 是一个面向自主 AI Agent 的图结构安全保障与运行时治理框架。**

它关注的不是单独判断一条 Prompt 或一段模型输出是否安全，而是把 Agent 从**获取信息、形成证据、推理、决策、授权到执行**的完整过程连接起来，对其中的来源、关系、状态和权限进行验证、追踪和控制。

简单来说，GraphSAG 希望解决的是：

> **当一个 AI Agent 要采取行动时，我们能否知道它为什么这么做、依据了什么、这些依据来自哪里、谁允许它这么做，以及这个决定是否仍然有效？**
GraphSAG 将这些信息组织成可验证的关系结构，并在运行过程中根据风险和系统状态调整治理策略。

---

## 为什么需要 GraphSAG
传统 AI 应用的安全控制通常围绕几个边界展开：

```
Input
  ↓
Model
  ↓
Output
  ↓
Tool
```
因此常见的安全措施包括：

- Prompt / Input Filtering
- Output Filtering
- Content Moderation
- Tool Permission
- Identity / Access Control
但自主 Agent 的实际运行链路正在变得更复杂：

```
                 ┌──────────────┐
                 │ Environment  │
                 └──────┬───────┘
                        ↓
                  Perception
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
     Memory           RAG          External Data
        └───────────────┼───────────────┘
                        ↓
                    Reasoning
                        ↓
                     Decision
                        ↓
                  Tool / Action
                        ↓
                    Execution
                        ↓
                    Feedback
                        └───────→ next cycle
```
这时，一个安全问题可能并不是“模型输出了恶意内容”。

例如：

- 一个来源不可靠的信息进入 Agent；
- 信息被写入共享记忆；
- 后续检索再次得到这条信息；
- Agent 将其当成事实参与推理；
- 推理结果生成一个行动建议；
- 行动建议获得工具权限；
- 最终产生现实世界的操作。
如果只检查最终输出，很难回答：

> **问题究竟从哪里开始？**
GraphSAG 的设计重点，就是把这条链路显式化。

---

# GraphSAG 做什么
GraphSAG 围绕六个核心环节工作：

```
Evidence
   ↓
Validation
   ↓
Relation / Provenance
   ↓
Decision
   ↓
Authorization
   ↓
Execution
   ↓
Audit / Feedback
```
对应到系统中：

能力作用Evidence Contract规范 Agent 使用的证据Provider Registry管理证据和安全信息的提供方Security Profile根据场景确定安全要求Decision将证据、策略和风险转化为明确决策Provenance记录决策与证据之间的关系Authorization将决策与实际执行权限绑定Audit对重要决策和执行进行持久化记录Adaptive Governance根据运行状态动态调整治理级别
---

# 核心特点

## 1. 从“输出安全”转向“决策链安全”
GraphSAG 不只关心：

```
Model Output
```
而是关注：

```
Evidence
   ↓
Reasoning Context
   ↓
Decision
   ↓
Authorization
   ↓
Execution
```
因此可以追踪：

- 为什么产生这个 Decision？
- 使用了哪些证据？
- 证据来自哪个 Provider？
- 使用了哪个 Policy？
- 哪个主体发起了请求？
- Decision 属于哪一次运行？
- 最终执行的 Action 是否仍然属于原授权范围？

---

## 2. 用关系图记录“为什么”
GraphSAG 将重要对象之间的关系显式化。

一个典型的决策关系可以表示为：

```
Principal
    │
    ▼
 Request
    │
    ├───────────────┐
    ▼               ▼
Evidence A       Evidence B
    │               │
    └───────┬───────┘
            ▼
         Decision
            │
            ▼
       Authorization
            │
            ▼
         Execution
```
因此安全审计不再只是：

```
"action=transfer"
```
而可以进一步追踪：

```
谁发起？
↓
使用了什么证据？
↓
证据由谁提供？
↓
经过什么策略？
↓
为什么允许？
↓
获得什么权限？
↓
执行了什么？
```
这也是 GraphSAG 中 **Graph** 的核心作用。

---

# 3. Evidence Contract
GraphSAG 不把任意一段文本、JSON 或 LLM 输出直接当作可信事实。

Evidence 会绑定请求上下文和生命周期信息，例如：

```
request_id
principal_id
generation
provider_id
provider_version
registry_version
policy_version
issued_at
expires_at
nonce
digest
signature
```
由此可以检查：

- 来源是否匹配；
- 请求是否匹配；
- Agent generation 是否匹配；
- Provider 是否在 Registry 中；
- Registry / Policy 是否发生变化；
- Evidence 是否过期；
- Evidence 是否被重复使用；
- Evidence 是否被修改。

### 一个重要边界
GraphSAG 不把：

```
Signed Evidence
```
等同于：

```
Real-world Truth
```
密码学机制能够帮助验证来源和完整性，但不能证明现实世界中的事实一定正确。

因此 GraphSAG 将：

**来源可信**

和

**事实真实**

明确分开。

---

# 4. Provider Registry
自主 Agent 往往同时依赖多个信息和安全 Provider：

```
Identity Provider
Risk Provider
Policy Provider
Knowledge Provider
Memory Provider
Reputation Provider
Threat Intelligence Provider
Environment Provider
```
GraphSAG 使用 Provider Registry 统一描述这些 Provider。

每个 Provider 可以具有：

```
Provider ID
Version
Capability
Security Profile
Trust / Requirement Level
Status
```
其中一个重要区分是：

```
REQUIRED
OPTIONAL
```

### REQUIRED
关键 Provider 发生：

```
timeout
error
missing
invalid
deny
```
时，系统按照安全策略进入失败关闭路径，而不是继续假设它正常工作。

### OPTIONAL
可选 Provider 出现异常时，可以根据策略：

```
记录异常
↓
降低证据完整度
↓
继续处理
```
或者进入更严格的治理状态。

这种设计避免了两种极端：

```
任何 Provider 出错 → 整个 Agent 停止
```
以及：

```
关键安全 Provider 出错 → 系统假装没发生
```

---

# 5. Decision
GraphSAG 不让模型输出直接成为执行许可。

模型可以提出：

```
Suggested Action
```
但最终 Decision 需要综合：

```
Request
+
Evidence
+
Provider Status
+
Security Profile
+
Policy
+
Risk
+
Governance State
```
然后形成明确的决策结果。

典型结果包括：

```
ALLOW
ALLOW_PARTIAL
DENY
FAIL_CLOSED
```

---

## ALLOW_PARTIAL
GraphSAG 并不把所有异常都简单处理成：

```
ALLOW / DENY
```
例如：

```
Provider A   → valid
Provider B   → valid
Provider C   → timeout
```
如果 C 属于 OPTIONAL Provider，则系统可以根据策略形成：

```
ALLOW_PARTIAL
```
并明确记录缺失的信息。

这样可以在安全性与系统可用性之间建立更加细粒度的控制。

---

# 6. Decision 与 Execution 分离
GraphSAG 不认为：

```
Decision = ALLOW
```
就意味着：

```
任何地方
任何时间
任何方式
都可以执行
```
执行权限需要进一步绑定：

```
Principal
Action
Resource
Generation
Expiration
```
形成受约束的 Capability。

例如：

```
principal = agent-001
action    = transfer
resource  = account-123
generation = 42
expires   = 10:31:00
```
这样可以限制：

- Decision 重放；
- 跨 Agent 使用；
- 跨 Generation 使用；
- 超范围执行；
- 过期执行。

---

# 7. Audit-before-Execution
对于高风险操作，GraphSAG 支持：

```
Decision
   ↓
Audit Commit
   ↓
Execution
```
如果必须审计的记录无法可靠写入：

```
Audit Commit Failed
        ↓
Fail Closed
        ↓
High-risk Action 不执行
```
这意味着：

> **对于高风险操作，“无法留下可靠审计记录”本身就是一个安全条件。**
同时支持审计记录完整性检查和关联验证。

---

# 8. Provenance
GraphSAG 将：

```
Request
Evidence
Provider
Policy
Decision
Authorization
Execution
```
之间的关系保存下来。

因此一次行动可以形成完整的 Provenance Chain：

```
Request
   │
   ├── Evidence A
   │      └── Provider A
   │
   ├── Evidence B
   │      └── Provider B
   │
   └── Policy
          │
          ▼
       Decision
          │
          ▼
    Authorization
          │
          ▼
       Execution
```
这为：

- 安全审计
- 故障定位
- Incident Investigation
- 决策复盘
- Agent 行为分析
- 安全研究
提供统一的数据基础。

---

# 9. 动态治理
Agent 是持续运行的系统，而不是一次性请求。

GraphSAG 因此预留动态治理状态：

```
NORMAL
   ↓
RESTRICTED
   ↓
ISOLATED
   ↓
EMERGENCY_STOP
```
状态变化可以由多个信号共同触发，例如：

- Evidence 异常；
- Provider 故障；
- 身份异常；
- Replay；
- 风险等级变化；
- 交互异常；
- 环境变化；
- 安全检测结果。
动态治理可以：

- 降低权限；
- 增加验证；
- 限制 Provider；
- 隔离 Agent；
- 暂停高风险动作；
- 停止执行。
但运行时状态不能任意修改系统最基本的信任和授权规则。

---

# 10. GraphSAG 与 LLM 的关系
GraphSAG 不依赖某一个特定模型。

LLM 可以用于：

- 推理；
- 分类；
- 信息抽取；
- 风险分析；
- 生成候选 Decision；
- 生成结构化 Evidence；
- Agent Planning。
但：

```
LLM
≠
Authorization Authority
```
最终的安全决策仍然需要经过 GraphSAG 定义的证据、策略、权限和治理流程。

---

# DeepSeek V4
GraphSAG 预留了 LLM Adapter 接口。

当前工程设计可以接入：

```
DeepSeek V4
```
但模型适配层与安全治理层保持分离。

因此未来可以接入其他模型，而无需重新设计：

```
Evidence
Provider
Decision
Audit
Authorization
Provenance
Governance
```

---

# GraphSAG 与 RAG / GraphRAG
GraphSAG 不试图替代：

- RAG
- GraphRAG
- Knowledge Graph
- Agent Framework
- IAM
- Policy Engine
- Observability Platform
它们可以组合使用。

典型结构：

```
                    LLM
                     │
          ┌──────────┴──────────┐
          │                     │
         RAG                 GraphRAG
          │                     │
          └──────────┬──────────┘
                     ↓
                  Evidence
                     ↓
                 GraphSAG
                     ↓
                  Decision
                     ↓
                Authorization
                     ↓
                  Tool/API
```
GraphSAG 关注的是：

> **这些信息如何进入 Agent 的决策，以及决策如何获得现实世界的执行能力。**

---

# GraphSAG 适用场景

## Autonomous Agents
用于具有自主规划和工具调用能力的 Agent。

重点关注：

- 工具调用；
- 决策授权；
- 行为审计；
- 证据追踪；
- 动态风险控制。

## Agentic RAG
用于需要根据检索结果采取行动的 RAG Agent。

重点关注：

- 检索来源；
- Evidence 生命周期；
- 来源关联；
- Decision Provenance；
- 风险控制。

## Multi-Agent Systems
用于多个 Agent 之间存在通信、协作和共享状态的系统。

例如：

```
Agent A
   ↓
Agent B
   ↓
Agent C
   ↓
Tool
```
GraphSAG 可以记录：

```
Agent Identity
Message / Evidence
Decision
Authorization
Execution
```
从而建立 Agent 之间的安全关系。

## Tool Calling
适合具有现实执行能力的工具：

- API
- Database
- File System
- Cloud Service
- DevOps System
- Enterprise System
- Automation Platform
尤其适合解决：

> **模型认为“应该调用工具”，并不意味着系统就应该允许调用工具。**

---

# 架构

```
┌──────────────────────────────────────────────┐
│              Autonomous Agent                │
│                                              │
│   LLM / Planner / Memory / RAG / Tools      │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│                  GraphSAG                    │
│                                              │
│  Identity ─────── Request ───── Security    │
│                                    Profile   │
│                       │                      │
│                       ▼                      │
│               Provider Registry              │
│                       │                      │
│                       ▼                      │
│                  Evidence                    │
│                       │                      │
│                       ▼                      │
│              Validation / Trust              │
│                       │                      │
│                       ▼                      │
│                   Decision                   │
│                    │    │                    │
│                    │    └── Provenance       │
│                    │                         │
│                    ├──── Audit               │
│                    │                         │
│                    ▼                         │
│              Authorization                   │
│                    │                         │
│                    ▼                         │
│                 Capability                   │
└────────────────────┬─────────────────────────┘
                     │
                     ▼
                Tool / Action
```

---

# 项目结构

```
GraphSAG/
├── src/
│   └── graphsag/
│       ├── adapters/
│       ├── api/
│       ├── domain/
│       ├── engine/
│       ├── governance/
│       ├── graph/
│       ├── observability/
│       ├── security/
│       └── storage/
│
├── tests/
│   ├── test_core.py
│   ├── test_hardening.py
│   ├── test_policy_auth.py
│   └── test_sqlite.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── G3-IMPLEMENTATION.md
│   ├── RELEASE-GATE.md
│   ├── SECURITY-BOUNDARIES.md
│   ├── SECURITY-REGRESSION-CORPUS.md
│   └── THREAT-MODEL.md
│
├── schemas/
├── deployment/
├── scripts/
├── pyproject.toml
├── Dockerfile
├── README.md
└── README.zh-CN.md
```

---

# 当前版本

## GraphSAG v1.0.0
当前的参考实现版本。

该版本提供安全治理内核和集成边界，不等同于所有部署环境的生产认证。

### 已具备

- Evidence Contract
- Evidence Validation
- Provider Registry
- REQUIRED / OPTIONAL Provider Governance
- Security Profile
- Decision Contract
- Decision Aggregation
- ALLOW / ALLOW_PARTIAL / DENY / FAIL_CLOSED
- Replay Protection
- Evidence Expiration
- Cryptographic Provenance
- Audit
- Audit Integrity Verification
- Decision-to-Execution Binding
- Capability-based Authorization
- Provenance Graph
- Adaptive Governance
- Workload Identity Integration Boundary
- Telemetry Boundary
- DeepSeek V4 Adapter Boundary
- Security Regression Tests
当前版本已经包含确定性单元测试、安全回归测试、源码编译检查和 SQLite 审计测试。

> v1.0.0 不代表 GraphSAG 已经完成所有生产环境适配、形式化验证或第三方安全认证。

---

# 安全边界
GraphSAG 可以帮助系统验证：

- 证据完整性；
- 请求绑定；
- 身份关联；
- Provider 状态；
- Policy / Registry 版本；
- Evidence 生命周期；
- Replay；
- Decision 合法性；
- Decision 与 Execution 的绑定；
- 高风险操作的审计要求；
- 动态治理状态。
但 GraphSAG 不声称能够保证：

- 现实世界事实绝对正确；
- LLM 永不产生错误；
- Provider 本身永远可信；
- 主机和操作系统不存在漏洞；
- 网络环境绝对安全；
- KMS / HSM 配置绝对正确；
- 部署环境没有错误配置；
- 不存在未知安全漏洞；
- 已完成第三方安全认证。
生产部署仍然需要结合具体环境完成：

- Workload Identity；
- OIDC / mTLS；
- KMS / HSM；
- 网络隔离；
- HA / Disaster Recovery；
- SBOM；
- 镜像签名与验证；
- Secret Management；
- OpenTelemetry；
- 压力测试；
- 故障注入；
- 渗透测试；
- 独立安全审计。

---

# 路线图
GraphSAG 的后续方向不是简单增加更多检测规则，而是逐步扩大可验证关系的范围。

```
v1.0
 │
 ├── Evidence
 ├── Decision
 ├── Provenance
 ├── Authorization
 ├── Audit
 └── Runtime Governance
        │
        ▼
后续版本
 │
 ├── RAG / GraphRAG Security
 ├── Memory Security
 ├── Knowledge Graph Integrity
 └── Multi-Agent Communication
        │
        ▼
后续版本
 │
 ├── Cross-Layer Graph
 ├── Runtime Risk Graph
 ├── Dynamic Risk Propagation
 └── Adaptive Governance
        │
        ▼
长期方向
 │
 ├── Policy Verification
 ├── Distributed Deployment
 ├── Security Evaluation
 └── Large-scale Agent Governance
```

---

# 一个更长远的方向
GraphSAG 当前首先解决的是：

> **如何让 Agent 的重要决策和执行过程可验证、可追踪、可约束。**
进一步发展之后，系统可以逐渐形成：

```
Environment
     ↓
Observation
     ↓
State
     ↓
Evidence
     ↓
Reasoning
     ↓
Decision
     ↓
Action
     ↓
Feedback
     ↺
```
也就是说，软件系统不再只是：

```
Input → Output
```
而逐渐具有：

```
感知
状态
记忆
判断
行动
反馈
适应
治理
```
GraphSAG 希望为这种持续运行、持续变化的自主系统提供一套可以落地的安全关系模型。

这是 GraphSAG 更长期的研究与工程方向。

---

# Design Principles
GraphSAG 遵循几个基本原则：

### Evidence over assertion
重要决策需要有可验证依据，而不是只依赖模型生成的结论。

### Authorization over intention
Agent 想做什么，不等于系统允许它做什么。

### Provenance over black-box result
不仅保存结果，也保存结果与依据之间的关系。

### Fail-closed for critical paths
关键安全条件无法满足时，高风险动作不应默认继续。

### Explicit trust boundaries
模型、Provider、Memory、RAG、Tool 和执行环境不应因为处于同一个 Agent 流程中就自动获得相同信任等级。

### Adaptive, but bounded
系统可以根据环境变化收紧控制，但动态机制不能随意改变最基本的信任和授权边界。

---

# 快速开始

```
git clone <YOUR_REPOSITORY_URL>
cd GraphSAG

python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -e ".[test]"

pytest -q
```
也可以运行仓库提供的验证脚本：

```bash
./scripts/verify.sh
```

---

# 开发说明
GraphSAG 的开发重点不是单纯增加功能，而是保证每一个新增能力都不会绕过：

```
Identity
Evidence
Policy
Decision
Authorization
Audit
Provenance
Governance
```
任何新的 Provider、Tool 或 Adapter，都应明确其：

- 输入；
- 输出；
- 信任级别；
- 生命周期；
- 错误处理；
- 安全影响；
- 审计要求；
- 与现有 Decision Contract 的关系。

---

# 贡献指南
欢迎以下方向的贡献：

- Agent Security
- Graph Security
- Provenance
- Agentic RAG
- Knowledge Graph
- Multi-Agent Security
- Runtime Governance
- Policy Engineering
- Identity / Authorization
- Security Testing
- Observability
- Performance Engineering
提交 Pull Request 时，请尽可能同时提供：

1. 设计说明；
2. 测试；
3. 安全影响分析；
4. 兼容性说明；
5. 必要的文档更新。
对于涉及 Authorization、Evidence、Decision、Audit 或 Governance 的修改，需要特别说明是否改变现有安全语义。

---

## 相关文档

- [端到端支付 Agent 示例](examples/README.md)
- [系统架构](docs/ARCHITECTURE.md)
- [安全边界](docs/SECURITY-BOUNDARIES.md)
- [威胁模型](docs/THREAT-MODEL.md)
- [1.0 发布定义](docs/1.0-RELEASE.md)
- [发布门禁](docs/RELEASE-GATE.md)
- [G3 工程实现](docs/G3-IMPLEMENTATION.md)
- [安全回归测试集](docs/SECURITY-REGRESSION-CORPUS.md)

## 实现映射

| 能力 | 当前实现 |
| --- | --- |
| 请求、证据、决策和审计事件模型 | [`src/graphsag/domain/models.py`](src/graphsag/domain/models.py) |
| Provider 注册表与版本单调性 | [`src/graphsag/engine/registry.py`](src/graphsag/engine/registry.py)、[`src/graphsag/engine/versioning.py`](src/graphsag/engine/versioning.py) |
| 证据绑定、完整性、过期和重放校验 | [`src/graphsag/engine/evidence.py`](src/graphsag/engine/evidence.py)、[`src/graphsag/security/replay.py`](src/graphsag/security/replay.py) |
| Ed25519 证据签名验证 | [`src/graphsag/security/crypto.py`](src/graphsag/security/crypto.py) |
| 确定性决策与必需 Provider 失败关闭 | [`src/graphsag/engine/decision.py`](src/graphsag/engine/decision.py) |
| 决策执行阶段重新校验 | [`src/graphsag/engine/enforcement.py`](src/graphsag/engine/enforcement.py) |
| 能力绑定 | [`src/graphsag/security/capability.py`](src/graphsag/security/capability.py) |
| 溯源图 | [`src/graphsag/graph/provenance.py`](src/graphsag/graph/provenance.py)、[`src/graphsag/graph/builder.py`](src/graphsag/graph/builder.py) |
| 审计持久化与哈希链 | [`src/graphsag/storage/sqlite_audit.py`](src/graphsag/storage/sqlite_audit.py)、[`src/graphsag/storage/audit_chain.py`](src/graphsag/storage/audit_chain.py) |
| 动态治理、身份和遥测集成边界 | [`src/graphsag/governance/adaptive.py`](src/graphsag/governance/adaptive.py)、[`src/graphsag/security/identity.py`](src/graphsag/security/identity.py)、[`src/graphsag/observability/telemetry.py`](src/graphsag/observability/telemetry.py) |
| DeepSeek V4 适配器边界 | [`src/graphsag/adapters/llm.py`](src/graphsag/adapters/llm.py) |

## API 与部署边界

可选的 FastAPI 接口位于 [`src/graphsag/api/app.py`](src/graphsag/api/app.py)，安装 API 依赖：

```bash
pip install -e ".[api]"
```

接口只负责接收请求并调用决策内核；生产部署必须提供真实的工作负载身份验证器。不能把未验证的 HTTP header、模型输出或 Provider 输出直接当作授权依据。Kubernetes、密钥托管、OIDC/mTLS、网络策略、备份恢复和高可用存储仍属于部署方责任。

# 安全说明
如果发现 GraphSAG 的安全漏洞，请不要直接在公开 Issue 中披露完整攻击细节。

当前仓库未提供公开的安全报告地址。请在披露敏感细节前，先联系项目维护者并遵循负责任披露原则。

---

# 许可证说明
当前仓库未包含 `LICENSE` 文件；在明确许可证之前，请不要将其作为已授予许可的第三方依赖分发。

---

# 状态
**当前版本：v1.0.0**

GraphSAG 当前是一个安全治理内核/参考实现。

它已经具备基础治理链路和安全约束，但生产部署仍需完成环境特定的验证：

```
Evidence
   ↓
Graph
   ↓
Decision
   ↓
Authorization
   ↓
Execution
   ↓
Audit
   ↓
Adaptive Governance
```
如果你正在构建具有自主决策、知识检索、记忆、工具调用或多 Agent 协作能力的 AI 系统，欢迎从实际问题、攻击案例、部署经验和工程约束出发参与讨论。

**GraphSAG 的目标不是让 Agent 少做事，而是让 Agent 在获得更强自主能力的同时，能够解释自己为什么这么做，并让关键行动始终处于明确的安全边界之内。**