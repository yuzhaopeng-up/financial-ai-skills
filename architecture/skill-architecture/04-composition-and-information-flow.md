# 04 Skill 组合关系与信息流

## 1. 六类基础构建块

电信课程中的六个基础组件可以抽象为所有行业通用的 Skill Building Blocks：

| 基础构建块 | 作用 | 已有相似Skill | 可复用到哪些场景 |
|---|---|---|---|
| Info-Extractor | 原始输入 → 结构化事实 | financial_extract、application-material-checker、invoice_check、meeting_minutes | 材料审核、尽调、投诉、工单、合同、报表 |
| Data-Analyst | 数据 → 趋势/异常/洞察 | data-analysis-skill、kpi_performance、performance_attribution、cashflow_forecast | 经营分析、投研、风险预警、运营日报 |
| Knowledge-RAG | 问题 → 有依据答案 | product-manual-rag、regulatory-policy-rag、research_rag、multi-search-engine | 客服、产品经理、监管解读、研报查询 |
| Report-Generator | 事实/洞察 → 报告 | ops_daily_report、market_view、research-report、roadshow_material、fund_research | 日报、周报、调研纪要、路演材料、投研报告 |
| Security-Guard | 权限/合规/风险检查 | compliance_auto、risk-compliance、cyber-owasp-review、audit_sampling、aml_rating | Skill上线门禁、外发审批、合规检查 |
| Archive-Manager | 输出 → 资产沉淀 | ontology、regulatory_reporting、meeting_minutes、feishu-doc-manager | 知识库、案例库、审计库、FAQ、经营复盘 |

## 2. 组合模板

### 模板A：材料审核

```text
Info-Extractor → Rule Validator → Security-Guard → Report-Generator → Archive-Manager
```

代表：`application-material-checker`、`corp_account_opening`、`invoice_check`。

### 模板B：知识库问答

```text
Question Parser → Knowledge-RAG → Citation Checker → Security-Guard → Archive-Manager
```

代表：`product-manual-rag`、`regulatory-policy-rag`、`research_rag`。

### 模板C：经营日报/分析报告

```text
Info-Extractor / Dataset Loader → Data-Analyst → Report-Generator → Human Review → Archive-Manager
```

代表：`ops_daily_report`、`market_view`、`fund_research`、`research-report`。

### 模板D：客户服务闭环

```text
Info-Extractor → Intent Router → Knowledge-RAG / Policy Rules → Response Generator → Security-Guard → Archive-Manager
```

代表：`smart_customer_service`、`customer-marketing`、`collection_optimize`、`lobby_routing`。

## 3. 无差别信息流契约

所有组合 Skill 应使用统一字段，降低拼接成本：

| 字段 | 含义 | 必填 |
|---|---|---|
| `status` | success/partial/error/pending_confirmation | 是 |
| `data` | 结构化结果 | 是 |
| `missing_fields` | 缺失字段 | 是 |
| `source` | 数据/知识来源 | 是 |
| `confidence` | 置信度 | 是 |
| `next_actions` | 下一步动作 | 是 |
| `citations` | 知识/文档引用 | RAG类必填 |
| `audit` | 审计摘要 | 写入/外发/高风险必填 |

## 4. 复用优先级

1. 先复用 L0 连接器与平台工具。
2. 再复用 L1 基础能力。
3. 业务规则不同，只替换规则配置，不重写引擎。
4. 报告模板不同，只替换模板，不重写提取和分析。
5. 涉及多个角色和状态，再升级为 L3/多Agent。
