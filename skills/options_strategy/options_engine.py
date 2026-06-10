"""
期权策略分析引擎
基于 Black-Scholes 框架计算希腊值和多情景损益分析
"""

import math
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

# ─────────────────────────────────────────
# 尝试导入科学计算库
# ─────────────────────────────────────────
try:
    from scipy.stats import norm
except ImportError:
    # fallback: 使用近似公式
    norm = None

# ─────────────────────────────────────────
# 数据结构
# ─────────────────────────────────────────

class StrategyType(Enum):
    BUY_CALL = "买入认购"
    BUY_PUT = "买入认沽"
    BULL_CALL_SPREAD = "牛市价差"
    BEAR_PUT_SPREAD = "熊市价差"
    STRADDLE = "跨式组合"
    STRANGLE = "宽跨式组合"

@dataclass
class Greeks:
    """希腊值"""
    delta: float      #标的价格变化对期权价值的影响
    gamma: float      #Delta变化率
    vega: float       #波动率变化影响
    theta: float      #时间衰减
    rho: float        #利率影响

@dataclass
class ScenarioResult:
    """单情景分析结果"""
    scenario: str          # 情景描述
    spot_change_pct: float # 标的价格变化%
    final_spot: float      # 到期标的价格
    payoff: float          # 期权 payoff（扣除权利金前）
    net_pnl: float         # 净损益（扣除权利金后）
    roi: float             # 收益率%

@dataclass
class StrategyAnalysis:
    """完整策略分析结果"""
    strategy_type: str
    spot_price: float
    strike_prices: List[float]
    premium: float
    days_to_expiry: int
    volatility: float
    risk_free_rate: float
    greeks: Greeks
    scenarios: List[ScenarioResult]
    max_profit: Optional[float]
    max_loss: Optional[float]
    breakeven_points: List[float]
    适用场景: str
    策略特点: str
    注意事项: str

# ─────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────

def _norm_cdf(x: float) -> float:
    """标准正态分布 CDF"""
    if norm is not None:
        return norm.cdf(x)
    # 近似：Abramowitz and Stegun formula
    a1 = 0.2316419
    a2 = -0.358209
    a3 = -0.022782
    a4 = 0.000152
    a5 = 0.000152
    k = 1.0 / (1.0 + a1 * abs(x))
    poly = k * (a2 + k * (a3 + k * (a4 + k * a5)))
    m = math.exp(-x * x / 2) / math.sqrt(2 * math.pi)
    if x >= 0:
        return 1.0 - m * poly
    else:
        return m * poly

def _norm_pdf(x: float) -> float:
    """标准正态分布 PDF"""
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)

def _bs_d1_d2(S: float, K: float, T: float, r: float, sigma: float) -> Tuple[float, float]:
    """计算 d1 和 d2"""
    if T <= 0 or sigma <= 0:
        return 0.0, 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return d1, d2

def _bs_call_price(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Black-Scholes 认购期权价格"""
    if T <= 0:
        return max(0, S - K)
    d1, d2 = _bs_d1_d2(S, K, T, r, sigma)
    return S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)

def _bs_put_price(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Black-Scholes 认沽期权价格"""
    if T <= 0:
        return max(0, K - S)
    d1, d2 = _bs_d1_d2(S, K, T, r, sigma)
    return K * math.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)

def _bs_call_greeks(S: float, K: float, T: float, r: float, sigma: float) -> Greeks:
    """认购期权希腊值"""
    if T <= 0 or sigma <= 0:
        spot = S - K
        return Greeks(
            delta=1.0 if spot > 0 else 0.0,
            gamma=0.0, vega=0.0,
            theta=max(0, spot) / max(T, 1e-6),
            rho=0.0
        )
    d1, d2 = _bs_d1_d2(S, K, T, r, sigma)
    delta = _norm_cdf(d1)
    gamma = _norm_pdf(d1) / (S * sigma * math.sqrt(T))
    vega = S * _norm_pdf(d1) * math.sqrt(T) / 100  # 每1%波动率
    theta = (-S * _norm_pdf(d1) * sigma / (2 * math.sqrt(T))
             - r * K * math.exp(-r * T) * _norm_cdf(d2)) / 365
    rho = K * T * math.exp(-r * T) * _norm_cdf(d2) / 100
    return Greeks(delta=delta, gamma=gamma, vega=vega, theta=theta, rho=rho)

