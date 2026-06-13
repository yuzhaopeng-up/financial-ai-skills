---
name: contract-review
description: "金融AI技能 - 合同智能审查引擎。自动审查合同条款，识别风险点，提供修改建议。支持多种合同类型，覆盖金融行业常见合同风险。"
version: 1.0.0
author: ArkClaw
license: MIT
metadata:
  hermes:
    tags: [contract, review, legal, risk, 合同, 审查, 法务, 风险]
    related_skills: [ai-contract-review-cn, compliance-check]
prerequisites:
  commands: [python3]
---

# 合同智能审查引擎 v1.0

> 合同文本/文件 → 风险条款清单 + 修改建议

## 一、核心能力

| 能力 | 说明 |
|------|------|
| 风险识别 | 自动识别合同中的风险条款 |
| 条款分类 | 按类型分类风险条款 |
| 修改建议 | 提供具体的修改建议 |
| 合规检查 | 检查是否符合监管要求 |

## 二、支持合同类型

- 贷款合同
- 担保合同
- 理财合同
- 保险合同
- 投资协议
- 保密协议
- 服务合同

## 三、输入格式

```
合同审查 [合同文本]
审查 合同内容
风险检查 合同文本
```

## 四、风险等级

| 等级 | 标识 | 说明 |
|------|------|------|
| 高风险 | 🔴 | 需立即修改 |
| 中风险 | 🟡 | 建议修改 |
| 低风险 | 🟢 | 注意事项 |
