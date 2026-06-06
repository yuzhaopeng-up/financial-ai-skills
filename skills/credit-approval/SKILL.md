---
name: credit-approval
version: 1.0.0
description: 信贷审批 Skill - 信贷申请受理、信用评分、审批决策、额度测算、贷后预警
author: yuzhaopeng-up
category: financial-ai
tags:
  - credit-approval
  - loan-processing
  - credit-scoring
  - risk-assessment
  - decision-engine
  - limit-calculation
  - post-loan-monitoring
  - retail-lending
  - corporate-lending
  - automated-underwriting
license: MIT
---

# Credit Approval Skill (信贷审批)

## 概述

信贷审批 Skill，覆盖零售和对公信贷从申请受理到贷后监控的完整生命周期。复用 due-diligence 的企业信息采集能力和 risk-compliance 的风险评估体系。

**适用场景**：个人消费贷、住房按揭、经营贷、对公流贷、项目融资

**书中对应**：第14章 "信贷审批智能化"、第15章 "贷后管理"

## 能力清单

| 能力 | 描述 | 书中对应 |
|------|------|---------|
| 信贷申请受理 | 申请信息校验、材料完整性检查 | 第14章 14.1 |
| 信用评分模型 | 多维度信用评分、行为评分 | 第14章 14.2 |
| 审批决策引擎 | 规则引擎+模型决策、自动审批 | 第14章 14.3 |
| 额度测算模型 | 收入偿债比、抵押物评估 | 第14章 14.4 |
| 担保评估 | 担保人资质、抵质押物估值 | 第14章 14.5 |
| 合同生成 | 标准化合同条款、风险提示 | 第14章 14.6 |
| 贷后预警 | 还款监控、风险信号识别 | 第15章 15.1 |
| 催收策略 | 分级催收、智能外呼 | 第15章 15.2 |

## 快速开始

```python
from credit_approval import CreditApprovalEngine

# 初始化审批引擎
engine = CreditApprovalEngine()

# 提交申请
application = engine.submit_application(
    applicant_type="个人",
    name="张三",
    id_number="31010119900101XXXX",
    loan_amount=500000,
    loan_purpose="住房装修",
    income_monthly=20000
)

# 执行审批
result = engine.process_approval(application)

# 输出结果
print(result.to_markdown())
```

## 模块结构

```
credit-approval/
├── SKILL.md              # 本文件
├── credit_approval.py    # 主引擎
├── application.py        # 信贷申请受理
├── credit_scorer.py      # 信用评分模型
├── decision_engine.py    # 审批决策引擎
├── limit_calculator.py   # 额度测算模型
├── collateral_eval.py    # 担保评估
├── post_loan_monitor.py  # 贷后监控预警
└── examples/
    └── demo.py           # 演示脚本
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0.0 | 2026-06-06 | 初始发布，8大能力 |