def _bs_put_greeks(S: float, K: float, T: float, r: float, sigma: float) -> Greeks:
    """认沽期权希腊值"""
    if T <= 0 or sigma <= 0:
        spot = K - S
        return Greeks(
            delta=-1.0 if spot > 0 else 0.0,
            gamma=0.0, vega=0.0,
            theta=max(0, spot) / max(T, 1e-6),
            rho=0.0
        )
    d1, d2 = _bs_d1_d2(S, K, T, r, sigma)
    delta = _norm_cdf(d1) - 1
    gamma = _norm_pdf(d1) / (S * sigma * math.sqrt(T))
    vega = S * _norm_pdf(d1) * math.sqrt(T) / 100
    theta = (-S * _norm_pdf(d1) * sigma / (2 * math.sqrt(T))
             + r * K * math.exp(-r * T) * _norm_cdf(-d2)) / 365
    rho = -K * T * math.exp(-r * T) * _norm_cdf(-d2) / 100
    return Greeks(delta=delta, gamma=gamma, vega=vega, theta=theta, rho=rho)

# ─────────────────────────────────────────
# 情景分析
# ─────────────────────────────────────────

SCENARIO_CHANGES = [+0.20, +0.10, +0.05, -0.05, -0.10, -0.20]
SCENARIO_LABELS  = ["标的+20%", "标的+10%", "标的+5%", "标的-5%", "标的-10%", "标的-20%"]

def _build_scenarios(
    payoff_fn,
    premium: float,
    spot: float,
) -> List[ScenarioResult]:
    results = []
    for pct, label in zip(SCENARIO_CHANGES, SCENARIO_LABELS):
        final_spot = round(spot * (1 + pct), 4)
        payoff = payoff_fn(final_spot)
        net = payoff - premium
        roi = net / premium * 100 if premium != 0 else 0
        results.append(ScenarioResult(
            scenario=label,
            spot_change_pct=round(pct * 100, 2),
            final_spot=final_spot,
            payoff=round(payoff, 4),
            net_pnl=round(net, 4),
            roi=round(roi, 2),
        ))
    return results

# ─────────────────────────────────────────
# 策略分析实现
# ─────────────────────────────────────────

def _analyze_buy_call(
    spot: float, strike: float, premium: float,
    T: float, r: float, sigma: float,
) -> StrategyAnalysis:
    """买入认购"""
    greeks = _bs_call_greeks(spot, strike, T, r, sigma)
    max_profit = float('inf')
    max_loss = -premium

    def payoff(s):
        return max(0, s - strike)

    scenarios = _build_scenarios(payoff, premium, spot)
    breakeven = [round(strike + premium, 4)]

    return StrategyAnalysis(
        strategy_type="买入认购 (Buy Call)",
        spot_price=spot, strike_prices=[strike],
        premium=premium,
        days_to_expiry=int(T * 365),
        volatility=sigma, risk_free_rate=r,
        greeks=greeks, scenarios=scenarios,
        max_profit=max_profit, max_loss=round(max_loss, 4),
        breakeven_points=breakeven,
        适用场景="强烈看涨后市，预期标的大幅上涨；适合作为杠杆性投资工具",
        策略特点="损失有限（仅权利金），收益无限；Delta 高，Gamma 中等",
        注意事项="需要标的涨幅超过权利金成本才能盈利；Theta 为负，每天时间价值衰减"
    )

def _analyze_buy_put(
    spot: float, strike: float, premium: float,
    T: float, r: float, sigma: float,
) -> StrategyAnalysis:
    """买入认沽"""
    greeks = _bs_put_greeks(spot, strike, T, r, sigma)
    max_profit = strike - premium  # 标的价格跌到0时最大
    max_loss = -premium

    def payoff(s):
        return max(0, strike - s)

    scenarios = _build_scenarios(payoff, premium, spot)
    breakeven = [round(strike - premium, 4)]

    return StrategyAnalysis(
        strategy_type="买入认沽 (Buy Put)",
        spot_price=spot, strike_prices=[strike],
        premium=premium,
        days_to_expiry=int(T * 365),
        volatility=sigma, risk_free_rate=r,
        greeks=greeks, scenarios=scenarios,
        max_profit=round(max_profit, 4), max_loss=round(max_loss, 4),
        breakeven_points=breakeven,
        适用场景="看跌后市，用于套保或投机；适合作为组合保险",
        策略特点="损失有限（仅权利金），收益有限（最高 strike - premium）；Delta 负值，方向性明确",
        注意事项="需要标的跌幅超过权利金成本才能盈利；Theta 为负"
    )

