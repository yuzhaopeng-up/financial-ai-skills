"""
投资组合优化引擎 - 基于有效前沿理论（Efficient Frontier）
Portfolio Optimization Engine based on Markowitz Mean-Variance Model
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

try:
    from scipy.optimize import minimize
except ImportError:
    minimize = None


class RiskPreference(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class OptimizationGoal(Enum):
    REDUCE_RISK = "reduce_risk"
    ENHANCE_RETURN = "enhance_return"
    BALANCE = "balance"


@dataclass
class Asset:
    """单个资产定义"""
    name: str          # 资产名称
    category: str      # 类别：stock/bond/alternative/cash
    expected_return: float  # 预期年化收益率
    volatility: float  # 年化波动率
    max_weight: float = 1.0   # 最大权重
    min_weight: float = 0.0  # 最小权重

    @property
    def risk_adjusted_return(self) -> float:
        """风险调整收益（简化版夏普比率假设无风险利率为3%）"""
        rf = 0.03
        return (self.expected_return - rf) / self.volatility if self.volatility > 0 else 0


@dataclass
class PortfolioMetrics:
    """组合指标"""
    expected_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    var_95: float  # 95% VaR

    def to_dict(self) -> Dict:
        return {
            "expected_return": round(self.expected_return, 4),
            "volatility": round(self.volatility, 4),
            "sharpe_ratio": round(self.sharpe_ratio, 4),
            "max_drawdown": round(self.max_drawdown, 4),
            "var_95": round(self.var_95, 4)
        }


@dataclass
class AdjustmentItem:
    """调仓项"""
    action: str        # buy/sell/hold
    asset_name: str
    current_weight: float
    target_weight: float
    weight_change: float
    priority: int      # 1=最高优先级
    reason: str

    def to_dict(self) -> Dict:
        return {
            "action": self.action,
            "asset": self.asset_name,
            "current_weight": round(self.current_weight, 4),
            "target_weight": round(self.target_weight, 4),
            "ratio": round(self.weight_change, 4),
            "priority": self.priority,
            "reason": self.reason
        }


# ============================================================
# 内置资产库（20+可配置资产）
# ============================================================

BUILTIN_ASSETS: Dict[str, Asset] = {
    # ---- 权益类 ----
    "沪深300": Asset("沪深300", "stock", 0.10, 0.22, max_weight=0.6),
    "中证500": Asset("中证500", "stock", 0.12, 0.28, max_weight=0.4),
    "创业板": Asset("创业板", "stock", 0.15, 0.35, max_weight=0.3),
    "港股蓝筹": Asset("港股蓝筹", "stock", 0.09, 0.25, max_weight=0.3),
    "标普500": Asset("标普500", "stock", 0.08, 0.18, max_weight=0.4),
    "纳斯达克100": Asset("纳斯达克100", "stock", 0.12, 0.24, max_weight=0.35),
    "日经225": Asset("日经225", "stock", 0.07, 0.20, max_weight=0.2),
    "印度股市": Asset("印度股市", "stock", 0.14, 0.30, max_weight=0.2),
    "德国股市": Asset("德国股市", "stock", 0.06, 0.22, max_weight=0.2),

    # ---- 固定收益类 ----
    "国债": Asset("国债", "bond", 0.035, 0.04, max_weight=0.8),
    "信用债AA+": Asset("信用债AA+", "bond", 0.055, 0.08, max_weight=0.5),
    "可转债": Asset("可转债", "bond", 0.08, 0.15, max_weight=0.3),
    "货币基金": Asset("货币基金", "bond", 0.025, 0.005, max_weight=0.5),
    "短期理财": Asset("短期理财", "bond", 0.03, 0.01, max_weight=0.4),

    # ---- 另类资产 ----
    "黄金": Asset("黄金", "alternative", 0.06, 0.15, max_weight=0.2),
    "原油": Asset("原油", "alternative", 0.05, 0.35, max_weight=0.15),
    "农产品CTA": Asset("农产品CTA", "alternative", 0.08, 0.20, max_weight=0.15),
    "REITs": Asset("REITs", "alternative", 0.07, 0.18, max_weight=0.2),

    # ---- 现金类 ----
    "现金": Asset("现金", "cash", 0.015, 0.001, max_weight=1.0, min_weight=0.0),
}


class CorrelationMatrix:
    """相关性矩阵（简化估计，实际应使用历史数据）"""

    @staticmethod
    def get_correlation_matrix(asset_names: List[str]) -> np.ndarray:
        n = len(asset_names)
        corr = np.eye(n)
        # 简化：同类资产高相关，跨类资产低相关
        for i, a in enumerate(asset_names):
            for j, b in enumerate(asset_names):
                if i == j:
                    continue
                cat_a = BUILTIN_ASSETS.get(a, Asset(a, "", 0, 0)).category
                cat_b = BUILTIN_ASSETS.get(b, Asset(b, "", 0, 0)).category
                if cat_a == cat_b:
                    corr[i, j] = 0.65
                else:
                    corr[i, j] = 0.15
        return corr


# ============================================================
# 核心引擎
# ============================================================

class PortfolioOptimizeEngine:
    """
    投资组合优化引擎
    基于 Markowitz 均值-方差模型，在有效前沿上寻找最优配置
    """

    def __init__(self, risk_free_rate: float = 0.03):
        self.risk_free_rate = risk_free_rate
        self.assets = BUILTIN_ASSETS

    # ---- 公开 API ----

    def optimize(
        self,
        current_portfolio: Dict[str, float],
        risk_preference: str = "medium",
        return_target: Optional[float] = None,
        capital_constraint: Optional[float] = None,
        optimization_goal: str = "balance",
        selected_assets: Optional[List[str]] = None,
    ) -> Dict:
        """
        主入口：执行组合优化

        :param current_portfolio: 当前持仓 {"资产名": 权重}，权重和为1
        :param risk_preference: low/medium/high
        :param return_target: 目标年化收益（如0.08）
        :param capital_constraint: 资金量约束（元）
        :param optimization_goal: reduce_risk / enhance_return / balance
        :param selected_assets: 指定参与的资产列表（默认全部）
        :return: 优化结果字典
        """
        # 1. 确定参与优化的资产（将通用类别映射到具体资产）
        if selected_assets is None:
            # 从当前持仓 + 高流动性资产中选
            active = []
            for k, v in current_portfolio.items():
                if v > 0.001:
                    resolved = self._resolve_asset_name(k)
                    if resolved not in active:
                        active.append(resolved)
            # 补充现金
            if "现金" not in active:
                active.append("现金")
        else:
            active = [self._resolve_asset_name(a) for a in selected_assets]

        # 2. 构建当前组合指标
        current_metrics = self._calc_portfolio_metrics(current_portfolio, active)

        # 3. 确定优化方向
        goal = OptimizationGoal(optimization_goal)
        risk_pref = RiskPreference(risk_preference)

        # 4. 在有效前沿上搜索最优组合
        optimal_weights = self._find_optimal_portfolio(
            active, goal, risk_pref, return_target
        )

        # 5. 计算最优组合指标
        optimal_metrics = self._calc_portfolio_metrics(optimal_weights, active)

        # 6. 生成调仓建议
        adjustments = self._generate_adjustments(
            current_portfolio, optimal_weights, active
        )

        # 7. 对比分析
        comparison = self._compare_portfolios(current_metrics, optimal_metrics)

        # 8. 执行优先级
        execution_priority = sorted(
            adjustments, key=lambda x: x.priority
        )

        # 9. 资本约束检查
        capital_info = {}
        if capital_constraint is not None:
            capital_info = self._check_capital_constraint(
                current_portfolio, optimal_weights, capital_constraint
            )

        return {
            "optimized_portfolio": {
                "weights": {k: round(v, 4) for k, v in optimal_weights.items()},
                "metrics": optimal_metrics.to_dict(),
            },
            "current_portfolio": {
                "weights": {k: round(v, 4) for k, v in current_portfolio.items()},
                "metrics": current_metrics.to_dict(),
            },
            "adjustments": [a.to_dict() for a in adjustments],
            "comparison": comparison,
            "execution_priority": [a.to_dict() for a in execution_priority],
            "capital_constraint": capital_info,
        }

    def parse_portfolio_from_text(self, text: str) -> Dict[str, float]:
        """
        从自然语言解析持仓比例
        例如："股票70%债券20%现金10%" -> {"stock": 0.7, "bond": 0.2, "cash": 0.1}
        """
        import re

        text = text.replace("％", "%").replace("仓", "")

        # 映射
        category_map = {
            "stock": ["股票", "权益", "A股", "港股", "美股", "沪深", "创业板", "蓝筹"],
            "bond": ["债券", "债", "国债", "信用债", "可转债", "理财"],
            "fund": ["基金", "ETF", "指数"],
            "cash": ["现金", "活期", "货币"],
            "alternative": ["黄金", "原油", "商品", "REITs"],
        }

        result = {}
        remaining = text

        for cat, keywords in category_map.items():
            for kw in keywords:
                # 匹配 "XX N%" 或 "XX N.%" 或 "XX N%"
                pattern = rf"{kw}[\s:：]*(\d+\.?\d*)%"
                m = re.search(pattern, remaining)
                if m:
                    result[cat] = float(m.group(1)) / 100.0
                    remaining = remaining[:m.start()] + remaining[m.end():]
                    break

        # 归一化
        total = sum(result.values())
        if total > 0:
            result = {k: v / total for k, v in result.items()}

        return result

    # ---- 私有方法 ----

    def _find_optimal_portfolio(
        self,
        asset_names: List[str],
        goal: OptimizationGoal,
        risk_pref: RiskPreference,
        return_target: Optional[float],
    ) -> Dict[str, float]:
        """在有效前沿上寻找最优配置"""

        n = len(asset_names)
        returns = np.array([self.assets[a].expected_return for a in asset_names])
        vols = np.array([self.assets[a].volatility for a in asset_names])
        max_ws = np.array([self.assets[a].max_weight for a in asset_names])
        min_ws = np.array([self.assets[a].min_weight for a in asset_names])

        corr = CorrelationMatrix.get_correlation_matrix(asset_names)
        cov = np.outer(vols, vols) * corr

        # 目标函数：最小化组合方差
        def portfolio_variance(w):
            return float(w @ cov @ w)

        def portfolio_return(w):
            return float(w @ returns)

        # 约束
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

        if return_target is not None:
            constraints.append({
                "type": "ineq",
                "fun": lambda w: portfolio_return(w) - return_target
            })

        # 根据优化目标设置风险约束
        if goal == OptimizationGoal.REDUCE_RISK:
            # 目标波动率比当前更低（估算）
            current_vol = float(np.sqrt(np.ones(n) @ cov @ np.ones(n)) * 0.7)
            constraints.append({
                "type": "ineq",
                "fun": lambda w: current_vol * 0.85 - np.sqrt(w @ cov @ w)
            })
        elif goal == OptimizationGoal.ENHANCE_RETURN:
            # 至少达到一定收益
            constraints.append({
                "type": "ineq",
                "fun": lambda w: portfolio_return(w) - 0.08
            })

        bounds = list(zip(min_ws, max_ws))

        # 风险偏好影响初始权重
        if risk_pref == RiskPreference.LOW:
            x0 = np.array([min_ws[i] + (max_ws[i] - min_ws[i]) * 0.1 for i in range(n)])
        elif risk_pref == RiskPreference.HIGH:
            x0 = np.array([min_ws[i] + (max_ws[i] - min_ws[i]) * 0.8 for i in range(n)])
        else:
            x0 = np.array([min_ws[i] + (max_ws[i] - min_ws[i]) * 0.5 for i in range(n)])

        x0 = x0 / x0.sum()  # 归一化

        if minimize is not None:
            res = minimize(
                portfolio_variance,
                x0,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
                options={"maxiter": 500}
            )
            if res.success:
                weights = res.x
            else:
                weights = x0  # fallback
        else:
            weights = x0

        weights = np.clip(weights, 0, 1)
        weights = weights / weights.sum()

        return {asset_names[i]: float(weights[i]) for i in range(n)}

    # 类别 -> 实际资产名映射
    CATEGORY_ASSET_MAP = {
        "stock": ["沪深300", "标普500"],
        "bond": ["国债", "信用债AA+"],
        "cash": ["现金"],
        "fund": ["货币基金"],
        "alternative": ["黄金"],
    }

    def _resolve_asset_name(self, key: str) -> str:
        """将通用类别 key 解析为实际资产名"""
        if key in self.assets:
            return key
        # 模糊匹配
        for cat, names in self.CATEGORY_ASSET_MAP.items():
            if key == cat or key in cat:
                return names[0]
        return key

    def _calc_portfolio_metrics(
        self, weights: Dict[str, float], asset_names: List[str]
    ) -> PortfolioMetrics:
        """计算组合风险收益指标"""
        # 将通用类别 key 映射到实际资产
        resolved = {}
        for k, v in weights.items():
            resolved[self._resolve_asset_name(k)] = v
        w = np.array([resolved.get(a, 0.0) for a in asset_names])
        returns = np.array([self.assets[a].expected_return for a in asset_names])
        vols = np.array([self.assets[a].volatility for a in asset_names])
        corr = CorrelationMatrix.get_correlation_matrix(asset_names)
        cov = np.outer(vols, vols) * corr

        port_return = float(w @ returns)
        port_vol = float(np.sqrt(w @ cov @ w))

        # 夏普比率
        sharpe = (port_return - self.risk_free_rate) / port_vol if port_vol > 0 else 0

        # 简化最大回撤（假设正态分布，2.33个标准差）
        max_dd = min(1.0, 2.33 * port_vol)

        # 95% VaR
        var_95 = 1.65 * port_vol

        return PortfolioMetrics(
            expected_return=port_return,
            volatility=port_vol,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            var_95=var_95,
        )

    def _generate_adjustments(
        self,
        current: Dict[str, float],
        optimal: Dict[str, float],
        asset_names: List[str],
    ) -> List[AdjustmentItem]:
        """生成调仓建议"""
        adjustments = []
        threshold = 0.01  # 1%以上才建议调仓

        # 将当前组合的通用类别 key 也加入比较
        all_assets = set(list(optimal.keys()))
        # 同时显示当前组合的key到实际资产的映射
        current_display = {}
        for k in current.keys():
            if k not in optimal:
                resolved = self._resolve_asset_name(k)
                if resolved in optimal:
                    current_display[resolved] = current.get(k, 0)
                else:
                    all_assets.add(k)
                    current_display[k] = current.get(k, 0)

        priority_counter = 1
        for asset in all_assets:
            cur_w = current_display.get(asset, current.get(asset, 0.0))
            opt_w = optimal.get(asset, 0.0)
            change = opt_w - cur_w

            if abs(change) < threshold:
                action = "hold"
                reason = "调整幅度过小，维持现状"
                priority = 99
            elif change > 0:
                action = "buy"
                reason = f"增配至{opt_w*100:.1f}%，提升组合风险收益效率"
                priority = priority_counter
                priority_counter += 1
            else:
                action = "sell"
                reason = f"减配至{opt_w*100:.1f}%，降低风险暴露"
                priority = priority_counter
                priority_counter += 1

            adjustments.append(AdjustmentItem(
                action=action,
                asset_name=asset,
                current_weight=cur_w,
                target_weight=opt_w,
                weight_change=change,
                priority=priority,
                reason=reason,
            ))

        return adjustments

    def _compare_portfolios(
        self, current: PortfolioMetrics, optimized: PortfolioMetrics
    ) -> Dict:
        """当前组合 vs 优化组合对比"""
        return {
            "return_change": round(optimized.expected_return - current.expected_return, 4),
            "volatility_change": round(optimized.volatility - current.volatility, 4),
            "sharpe_change": round(optimized.sharpe_ratio - current.sharpe_ratio, 4),
            "risk_reduction": round(
                (current.volatility - optimized.volatility) / current.volatility, 4
            ) if current.volatility > 0 else 0,
            "summary": self._generate_summary(current, optimized),
        }

    def _generate_summary(self, current: PortfolioMetrics, optimized: PortfolioMetrics) -> str:
        """生成文字摘要"""
        vol_chg = optimized.volatility - current.volatility
        ret_chg = optimized.expected_return - current.expected_return
        sharpe_chg = optimized.sharpe_ratio - current.sharpe_ratio

        lines = []
        lines.append(f"优化后预期年化收益 {optimized.expected_return*100:.2f}%"
                     f"（{'+' if ret_chg >= 0 else ''}{ret_chg*100:.2f}%）")
        lines.append(f"优化后年化波动率 {optimized.volatility*100:.2f}%"
                     f"（{'+' if vol_chg >= 0 else ''}{vol_chg*100:.2f}%）")
        lines.append(f"夏普比率 {optimized.sharpe_ratio:.3f}"
                     f"（{'+' if sharpe_chg >= 0 else ''}{sharpe_chg:.3f}）")

        if vol_chg < -0.01:
            lines.append("✓ 组合风险显著下降，配置更加稳健")
        elif vol_chg < 0:
            lines.append("✓ 组合风险小幅下降")
        elif sharpe_chg > 0.05:
            lines.append("✓ 风险收益效率明显提升")
        else:
            lines.append("→ 组合在有效前沿上达到最优")

        return "\n".join(lines)

    def _check_capital_constraint(
        self,
        current: Dict[str, float],
        optimal: Dict[str, float],
        total_capital: float,
    ) -> Dict:
        """资金约束检查"""
        changes = {}
        for asset in set(list(current.keys()) + list(optimal.keys())):
            cur = current.get(asset, 0.0)
            opt = optimal.get(asset, 0.0)
            changes[asset] = (opt - cur) * total_capital

        buy_total = sum(v for v in changes.values() if v > 0)
        sell_total = sum(v for v in changes.values() if v < 0)

        return {
            "total_capital": total_capital,
            "buy_amount": round(buy_total, 2),
            "sell_amount": round(abs(sell_total), 2),
            "net_cash_flow": round(buy_total + sell_total, 2),
            "per_asset": {k: round(v, 2) for k, v in changes.items() if abs(v) > 100},
        }


# ============================================================
# CLI 支持（兼容旧接口）
# ============================================================

def parse_cli_args(text: str) -> Dict:
    """解析CLI文本输入"""
    import re

    # 提取当前持仓
    portfolio = {}
    # 匹配 "股票N%" 等模式
    stock_match = re.search(r'股(票|权)[\s:：]*(\d+\.?\d*)%?', text)
    if stock_match:
        portfolio["stock"] = float(stock_match.group(2)) / 100

    bond_match = re.search(r'债(券|)[\s:：]*(\d+\.?\d*)%?', text)
    if bond_match:
        portfolio["bond"] = float(bond_match.group(2)) / 100

    cash_match = re.search(r'现(金|)[\s:：]*(\d+\.?\d*)%?', text)
    if cash_match:
        portfolio["cash"] = float(cash_match.group(2)) / 100

    fund_match = re.search(r'基(金|)[\s:：]*(\d+\.?\d*)%?', text)
    if fund_match:
        portfolio["fund"] = float(fund_match.group(2)) / 100

    # 归一化
    total = sum(portfolio.values())
    if total > 0:
        portfolio = {k: v / total for k, v in portfolio.items()}

    # 优化目标
    if "风险降低" in text or "降低风险" in text or "稳健" in text:
        goal = "reduce_risk"
    elif "收益" in text or "增强" in text or "提高" in text:
        goal = "enhance_return"
    else:
        goal = "balance"

    # 风险偏好
    if "保守" in text or "低风险" in text:
        risk_pref = "low"
    elif "激进" in text or "高风险" in text:
        risk_pref = "high"
    else:
        risk_pref = "medium"

    return {
        "portfolio": portfolio,
        "goal": goal,
        "risk_preference": risk_pref,
    }
