# quant_backtest - 量化回测引擎

## 功能概述
基于随机模拟K线数据的量化策略回测引擎，支持六种策略类型，返回完整回测报告。

## 支持策略

| 策略 | 关键字 | 说明 |
|------|--------|------|
| 均线交叉 | ma_cross | 短周期上穿/下穿长周期均线 |
| MACD | macd | MACD金叉/死叉信号 |
| RSI | rsi | RSI超买超卖阈值策略 |
| 布林带 | bollinger | 价格触及布林带上下轨策略 |
| 动量策略 | momentum | 追涨杀跌动量策略 |
| 价值投资 | value | 低估值买入持有策略 |

## 核心类

### BacktestEngine

```python
from quant_backtest import BacktestEngine

engine = BacktestEngine(
    strategy="ma_cross",      # 策略类型
    symbol="000001.SH",        # 标的代码
    start_date="2024-01-01",  # 开始日期
    end_date="2024-12-31",    # 结束日期
    initial_capital=1000000,  # 初始资金
    fast_period=20,           # 快周期（均线策略）
    slow_period=60            # 慢周期（均线策略）
)
report = engine.run()
```

## 回测报告字段

- **收益率曲线描述** (`equity_curve`)
- **年化收益率** (`annual_return`)
- **夏普比率** (`sharpe_ratio`)
- **最大回撤** (`max_drawdown`)
- **胜率** (`win_rate`)
- **盈亏比** (`profit_loss_ratio`)
- **卡尔玛比率** (`calmar_ratio`)
- **月度收益统计** (`monthly_returns`)
- **买卖信号示例** (`trade_signals`)

## CLI 使用

```bash
python3 scripts/backtest_cli.py generate "均线交叉 20日60日 上证指数 2024年"
python3 scripts/backtest_cli.py report --format=json
```

## 企微集成

```bash
python3 wecom_integration.py --report_id <id>
```
