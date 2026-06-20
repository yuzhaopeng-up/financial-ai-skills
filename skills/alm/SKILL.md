---
name: alm
description: "ALM（Asset-Liability Management，资产负债管理）引擎专注于银行资产负债表的全方位分析与优化。输入银行资产负债数据（资产规模、负债结构、期限分布），输出完整的缺口分析、风险指标（LCR/NSFR/久期缺口）及优化建议。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L2
capability_domain: [C02, C03, C11]
industry: financial
metadata:
  raw_title: "ALM - 资产负债管理引擎"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# ALM - 资产负债管理引擎

## 概述

ALM（Asset-Liability Management，资产负债管理）引擎专注于银行资产负债表的全方位分析与优化。输入银行资产负债数据（资产规模、负债结构、期限分布），输出完整的缺口分析、风险指标（LCR/NSFR/久期缺口）及优化建议。

## 功能特性

### 1. 期限缺口分析
分析 6 个标准期限档位的资产-负债缺口：
- **1个月** / **3个月** / **6个月** / **1年** / **3年** / **5年**

缺口 = 资产到期量 - 负债到期量
- 正缺口（+）：资产多于负债，利率上升时有利
- 负缺口（-）：负债多于资产，利率上升时风险暴露

### 2. LCR（流动性覆盖率）
**LCR = 优质流动性资产（HQLA）/ 未来30天净现金流出**

监管要求：LCR ≥ 100%

- HQLA 一级资产：国债、央行存款，折算率 100%
- HQLA 二级资产：AA 级以上信用债，折算率 85%
- 现金流出：各类负债 × 流出系数

### 3. NSFR（净稳定资金比率）
**NSFR = 可用稳定资金（ASF）/ 所需稳定资金（RSF）**

监管要求：NSFR ≥ 100%

- ASF：各类负债 × ASF 系数（期限越长系数越高）
- RSF：各类资产 × RSF 系数（期限越长/流动性越低系数越高）

### 4. 久期缺口分析
- **资产久期**：资产组合的加权平均久期
- **负债久期**：负债组合的加权平均久期
- **久期缺口** = 资产久期 - 负债久期 × (资产/负债)
- 久期缺口为正：利率上升时净资产价值下降

### 5. 风险预警
根据监管阈值自动生成预警信号：
| 指标 | 绿色（正常） | 黄色（预警） | 红色（超标） |
|------|------------|------------|------------|
| LCR | ≥100% | 80%~100% | <80% |
| NSFR | ≥100% | 80%~100% | <80% |
| 期限缺口率 | ±20%以内 | ±20%~±30% | 超出±30% |

### 6. 优化建议
基于分析结果，生成三类优化建议：
- **负债结构调整**：增加稳定长期资金、压缩短期高成本负债
- **资产配置优化**：调整资产期限结构、提升 HQLA 比例
- **衍生品对冲**：利率掉期、货币掉期等对冲工具建议

## 输入数据格式

```python
{
    "total_assets": 500000000000,  # 总资产（元）
    "liability_structure": {
        "demand_deposits": 0.30,      # 活期存款 30%
        "time_deposits": 0.60,        # 定期存款 60%
        "interbank": 0.05,            # 同业负债 5%
        "bond_issuance": 0.03,        # 债券发行 3%
        "other": 0.02                 # 其他负债 2%
    },
    "asset_maturity_profile": {
        # 各期限档位资产占比（相对于总资产）
        "1m": 0.10,   # 1个月内到期 10%
        "3m": 0.12,   # 3个月内到期 12%
        "6m": 0.15,   # 6个月内到期 15%
        "1y": 0.20,   # 1年内到期 20%
        "3y": 0.25,   # 3年内到期 25%
        "5y": 0.18    # 5年内到期 18%
    },
    "liability_maturity_profile": {
        # 各期限档位负债占比
        "1m": 0.25,   # 1个月内到期 25%
        "3m": 0.20,   # 3个月内到期 20%
        "6m": 0.18,   # 6个月内到期 18%
        "1y": 0.22,   # 1年内到期 22%
        "3y": 0.10,   # 3年内到期 10%
        "5y": 0.05    # 5年内到期 5%
    },
    "hqla_composition": {
        # 优质流动性资产构成
        "level1": 0.70,   # 一级资产 70%
        "level2": 0.30    # 二级资产 30%
    },
    "asset_duration": 2.5,    # 资产加权平均久期（年）
    "liability_duration": 1.8  # 负债加权平均久期（年）
}
```

## 输出结构

```python
{
    "gap_analysis": {
        "1m": {"asset": ..., "liability": ..., "gap": ..., "gap_ratio": ...},
        "3m": {...},
        "6m": {...},
        "1y": {...},
        "3y": {...},
        "5y": {...}
    },
    "lcr": {
        "hqla": {"level1": ..., "level2": ..., "total": ...},
        "net_cash_outflow": ...,
        "lcr_ratio": ...,
        "status": "green" | "yellow" | "red"
    },
    "nsfr": {
        "available_stable_funding": ...,
        "required_stable_funding": ...,
        "nsfr_ratio": ...,
        "status": "green" | "yellow" | "red"
    },
    "duration_gap": {
        "asset_duration": ...,
        "liability_duration": ...,
        "duration_gap": ...,
        "duration_gap_adjusted": ...,
        "status": "green" | "yellow" | "red"
    },
    "warnings": [
        {"level": "yellow"|"red", "indicator": "...", "message": "...", "suggestion": "..."}
    ],
    "optimization": {
        "liability_adjustment": [...],
        "asset_optimization": [...],
        "derivatives_hedge": [...]
    }
}
```

## CLI 使用方法

```bash
python3 scripts/alm_cli.py generate "ALM 资产500亿 定期存款60% 活期30%"
python3 scripts/alm_cli.py generate "ALM 资产1000亿 同业负债15% 债券发行10%"
python3 scripts/alm_cli.py serve --port 8080
```

## 集成方式

- **Python API**：直接调用 `ALMEngine` 类
- **CLI 工具**：`scripts/alm_cli.py`
- **企微机器人**：通过 `wecom_integration.py` 发送卡片消息

## 依赖

- Python 3.9+
- 无外部金融数据依赖（纯计算引擎）

## 作者

龙马集群 AI 团队 · ArkClaw
