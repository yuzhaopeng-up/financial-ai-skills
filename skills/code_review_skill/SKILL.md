---
name: code_review_skill
description: "代码安全审查技能，对输入代码片段进行多维度安全审查，识别 SQL 注入、XSS、敏感信息泄露等安全漏洞，并提供修复建议与代码质量评分。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L1
capability_domain: [C02, C09, C10]
industry: universal
metadata:
  raw_title: "Code Review Skill - 代码安全审查"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# Code Review Skill - 代码安全审查

## 概述

代码安全审查技能，对输入代码片段进行多维度安全审查，识别 SQL 注入、XSS、敏感信息泄露等安全漏洞，并提供修复建议与代码质量评分。

## 核心能力

- **安全漏洞识别**：SQL 注入、XSS、敏感信息泄露、硬编码凭证、危险函数调用
- **严重程度分级**：HIGH / MEDIUM / LOW
- **代码质量评分**：10 分制，覆盖可读性、安全性、最佳实践
- **修复建议**：每条问题提供具体修复方案

## 支持语言

Python / Java / JavaScript / SQL / Go / C++ / PHP

## 审查标准

### HIGH 级别（必须修复）
- SQL 拼接查询（未使用参数化）
- 硬编码密码/API Key/私钥
- 命令注入（eval / exec / system）
- 路径遍历
- 反序列化漏洞

### MEDIUM 级别（建议修复）
- 缺少输入验证
- 危险文件权限
- 日志敏感信息泄露
- 不安全的随机数
- 缺少 HTTPS

### LOW 级别（可选优化）
- 代码注释缺失
- 命名不规范
- 冗余代码
- 魔法数字

## 输出格式

```json
{
  "summary": {
    "language": "Python",
    "total_issues": 3,
    "high": 1,
    "medium": 1,
    "low": 1,
    "quality_score": 6.5
  },
  "issues": [
    {
      "id": 1,
      "severity": "HIGH",
      "category": "SQL_INJECTION",
      "title": "SQL 拼接查询 - 未使用参数化",
      "location": "line 12",
      "description": "用户输入直接拼接到 SQL 语句中",
      "code_snippet": "SELECT * FROM users WHERE name = '" + username + "'",
      "fix_suggestion": "使用参数化查询：cursor.execute('SELECT * FROM users WHERE name = %s', (username,))"
    }
  ]
}
```

## 使用方式

### CLI
```bash
python3 scripts/code_review_cli.py generate "代码审查 Python 用户输入SQL拼接查询 未使用参数化"
```

### Python API
```python
from code_review_engine import CodeReviewEngine

engine = CodeReviewEngine()
report = engine.review(
    code="SELECT * FROM users WHERE name = '" + username + "'",
    language="Python",
    standards=["sql_injection", "hardcoded_secret"]
)
print(report)
```

## 企微集成

通过 `wecom_integration.py` 将审查报告以卡片形式推送至企业微信。

```python
from wecom_integration import send_review_card

send_review_card(report, webhook_url="https://qyapi.weixin.qq.com/...")
```
