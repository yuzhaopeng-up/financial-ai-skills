---
name: research_notes
description: "券商调研纪要结构化处理引擎，输入调研原始信息，返回标准化结构化纪要。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L2
capability_domain: [C01, C02, C03]
industry: financial
metadata:
  raw_title: "Research Notes Skill - 调研纪要生成引擎"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# Research Notes Skill - 调研纪要生成引擎

## 概述

券商调研纪要结构化处理引擎，输入调研原始信息，返回标准化结构化纪要。

## 功能

- 解析调研纪要文本，提取关键信息
- 生成结构化纪要：出席人员、核心交流、关键数据、承诺事项、风险点、投资建议、待跟进
- 情感分析：管理层信心指数（1-10分）
- 信息可信度评分（1-10分）
- 数据脱敏：自动将真实公司名替换为"某公司"

## 输入参数

```python
{
    "company": str,           # 公司名称（脱敏后输出为"某公司"）
    "subject": str,           # 调研对象（IR/管理层/分析师等）
    "method": str,            # 调研方式（现场调研/电话调研/策略会等）
    "raw_notes": str,         # 纪要原文
    "date": str,              # 调研日期（YYYY-MM-DD）
}
```

## 输出结构

```python
{
    "attendees": List[str],           # 出席人员
    "core_discussions": List[str],     # 核心交流内容
    "key_data": List[dict],            # 关键数据（{指标, 数值, 说明}）
    "commitments": List[dict],         # 承诺事项（{事项, 承诺时间, 状态}）
    "risk_points": List[str],           # 风险点
    "investment_suggestion": str,       # 投资建议
    "follow_up_questions": List[str],   # 待跟进问题
    "sentiment_analysis": {
        "confidence_index": float,      # 管理层信心指数（1-10）
        "sentiment_label": str,        # 乐观/中性/谨慎
    },
    "credibility_score": float,         # 信息可信度评分（1-10）
    "metadata": {
        "company_masked": str,         # 脱敏后公司名
        "调研日期": str,
        "调研方式": str,
        "生成时间": str,
    }
}
```

## CLI 用法

```bash
# 生成纪要
python3 scripts/notes_cli.py generate "调研纪要 某上市公司 IR调研 纪要包含光伏扩产计划和毛利率下降"

# 以 JSON 格式输出
python3 scripts/notes_cli.py generate "..." --format json

# 输出到文件
python3 scripts/notes_cli.py generate "..." --output result.json
```

## 依赖

- Python 3.8+
- arkcloudsdk（豆包大模型）

## 目录结构

```
research_notes/
├── SKILL.md
├── notes_engine.py      # 核心引擎
├── __init__.py
├── scripts/
│   └── notes_cli.py     # CLI 入口
└── wecom_integration.py # 企微卡片
```
