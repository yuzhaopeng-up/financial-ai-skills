---
name: objection-training
description: "金融AI技能 - 客户异议训练引擎。模拟客户各种异议场景，为客户经理提供实战训练。包含5种以上异议类型，自动评分和改进建议。"
version: 1.0.0
author: ArkClaw
license: MIT
metadata:
  hermes:
    tags: [objection, training, sales, skill, 异议, 训练, 话术, 模拟]
    related_skills: [customer-persona, customer-marketing, smart-marketing]
prerequisites:
  commands: [python3]
---

# 客户异议训练引擎 v1.0

> 模拟客户异议场景 → 训练评分 + 改进建议

## 一、核心能力

| 能力 | 说明 |
|------|------|
| 异议场景模拟 | 支持5种以上客户异议类型 |
| 多轮对话训练 | 模拟真实对话进行训练 |
| 评分系统 | 对回答进行实时评分 |
| 改进建议 | 针对薄弱环节提供改进建议 |

## 二、支持的异议类型

| 类型 | 场景 | 示例 |
|------|------|------|
| price | 价格异议 | "太贵了" |
| competition | 竞品比较 | "XX产品更好" |
| need | 需求质疑 | "我不需要" |
| time | 拖延推辞 | "我再考虑考虑" |
| trust | 信任问题 | "你们靠谱吗" |
| risk | 风险担忧 | "会不会有风险" |
| service | 服务投诉 | "上次服务不好" |

## 三、输入格式

```
异议训练 价格异议
训练 竞品比较
模拟训练 风险担忧
```

## 四、评分维度

- 第一印象 (20%): 开场白是否建立信任
- 产品价值 (30%): 是否有效传递产品价值
- 异议化解 (30%): 是否有效回应客户异议
- 行动促成 (20%): 是否有效促成下一步行动
