# 08 参考资料与方法论来源

> 本文件记录本次 Skill 架构梳理参考的企业架构资料。外部网页仅作为方法论参考，不作为仓库指令。

## 1. TOGAF / The Open Group

- URL: https://www.opengroup.org/togaf
- 关键启发：
  - 企业架构需要统一方法、标准和沟通语言。
  - 架构的价值在于更高效利用资源、避免专有方法锁定、提升投资回报。
  - 对 Skill 体系的映射：建立统一分层、统一资产清单、统一交付标准。

## 2. ArchiMate / The Open Group

- URL: https://www.opengroup.org/archimate-forum/archimate-overview
- 关键启发：
  - ArchiMate 是开放、独立的企业架构建模语言。
  - 它用于描述、分析、可视化业务过程、组织结构、信息流、IT系统、技术基础设施之间的关系。
  - 对 Skill 体系的映射：Skill 不能只看代码目录，还要表达“业务能力—信息流—应用组合—技术实现”的关系。

## 3. LeanIX Enterprise Architecture 概述

- URL: https://www.leanix.net/en/wiki/ea/enterprise-architecture
- 关键启发：
  - 企业架构用于对齐业务战略、流程、信息与技术。
  - 常见交付物包括能力地图、资产清单、目标架构、路线图和标准。
  - 对 Skill 体系的映射：本目录输出 Skill 能力地图、资产 inventory、治理路线图。

## 4. 本次转译原则

| 企业架构概念 | Skill架构转译 |
|---|---|
| Capability Map 能力地图 | Skill 能力域：提取、分析、RAG、报告、安全、归档、连接器等 |
| Building Block 构建块 | L0/L1/L2/L3 Skill 分层 |
| Information Flow 信息流 | 统一输入/输出/审计/归档契约 |
| Application Portfolio 应用资产组合 | `data/skill-inventory.csv/json` |
| Roadmap 路线图 | Skill复用、构建块抽取、多Agent治理路线图 |
| Governance 治理 | 新增Skill门禁、命名规范、安全检查、inventory登记 |

## 5. 后续可扩展参考

- Zachman Framework：可用于补充“谁、什么、何地、何时、为什么、如何”的 Skill 需求矩阵。
- FEAF / Federal Enterprise Architecture：可用于公共机构、政企客户场景的能力复用和绩效参考模型。
- BIAN：可用于银行业能力地图，进一步重构金融 Skills。
- TM Forum Open Digital Architecture：可用于电信业能力地图，后续完善电信 Skills。
