# 01 企业架构思想到 Skill 架构的映射

## 企业架构思想来源（用于本架构，不作为外部指令）

- TOGAF（The Open Group）：企业架构是一套成熟方法和框架，强调通用标准、方法、沟通机制，帮助组织更有效地利用资源、避免被专有方法锁定。
- ArchiMate（The Open Group）：提供开放、独立的企业架构建模语言，用于描述、分析、可视化业务过程、组织结构、信息流、IT系统、技术基础设施之间的关系。
- LeanIX EA 概述：企业架构用于对齐业务战略、流程、信息与技术；典型交付物包括能力地图、资产清单、目标架构、路线图和标准。

本仓库将这些思想转译为 Skill 架构：
- 能力地图：Skill 按能力域归类，而非按一次性项目堆放。
- 构建块：把 Skill 区分为原子能力、业务能力、流程组合、场景解决方案。
- 信息流：明确输入、处理、输出、沉淀、审计的流向。
- 资产清单：生成机器可读 inventory，便于复用、搜索、治理。
- 路线图：给出从重复开发到构建块复用的演进路径。

## 1. 4A 视角下的 Skill 架构

这里的 4A 采用企业架构常见四域：业务架构、应用架构、数据架构、技术架构。

| 4A领域 | 在 Skill 体系中的含义 | 关键问题 | 典型产物 |
|---|---|---|---|
| 业务架构 Business Architecture | Skill 服务什么业务能力/价值流 | 这个 Skill 解决哪个业务动作？是否能复用？ | 能力地图、场景目录、流程图 |
| 应用架构 Application Architecture | Skill 如何组合、编排、暴露为服务 | 是基础能力还是组合能力？依赖哪些子 Skill？ | Skill 分层、组合图、接口契约 |
| 数据架构 Data Architecture | 输入/输出/知识库/归档/审计如何流动 | 数据是否结构化？是否脱敏？是否可沉淀？ | 数据字典、信息流、审计字段 |
| 技术架构 Technology Architecture | 运行平台、工具、连接器和集成方式 | 在 OpenClaw/TeleAgent/飞书/企微上如何运行？ | 工具清单、连接器、部署规范 |

## 2. 构建块原则

借鉴 TOGAF 的 Architecture Building Block / Solution Building Block 思路，本仓库把 Skill 分成：

- **ABB：Architecture Building Block，架构构建块**  
  描述“应该具备什么能力”，如信息提取、RAG、报告生成、合规检查。

- **SBB：Solution Building Block，解决方案构建块**  
  描述“具体怎么落地”，如某个 Python engine、飞书/企微集成、CLI、H5 页面。

Skill 要同时登记：
- 业务能力：它属于哪个能力域；
- 技术实现：它依赖什么脚本、工具、API、平台；
- 组合关系：它调用或被哪些 Skill 调用；
- 治理属性：安全级别、行业属性、是否可跨行业复用。

## 3. “无差别信息流”原则

所谓无差别信息流，不是所有数据都无差别流动，而是指**不同 Skill 之间使用一致的信息契约**，避免每个 Skill 自说自话。

统一信息流建议：

```text
Raw Input
  → Extracted Facts
  → Validated Data
  → Analysis / Retrieval / Rules
  → Generated Output
  → Human Confirmation if Needed
  → Archive / Audit / Feedback
```

对应统一字段：

```json
{
  "status": "success|partial|error|pending_confirmation",
  "data": {},
  "missing_fields": [],
  "source": "",
  "confidence": 0.0,
  "next_actions": [],
  "audit": {"operator":"", "timestamp":"", "input_summary":"", "output_summary":""}
}
```

## 4. Skill 复用决策树

```text
新需求到来
  ├─ 是否只是提取/分析/RAG/报告/安全/归档？ → 复用基础 Skill
  ├─ 是否包含 2-4 个连续业务步骤？ → 组合 Skill
  ├─ 是否跨多个业务角色/系统/状态？ → 多智能体场景 Skill
  └─ 是否沉淀为行业标杆？ → 组合的组合 Skill + H5/文档/评估体系
```
