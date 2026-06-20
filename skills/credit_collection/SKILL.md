---
name: credit_collection
description: "本技能提供标准化的信用卡逾期催收决策引擎，支持M1-M3+全阶段催收策略生成、合规红线检测、催收话术输出及企微卡片推送。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L2
capability_domain: [C02, C04, C05]
industry: legal
metadata:
  raw_title: "Credit Collection Skill - 信用卡逾期催收引擎"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# Credit Collection Skill - 信用卡逾期催收引擎

## 概述

本技能提供标准化的信用卡逾期催收决策引擎，支持M1-M3+全阶段催收策略生成、合规红线检测、催收话术输出及企微卡片推送。

## 功能特性

- **逾期阶段智能判断**：M1(1-30天) / M2(31-60天) / M3(61-90天) / M3+(90天以上)
- **催收策略匹配**：M1短信 → M2电话 → M3上门 → M3+移交法务
- **优先级评估**：紧急/高/中/低四档
- **分期还款建议**：根据欠款金额和逾期天数生成个性化分期方案
- **合规红线检测**：自动拦截违规催收行为
- **标准化话术**：分阶段催收话术模板

## 合规红线（硬约束）

| 规则 | 说明 |
|------|------|
| 时间限制 | 禁止晚上21:00后催收 |
| 第三人保护 | 禁止联系债务人以外的第三人 |
| 禁止威胁恐吓 | 不得使用威胁、恐吓、骚扰性语言 |
| 禁止暴力 | 不得使用暴力或暴力威胁 |
| 个人信息保护 | 不得泄露债务人个人信息 |

## 逾期阶段定义

```
M1:  1-30天   →  短信催收为主
M2:  31-60天  →  电话催收为主
M3:  61-90天  →  上门催收为主
M3+: 90天以上 →  移交法务/诉讼
```

## 使用方式

### Python API

```python
from credit_collection import CreditCollectionEngine

engine = CreditCollectionEngine()
result = engine.generate_collection_plan(
    overdue_days=30,
    outstanding_amount=50000,
    customer_type="personal",
    payment_history=["按时", "逾期1次", "逾期2次"],
    contact_valid=True
)
print(result)
```

### CLI

```bash
python3 scripts/collection_cli.py generate "催收 客户逾期30天 欠款5万 首次逾期 联系方式有效"
```

## 输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| stage | string | 逾期阶段 (M1/M2/M3/M3+) |
| priority | string | 催收优先级 |
| strategies | list | 催收策略列表 |
| installment_advice | dict | 分期还款建议 |
| legal_warning | string | 法律后果提示 |
| scripts | dict | 催收话术（分阶段） |
| compliance_check | dict | 合规检测结果 |
| red_line_violations | list | 违规行为列表 |

## 文件结构

```
credit_collection/
├── SKILL.md              # 本文档
├── collection_engine.py   # 核心引擎
├── __init__.py           # 模块导出
├── scripts/
│   └── collection_cli.py # CLI入口
└── wecom_integration.py  # 企微卡片集成
```
