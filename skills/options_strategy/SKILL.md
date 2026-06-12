# 期权策略分析技能 (options_strategy)

## 概述

本技能提供完整的期权策略分析能力，基于 Black-Scholes 框架计算希腊值，并输出多情景损益分析。

## 支持的策略类型

| 策略名称 | 英文名 | 说明 |
|---------|--------|------|
| 买入认购 | Buy Call | 支付权利金，获得以行权价买入标的资产的权利 |
| 买入认沽 | Buy Put | 支付权利金，获得以行权价卖出标的资产的权利 |
| 牛市价差 | Bull Call Spread | 买入低行权价认购 + 卖出高行权价认购 |
| 熊市价差 | Bear Put Spread | 买入高行权价认沽 + 卖出低行权价认沽 |
| 跨式组合 | Straddle | 同时买入相同行权价的认购和认沽 |
| 宽跨式组合 | Strangle | 同时买入不同行权价的认购和认沽 |

## 输入参数

| 参数 | 说明 | 示例 |
|------|------|------|
| strategy_type | 策略类型 | 买入认购 / 买入认沽 / 牛市价差 / 熊市价差 / 跨式组合 / 宽跨式组合 |
| spot_price | 标的资产当前价格 | 50 |
| strike_price | 行权价（支持多个，如牛市价差需两个） | 52 |
| premium | 权利金（总权利金支出或收入） | 2 |
| days_to_expiry | 距离到期天数 | 30 |
| volatility | 波动率（年化，百分比或小数） | 25 |
| risk_free_rate | 无风险利率（年化，默认2.5%） | 0.025 |

## 输出内容

### 希腊值分析
- **Delta**: 标的价格变化对期权价值的影响
- **Gamma**: Delta 变化率
- **Vega**: 波动率变化对期权价值的影响
- **Theta**: 时间衰减效应
- **Rho**: 利率变化对期权价值的影响

### 情景损益分析
分析 6 种到期情景下的损益：
- 标的 +20%、+10%、+5%、-5%、-10%、-20%

### 策略摘要
- 最大收益 / 最大损失
- 盈亏平衡点
- 适用场景
- 策略特点

## 使用方式

### CLI
```bash
python3 scripts/options_cli.py generate "期权策略 买入认购 标的50元 行权价52元 权利金2元 剩余30天"
```

### Python API
```python
from options_strategy import OptionsStrategyEngine

engine = OptionsStrategyEngine()
result = engine.analyze(
    strategy_type="买入认购",
    spot_price=50,
    strike_price=52,
    premium=2,
    days_to_expiry=30,
    volatility=0.25,
    risk_free_rate=0.025
)
```

## 依赖

- Python 3.8+
- numpy
- scipy

## 文件结构

```
options_strategy/
├── SKILL.md
├── options_engine.py      # 核心引擎
├── __init__.py
├── scripts/
│   └── options_cli.py     # CLI 入口
└── wecom_integration.py   # 企微卡片输出
```
