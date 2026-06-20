---
name: expense_audit
description: "费用报销审计技能，自动审核员工报销单据，判断通过/驳回/需补充，识别违规类型，提供风险提示与合规建议。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L1
capability_domain: [C02, C04, C10]
industry: financial
metadata:
  raw_title: "Expense Audit Skill（费用报销审计）"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# Expense Audit Skill（费用报销审计）

## 概述

费用报销审计技能，自动审核员工报销单据，判断通过/驳回/需补充，识别违规类型，提供风险提示与合规建议。

## 核心规则

### 招待费标准
- **上限**：招待费 ≤ 收入 × 0.5‰（千分之五）
- **事前审批**：招待费单笔 > 1000元必须事前审批
- **发票要求**：必须有正规发票，发票内容与报销事项一致

### 通用规则
- 单笔报销金额 > 50000元 需部门负责人额外审批
- 发票日期晚于报销日期 驳回
- 费用类型与部门不匹配 标记风险
- 同一员工同一类型费用本月累计异常 标记风险

## 输入

```json
{
  "employee": "员工姓名",
  "department": "部门",
  "expense_type": "费用类型（招待费/差旅费/办公费/交通费/培训费/其他）",
  "amount": 5000,
  "invoice": "有/无/待补",
  "pre_approval": "有/无（事前审批）",
  "remarks": "备注"
}
```

## 输出

```json
{
  "status": "通过|驳回|需补充",
  "violations": ["违规类型列表"],
  "risk_level": "高|中|低",
  "suggestions": ["合规建议列表"],
  "details": "详细说明"
}
```

## 违规类型编码

| 代码 | 违规类型 |
|------|----------|
| V001 | 招待费超收入千分之五上限 |
| V002 | 招待费事前未审批 |
| V003 | 缺少正规发票 |
| V004 | 发票日期晚于报销日期 |
| V005 | 单笔金额超限未额外审批 |
| V006 | 费用类型与部门不匹配 |
| V007 | 同员工同类型费用本月累计异常 |

## 使用方式

### CLI
```bash
python3 scripts/expense_cli.py generate "费用报销 张三 市场部 招待费 5000元 事前未审批"
```

### 企微机器人
```python
from expense_audit import ExpenseAuditEngine
engine = ExpenseAuditEngine()
result = engine.audit(employee="张三", department="市场部", expense_type="招待费", amount=5000, invoice="有", pre_approval="无")
```
