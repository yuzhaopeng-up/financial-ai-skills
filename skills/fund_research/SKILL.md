---
name: fund-research
description: "Financial AI Skill - 基金研究报告生成器。输入基金代码/名称，自动输出基金分析报告（业绩归因+收益分解+风险分析+基金经理评价+投资建议）。覆盖公募/私募/货币/债券/混合型基金。"
version: 1.0.0
author: ArkClaw
license: MIT
metadata:
  hermes:
    tags: [fund, research, analysis,基金,研究]
    related_skills: [research-report, market-view]
prerequisites:
  commands: [python3]
---

# 基金研究报告生成器 v1.0

> 输入基金代码/名称 → 秒级输出基金分析报告

## 一、核心能力

| 能力 | 说明 |
|------|------|
| 业绩归因 | 近1/3/6月及成立以来收益率，自动对比基准 |
| 收益分解 | Alpha/Beta/择时/选股贡献拆解 |
| 风险分析 | 最大回撤/夏普比率/波动率/卡玛比率 |
| 经理评价 | 从业年限/管理规模/代表作/风格标签 |
| 配置建议 | 低配/标配/高配建议+理由 |

## 二、输入格式

```
基金研究 110011 易方达中小盘
基金分析 兴全趋势投资混合
基金报告 沪深300ETF
```

## 三、输出格式

text / json / markdown / wecom_card
