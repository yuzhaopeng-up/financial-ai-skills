---
name: esg_research
description: "ESG研究技能提供中国上市公司的ESG（环境、社会、治理）评分分析报告，支持E/S/G三维评分 + 综合评分 + 同业对比 + 风险点 + 改进建议。"
version: 1.0.0
author: Hermes-Brain
license: MIT
layer: L2
capability_domain: [C02, C03, C09]
industry: financial
metadata:
  raw_title: "ESG Research Skill - ESG研究技能"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# ESG Research Skill - ESG研究技能

## 概述

ESG研究技能提供中国上市公司的ESG（环境、社会、治理）评分分析报告，支持**E/S/G三维评分 + 综合评分 + 同业对比 + 风险点 + 改进建议**。

## 核心功能

- **ESG评分**：环境（E）、社会（S）、治理（G）三维独立评分 + 综合评分
- **同业对比**：覆盖同一行业内5家竞争对手对比
- **风险分析**：识别E/S/G各维度核心风险
- **改进建议**：针对短板维度提供可执行建议
- **企微卡片**：一键生成企业微信交互卡片

## 内置数据

- **50+ 中国上市公司**：覆盖某新能源龙头企业、某新能源汽车企业、某股份制银行、某国有大行、某大型保险集团、某白酒龙头企业、某互联网巨头、某互联网巨头、某光伏龙头企业、某电力龙头企业等
- **20+ 行业**：动力电池、新能源汽车、商业银行、保险、白酒、互联网、光伏、水电、核电、医药等
- **数据来源**：2025年年报/ESG报告

## 使用方式

### Python API

```python
from esg_engine import ESGEngine

engine = ESGEngine()

# 生成文本报告
report = engine.generate_report("某新能源龙头企业")
print(report)

# 生成JSON格式
json_report = engine.generate_report("某股份制银行", format="json")

# 生成Markdown格式
md_report = engine.generate_report("某互联网巨头", format="markdown")

# 列出所有公司
companies = engine.list_companies()

# 列出所有行业
industries = engine.list_industries()
```

### CLI 命令行

```bash
# ESG研究（文本格式，默认）
python3 scripts/esg_cli.py generate "ESG研究 某新能源龙头企业"

# ESG分析（Markdown格式）
python3 scripts/esg_cli.py generate "ESG分析 某股份制银行" --format=markdown

# 输出到文件
python3 scripts/esg_cli.py generate "ESG查询 某互联网巨头" --format=text --output /tmp/某互联网巨头_esg.md

# 列出所有公司
python3 scripts/esg_cli.py list

# 搜索公司
python3 scripts/esg_cli.py search "白酒"

# 列出所有行业
python3 scripts/esg_cli.py industries
```

## ESG评分维度说明

### E（环境）

- **碳排放**：范围一/二/三碳足迹、碳强度、减排目标
- **能源**：清洁能源使用率、能耗强度、节能改造
- **水资源**：单位产品水耗、废水处理、水资源管理
- **废弃物**：固废/危废处理、回收利用率

### S（社会）

- **员工关怀**：薪酬福利、员工满意度、培训投入
- **安全生产**：工伤率、安全认证、管理体系
- **供应链**：供应商ESG审计、人权风险、溯源管理
- **社区公益**：公益投入、乡村振兴、消费者保护

### G（治理）

- **董事会结构**：独立性、女性占比、专业委员会
- **信息披露**：ESG报告评级、TCFD/ISSB对齐、透明度
- **反腐合规**：合规体系、举报机制、培训覆盖
- **股东权益**：分红比例、中小股东保护、关联交易

## ESG评级体系

| 评级 | 综合评分 | 说明 |
|------|---------|------|
| AAA | ≥90 | 卓越 |
| AA | ≥80 | 优秀 |
| A | ≥70 | 良好 |
| BBB | ≥60 | 中等 |
| BB | ≥50 | 偏弱 |
| B | <50 | 较弱 |

## 企微集成

```python
from wecom_integration import WecomCard

card = WecomCard.build_esg_card(esg_json_data)
# 发送到企微webhook
result = send_wecom_card(card, "YOUR_WEBHOOK_URL")
```

## 输出示例

```
==================================================
  ESG 研究报告：某新能源龙头企业
==================================================
行业：动力电池  |  ESG评级：AA
数据来源：内置ESG数据库（截至2025年年报/ESG报告）

--------------------------------------------------
  📊 ESG 评分
--------------------------------------------------
  E（环境）   82  +11.0 ↑  行业均值 71
  S（社会）   78   +6.0 ↑  行业均值 72
  G（治理）   75   +5.0 ↑  行业均值 70
  ──────────────────────────────
  综合评分   79   +8.0 ↑  行业均值 71

--------------------------------------------------
  🔍 核心亮点
--------------------------------------------------
  动力电池行业ESG标杆，环保技术全球领先
```

## 路径结构

```
esg_research/
├── SKILL.md              # 本文档
├── esg_engine.py         # 核心引擎
├── __init__.py           # 导出
├── wecom_integration.py  # 企微卡片
└── scripts/
    └── esg_cli.py        # CLI入口
```
