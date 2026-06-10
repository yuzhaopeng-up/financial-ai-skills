---
name: market-view
description: "Financial AI Skill - 市场观点输出引擎。输入市场数据/新闻/行情，自动生成日报/周报观点输出（大盘综述+行业表现+热点主题+资金流向+下周展望）。覆盖A股/港股/美股，零外部依赖。"
version: 1.0.0
author: ArkClaw
license: MIT
metadata:
  hermes:
    tags: [market, daily, weekly, report,市场,日报,周报]
    related_skills: [research-report, meeting-minutes]
prerequisites:
  commands: [python3]
---

# 市场观点输出引擎 v1.0

> 输入市场数据 → 秒级输出日报/周报（综述+行业+热点+资金+展望）

## 一、核心能力

| 能力 | 说明 |
|------|------|
| 大盘综述 | 沪深港三大指数涨跌+成交量+北向资金 |
| 行业表现 | 领涨/领跌行业，自动标注驱动逻辑 |
| 热点主题 | 当日/周热门主题，自动关联龙头个股 |
| 资金流向 | 北向/主力/超大单资金流向统计 |
| 周报扩展 | 相比日报增加周度环比、同比对比 |

## 二、输入格式

```
市场日报 今天A股收盘情况
市场周报 本周港股科技板块
观点输出 沪深300 2025年第一周
```

## 三、输出格式

text / json / markdown / wecom_card
