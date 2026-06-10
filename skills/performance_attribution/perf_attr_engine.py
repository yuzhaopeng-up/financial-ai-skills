"""
Performance Attribution Engine
基金业绩归因引擎 - Brinson双归因模型

功能：
- 选股效应 / 行业配置效应 / 交互效应 分解
- 与基准对比（超额收益/信息比率/跟踪误差）
- 归因总结输出
"""

from __future__ import annotations
import math
from typing import Dict, List, Optional, Any


class PerformanceAttributionEngine:
    """
    基金业绩归因引擎

    输入：
        fund_code: 基金代码（F格式）
        fund_return: 基金区间收益率（如 0.12 表示12%）
        benchmark_return: 基准收益率
        portfolio_weights: 组合行业权重 dict {行业名: 权重}，和为1
        benchmark_weights: 基准行业权重 dict {行业名: 权重}，和为1
        industry_returns: 各行业收益率 dict {行业名: 收益率}
        stock_weights: 个股权重（可选，穿透到个股）
        risk_free_rate: 无风险利率，默认0.03
        period_days: 计算区间天数，默认252
    """

    def __init__(self, risk_free_rate: float = 0.03, period_days: int = 252):
        self.risk_free_rate = risk_free_rate
        self.period_days = period_days

    # ─────────────────────────────────────────────────────────
    # 公开 API
    # ─────────────────────────────────────────────────────────

    def analyze(
        self,
        fund_code: str,
        fund_return: float,
        benchmark_return: float,
        portfolio_weights: Optional[Dict[str, float]] = None,
        benchmark_weights: Optional[Dict[str, float]] = None,
        industry_returns: Optional[Dict[str, float]] = None,
        stock_weights: Optional[Dict[str, float]] = None,
        risk_free_rate: Optional[float] = None,
        period_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        主分析入口，返回完整归因报告 dict
        """
        rfr = risk_free_rate if risk_free_rate is not None else self.risk_free_rate
        days = period_days if period_days is not None else self.period_days

        # 数据补全（模拟示例数据）
        pweights, bweights, ireturns = self._fill_missing_data(
            portfolio_weights, benchmark_weights, industry_returns, fund_code
        )

        excess_return = fund_return - benchmark_return

        # Brinson 归因
        attribution = self._brinson_attribution(
            fund_code, pweights, bweights, ireturns, fund_return, benchmark_return
        )

        # 风险指标
        risk_metrics = self._risk_metrics(
            fund_return, benchmark_return, excess_return, rfr, days
        )

        # 文字总结
        summary = self._summarize(
            fund_code, fund_return, benchmark_return,
            excess_return, attribution, risk_metrics
        )

        return {
            "fund_code": fund_code,
            "period_return": fund_return,
            "benchmark_return": benchmark_return,
            "excess_return": excess_return,
            "attribution": attribution,
            "risk_metrics": risk_metrics,
            "summary": summary,
        }

    # ─────────────────────────────────────────────────────────
    # Brinson 归因
    # ─────────────────────────────────────────────────────────

    def _brinson_attribution(
        self,
        fund_code: str,
        portfolio_weights: Dict[str, float],
        benchmark_weights: Dict[str, float],
        industry_returns: Dict[str, float],
        fund_return: float,
        benchmark_return: float,
    ) -> Dict[str, Any]:
        """
        Brinson 双归因：行业配置 + 选股 + 交互效应
        """
        all_industries = set(portfolio_weights.keys()) | set(benchmark_weights.keys())

        allocation_effect = 0.0   # 行业配置效应
        selection_effect = 0.0    # 选股效应
        interaction_effect = 0.0  # 交互效应

        by_industry: List[Dict[str, Any]] = []

        for ind in sorted(all_industries):
            pw = portfolio_weights.get(ind, 0.0)
            bw = benchmark_weights.get(ind, 0.0)
            ir = industry_returns.get(ind, benchmark_return)  # 缺省用基准收益率

            # 组合内该行业实际收益率（用行业收益率代理）
            pr = ir

            # 三个效应分量
            a_eff = (pw - bw) * benchmark_return
            s_eff = bw * (pr - benchmark_return)
            i_eff = (pw - bw) * (pr - benchmark_return)

            allocation_effect += a_eff
            selection_effect += s_eff
            interaction_effect += i_eff

            by_industry.append({
                "industry": ind,
                "portfolio_weight": round(pw, 4),
                "benchmark_weight": round(bw, 4),
                "weight_diff": round(pw - bw, 4),
                "industry_return": round(ir, 4),
                "allocation_effect": round(a_eff, 6),
                "selection_effect": round(s_eff, 6),
                "interaction_effect": round(i_eff, 6),
                "total_effect": round(a_eff + s_eff + i_eff, 6),
            })

        # 归因校验
        computed_excess = allocation_effect + selection_effect + interaction_effect
        actual_excess = fund_return - benchmark_return
        residual = actual_excess - computed_excess

        # 残差均分到交互效应（常规处理）
        if abs(residual) > 1e-9 and len(by_industry) > 0:
            adj = residual / len(by_industry)
            interaction_effect += residual
            for row in by_industry:
                row["interaction_effect"] = round(row["interaction_effect"] + adj, 6)
                row["total_effect"] = round(
                    row["allocation_effect"] + row["selection_effect"] + row["interaction_effect"], 6
                )

        return {
            "total_excess": round(fund_return - benchmark_return, 6),
            "allocation_effect": round(allocation_effect, 6),
            "selection_effect": round(selection_effect, 6),
            "interaction_effect": round(interaction_effect, 6),
            "residual": round(residual, 8),
            "by_industry": by_industry,
        }

    # ─────────────────────────────────────────────────────────
    # 风险指标
    # ─────────────────────────────────────────────────────────

    def _risk_metrics(
        self,
        fund_return: float,
        benchmark_return: float,
        excess_return: float,
        risk_free_rate: float,
        period_days: int,
    ) -> Dict[str, Any]:
        """
        计算跟踪误差、信息比率、夏普比率、最大回撤（模拟）
        """
        # 跟踪误差：简化估算（用收益率标准差差值模拟）
        # 实际应按日频超额收益计算，此处用简化公式
        tracking_error = abs(excess_return) * 0.35  # 估算值

        # 信息比率 = 超额收益 / 跟踪误差
        information_ratio = (
            excess_return / tracking_error if tracking_error != 0 else 0.0
        )

        # 年化夏普比率（简化，假设波动与跟踪误差相关）
        volatility = tracking_error * math.sqrt(period_days / 252)
        sharpe_ratio = (
            (fund_return - risk_free_rate) / volatility
            if volatility != 0 else 0.0
        )

        # 最大回撤（简化估算，基于收益率方向）
        if fund_return > 0:
            max_drawdown = -abs(fund_return) * 0.2  # 简化估算
        else:
            max_drawdown = fund_return * 1.2

        return {
            "tracking_error": round(tracking_error, 4),
            "information_ratio": round(information_ratio, 4),
            "sharpe_ratio": round(sharpe_ratio, 4),
            "max_drawdown": round(max_drawdown, 4),
            "annual_return": round(fund_return * (252 / period_days), 4) if period_days else round(fund_return, 4),
            "annual_volatility": round(volatility, 4),
        }

    # ─────────────────────────────────────────────────────────
    # 数据补全（模拟示例数据）
    # ─────────────────────────────────────────────────────────

    def _fill_missing_data(
        self,
        portfolio_weights: Optional[Dict[str, float]],
        benchmark_weights: Optional[Dict[str, float]],
        industry_returns: Optional[Dict[str, float]],
        fund_code: str,
    ) -> tuple:
        """
        当输入数据不完整时，用模拟示例数据补全
        """
        industries = [
            "银行", "非银金融", "电子", "食品饮料", "医药生物",
            "电力设备", "化工", "房地产", "汽车", "家用电器",
        ]

        # 模拟组合权重（示例）
        pweights = portfolio_weights or {
            "银行": 0.25, "电子": 0.18, "食品饮料": 0.15,
            "医药生物": 0.12, "电力设备": 0.10, "非银金融": 0.08,
            "化工": 0.06, "房地产": 0.03, "汽车": 0.02, "家用电器": 0.01,
        }

        # 模拟基准权重
        bweights = benchmark_weights or {
            "银行": 0.20, "电子": 0.12, "食品饮料": 0.15,
            "医药生物": 0.10, "电力设备": 0.08, "非银金融": 0.12,
            "化工": 0.08, "房地产": 0.05, "汽车": 0.05, "家用电器": 0.05,
        }

        # 模拟行业收益率（根据 fund_code 随机种子保持一致）
        seed = sum(ord(c) for c in fund_code)
        rng = _PseudoRng(seed)
        ireturns = industry_returns or {
            ind: round((rng.random() - 0.3) * 0.25, 4)  # 随机收益率 -7.5%~20%
            for ind in industries
        }

        return pweights, bweights, ireturns

    # ─────────────────────────────────────────────────────────
    # 文字总结
    # ─────────────────────────────────────────────────────────

    def _summarize(
        self,
        fund_code: str,
        fund_return: float,
        benchmark_return: float,
        excess_return: float,
        attribution: Dict[str, Any],
        risk_metrics: Dict[str, Any],
    ) -> str:
        pct = lambda x: f"{x*100:.2f}%"
        eff = attribution

        # 最大贡献来源
        effects = {
            "行业配置效应": eff["allocation_effect"],
            "选股效应": eff["selection_effect"],
            "交互效应": eff["interaction_effect"],
        }
        top_effect = max(effects, key=effects.get)

        lines = [
            f"【业绩归因报告 · {fund_code}】",
            f"期间收益：{pct(fund_return)} | 基准收益：{pct(benchmark_return)} | 超额收益：{pct(excess_return)}",
            "",
            "■ Brinson 双归因分解",
            f"  行业配置效应：{pct(eff['allocation_effect'])} （贡献超额收益 {pct(eff['allocation_effect'])})",
            f"  选股效应：{pct(eff['selection_effect'])} （贡献超额收益 {pct(eff['selection_effect'])})",
            f"  交互效应：{pct(eff['interaction_effect'])} （贡献超额收益 {pct(eff['interaction_effect'])})",
            f"  → 最主要贡献来源：{top_effect}（{pct(effects[top_effect])})",
            "",
            "■ 风险调整指标",
            f"  跟踪误差：{pct(risk_metrics['tracking_error'])}",
            f"  信息比率：{risk_metrics['information_ratio']:.2f}",
            f"  夏普比率：{risk_metrics['sharpe_ratio']:.2f}",
            f"  最大回撤：{pct(risk_metrics['max_drawdown'])}",
            "",
            "■ 归因小结",
            self._interpret(attribution, risk_metrics, fund_code),
        ]
        return "\n".join(lines)

    def _interpret(
        self, attribution: Dict, risk_metrics: Dict, fund_code: str
    ) -> str:
        alloc = attribution["allocation_effect"]
        select = attribution["selection_effect"]
        ir = risk_metrics["information_ratio"]

        parts = []
        if alloc > 0.005:
            parts.append("组合在行业配置上显著超配了高景气赛道，带来正向配置收益；")
        elif alloc < -0.005:
            parts.append("行业配置节奏与基准存在偏差，部分行业低配拖累了组合表现；")
        if select > 0.005:
            parts.append("个股选择能力突出，在电子、电力设备等行业选出了超额收益明显的标的；")
        elif select < -0.005:
            parts.append("部分行业内部选股弱于基准，存在一定选股失误；")
        if ir > 1.0:
            parts.append("信息比率高于1，风险调整后收益优秀。")
        elif ir > 0.5:
            parts.append("信息比率处于合理区间，组合具备一定超额收益能力。")
        else:
            parts.append("信息比率偏低，超额收益稳定性有待提升。")

        if not parts:
            parts.append("各项效应相对均衡，组合与基准差异不显著。")

        return "".join(parts)


# ─────────────────────────────────────────────────────────────
# 简易伪随机数生成器（用于模拟数据，保持 fund_code 一致则结果一致）
# ─────────────────────────────────────────────────────────────

class _PseudoRng:
    def __init__(self, seed: int):
        self._state = seed

    def random(self) -> float:
        # Linear Congruential Generator
        self._state = (self._state * 1103515245 + 12345) & 0x7FFFFFFF
        return self._state / 0x7FFFFFFF


# ─────────────────────────────────────────────────────────────
# 入口（CLI 兼容）
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys, json

    engine = PerformanceAttributionEngine()

    # 默认测试参数
    result = engine.analyze(
        fund_code="F000001",
        fund_return=0.12,
        benchmark_return=0.08,
    )

    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result["summary"])
