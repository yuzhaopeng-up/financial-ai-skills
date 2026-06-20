---
name: cashflow_forecast
description: "输入企业资金数据，返回未来1/3/6/12个月的资金预测及缺口预警（含应对方案）。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L1
capability_domain: [C02, C03, C09]
industry: universal
metadata:
  raw_title: "资金预测（Cashflow Forecast）技能"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# 资金预测（Cashflow Forecast）技能

## 概述
输入企业资金数据，返回未来1/3/6/12个月的资金预测及缺口预警（含应对方案）。

## 输入参数
| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| current_cash | float | 当前资金（万元） | 200 |
| receivables | float | 应收款项（万元） | 500 |
| payables | float | 应付款项（万元） | 300 |
| monthly_expense | float | 月均支出（万元） | 100 |

## 输出结构
```json
{
  "forecast": {
    "month_1": { "cash": 600.0, "status": "normal" },
    "month_3": { "cash": 300.0, "status": "normal" },
    "month_6": { "cash": -300.0, "status": "warning" },
    "month_12": { "cash": -900.0, "status": "danger" }
  },
  "gap_warning": {
    "month_6": { "gap": 300.0, "severity": "red", "deadline": "约6个月后" },
    "month_12": { "gap": 900.0, "severity": "red", "deadline": "约12个月后" }
  },
  "solutions": [
    { "action": "加速应收账款回收", "expected_impact": "+500万", "timeline": "1-2个月" },
    { "action": "谈判延长应付账期", "expected_impact": "+300万", "timeline": "1个月" }
  ]
}
```

## 预警规则
- **normal**（绿色）：资金 > 月支出 × 3
- **warning**（橙色）：资金 ≤ 月支出 × 3 且 > 0
- **danger**（红色）：资金 ≤ 0
- **缺口预警提前3个月红色标注**，即 Month_6/Month_12 出现负值时，gap_warning 中对应月份标记为 `severity: "red"`

## 引擎
- `CashflowForecastEngine`：核心预测类
  - `forecast(current_cash, receivables, payables, monthly_expense) -> dict`

## 集成
- `scripts/cashflow_cli.py`：CLI 入口
- `wecom_integration.py`：企微卡片推送

## CLI 用法
```bash
python3 scripts/cashflow_cli.py generate "资金预测 当前资金200万 应收500万 应付300万 月支出100万"
```

## 测试
```bash
python3 scripts/cashflow_cli.py generate "资金预测 当前资金200万 应收500万 应付300万 月支出100万"
```