def _analyze_bull_call_spread(
    spot: float, strike_low: float, strike_high: float, premium: float,
    T: float, r: float, sigma: float,
) -> StrategyAnalysis:
    """牛市价差（认购）"""
    # 买入低行权价认购，卖出高行权价认购
    c_low = _bs_call_price(spot, strike_low, T, r, sigma)
    c_high = _bs_call_price(spot, strike_high, T, r, sigma)
    net_premium = c_low - c_high  # 买入付权利金（正）
    # premium 为策略总权利金支出（可正可负）
    greeks_low = _bs_call_greeks(spot, strike_low, T, r, sigma)
    greeks_high = _bs_call_greeks(spot, strike_high, T, r, sigma)
    greeks = Greeks(
        delta=greeks_low.delta - greeks_high.delta,
        gamma=greeks_low.gamma - greeks_high.gamma,
        vega=greeks_low.vega - greeks_high.vega,
        theta=greeks_low.theta - greeks_high.theta,
        rho=greeks_low.rho - greeks_high.rho,
    )
    max_profit = (strike_high - strike_low) - premium
    max_loss = -premium

    def payoff(s):
        return max(0, s - strike_low) - max(0, s - strike_high)

    scenarios = _build_scenarios(payoff, premium, spot)
    breakeven = [round(strike_low + premium, 4)]

    return StrategyAnalysis(
        strategy_type="牛市价差 (Bull Call Spread)",
        spot_price=spot, strike_prices=[strike_low, strike_high],
        premium=premium,
        days_to_expiry=int(T * 365),
        volatility=sigma, risk_free_rate=r,
        greeks=greeks, scenarios=scenarios,
        max_profit=round(max_profit, 4), max_loss=round(max_loss, 4),
        breakeven_points=breakeven,
        适用场景="温和看涨，预期标的小幅上涨；降低纯买入认购的成本",
        策略特点="成本低于单腿买入认购，损失有限；收益有上限；Vega 敞口较小",
        注意事项="收益被行权价差限制；需要标的上涨到高行权价以上才能获得最大收益"
    )

def _analyze_bear_put_spread(
    spot: float, strike_high: float, strike_low: float, premium: float,
    T: float, r: float, sigma: float,
) -> StrategyAnalysis:
    """熊市价差（认沽）"""
    # 买入高行权价认沽，卖出低行权价认沽
    p_high = _bs_put_price(spot, strike_high, T, r, sigma)
    p_low = _bs_put_price(spot, strike_low, T, r, sigma)
    greeks_high = _bs_put_greeks(spot, strike_high, T, r, sigma)
    greeks_low = _bs_put_greeks(spot, strike_low, T, r, sigma)
    greeks = Greeks(
        delta=greeks_high.delta - greeks_low.delta,
        gamma=greeks_high.gamma - greeks_low.gamma,
        vega=greeks_high.vega - greeks_low.vega,
        theta=greeks_high.theta - greeks_low.theta,
        rho=greeks_high.rho - greeks_low.rho,
    )
    max_profit = (strike_high - strike_low) - premium
    max_loss = -premium

    def payoff(s):
        return max(0, strike_high - s) - max(0, strike_low - s)

    scenarios = _build_scenarios(payoff, premium, spot)
    breakeven = [round(strike_high - premium, 4)]

    return StrategyAnalysis(
        strategy_type="熊市价差 (Bear Put Spread)",
        spot_price=spot, strike_prices=[strike_high, strike_low],
        premium=premium,
        days_to_expiry=int(T * 365),
        volatility=sigma, risk_free_rate=r,
        greeks=greeks, scenarios=scenarios,
        max_profit=round(max_profit, 4), max_loss=round(max_loss, 4),
        breakeven_points=breakeven,
        适用场景="温和看跌，预期标的小幅下跌；降低纯买入认沽的成本",
        策略特点="成本低于单腿买入认沽，损失有限；收益有上限；Vega 敞口较小",
        注意事项="收益被行权价差限制；需要标的下跌到低行权价以下才能获得最大收益"
    )

