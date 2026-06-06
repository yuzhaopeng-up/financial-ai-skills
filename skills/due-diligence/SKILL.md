---
name: due-diligence
version: 1.0.0
description: 对公客户尽职调查 Skill - 企业信息采集、行业研究、风险评分、尽调报告生成
author: yuzhaopeng-up
category: financial-ai
tags:
  - due-diligence
  - corporate-banking
  - risk-assessment
  - industry-research
  - credit-analysis
  - compliance
  - investigation
  - report-generation
  - financial-analysis
  - enterprise-data
license: MIT
---

# Due Diligence Skill (对公尽调)

## 概述

对公客户尽职调查 Skill，覆盖企业客户从信息采集到报告生成的完整尽调流程。复用 risk-compliance 的评分能力，实现企业风险量化评估。

**适用场景**：对公开户、授信审批、贷后管理、投前尽调、供应商准入

**书中对应**：第11章 "对公客户尽职调查"、第10章 "风控合规"

## 能力清单

| 能力 | 描述 | 书中对应 |
|------|------|---------|
| 企业信息采集 | 工商、司法、舆情、财务多源采集 | 第11章 11.1 |
| 行业研究分析 | 行业地位、竞争格局、发展趋势 | 第11章 11.2 |
| 关联关系挖掘 | 股权穿透、实际控制人、关联交易 | 第11章 11.3 |
| 财务健康评分 | 偿债/盈利/运营/成长四维评分 | 第11章 11.4 |
| 风险综合评级 | 复用 risk-compliance 评分体系 | 第10章 10.3 |
| 尽调报告生成 | 标准化 Markdown/Word 报告 | 第11章 11.5 |
| 舆情监控预警 | 负面新闻、诉讼、失信实时追踪 | 第11章 11.6 |
| 担保圈识别 | 复用 knowledge_graph 担保链检测 | 第10章 10.2.3 |

## 快速开始

```python
from due_diligence import DueDiligenceEngine

# 初始化尽调引擎
engine = DueDiligenceEngine()

# 执行完整尽调
report = engine.conduct_due_diligence(
    company_name="示例科技有限公司",
    credit_code="91310000XXXXXXXXXX",
    industry="软件和信息技术服务业"
)

# 输出报告
print(report.to_markdown())
```

## 模块结构

```
due-diligence/
├── SKILL.md              # 本文件
├── due_diligence.py      # 主引擎
├── company_collector.py  # 企业信息采集
├── industry_research.py  # 行业研究分析
├── financial_scorer.py   # 财务健康评分
├── risk_assessor.py      # 风险综合评级
├── report_generator.py   # 尽调报告生成
├── public_opinion.py     # 舆情监控预警
└── examples/
    └── demo.py           # 演示脚本
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0.0 | 2026-06-06 | 初始发布，8大能力 |
