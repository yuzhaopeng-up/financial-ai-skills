---
name: family-trust
description: "Financial AI Skill - 家族信托方案引擎。输入客户画像/资产规模/传承目标，自动生成家族信托设立方案（架构设计+资产配置+税务筹划+受益人安排+风险隔离）。覆盖银行私行/信托公司高净值客户场景。"
version: 1.0.0
author: ArkClaw
license: MIT
metadata:
  hermes:
    tags: [trust, family, wealth, inheritance,信托,家族,传承]
    related_skills: [roadshow-material, global-asset-allocation]
prerequisites:
  commands: [python3]
---

# 家族信托方案引擎 v1.0

> 输入客户画像+资产规模 → 秒级输出家族信托设立方案

## 一、核心能力

| 能力 | 说明 |
|------|------|
| 架构设计 | 信托类型（他益/自益/半自益）+设立地点选择 |
| 资产配置 | 境内/境外资产大类配置比例建议 |
| 税务筹划 | 中国税务居民海外信托申报要点 |
| 受益人安排 | 代际传承路径+保护性条款设计 |
| 风险隔离 | 与家业/企业债务隔离有效性分析 |

## 二、输入格式

```
家族信托 客户50岁 资产3亿 想传承给子女
信托方案 民营企业主 资产5亿 企业债务需隔离
家族信托方案 准备上市企业主 资产10亿 税务居民中国
```

## 三、输出格式

text / json / markdown / wecom_card
