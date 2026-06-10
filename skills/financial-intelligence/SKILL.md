---
name: financial-intelligence
description: "Financial AI Skill - 6大财务场景AI赋能：发票查验、预算管控、财报速读、税务筹划、费用报销、资金预测。基于规则引擎的轻量级财务智能体，零API费用，毫秒级响应。"
version: 1.0.0
author: Financial AI Community
license: MIT
metadata:
  hermes:
    tags: [finance, accounting, invoice, budget, report, tax, expense, cashflow]
    related_skills: []
prerequisites:
  commands: [python3]
---

# Financial AI — 财务智能体 v1.0

> 基于规则引擎的轻量级财务智能体，6大场景全覆盖。
> 
> ⚡ 零API费用 | 🚀 毫秒级响应 | 📦 开箱即用

## 一、6大财务智能体

| 智能体 | 触发关键词 | 核心能力 |
|--------|-----------|---------|
| **发票查验** | 发票、查验、OCR | 发票信息提取、真伪校验、合规审查 |
| **预算管控** | 预算、超支、预警 | 预算执行跟踪、偏差分析、预警推送 |
| **财报速读** | 财报、年报、季报 | 关键指标提取、趋势分析、风险扫描 |
| **税务筹划** | 税务、节税、合规 | 税负分析、优惠政策匹配、合规建议 |
| **费用报销** | 报销、费用、审批 | 费用分类、合规检查、审批流建议 |
| **资金预测** | 现金流、预测、资金 | 现金流建模、短期预测、缺口预警 |

## 二、快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git

# 复制Skill到Hermes目录
cp -r financial-ai-skills/skills/financial-intelligence ~/.hermes/skills/
```

### CLI工具调用

```bash
cd ~/.hermes/skills/financial-intelligence/scripts

# 发票查验
python3 financial_cli.py invoice 011001900111 12345678

# 预算管控
python3 financial_cli.py budget 市场部

# 财报速读
python3 financial_cli.py report 美的集团 2025

# 税务筹划
python3 financial_cli.py tax 演示企业

# 费用报销
python3 financial_cli.py expense "北京出差机票" 1580

# 资金预测
python3 financial_cli.py cashflow 30
```

### Python API调用

```python
import sys
sys.path.insert(0, "~/.hermes/skills/financial-intelligence")

from engines import InvoiceEngine, BudgetEngine, ReportEngine
from formatters import FinancialFormatter

# 发票查验
engine = InvoiceEngine()
result = engine.verify("011001900111", "12345678")
print(FinancialFormatter.format_invoice(result))

# 预算管控
engine = BudgetEngine()
result = engine.analyze(dept="市场部")
print(FinancialFormatter.format_budget(result))

# 财报速读
engine = ReportEngine()
result = engine.analyze(company_name="美的集团", year=2025)
print(FinancialFormatter.format_report(result))
```

## 三、场景触发规则

当用户输入包含以下关键词时，调用对应的财务智能体：

| 场景 | 触发词 | 示例 |
|------|--------|------|
| invoice | 发票、查验、验真 | "查验发票 011001900111 12345678" |
| budget | 预算、超支、执行率 | "市场部Q2预算" |
| report | 财报、年报、速读 | "速读美的集团2025年报" |
| tax | 税务、税负、节税 | "分析演示企业税务" |
| expense | 报销、费用、审批 | "报销 北京出差机票 1580" |
| cashflow | 现金流、预测、资金 | "预测30天现金流" |

## 四、演示数据说明

所有引擎内置 Mock 数据，支持稳定演示输出：
- 发票：偶数尾号=真票，奇数尾号=异常
- 预算：市场部/技术部/财务部固定数据
- 财报：美的集团/某股份制银行A真实公开指标
- 税务：演示企业固定税负数据
- 报销：基于金额和描述的规则引擎
- 资金：演示企业固定现金流数据

## 五、项目结构

```
financial-intelligence/
├── engines/
│   ├── __init__.py
│   ├── invoice_engine.py      # 发票查验引擎
│   ├── budget_engine.py       # 预算管控引擎
│   ├── report_engine.py       # 财报速读引擎
│   ├── tax_engine.py          # 税务筹划引擎
│   ├── expense_engine.py      # 费用报销引擎
│   └── cashflow_engine.py     # 资金预测引擎
├── formatters/
│   ├── __init__.py
│   └── financial_formatter.py # Markdown格式化输出
├── scripts/
│   └── financial_cli.py       # CLI工具
└── SKILL.md                   # 本文件
```

## 六、技术特点

- **纯Python实现**：无外部API依赖，零调用成本
- **规则引擎**：100%可复现结果，适合财务合规场景
- **模块化设计**：6大引擎独立，可单独使用
- **Markdown输出**：适配IM平台（企业微信、飞书、钉钉等）
- **可扩展**：基于类结构，易于添加新引擎

## 七、版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-06-06 | 初始发布，6大财务引擎完整实现 |

## 许可证

[MIT License](../../LICENSE)

---

*Financial AI Community | 以真实用户反馈为唯一北极星指标*
