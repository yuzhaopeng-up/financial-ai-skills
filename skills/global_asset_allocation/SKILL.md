---
name: global-asset-allocation
description: "Financial AI Skill - 全球资产配置引擎。输入客户风险偏好/资产规模/配置目标，自动生成全球资产配置方案（区域分布+资产类别+货币对冲+再平衡策略）。覆盖银行私行/外资行高净值客户跨境配置场景。"
version: 1.0.0
author: ArkClaw
license: MIT
metadata:
  hermes:
    tags: [asset, allocation, global, portfolio,配置,全球,跨境]
    related_skills: [family-trust, roadshow-material, fund-research]
prerequisites:
  commands: [python3]
---

# 全球资产配置引擎 v1.0

> 输入风险偏好+资产规模 → 秒级输出全球资产配置方案

## 一、核心能力

| 能力 | 说明 |
|------|------|
| 风险适配 | R1-R5风险等级自动匹配配置方案 |
| 区域配置 | A股/港股/美股/欧股/新兴市场/黄金/REITs |
| 货币对冲 | 美元/欧元/港元/日元资产对冲策略 |
| 再平衡 | 触发阈值+执行策略自动生成 |
| 合规提示 | 外汇管制/CRS申报/合规风险提示 |

## 二、输入格式

```
全球配置 高净值客户 风险等级R3 资产1亿
跨境配置 稳健型 资产5000万 子女海外教育
资产配置 保守型 资产2亿 养老规划
```

## 三、输出格式

text / json / markdown / wecom_card
