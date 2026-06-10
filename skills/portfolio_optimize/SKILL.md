# portfolio_optimize - 投资组合优化引擎

## 功能概述

基于**有效前沿理论（Efficient Frontier）** 的投资组合优化引擎，在给定风险约束下最大化预期收益，支持 Markowitz 均值-方差模型。

## 核心能力

- **智能持仓分析**：解析客户现有持仓（股票/债券/基金/现金比例）
- **有效前沿优化**：在风险约束下计算最优配置
- **调仓建议生成**：买入/卖出/持有建议 + 执行优先级
- **风险收益评估**：预期收益、年化波动率、夏普比率、最大回撤
- **对比分析**：当前组合 vs 优化组合差异分析

## 内置资产库（20+）

### 权益类
- A股大盘（沪深300）、A股中小盘（中证500）、A股创业板
- 港股蓝筹、美股大盘（标普500）、美股科技（纳斯达克100）
- 日本股市、印度股市、德国股市

### 固定收益类
- 利率债（国债）、信用债（AA+）、可转债
- 货币基金、短期理财

### 另类资产
- 黄金、原油、农产品（CTA）
- REITs（房地产信托）

### 现金类
- 现金/活期存款

## 输入参数

| 参数 | 说明 | 示例 |
|------|------|------|
| current_portfolio | 当前持仓 | {"stock": 0.7, "bond": 0.2, "cash": 0.1} |
| risk_preference | 风险偏好 | "low" / "medium" / "high" |
| return_target | 收益目标 | 0.08（年化8%）|
| capital_constraint | 资金约束 | 1000000（元）|
| optimization_goal | 优化目标 | "reduce_risk" / "enhance_return" / "balance" |

## 输出结构

```json
{
  "optimized_portfolio": {
    "assets": [...],
    "expected_return": 0.072,
    "volatility": 0.12,
    "sharpe_ratio": 0.6,
    "max_drawdown": 0.18
  },
  "adjustment建议": [
    {"action": "sell", "asset": "A股大盘", "ratio": -0.15, "priority": 1},
    {"action": "buy", "asset": "黄金", "ratio": 0.10, "priority": 2}
  ],
  "comparison": {
    "current_vs_optimized": {...}
  },
  "execution_priority": [...]
}
```

## 使用方式

### CLI
```bash
python3 scripts/port_opt_cli.py generate "组合优化 当前持仓股票70%债券20%现金10% 目标风险降低"
```

### Python API
```python
from portfolio_optimize import PortfolioOptimizeEngine
engine = PortfolioOptimizeEngine()
result = engine.optimize(
    current_portfolio={"stock": 0.7, "bond": 0.2, "cash": 0.1},
    optimization_goal="reduce_risk"
)
```

## 依赖

- numpy>=1.21.0
- scipy>=1.7.0

## 目录结构

```
portfolio_optimize/
├── SKILL.md
├── port_opt_engine.py    # 核心优化引擎
├── __init__.py
├── scripts/
│   └── port_opt_cli.py   # CLI入口
└── wecom_integration.py  # 企微卡片
```
