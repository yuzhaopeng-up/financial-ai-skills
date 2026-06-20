---
name: ipo_analysis
description: "IPO分析技能：输入公司名称/行业/上市板块/预计募资额，返回完整估值分析报告。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L2
capability_domain: [C02, C03, C11]
industry: financial
metadata:
  raw_title: "IPO Analysis Skill"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# IPO Analysis Skill

## 概述

IPO分析技能：输入公司名称/行业/上市板块/预计募资额，返回完整估值分析报告。

## 功能模块

1. **三种估值方法**
   - PE估值：参考行业平均PE × 预测EPS
   - PB估值：参考净资产 × PB比率
   - PS估值：参考市销率

2. **同业可比公司对比**
   - 选取5家可比上市公司
   - 对比关键财务指标

3. **定价区间建议**
   - 基于三种估值方法综合给出建议价格区间

4. **中签率估算**
   - 基于募资额和市场情绪

5. **上市后表现预测**
   - 首日涨幅预测
   - 长期表现参考历史案例

## 使用方式

```bash
# CLI方式
python3 scripts/ipo_cli.py generate "IPO分析 某科技公司 科创板 募资10亿"

# Python方式
from ipo_analysis import IPOAnalysisEngine
engine = IPOAnalysisEngine()
result = engine.analyze(
    company_name="某科技公司",
    industry="半导体",
    board="科创板",
    fundraising_amount=10_000_000_000  # 100亿
)
```

## 内置数据

- 10+知上市公司IPO案例（数据已脱敏，用"某公司"替代）
- 行业平均PE/PB/PS参考值
- 市场情绪指数模型

## 数据脱敏

所有输出中使用"某公司"替代真实公司名称。
