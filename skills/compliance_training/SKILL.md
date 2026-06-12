# 合规培训技能 (compliance_training)

## 概述

合规培训技能专注于金融行业合规培训方案生成，支持多种岗位类型、培训主题和时长要求，输出完整的培训方案、案例分析、测试题目和效果评估。

## 功能特性

- **培训方案生成**：根据岗位类型、培训主题和时长要求，生成完整的培训方案
- **培训主题库**：覆盖销售合规、反洗钱、信息安全、消费者权益保护、关联交易、内幕交易六大主题
- **案例库**：真实违规案例（已脱敏）+ 处罚结果
- **课后测试**：10题选择题，涵盖法规要点和案例分析
- **培训效果评估**：多维度评估体系
- **合规要点速查卡**：快速参考指南

## 岗位类型

- 客户经理
- 柜员
- 风控专员
- 稽核审计
- 中层管理
- 高管

## 培训主题

1. 销售合规
2. 反洗钱
3. 信息安全
4. 消费者权益保护
5. 关联交易
6. 内幕交易

## 时长要求

支持 30分钟 / 45分钟 / 60分钟 / 90分钟 / 120分钟

## 输出内容

1. **培训方案**：课件大纲 + 教学案例 + 测试题目
2. **培训内容**：法规要点 + 案例分析 + 违规后果
3. **课后测试**：10题选择题（附答案）
4. **效果评估**：培训满意度 + 知识掌握度 + 行为改变度
5. **合规要点速查卡**：快速参考指南

## 使用方式

### Python API

```python
from compliance_training import ComplianceTrainingEngine

engine = ComplianceTrainingEngine()
result = engine.generate_training(
    job_type="客户经理",
    department="销售部",
    topic="销售合规",
    duration_minutes=60
)
print(result)
```

### CLI

```bash
python3 scripts/training_cli.py generate "合规培训 客户经理 销售合规 60分钟"
```

## 企微集成

支持通过 wecom_integration.py 发送培训内容至企业微信。

## 技术架构

- 核心引擎：`training_engine.py`
- CLI入口：`scripts/training_cli.py`
- 企微集成：`wecom_integration.py`
