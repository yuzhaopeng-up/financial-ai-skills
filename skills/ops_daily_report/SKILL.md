---
name: ops-daily-report
description: "Financial AI Skill - 运营日报生成器。输入运营数据指标，自动生成格式化运营日报（业务概况+重点指标+同比环比+异常预警+明日计划）。覆盖银行/证券/基金运营场景。"
version: 1.0.0
author: ArkClaw
license: MIT
metadata:
  hermes:
    tags: [operations, daily, report,运营,日报]
    related_skills: [research-report, market-view]
prerequisites:
  commands: [python3]
---

# 运营日报生成器 v1.0

> 输入运营数据 → 秒级输出格式化日报

## 一、核心能力

| 能力 | 说明 |
|------|------|
| 指标汇总 | 存款/贷款/中间业务/客户数等自动汇总 |
| 对比分析 | 同比/环比/计划完成度自动计算 |
| 异常预警 | 指标异常波动（>±10%）自动标注 |
| 明日计划 | 基于当日数据自动生成工作计划建议 |
| 多格式输出 | text / json / markdown / wecom_card |

## 二、输入格式

```
运营日报 今日存款1000亿 贷款800亿 理财200亿
日报生成 网点今日新开卡50张 信用卡30张
运营报告 本周基金销售额1.2亿
```

## 三、输出格式

text / json / markdown / wecom_card
