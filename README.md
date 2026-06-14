# 🦞 Financial AI Skills — 金融AI智能体集群

> **中文** | [English](#english-version)
>
> 面向金融机构的AI智能体Skill集合，封装8大金融业务场景的智能化能力。
> 由龙马集群（DragonHorse Cluster）出品，基于真实银行培训场景打磨。

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()

---

## 🎯 项目简介

本项目是**国内首个**面向金融业务领域的AI智能体Skill开源集合，将金融机构日常业务中的高频场景封装为可复用的AI能力模块。

**核心特色：**
- 🏦 **真实业务场景** — 来自500+金融机构培训实践
- 🤖 **多智能体协同** — 支持多节点AI协同分析
- 📱 **即插即用** — 标准化接口，快速集成到现有系统
- 🔒 **隐私安全** — 支持本地部署，数据不出域

---

## 🚀 八大财务智能体

| 智能体 | 场景 | 核心能力 | 适用岗位 |
|--------|------|----------|----------|
| 🧾 **发票查验** | 发票管理 | OCR识别、真伪查验、合规审查、重复检测 | 财务/报销 |
| 📊 **预算管控** | 预算管理 | 执行跟踪、偏差分析、预警推送 | 财务经理 |
| 📈 **财报速读** | 财务分析 | 关键指标提取、趋势分析、风险扫描 | 分析师 |
| 🏛️ **税务筹划** | 税务管理 | 税负分析、优惠匹配、合规建议 | 税务专员 |
| 📝 **费用报销** | 报销管理 | 智能分类、合规检查、审批建议 | 全员 |
| 💰 **资金预测** | 资金管理 | 现金流建模、短期预测、缺口预警 | 资金经理 |
| 📋 **采购合同分析** | 合同管理 | 风险识别、供应商评估、合规审计 | 采购/法务 |
| 🛡️ **财务风控日报** | 风险管理 | 多维度扫描、可视化Dashboard、日报生成 | 风控人员 |

---

## 📦 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
cd financial-ai-skills

# 安装依赖
pip install -r requirements.txt
```

### 使用示例

```python
from skills.financial_intelligence.engines import InvoiceEngine, BudgetEngine

# 发票查验
engine = InvoiceEngine()
result = engine.verify(invoice_code="011001900111", invoice_no="12345678")
print(result)

# 预算分析
engine = BudgetEngine()
result = engine.analyze(department="市场部", quarter="Q2")
print(result)
```

### CLI工具

```bash
# 发票查验
python -m skills.financial_intelligence.scripts.financial_cli invoice 011001900111 12345678

# 预算查询
python -m skills.financial_intelligence.scripts.financial_cli budget 市场部

# 财报速读
python -m skills.financial_intelligence.scripts.financial_cli report 示例制造集团 2025
```

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    Financial AI Skills                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Engines   │  │  Formatters │  │    CLI      │     │
│  │  (核心引擎)  │  │  (格式化器)  │  │  (命令行)   │     │
│  └──────┬──────┘  └─────────────┘  └─────────────┘     │
│         │                                               │
│  ┌──────┴──────────────────────────────────────┐       │
│  │           Multi-Agent Coordination            │       │
│  │              (多智能体协同层)                  │       │
│  └───────────────────────────────────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🤝 多智能体协同

本Skill支持多节点AI协同分析模式：

```python
# 示例：采购合同多节点协同分析
from skills.financial_intelligence.engines import ContractEngine

# 单节点模式
result = engine.analyze(contracts_data)

# 多节点协同模式（需配置节点）
result = engine.analyze_coordinated(
    contracts_data,
    nodes=["kimi_claw", "ark_claw"],
    fallback=True  # 支持故障切换
)
```

---

## 📚 文档

- [使用指南](docs/USAGE.md)
- [API文档](docs/API.md)
- [开发指南](docs/DEVELOPMENT.md)
- [场景示例](examples/)

---

## 🎓 关于作者

**Financial AI Contributors** — 龙马集群创始人

- 24本专著（项目管理、产品管理、知识管理方向）
- 服务500+金融机构的AI培训与咨询经验
- 2024-2025年开发120+Coze智能体，服务银行培训场景

---

## 📄 许可

MIT License — 详见 [LICENSE](LICENSE) 文件

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yuzhaopeng-up/financial-ai-skills&type=Date)](https://star-history.com/#yuzhaopeng-up/financial-ai-skills&Date)

---

## 📮 联系我们

- 问题反馈: [GitHub Issues](../../issues)
- 技术交流: 龙马集群飞书群
- 培训咨询: Financial AI Contributors老师

---

> 🦞 **龙马集群出品** | 让AI成为金融业务的得力助手

---

<a name="english-version"></a>

# 🦞 Financial AI Skills (English)

> AI Agent Skill collection for financial institutions, covering 8 major business scenarios.

## Overview

This is the **first open-source** AI Agent Skill collection for financial business in China, encapsulating high-frequency scenarios from 500+ financial institutions.

## Features

- 🏦 Real-world banking scenarios
- 🤖 Multi-agent coordination
- 📱 Plug-and-play integration
- 🔒 Local deployment support

## Quick Start

```bash
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
pip install -r requirements.txt
```

```python
from skills.financial_intelligence.engines import InvoiceEngine
engine = InvoiceEngine()
result = engine.verify("011001900111", "12345678")
```

## License

MIT License