def _analyze_straddle(
    spot: float, strike: float, premium: float,
    T: float, r: float, sigma: float,
) -> StrategyAnalysis:
    """跨式组合 (Straddle)"""
    c = _bs_call_price(spot, strike, T, r, sigma)
    p = _bs_put_price(spot, strike, T, r, sigma)
    total_premium = c + p  # 理论总权利金
    greeks_c = _bs_call_greeks(spot, strike, T, r, sigma)
    greeks_p = _bs_put_greeks(spot, strike, T, r, sigma)
    greeks = Greeks(
        delta=greeks_c.delta + greeks_p.delta,
        gamma=greeks_c.gamma + greeks_p.gamma,
        vega=greeks_c.vega + greeks_p.vega,
        theta=greeks_c.theta + greeks_p.theta,
        rho=greeks_c.rho + greeks_p.rho,
    )
    max_profit = float('inf')
    max_loss = -total_premium

    def payoff(s):
        return max(0, s - strike) + max(0, strike - s)

    scenarios = _build_scenarios(payoff, premium, spot)
    breakeven = [
        round(strike - total_premium, 4),
        round(strike + total_premium, 4),
    ]

    return StrategyAnalysis(
        strategy_type="跨式组合 (Straddle)",
        spot_price=spot, strike_prices=[strike],
        premium=premium,
        days_to_expiry=int(T * 365),
        volatility=sigma, risk_free_rate=r,
        greeks=greeks, scenarios=scenarios,
        max_profit=max_profit, max_loss=round(max_loss, 4),
        breakeven_points=breakeven,
        适用场景="预期标的价格将大幅波动，但方向不确定；适合重大事件前夕（如财报、联储会议）",
        策略特点="双向做多波动率；Gamma 和 Vega 敞口最大；无论涨跌均有盈利可能",
        注意事项="需要大幅波动才能盈利；Theta 每天加速衰减；成本较高（两个权利金）"
    )

def _analyze_strangle(
    spot: float, strike_call: float, strike_put: float, premium: float,
    T: float, r: float, sigma: float,
) -> StrategyAnalysis:
    """宽跨式组合 (Strangle)"""
    c = _bs_call_price(spot, strike_call, T, r, sigma)
    p = _bs_put_price(spot, strike_put, T, r, sigma)
    total_premium = c + p
    greeks_c = _bs_call_greeks(spot, strike_call, T, r, sigma)
    greeks_p = _bs_put_greeks(spot, strike_put, T, r, sigma)
    greeks = Greeks(
        delta=greeks_c.delta + greeks_p.delta,
        gamma=greeks_c.gamma + greeks_p.gamma,
        vega=greeks_c.vega + greeks_p.vega,
        theta=greeks_c.theta + greeks_p.theta,
        rho=greeks_c.rho + greeks_p.rho,
    )
    max_profit = float('inf')
    max_loss = -total_premium

    def payoff(s):
        return max(0, s - strike_call) + max(0, strike_put - s)

    scenarios = _build_scenarios(payoff, premium, spot)
    breakeven = [
        round(strike_put - total_premium, 4),
        round(strike_call + total_premium, 4),
    ]

    return StrategyAnalysis(
        strategy_type="宽跨式组合 (Strangle)",
        spot_price=spot, strike_prices=[strike_call, strike_put],
        premium=premium,
        days_to_expiry=int(T * 365),
        volatility=sigma, risk_free_rate=r,
        greeks=greeks, scenarios=scenarios,
        max_profit=max_profit, max_loss=round(max_loss, 4),
        breakeven_points=breakeven,
        适用场景="预期标的价格将大幅波动但方向不确定，但比 Straddle 成本更低（使用虚值期权）",
        策略特点="双向做多波动率，成本低于 Straddle；需要更大波动才能盈利",
        注意事项="需要比 Straddle 更大的波动才能盈利；Theta 同样每天衰减"
    )

# ─────────────────────────────────────────
# 主引擎类
# ─────────────────────────────────────────

