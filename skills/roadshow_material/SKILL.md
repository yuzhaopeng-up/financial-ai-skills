---
name: roadshow-material
description: "Financial AI Skill - 路演材料生成器。输入产品信息/目标客户/演讲时长，自动生成路演PPT大纲+讲稿（开场白+产品亮点+对比优势+风险揭示+结语）。覆盖银行理财/基金/信托产品路演场景。"
version: 1.0.0
author: ArkClaw
license: MIT
metadata:
  hermes:
    tags: [roadshow, pitch, PPT,讲稿,路演]
    related_skills: [research-report, fund-research, family-trust]
prerequisites:
  commands: [python3]
---

# 路演材料生成器 v1.0

> 输入产品信息+目标客户 → 秒级输出PPT大纲+完整讲稿

## 一、核心能力

| 能力 | 说明 |
|------|------|
| 受众适配 | 根据客户类型（零售/高净值/机构）调整话术风格 |
| PPT大纲生成 | 8-15页标准路演框架，自动布局 |
| 讲稿生成 | 每页要点+话术+时间分配，演讲稿直接可用 |
| 对比优势 | 竞品对比表格，自动生成差异化话术 |
| 风险揭示 | 监管要求的标准风险揭示文本 |

## 二、输入格式

```
路演材料生成 固收类理财产品 目标客户是50岁以上保守型投资者
路演 生成私募股权基金 机构客户 30分钟
路演材料 家族信托 目标高净值 45分钟
```

## 三、输出格式

text / json / markdown / wecom_card
