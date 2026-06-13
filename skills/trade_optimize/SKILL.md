# trade_optimize - 交易指令优化引擎

> 交易标的 + 手数 + 价格 → 优化下单策略

## 功能概述

算法交易指令优化引擎，将大单拆分为最优下单策略，最小化市场冲击、提升执行效率。支持 TWAP / VWAP / POV / IS 四种核心算法，回测对比基准收益，验收标准：回测收益率提升 ≥5%。

## 支持算法

| 算法 | 关键字 | 说明 |
|------|--------|------|
| TWAP | twap | 时间加权平均价格，按时间均匀拆分 |
| VWAP | vwap | 成交量加权平均价格，按历史量分布拆分 |
| POV | pov | 成交量占比，固定%跟随市场节奏 |
| IS | is | 实现缺口算法，权衡市场冲击与时机风险 |

## 核心类

```python
from trade_optimize import TradeOptimizeEngine

engine = TradeOptimizeEngine(
    symbol="600036.SH",     # 交易标的
    quantity=100000,         # 总股数
    side="buy",             # buy / sell
    price=35.50,           # 限价（参考价）
    start_time="09:30",    # 开始时间
    end_time="14:57",      # 结束时间
    algorithm="vwap",      # 算法选择
    vol_profile=[...],      # 历史分钟成交量分布（可选）
)
result = engine.optimize()
```

## 输出字段

- **订单拆分列表** (`slices`) - 每份订单的时间/价格/数量
- **预期执行均价** (`expected_vwap`)
- **市场冲击估算** (`market_impact_bps`) - 基点
- **基准对比** (`baseline_return`) - vs 无优化盲目下单
- **回测结果** (`backtest`) - 收益率 / 夏普 / 最大回撤
- **优化评分** (`score`) - 0-100 综合评分

## 回测指标

- 回测收益率 vs 基准收益率（验收标准 ≥5% 提升）
- 夏普比率
- 最大回撤
- 执行完成率

## CLI 使用

```bash
python3 scripts/trade_optimize_cli.py optimize --symbol 600036.SH --quantity 100000 --price 35.50 --algorithm vwap
python3 scripts/trade_optimize_cli.py backtest --symbol 600036.SH --quantity 50000 --algorithm twap
python3 scripts/trade_optimize_cli.py compare --symbol 600036.SH --quantity 80000
```

## 企微集成

```bash
python3 wecom_integration.py --symbol 600036.SH --quantity 100000 --price 35.50 --algorithm vwap
```
