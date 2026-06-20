---
name: policy_management
description: "保单管理技能提供完整的保单检视与保全服务，涵盖保障缺口分析、现金价值计算、保全建议及家庭保障全景图。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L2
capability_domain: [C02, C03, C05]
industry: universal
metadata:
  raw_title: "保单管理技能 (Policy Management Skill)"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# 保单管理技能 (Policy Management Skill)

## 概述

保单管理技能提供完整的保单检视与保全服务，涵盖保障缺口分析、现金价值计算、保全建议及家庭保障全景图。

## 核心功能

### 1. 保单检视报告
- **保障缺口分析**：基于客户收入/负债/家庭结构计算应有保额
- **保费合理性评估**：对比市场同类产品，评估保费是否合理
- **现金价值走势**：使用精算复利公式计算当前现金价值和未来趋势

### 2. 保全建议
- **加保**：保障不足时的加保方案
- **减保**：保费压力时的减保方案
- **险种转换**：产品优化组合建议
- **退保**：最后手段的退保分析
- **自动垫交**：现金价值垫交保费分析
- **到期处理**：期满后的处理方案

### 3. 续期提醒
- 下次缴费日期提醒
- 缴费年期进度
- 失效风险预警

### 4. 家庭保障全景图
- 整合家庭所有成员保单
- 整体保障评估
- 家庭保障热力图

## 使用方法

### CLI
```bash
python3 scripts/policy_cli.py generate "保单检视 寿险50万 重疾30万 年缴保费2万 已缴5年"
```

### Python API
```python
from policy_management import PolicyManagementEngine

engine = PolicyManagementEngine()
result = engine.generate_review(
    policies=[
        {"type": "寿险", "sum_insured": 500000, "annual_premium": 12000},
        {"type": "重疾", "sum_insured": 300000, "annual_premium": 8000},
    ],
    total_annual_premium=20000,
    years_paid=5,
    client_info={
        "annual_income": 300000,
        "total_debt": 800000,
        "family_size": 4,
        "children_count": 2,
    }
)
```

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| policies | list | 是 | 保单列表 |
| total_annual_premium | float | 是 | 年缴保费总额 |
| years_paid | int | 是 | 已缴年限 |
| client_info | dict | 否 | 客户信息（收入/负债/家庭） |

## 输出格式

返回包含以下模块的结构化报告：
- `coverage_gap`: 保障缺口分析
- `premium_analysis`: 保费合理性
- `cash_value`: 现金价值分析
- `policy_suggestions`: 保全建议
- `renewal_reminder`: 续期提醒
- `family_overview`: 家庭保障全景

## 技术规格

- 保障缺口计算：双十原则 + 生命价值法
- 现金价值：精算复利公式
- 假设利率：年复利 3.5%（可配置）
