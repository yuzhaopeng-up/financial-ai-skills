---
name: churn-recall
description: "金融AI技能 - 流失客户召回引擎。识别潜在流失客户，基于RFM模型和客户行为数据生成个性化召回话术和营销策略。降低客户流失率，提升客户活跃度。"
version: 1.0.0
author: ArkClaw
license: MIT
metadata:
  hermes:
    tags: [churn, recall, customer, retention, 流失, 召回, 客户挽留]
    related_skills: [customer-persona, customer-marketing, customer-health]
prerequisites:
  commands: [python3]
---

# 流失客户召回引擎 v1.0

> 客户ID/列表 → 流失风险评分 + 个性化召回话术

## 一、核心能力

| 能力 | 说明 |
|------|------|
| 流失风险识别 | 基于RFM模型识别高流失风险客户 |
| 流失原因分析 | 分析客户流失的可能原因 |
| 个性化话术 | 针对不同流失原因生成召回话术 |
| 营销策略 | 提供具体的营销策略和触达建议 |

## 二、输入格式

```
流失召回 客户ID列表
流失分析 张三 30天未登录
召回话术 李四 最近购买减少
```

## 三、输出格式

text / json / markdown / wecom_card

## 四、流失特征指标

- R（Recency）：最近一次购买距今天数
- F（Frequency）：购买频率
- M（Monetary）：消费金额
- 登录间隔
- 产品活跃度
- 客服咨询频率

## 五、召回策略

| 流失程度 | 风险等级 | 策略 |
|----------|----------|------|
| 轻度流失 | 黄色预警 | 权益提醒、优惠推送 |
| 中度流失 | 橙色预警 | 定向关怀、专属优惠 |
| 重度流失 | 红色预警 | 1V1回访、VIP专属方案 |