class OptionsStrategyEngine:
    """
    期权策略分析引擎
    支持6种基础策略的希腊值计算和多情景损益分析
    """

    def __init__(self):
        self.strategy_map = {
            "买入认购": _analyze_buy_call,
            "买入认沽": _analyze_buy_put,
            "牛市价差": _analyze_bull_call_spread,
            "熊市价差": _analyze_bear_put_spread,
            "跨式组合": _analyze_straddle,
            "宽跨式组合": _analyze_strangle,
        }

    def analyze(
        self,
        strategy_type: str,
        spot_price: float,
        strike_price: Union[float, List[float], Tuple[float, float]],
        premium: float,
        days_to_expiry: int = 30,
        volatility: Union[float, int] = 0.25,
        risk_free_rate: float = 0.025,
    ) -> StrategyAnalysis:
        """
        分析期权策略

        Args:
            strategy_type: 策略类型
            spot_price: 标的资产当前价格
            strike_price: 行权价（单腿策略用float，牛市/熊市价差用[float, float]，宽跨式用[float, float]）
            premium: 权利金（总净权利金支出，正=支出，负=收入）
            days_to_expiry: 距离到期天数
            volatility: 波动率（年化，默认25%）
            risk_free_rate: 无风险利率（年化，默认2.5%）

        Returns:
            StrategyAnalysis: 完整分析结果
        """
        # 处理波动率（支持百分比或小数）
        sigma = volatility / 100 if volatility > 1 else float(volatility)
        T = days_to_expiry / 365.0
        r = risk_free_rate

        # 解析策略
        strategy_type_clean = strategy_type.strip()
        if strategy_type_clean not in self.strategy_map:
            raise ValueError(
                f"不支持的策略类型: {strategy_type_clean}。"
                f"支持: {list(self.strategy_map.keys())}"
            )

        # 处理行权价
        if isinstance(strike_price, (int, float)):
            strike_list = [float(strike_price)]
        elif len(strike_price) == 2:
            strike_list = list(strike_price)
        else:
            raise ValueError(f"行权价参数格式有误: {strike_price}")

        fn = self.strategy_map[strategy_type_clean]

        # 分策略调用
        if strategy_type_clean in ("牛市价差",):
            K_low, K_high = min(strike_list[0], strike_list[1]), max(strike_list[0], strike_list[1])
            return fn(spot=float(spot_price), strike_low=K_low, strike_high=K_high,
                      premium=float(premium), T=T, r=r, sigma=sigma)
        elif strategy_type_clean in ("熊市价差",):
            K_high, K_low = max(strike_list[0], strike_list[1]), min(strike_list[0], strike_list[1])
            return fn(spot=float(spot_price), strike_high=K_high, strike_low=K_low,
                      premium=float(premium), T=T, r=r, sigma=sigma)
        elif strategy_type_clean in ("宽跨式组合",):
            K_put = min(strike_list[0], strike_list[1])
            K_call = max(strike_list[0], strike_list[1])
            return fn(spot=float(spot_price), strike_put=K_put, strike_call=K_call,
                      premium=float(premium), T=T, r=r, sigma=sigma)
        else:
            return fn(spot=float(spot_price), strike=strike_list[0],
                      premium=float(premium), T=T, r=r, sigma=sigma)

    def format_report(self, result: StrategyAnalysis) -> str:
        """格式化文本报告"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"  期权策略分析报告 — {result.strategy_type}")
        lines.append("=" * 60)

        # 基本信息
        strikes_str = "/".join(str(k) for k in result.strike_prices)
        lines.append(f"\n【基本信息】")
        lines.append(f"  标的价格     : {result.spot_price}")
        lines.append(f"  行权价       : {strikes_str}")
        lines.append(f"  权利金       : {result.premium:.4f}")
        lines.append(f"  剩余天数     : {result.days_to_expiry} 天")
        lines.append(f"  波动率       : {result.volatility:.2%}")
        lines.append(f"  无风险利率   : {result.risk_free_rate:.2%}")

        # 希腊值
        g = result.greeks
        lines.append(f"\n【希腊值分析】")
        lines.append(f"  Delta (Δ)   : {g.delta:+.4f}  (标的价格每上涨1元，期权价格变化)")
        lines.append(f"  Gamma (Γ)   : {g.gamma:+.6f}  (Delta每变化1元的加速率)")
        lines.append(f"  Vega (ν)    : {g.vega:+.4f}   (波动率每升1%，期权价格变化)")
        lines.append(f"  Theta (Θ)   : {g.theta:+.4f}  (每日时间价值衰减)")
        lines.append(f"  Rho (ρ)     : {g.rho:+.4f}    (利率每升1%，期权价格变化)")

        # 策略特征
        lines.append(f"\n【策略特征】")
        max_profit_str = "无限" if result.max_profit is None or result.max_profit == float('inf') \
            else f"{result.max_profit:.4f}"
        lines.append(f"  最大收益     : {max_profit_str}")
        lines.append(f"  最大损失     : {result.max_loss:.4f}")
        be_str = ", ".join(f"{b:.4f}" for b in result.breakeven_points)
        lines.append(f"  盈亏平衡点   : {be_str}")
        lines.append(f"\n  适用场景     : {result.适用场景}")
        lines.append(f"  策略特点     : {result.策略特点}")
        lines.append(f"  注意事项     : {result.注意事项}")

        # 情景分析
        lines.append(f"\n【情景损益分析】")
        header = f"  {'情景':<10} {'到期价格':>10} {'Payoff':>10} {'净损益':>10} {'收益率':>8}"
        lines.append(header)
        lines.append("  " + "-" * 52)
        for s in result.scenarios:
            sign = "+" if s.net_pnl >= 0 else ""
            roi_sign = "+" if s.roi >= 0 else ""
            lines.append(
                f"  {s.scenario:<10} {s.final_spot:>10.4f} {s.payoff:>10.4f} "
                f"{sign}{s.net_pnl:>10.4f} {roi_sign}{s.roi:>7.2f}%"
            )
        lines.append("=" * 60)
        return "\n".join(lines)

    def parse_cli_input(self, text: str) -> Dict:
        """
        解析自然语言 CLI 输入
        支持格式如：期权策略 买入认购 标的50元 行权价52元 权利金2元 剩余30天
        """
        import re

        # 策略类型
        strategy_patterns = [
            "买入认购", "买入认沽", "牛市价差", "熊市价差",
            "跨式组合", "宽跨式组合", "Straddle", "Strangle"
        ]
        found_strategy = None
        for p in strategy_patterns:
            if p in text:
                found_strategy = p
                break
        if not found_strategy:
            for p in strategy_patterns:
                if p.lower() in text.lower():
                    found_strategy = p
                    break

        # 提取所有数字（按出现顺序）
        nums = re.findall(r"[-+]?\d*\.?\d+", text)

        # 辅助：从关键词附近的文本片段提取数字
        def extract_num_after(keyword: str, default=None) -> float | None:
            # 找到关键词所在位置，提取其后的数字
            pattern = keyword + r"[^0-9\-]*?([-+]?\d*\.?\d+)"
            m = re.search(pattern, text)
            if m:
                return float(m.group(1))
            return default

        spot = extract_num_after("标的")
        if spot is None:
            spot = extract_num_after("现货")
        if spot is None:
            spot = extract_num_after("当前价")

        strike = extract_num_after("行权价")
        if strike is None:
            strike = extract_num_after("执行价")

        premium = extract_num_after("权利金")
        if premium is None:
            premium = extract_num_after("保费")

        days = extract_num_after("剩余")
        if days is None:
            days = extract_num_after("距到期")
        if days is not None:
            days = int(days)

        vol = extract_num_after("波动率")
        if vol is None:
            # vol 可能直接写数字后跟%
            m = re.search(r"波动率[^0-9]*?([-+]?\d*\.?\d+)", text)
            if m:
                vol = float(m.group(1))

        # fallback: 按顺序分配数字
        if nums:
            num_idx = 0
            if spot is None and len(nums) > num_idx:
                spot = float(nums[num_idx]); num_idx += 1
            if strike is None and len(nums) > num_idx:
                strike = float(nums[num_idx]); num_idx += 1
            if premium is None and len(nums) > num_idx:
                premium = float(nums[num_idx]); num_idx += 1
            if days is None and len(nums) > num_idx:
                days = int(float(nums[num_idx])); num_idx += 1
            if vol is None and len(nums) > num_idx:
                vol = float(nums[num_idx])

        # 默认值
        if days is None:
            days = 30
        if vol is None:
            vol = 25

        return {
            "strategy": found_strategy,
            "spot": spot,
            "strike": strike,
            "premium": premium,
            "days": days,
            "vol": vol,
        }
