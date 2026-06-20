# Skill Architecture 能力架构总览

> 目标：把 ArkClaw 已开发/已安装 Skills 梳理为可复用、可治理、可组合的企业级能力架构。  
> 位置：`architecture/skill-architecture/`，不与现有 `skills/` 代码目录重叠。  
> 生成时间：2026-06-20T18:55:04.350726+08:00

## 1. 为什么要做 Skill 架构

电信 Skill 实战课程给出的启发是：Skill 不能只按项目临时堆叠，而要像企业架构中的“构建块”一样管理。

- **基础 Skill** 像砖：信息提取、数据分析、知识检索、报告生成、安全检查、归档沉淀。
- **组合 Skill** 像房间：把多个基础能力串成一个业务流程，例如材料审核、产品手册RAG、投研报告。
- **组合的组合 Skill** 像楼层/建筑：面向完整业务场景，例如客户服务、厅堂运营、财富管理、财务综合智能体。
- **多智能体场景 Skill** 像工程总包：由不同角色 Agent 协同完成端到端价值流。

## 2. 盘点范围

| 指标 | 数量 |
|---|---:|
| 原始 SKILL.md 文件 | 283 |
| 去重后 Skill | 153 |
| 私有金融仓库 Skill | 90 |
| 工作区/插件/Agent 已安装 Skill | 63 |

## 3. 分层统计

| level | count |
| --- | --- |
| L2 组合Skill | 86 |
| L1 基础Skill | 36 |
| L0 原子/连接器Skill | 23 |
| L3 组合的组合Skill | 8 |

## 4. 行业属性统计

| scope | count |
| --- | --- |
| 行业专用：金融 | 73 |
| 跨行业通用 | 63 |
| 行业可迁移 | 17 |

## 5. 能力域统计

| capability_domain | count |
| --- | --- |
| C02 数据分析与洞察 | 36 |
| C09 集成连接器 | 32 |
| C05 风险/合规/安全 | 16 |
| C07 客户/营销/服务 | 16 |
| C01 信息提取与结构化 | 5 |
| C06 流程编排与路由 | 7 |
| C10 沉淀归档与治理 | 3 |
| C08 投资/组合/定价 | 17 |
| C04 报告/文档生成 | 12 |
| C03 知识检索与RAG | 9 |

## 6. 目录说明

| 文件 | 用途 |
|---|---|
| `01-enterprise-architecture-principles.md` | 企业架构思想如何映射到 Skill 架构 |
| `02-skill-layer-taxonomy.md` | L0/L1/L2/L3 分层规则与代表 Skill |
| `03-skill-inventory.md` | Skill 资产清单摘要 |
| `04-composition-and-information-flow.md` | 组合关系与“无差别信息流”设计 |
| `05-multi-agent-scenario-skills.md` | 多智能体联动场景 Skill |
| `06-cross-industry-vs-industry-specific.md` | 跨行业通用 vs 行业专用矩阵 |
| `07-governance-and-roadmap.md` | 治理机制与复用路线图 |
| `data/skill-inventory.json` | 机器可读全量 Skill 清单 |
| `data/skill-inventory.csv` | 表格版 Skill 清单 |
| `data/category-summary.json` | 分类统计 |

## 7. 快速结论

1. **跨行业通用构建块已经足够形成平台底座**：搜索、RAG、数据分析、报告、文档、飞书/企微、测试、代码审查、前端、TTS 等。
2. **金融 Skill 大量处在 L2/L3 层**：很多是业务流程组合或完整场景解决方案，复用时应拆回基础能力块。
3. **电信课程的 6 个基础组件可以成为所有行业的“Skill 六件套”**：Info-Extractor、Data-Analyst、Knowledge-RAG、Report-Generator、Security-Guard、Archive-Manager。
4. **多智能体联动不应泛化滥用**：只有当一个场景存在多个职责边界、状态传递和审计链路时，才升级为多 Agent。
5. **未来开发原则**：先查构建块，再做组合；先复用，再新增；新增 Skill 必须登记 inventory。
