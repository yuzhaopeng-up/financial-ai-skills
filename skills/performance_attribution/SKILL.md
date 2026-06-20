---
name: performance_attribution
description: "本技能对基金/组合进行 Brinson 双归因分析，拆解超额收益来源为行业配置效应、选股效应和交互效应，并输出与基准对比的风险收益指标（超额收益、信息比率、跟踪误差）。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L1
capability_domain: [C01, C02, C03]
industry: financial
metadata:
  raw_title: "Performance Attribution Skill（基金业绩归因）"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# Performance Attribution Skill（基金业绩归因）

## 概述

本技能对基金/组合进行 Brinson 双归因分析，拆解超额收益来源为**行业配置效应**、**选股效应**和**交互效应**，并输出与基准对比的风险收益指标（超额收益、信息比率、跟踪误差）。

## 核心能力

- **Brinson 双归因模型**：将组合相对于基准的超额收益分解为行业配置、选股和交互三部分
- **行业维度归因**：按中信/申万行业分类计算各行业的配置贡献与选股贡献
- **个股权重归因**：穿透到个股级别，分析重仓股的收益贡献
- **风险指标计算**：跟踪误差、信息比率、夏普比率、最大回撤等
- **归因可视化**：结构化文本输出，便于嵌入企微卡片或飞书文档

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| fund_code | str | 是 | 基金代码，格式 FXXXXXX（如 F000001） |
| fund_return | float | 是 | 区间收益率，如 0.12 表示 12% |
| benchmark_return | float | 是 | 基准收益率，如 0.08 表示 8% |
| portfolio_weights | dict | 否 | 组合行业权重，key=行业名，value=权重（和为1） |
| benchmark_weights | dict | 否 | 基准行业权重，key=行业名，value=权重（和为1） |
| industry_returns | dict | 否 | 各行业收益率，key=行业名，value=收益率 |
| stock_weights | dict | 否 | 个股权重（可缺省，用行业代理） |
| risk_free_rate | float | 否 | 无风险利率，默认 0.03 |
| period_days | int | 否 | 计算区间天数，默认 252 |

## 输出结构

```json
{
  "fund_code": "F000001",
  "period_return": 0.12,
  "benchmark_return": 0.08,
  "excess_return": 0.04,
  "attribution": {
    "total_excess": 0.04,
    "allocation_effect": 0.025,
    "selection_effect": 0.010,
    "interaction_effect": 0.005,
    "by_industry": [...]
  },
  "risk_metrics": {
    "tracking_error": 0.045,
    "information_ratio": 0.89,
    "sharpe_ratio": 1.52,
    "max_drawdown": -0.08
  },
  "summary": "归因分析文字总结"
}
```

## 使用方式

### CLI
```bash
python3 scripts/perf_attr_cli.py generate "业绩归因 F000001 收益率12% 基准8%"
python3 scripts/perf_attr_cli.py parse "F000001 12% 8%"
```

### Python API
```python
from performance_attribution import PerformanceAttributionEngine

engine = PerformanceAttributionEngine()
result = engine.analyze(
    fund_code="F000001",
    fund_return=0.12,
    benchmark_return=0.08,
    portfolio_weights={"银行": 0.3, "电子": 0.2, "食品饮料": 0.15},
    benchmark_weights={"银行": 0.25, "电子": 0.15, "食品饮料": 0.20},
    industry_returns={"银行": 0.10, "电子": 0.18, "食品饮料": 0.08}
)
print(result["summary"])
```

### 企微卡片
```bash
python3 wecom_integration.py send --fund F000001 --return 0.12 --benchmark 0.08
```

## 数据脱敏规则

- 基金代码统一使用 `FXXXXXX` 格式，不暴露真实代码
- 个股使用占位符 `SECTOR/INDUSTRY`，不暴露真实持仓
- 测试数据均使用模拟值

## 依赖

- Python 3.8+
- numpy, pandas（可选，无依赖时使用纯Python实现）

## 模型说明

### Brinson 双归因模型

超额收益 = 行业配置效应 + 选股效应 + 交互效应

- **行业配置效应**：组合在行业权重上相对于基准的超配/低配带来的收益贡献
- **选股效应**：组合在各个行业内选股能力带来的收益贡献
- **交互效应**：配置与选股共同作用的部分（避免重复计算）

公式：
```
Allocation = Σ (W_portfolio_i - W_benchmark_i) * R_benchmark_i
Selection  = Σ W_benchmark_i * (R_portfolio_i - R_benchmark_i)
Interaction = Σ (W_portfolio_i - W_benchmark_i) * (R_portfolio_i - R_benchmark_i)
```

## 版本

- v1.0.0（2026-06-10）：初始版本，支持 Brinson 双归因 + 风险指标
