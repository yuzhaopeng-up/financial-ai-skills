# 05 多智能体联动场景 Skill

## 1. 判定标准

一个 Skill 是否应该升级为多智能体，不看“是否复杂”，而看是否存在明确的多角色协同：

- 至少 3 个职责边界：如提取、分析、合规、生成、归档。
- 存在状态传递：待处理、处理中、待人工确认、已归档。
- 存在不同权限：只读、写入、外发、审批、删除。
- 存在审计链路：每个 Agent 的输入输出都要可追踪。
- 存在人机协同节点：高风险动作必须人工确认。

## 2. 已识别多智能体候选

| name | level | scope | capability_domain | multi_agent_note |
| --- | --- | --- | --- | --- |
| application-material-checker | L2 组合Skill | 行业可迁移 | C01 信息提取与结构化 | 可联动OCR/提取Agent、规则校验Agent、风险提示Agent、报告Agent。 |
| arkclaw-team-project-builder | L3 组合的组合Skill | 行业可迁移 | C06 流程编排与路由 | 项目经理Agent规划团队、创建成员、分配角色，是显式多智能体项目编排场景。 |
| collection-optimize | L2 组合Skill | 行业专用：金融 | C02 数据分析与洞察 | 催收策略可联动客户分层Agent、话术Agent、合规Agent、跟进Agent。 |
| financial-intelligence | L3 组合的组合Skill | 行业专用：金融 | C02 数据分析与洞察 | 财务综合智能体，覆盖发票、预算、报表、税务、费用、资金预测多个子能力。 |
| lobby_marketing | L2 组合Skill | 行业专用：金融 | C07 客户/营销/服务 | 厅堂营销联动客户画像、队列状态、产品推荐与话术生成。 |
| lobby_routing | L2 组合Skill | 行业专用：金融 | C06 流程编排与路由 | 厅堂分流可联动情绪识别、排队、营销推荐与人工柜员。 |
| research-report | L3 组合的组合Skill | 行业专用：金融 | C04 报告/文档生成 | 投研报告可联动检索Agent、财务分析Agent、估值Agent、风险Agent、写作Agent。 |
| smart_customer_service | L3 组合的组合Skill | 行业专用：金融 | C07 客户/营销/服务 | 客服意图识别、问题解答、转人工/工单处理，可拆为客服Agent、知识Agent、工单Agent。 |

## 3. 推荐多智能体模式

### 客户服务闭环

```text
客服Agent → 知识Agent → 工单Agent → 合规Agent → 回访Agent → 归档Agent
```

适用 Skill：`smart_customer_service`、`collection_optimize`、`lobby_routing`。

### 投研报告工厂

```text
检索Agent → 数据分析Agent → 估值Agent → 风险Agent → 写作Agent → 审核Agent
```

适用 Skill：`research-report`、`fund_research`、`securities_research`、`portfolio_management`。

### 财务智能体组

```text
票据Agent → 预算Agent → 费用Agent → 税务Agent → 资金预测Agent → 报告Agent
```

适用 Skill：`financial-intelligence`、`invoice_check`、`budget_control`、`expense_audit`、`tax_planning`、`cashflow_forecast`。

### 项目型 Skill 孵化

```text
项目经理Agent → 业务分析Agent → Skill工程Agent → 测试Agent → 文档Agent → 发布Agent
```

适用 Skill：`arkclaw-team-project-builder` 与 TeleAgent 技能孵化器。

## 4. 多智能体治理要求

- 每个 Agent 必须有独立职责，不允许“大家都能干所有事”。
- Agent 之间只传递统一信息流对象，不传散乱自然语言。
- 高风险动作必须进入 `pending_confirmation`。
- 最终归档必须记录每个 Agent 的 trace。
