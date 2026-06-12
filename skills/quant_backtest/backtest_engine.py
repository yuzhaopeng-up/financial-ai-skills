"""
量化回测引擎 - 基于随机模拟K线数据的策略回测
"""

import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple


class BacktestEngine:
    """量化回测引擎，支持六种策略类型"""

    STRATEGIES = ["ma_cross", "macd", "rsi", "bollinger", "momentum", "value"]

    def __init__(
        self,
        strategy: str = "ma_cross",
        symbol: str = "XXXXXX.SH",
        start_date: str = "2024-01-01",
        end_date: str = "2024-12-31",
        initial_capital: float = 1_000_000,
        fast_period: int = 20,
        slow_period: int = 60,
        seed: Optional[int] = 42,
    ):
        self.strategy = strategy.lower()
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.fast_period = fast_period
        self.slow_period = slow_period

        # 随机种子保证可重复
        random.seed(seed)

        self._validate()

    def _validate(self):
        if self.strategy not in self.STRATEGIES:
            raise ValueError(
                f"Unknown strategy '{self.strategy}'. "
                f"Supported: {self.STRATEGIES}"
            )
        if self.fast_period >= self.slow_period:
            raise ValueError("fast_period must be < slow_period")

    # ─────────────────────────────────────────────────────────
    # 数据生成（随机模拟K线）
    # ─────────────────────────────────────────────────────────

    def _generate_price_data(self) -> List[Dict[str, Any]]:
        """生成随机模拟日K线数据"""
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = datetime.strptime(self.end_date, "%Y-%m-%d")

        prices = []
        current_price = 3000.0  # 初始价格（如上证指数3000点）
        current_date = start

        # 生成随机游走参数
        daily_return_mean = 0.0002   # 日均收益
        daily_return_std = 0.015     # 日波动率

        while current_date <= end:
            # 跳过周末
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue

            # 随机游走
            daily_return = random.gauss(daily_return_mean, daily_return_std)
            open_price = current_price * (1 + random.gauss(0, 0.005))
            close_price = open_price * (1 + daily_return)
            high_price = max(open_price, close_price) * (1 + abs(random.gauss(0, 0.008)))
            low_price = min(open_price, close_price) * (1 - abs(random.gauss(0, 0.008)))
            volume = random.uniform(1e9, 5e9)

            prices.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": round(volume, 2),
            })

            current_price = close_price
            current_date += timedelta(days=1)

        return prices

    # ─────────────────────────────────────────────────────────
    # 技术指标计算
    # ─────────────────────────────────────────────────────────

    def _sma(self, data: List[float], period: int) -> List[Optional[float]]:
        """简单移动平均"""
        result = []
        for i in range(len(data)):
            if i < period - 1:
                result.append(None)
            else:
                sma = sum(data[i - period + 1:i + 1]) / period
                result.append(round(sma, 4))
        return result

    def _ema(self, data: List[float], period: int) -> List[Optional[float]]:
        """指数移动平均"""
        k = 2 / (period + 1)
        ema = [data[0]]
        for price in data[1:]:
            ema.append(price * k + ema[-1] * (1 - k))
        return [round(e, 4) for e in ema]

    def _macd(self, close: List[float]) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
        """MACD = DIF - DEA"""
        ema12 = self._ema(close, 12)
        ema26 = self._ema(close, 26)
        dif = []
        for a, b in zip(ema12, ema26):
            dif.append(round(a - b, 4) if (a and b) else None)
        dea = self._ema([d if d else 0 for d in dif], 9)
        macd = []
        for d, e in zip(dif, dea):
            macd.append(round((d - e) * 2, 4) if (d is not None and e) else None)
        return dif, dea, macd

    def _rsi(self, close: List[float], period: int = 14) -> List[Optional[float]]:
        """RSI指标"""
        if len(close) < period + 1:
            return [None] * len(close)
        gains = []
        losses = []
        for i in range(1, len(close)):
            delta = close[i] - close[i - 1]
            gains.append(max(delta, 0))
            losses.append(max(-delta, 0))
        result = [None] * (period + 1)
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            result.append(round(100 - 100 / (1 + rs), 2))
        return result

    def _bollinger_bands(
        self, close: List[float], period: int = 20, std_dev: float = 2.0
    ) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
        """布林带（中轨±2倍标准差）"""
        mid = self._sma(close, period)
        upper = []
        lower = []
        for i in range(len(close)):
            if i < period - 1:
                upper.append(None)
                lower.append(None)
            else:
                segment = close[i - period + 1:i + 1]
                std = math.sqrt(sum((x - (mid[i] or 0)) ** 2 for x in segment) / period)
                upper.append(round((mid[i] or 0) + std_dev * std, 4))
                lower.append(round((mid[i] or 0) - std_dev * std, 4))
        return mid, upper, lower

    # ─────────────────────────────────────────────────────────
    # 策略信号生成
    # ─────────────────────────────────────────────────────────

    def _generate_signals(self, prices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """根据策略生成买卖信号"""
        close = [p["close"] for p in prices]

        if self.strategy == "ma_cross":
            return self._ma_cross_signals(prices, close)
        elif self.strategy == "macd":
            return self._macd_signals(prices, close)
        elif self.strategy == "rsi":
            return self._rsi_signals(prices, close)
        elif self.strategy == "bollinger":
            return self._bollinger_signals(prices, close)
        elif self.strategy == "momentum":
            return self._momentum_signals(prices, close)
        elif self.strategy == "value":
            return self._value_signals(prices, close)
        return []

    def _ma_cross_signals(self, prices: List[Dict], close: List[float]) -> List[Dict]:
        signals = []
        ma_fast = self._sma(close, self.fast_period)
        ma_slow = self._sma(close, self.slow_period)
        for i in range(len(prices)):
            if ma_fast[i] is None or ma_slow[i] is None:
                continue
            prev_fast = ma_fast[i - 1] if i > 0 else None
            prev_slow = ma_slow[i - 1] if i > 0 else None
            if prev_fast is not None and prev_slow is not None:
                if prev_fast < prev_slow and ma_fast[i] > ma_slow[i]:
                    signals.append({**prices[i], "signal": "BUY", "reason": f"{self.fast_period}日均线金叉{self.slow_period}日均线"})
                elif prev_fast > prev_slow and ma_fast[i] < ma_slow[i]:
                    signals.append({**prices[i], "signal": "SELL", "reason": f"{self.fast_period}日均线死叉{self.slow_period}日均线"})
        return signals

    def _macd_signals(self, prices: List[Dict], close: List[float]) -> List[Dict]:
        signals = []
        dif, dea, macd = self._macd(close)
        for i in range(len(prices)):
            if dif[i] is None or dea[i] is None:
                continue
            if dif[i - 1] is not None and dif[i - 1] < dea[i - 1] and dif[i] > dea[i]:
                signals.append({**prices[i], "signal": "BUY", "reason": "MACD金叉（DIF上穿DEA）"})
            elif dif[i - 1] is not None and dif[i - 1] > dea[i - 1] and dif[i] < dea[i]:
                signals.append({**prices[i], "signal": "SELL", "reason": "MACD死叉（DIF下穿DEA）"})
        return signals

    def _rsi_signals(self, prices: List[Dict], close: List[float]) -> List[Dict]:
        signals = []
        rsi = self._rsi(close, 14)
        for i in range(len(prices)):
            if rsi[i] is None:
                continue
            if rsi[i - 1] is not None and rsi[i - 1] < 30 <= rsi[i]:
                signals.append({**prices[i], "signal": "BUY", "reason": f"RSI超卖区间（RSI={rsi[i]}）"})
            elif rsi[i - 1] is not None and rsi[i - 1] > 70 >= rsi[i]:
                signals.append({**prices[i], "signal": "SELL", "reason": f"RSI超买区间（RSI={rsi[i]}）"})
        return signals

    def _bollinger_signals(self, prices: List[Dict], close: List[float]) -> List[Dict]:
        signals = []
        mid, upper, lower = self._bollinger_bands(close, 20, 2.0)
        for i in range(len(prices)):
            if upper[i] is None or lower[i] is None:
                continue
            if close[i] <= lower[i]:
                signals.append({**prices[i], "signal": "BUY", "reason": f"价格触及布林下轨（close={close[i]}, lower={lower[i]}）"})
            elif close[i] >= upper[i]:
                signals.append({**prices[i], "signal": "SELL", "reason": f"价格触及布林上轨（close={close[i]}, upper={upper[i]}）"})
        return signals

    def _momentum_signals(self, prices: List[Dict], close: List[float]) -> List[Dict]:
        signals = []
        mom = self._sma(close, 5)  # 短期动量
        for i in range(10, len(prices)):
            if mom[i] is None or mom[i - 1] is None:
                continue
            # 动量转正买入，动量转负卖出
            if mom[i - 1] <= 0 and mom[i] > 0:
                signals.append({**prices[i], "signal": "BUY", "reason": "动量由负转正"})
            elif mom[i - 1] >= 0 and mom[i] < 0:
                signals.append({**prices[i], "signal": "SELL", "reason": "动量由正转负"})
        return signals

    def _value_signals(self, prices: List[Dict], close: List[float]) -> List[Dict]:
        signals = []
        # 价值投资：PE低于历史均值买入，高于均值卖出
        pe_series = [random.uniform(8, 15) for _ in close]  # 模拟PE
        for i in range(20, len(prices)):
            if i < len(pe_series) - 1:
                avg_pe = sum(pe_series[:i]) / i
                if pe_series[i] < avg_pe * 0.9:
                    signals.append({**prices[i], "signal": "BUY", "reason": f"价值低估（PE={pe_series[i]:.1f} < 均值{avg_pe:.1f}）"})
                elif pe_series[i] > avg_pe * 1.1:
                    signals.append({**prices[i], "signal": "SELL", "reason": f"价值高估（PE={pe_series[i]:.1f} > 均值{avg_pe:.1f}）"})
        return signals

    # ─────────────────────────────────────────────────────────
    # 回测模拟
    # ─────────────────────────────────────────────────────────

    def _run_backtest(self, prices: List[Dict], signals: List[Dict]) -> Dict[str, Any]:
        """执行回测模拟"""
        cash = self.initial_capital
        position = 0  # 持仓股数
        equity = []   # 每日权益
        trades = []   # 交易记录

        signal_map = {(s["date"], s["signal"]): s for s in signals}
        current_prices = {p["date"]: p["close"] for p in prices}

        for i, bar in enumerate(prices):
            date = bar["date"]
            close = bar["close"]

            # 当日权益
            equity.append({
                "date": date,
                "cash": round(cash, 2),
                "position_value": round(position * close, 2),
                "total": round(cash + position * close, 2),
            })

            key = (date, "BUY")
            if key in signal_map and cash > 0:
                buy_price = signal_map[key]["close"]
                shares = math.floor(cash / buy_price)
                if shares > 0:
                    cost = shares * buy_price
                    cash -= cost
                    position += shares
                    trades.append({
                        "date": date,
                        "action": "BUY",
                        "price": buy_price,
                        "shares": shares,
                        "amount": round(cost, 2),
                    })

            key = (date, "SELL")
            if key in signal_map and position > 0:
                sell_price = signal_map[key]["close"]
                proceeds = position * sell_price
                cash += proceeds
                trades.append({
                    "date": date,
                    "action": "SELL",
                    "price": sell_price,
                    "shares": position,
                    "amount": round(proceeds, 2),
                })
                position = 0

        # 最后一日平仓
        if position > 0 and equity:
            last_close = prices[-1]["close"]
            cash += position * last_close
            trades.append({
                "date": prices[-1]["date"],
                "action": "SELL",
                "price": last_close,
                "shares": position,
                "amount": round(position * last_close, 2),
            })
            position = 0

        return {"equity": equity, "trades": trades}

    # ─────────────────────────────────────────────────────────
    # 绩效指标计算
    # ─────────────────────────────────────────────────────────

    def _compute_metrics(self, equity: List[Dict]) -> Dict[str, Any]:
        """计算绩效指标"""
        if not equity:
            return {}

        total_values = [e["total"] for e in equity]
        initial = total_values[0]
        final = total_values[-1]

        # 总收益率
        total_return = (final - initial) / initial

        # 年化收益率（假设252交易日）
        n_days = len(equity)
        n_years = n_days / 252
        annual_return = (final / initial) ** (1 / n_years) - 1 if n_years > 0 else 0

        # 最大回撤
        peak = initial
        max_drawdown = 0.0
        max_drawdown_pct = 0.0
        for tv in total_values:
            if tv > peak:
                peak = tv
            dd = (peak - tv) / peak
            if dd > max_drawdown_pct:
                max_drawdown_pct = dd
                max_drawdown = peak - tv

        # 卡尔玛比率 = 年化收益 / 最大回撤
        calmar_ratio = annual_return / max_drawdown_pct if max_drawdown_pct > 0 else 0

        # 日收益率序列
        daily_returns = []
        for i in range(1, len(total_values)):
            dr = (total_values[i] - total_values[i - 1]) / total_values[i - 1]
            daily_returns.append(dr)

        # 夏普比率
        if daily_returns:
            mean_dr = sum(daily_returns) / len(daily_returns)
            std_dr = math.sqrt(sum((r - mean_dr) ** 2 for r in daily_returns) / len(daily_returns))
            sharpe_ratio = (mean_dr / std_dr) * math.sqrt(252) if std_dr > 0 else 0
        else:
            sharpe_ratio = 0

        # 月度收益统计
        monthly = {}
        for e in equity:
            y, m, _ = e["date"].split("-")
            key = f"{y}-{m}"
            if key not in monthly:
                monthly[key] = []
            monthly[key].append(e["total"])

        monthly_returns = {}
        sorted_months = sorted(monthly.keys())
        for i, month in enumerate(sorted_months):
            if i == 0:
                continue
            prev_month = sorted_months[i - 1]
            if monthly[prev_month] and monthly[month]:
                ret = (monthly[month][-1] - monthly[prev_month][-1]) / monthly[prev_month][-1]
                monthly_returns[month] = round(ret * 100, 2)

        # 收益率曲线描述
        equity_curve = "震荡上行"
        if total_return > 0.3:
            equity_curve = "强势上涨"
        elif total_return > 0.1:
            equity_curve = "温和上涨"
        elif total_return > 0:
            equity_curve = "小幅盈利"
        elif total_return > -0.1:
            equity_curve = "小幅亏损"
        elif total_return > -0.3:
            equity_curve = "明显回撤"
        else:
            equity_curve = "大幅亏损"

        return {
            "initial_capital": initial,
            "final_capital": round(final, 2),
            "total_return": round(total_return * 100, 2),
            "annual_return": round(annual_return * 100, 2),
            "max_drawdown": round(max_drawdown, 2),
            "max_drawdown_pct": round(max_drawdown_pct * 100, 2),
            "sharpe_ratio": round(sharpe_ratio, 3),
            "calmar_ratio": round(calmar_ratio, 3),
            "equity_curve": equity_curve,
            "monthly_returns": monthly_returns,
        }

    def _compute_trade_metrics(self, trades: List[Dict]) -> Dict[str, Any]:
        """计算交易统计"""
        if not trades:
            return {"win_rate": 0, "profit_loss_ratio": 0, "total_trades": 0}

        buy_trades = []
        sell_trades = []
        for t in trades:
            if t["action"] == "BUY":
                buy_trades.append(t)
            else:
                sell_trades.append(t)

        wins = []
        losses = []
        i = 0
        for buy in buy_trades:
            # 找下一个对应卖出
            for j in range(i, len(sell_trades)):
                if sell_trades[j]["shares"] == buy["shares"]:
                    pnl = (sell_trades[j]["price"] - buy["price"]) * buy["shares"]
                    if pnl > 0:
                        wins.append(pnl)
                    else:
                        losses.append(abs(pnl))
                    i = j + 1
                    break

        total_wins = sum(wins)
        total_losses = sum(losses) if losses else 0.001
        avg_win = total_wins / len(wins) if wins else 0
        avg_loss = total_losses / len(losses) if losses else 0.001

        return {
            "total_trades": len(trades) // 2,
            "win_trades": len(wins),
            "loss_trades": len(losses),
            "win_rate": round(len(wins) / (len(wins) + len(losses)) * 100, 2) if (wins or losses) else 0,
            "profit_loss_ratio": round(avg_win / avg_loss, 3) if avg_loss > 0 else 0,
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
        }

    # ─────────────────────────────────────────────────────────
    # 主入口
    # ─────────────────────────────────────────────────────────

    def run(self) -> Dict[str, Any]:
        """执行完整回测，返回报告"""
        prices = self._generate_price_data()
        signals = self._generate_signals(prices)
        result = self._run_backtest(prices, signals)

        metrics = self._compute_metrics(result["equity"])
        trade_metrics = self._compute_trade_metrics(result["trades"])

        # 买卖信号示例（最多5条）
        signal_examples = [
            {
                "date": s["date"],
                "signal": s["signal"],
                "close": s["close"],
                "reason": s["reason"],
            }
            for s in signals[:10]
        ]

        return {
            "strategy": self.strategy,
            "symbol": self.symbol,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "initial_capital": self.initial_capital,
            "price_count": len(prices),
            "signal_count": len(signals),
            "equity_curve": metrics.get("equity_curve", "N/A"),
            "metrics": {
                "annual_return": metrics.get("annual_return", 0),
                "sharpe_ratio": metrics.get("sharpe_ratio", 0),
                "max_drawdown_pct": metrics.get("max_drawdown_pct", 0),
                "win_rate": trade_metrics.get("win_rate", 0),
                "profit_loss_ratio": trade_metrics.get("profit_loss_ratio", 0),
                "calmar_ratio": metrics.get("calmar_ratio", 0),
                "total_return": metrics.get("total_return", 0),
            },
            "monthly_returns": metrics.get("monthly_returns", {}),
            "trade_signals": signal_examples,
            "trades": result["trades"],
            "equity_timeline": result["equity"],
        }

    def summary(self) -> str:
        """生成文本格式的回测摘要"""
        report = self.run()
        m = report["metrics"]

        lines = [
            f"═══ 回测报告 ═══",
            f"策略：{report['strategy']}",
            f"标的：{report['symbol']}",
            f"回测期：{report['start_date']} → {report['end_date']}",
            f"初始资金：¥{report['initial_capital']:,.0f}",
            f"数据天数：{report['price_count']}天 | 信号数：{report['signal_count']}次",
            f"",
            f"── 收益率曲线：{report['equity_curve']}",
            f"",
            f"── 关键指标",
            f"  年化收益率：{m['annual_return']:+.2f}%",
            f"  夏普比率：{m['sharpe_ratio']:.3f}",
            f"  最大回撤：{m['max_drawdown_pct']:.2f}%",
            f"  卡尔玛比率：{m['calmar_ratio']:.3f}",
            f"  胜率：{m['win_rate']:.2f}%",
            f"  盈亏比：{m['profit_loss_ratio']:.3f}",
            f"",
            f"── 月度收益",
        ]

        for month, ret in sorted(report["monthly_returns"].items()):
            sign = "+" if ret >= 0 else ""
            lines.append(f"  {month}: {sign}{ret:.2f}%")

        lines.append(f"")
        lines.append(f"── 买卖信号示例（前10条）")
        for s in report["trade_signals"][:5]:
            emoji = "🟢" if s["signal"] == "BUY" else "🔴"
            lines.append(f"  {emoji} {s['date']} {s['signal']} @ {s['close']} | {s['reason']}")

        return "\n".join(lines)


def parse_strategy_from_text(text: str) -> Tuple[str, int, int]:
    """从自然语言描述解析策略参数"""
    text_lower = text.lower()

    if "均线交叉" in text or "均线" in text or "ma_cross" in text_lower:
        strategy = "ma_cross"
        # 尝试提取周期
        import re
        nums = re.findall(r"\d+", text)
        fast = int(nums[0]) if len(nums) >= 1 else 20
        slow = int(nums[1]) if len(nums) >= 2 else 60
        return strategy, fast, slow
    elif "macd" in text_lower:
        return "macd", 12, 26
    elif "rsi" in text_lower:
        return "rsi", 14, 14
    elif "布林" in text:
        return "bollinger", 20, 20
    elif "动量" in text:
        return "momentum", 5, 5
    elif "价值" in text or "value" in text_lower:
        return "value", 20, 60
    else:
        return "ma_cross", 20, 60


def parse_date_range(text: str) -> Tuple[str, str]:
    """从文本解析日期范围"""
    import re
    years = re.findall(r"20\d{2}", text)
    if len(years) >= 2:
        return f"{years[0]}-01-01", f"{years[1]}-12-31"
    elif len(years) == 1:
        return f"{years[0]}-01-01", f"{years[0]}-12-31"
    return "2024-01-01", "2024-12-31"


def parse_symbol(text: str) -> str:
    """从文本解析标的代码"""
    if "上证" in text or "沪" in text:
        return "XXXXXX.SH"
    elif "深证" in text or "深" in text:
        return "399001.SZ"
    elif "创业板" in text:
        return "399006.SZ"
    elif "科创" in text:
        return "000688.SH"
    return "XXXXXX.SH"
