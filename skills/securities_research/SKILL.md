---
name: securities_research
description: "Skill Name: securities_research Skill Path: skills/securities_research/ Engine Class: SecuritiesResearchEngine Core Functionality: 基于行业研究框架，自动生成投研报告大纲、核心观点、数据支撑及投资建议"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L2
capability_domain: [C02, C03, C05]
industry: financial
metadata:
  raw_title: "Securities Research Skill（投研报告生成引擎）"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# Securities Research Skill（投研报告生成引擎）

## 概述

**Skill Name:** `securities_research`  
**Skill Path:** `skills/securities_research/`  
**Engine Class:** `SecuritiesResearchEngine`  
**Core Functionality:** 基于行业研究框架，自动生成投研报告大纲、核心观点、数据支撑及投资建议  

## 功能说明

输入公司名称/行业/研究类型（深度报告/行业跟踪/宏观策略/晨会点评），返回：

- 研究报告大纲
- 核心观点
- 数据支撑（财务/行业/竞争）
- 投资建议（买入/持有/卖出）
- 风险提示

## 研究类型

| 类型 | 英文 | 说明 |
|------|------|------|
| 深度报告 | `deep` | 全面深入分析，3-5年历史+未来展望 |
| 行业跟踪 | `industry` | 行业动态+公司近期经营情况 |
| 宏观策略 | `macro` | 宏观经济+大类资产配置建议 |
| 晨会点评 | `daily` | 当日市场点评，快读输出 |

## 内置行业研究框架（10+）

- **银行** — 净息差/资产质量/资本充足率/流动性指标
- **证券** — 经纪/投行/资管/自营四象限分析
- **保险** — 寿险EV/产险综合成本率/险资运用
- **房地产** — 销售/拿地/融资/政策环境四维框架
- **医药** — 研发管线/竞争格局/政策免疫/商业化
- **科技/半导体** — 技术路线/国产替代/下游需求
- **消费** — 品牌力/渠道力/产品力/供应链
- **新能源** — 政策+技术+成本+装机容量
- **能源/煤炭** — 供给格局/价格机制/运输通道
- **钢铁/建材** — 供需平衡/产能置换/原料成本
- **交通运输** — 客货运量/港口吞吐/航空景气

## 数据脱敏

所有输出使用"某公司"替代真实公司名。

## CLI 用法

```bash
# 生成深度报告
python3 scripts/sec_research_cli.py generate "投研报告 某新能源公司 深度报告"

# 行业跟踪
python3 scripts/sec_research_cli.py generate "投研报告 某光伏公司 行业跟踪"

# 宏观策略
python3 scripts/sec_research_cli.py generate "投研报告 宏观 宏观策略"

# 晨会点评
python3 scripts/sec_research_cli.py generate "投研报告 某证券公司 晨会点评"

# JSON 格式输出
python3 scripts/sec_research_cli.py generate "投研报告 某银行 深度报告" --format=json
```

## 输出格式

```json
{
  "report_type": "深度报告",
  "company": "某新能源公司",
  "industry": "新能源",
  "rating": "买入",
  "outline": [...],
  "core_views": [...],
  "financial_data": {...},
  "industry_data": {...},
  "competitive_data": {...},
  "investment_advice": "...",
  "risk_factors": [...]
}
```

## 企微卡片

通过 `wecom_integration.py` 生成企业微信卡片格式推送。

---

*本技能仅供内部投研参考，不构成投资建议。*
