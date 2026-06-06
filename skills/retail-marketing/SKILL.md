---
name: retail-marketing
version: 1.0.0
description: 零售营销 Skill - 客户画像、精准营销、产品推荐、AUM提升、营销效果评估
author: yuzhaopeng-up
category: financial-ai
tags:
  - retail-marketing
  - customer-segmentation
  - precision-marketing
  - product-recommendation
  - aum-growth
  - customer-lifetime-value
  - marketing-analytics
  - wealth-management
  - digital-marketing
  - campaign-optimization
license: MIT
---

# Retail Marketing Skill (零售营销)

## 概述

零售营销 Skill，覆盖零售客户从画像构建到营销效果评估的完整闭环。复用 wealth-management 的客户分析能力，实现精准营销和 AUM 提升。

**适用场景**：零售客户营销、产品推荐、客户分层运营、AUM提升、营销活动策划

**书中对应**：第12章 "零售营销"、第13章 "客户生命周期管理"

## 能力清单

| 能力 | 描述 | 书中对应 |
|------|------|---------|
| 客户画像构建 | 多维度标签体系，360°客户视图 | 第12章 12.1 |
| 客户分层运营 | RFM模型、AUM分层、生命周期分层 | 第12章 12.2 |
| 精准营销推荐 | 基于画像的产品推荐、时机推荐 | 第12章 12.3 |
| 产品匹配引擎 | 风险适配、需求匹配、收益预期匹配 | 第12章 12.4 |
| AUM提升策略 | 资产提升路径、交叉销售、向上销售 | 第12章 12.5 |
| 营销效果评估 | 转化率、ROI、客户满意度追踪 | 第12章 12.6 |
| 客户流失预警 | 流失风险评分、挽留策略推荐 | 第13章 13.1 |
| 营销活动策划 | 活动设计、渠道选择、预算分配 | 第12章 12.7 |

## 快速开始

```python
from retail_marketing import RetailMarketingEngine

# 初始化营销引擎
engine = RetailMarketingEngine()

# 构建客户画像
profile = engine.build_customer_profile(
    customer_id="C001",
    age=35,
    gender="男",
    aum=500000,
    risk_preference="稳健型",
    transaction_history=[...]
)

# 生成营销推荐
recommendations = engine.generate_recommendations(profile)

# 输出推荐报告
print(recommendations.to_markdown())
```

## 模块结构

```
retail-marketing/
├── SKILL.md              # 本文件
├── retail_marketing.py   # 主引擎
├── customer_profiler.py  # 客户画像构建
├── customer_segment.py   # 客户分层运营
├── recommendation.py     # 精准营销推荐
├── product_matcher.py    # 产品匹配引擎
├── aum_strategy.py       # AUM提升策略
├── campaign_evaluator.py # 营销效果评估
└── examples/
    └── demo.py           # 演示脚本
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0.0 | 2026-06-06 | 初始发布，8大能力 |
