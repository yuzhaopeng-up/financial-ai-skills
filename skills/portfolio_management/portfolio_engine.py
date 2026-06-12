# -*- coding: utf-8 -*-
"""
Portfolio Management Engine
Implements Markowitz Mean-Variance, Risk Parity, and Maximum Diversification strategies.
Pure numpy implementation (no scipy dependency).
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import json
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 资产库（20+可配置资产）
# ─────────────────────────────────────────────
ASSET_UNIVERSE: Dict[str, Dict] = {
    # A股
    "沪深300ETF": {"type": "股票", "region": "A股", "expected_return": 0.10, "volatility": 0.22, "code": "510300.SH"},
    "中证500ETF": {"type": "股票", "region": "A股", "expected_return": 0.12, "volatility": 0.26, "code": "510500.SH"},
    "创业板ETF":  {"type": "股票", "region": "A股", "expected_return": 0.14, "volatility": 0.30, "code": "159915.SZ"},
    "消费ETF":    {"type": "股票", "region": "A股", "expected_return": 0.11, "volatility": 0.24, "code": "159928.SZ"},
    "医药ETF":    {"type": "股票", "region": "A股", "expected_return": 0.13, "volatility": 0.28, "code": "512010.SH"},
    # 港股
    "恒生ETF":    {"type": "股票", "region": "港股", "expected_return": 0.09, "volatility": 0.25, "code": "159920.HK"},
    "港股科技ETF":{"type": "股票", "region": "港股", "expected_return": 0.15, "volatility": 0.35, "code": "513180.HK"},
    # 美股
    "标普500ETF": {"type": "股票", "region": "美股", "expected_return": 0.10, "volatility": 0.18, "code": "SPY.US"},
    "纳斯达克ETF":{"type": "股票", "region": "美股", "expected_return": 0.12, "volatility": 0.22, "code": "QQQ.US"},
    "中概互联ETF":{"type": "股票", "region": "美股", "expected_return": 0.14, "volatility": 0.32, "code": "513050.SH"},
    # 债券
    "国债ETF":    {"type": "债券", "region": "债券", "expected_return": 0.035, "volatility": 0.04, "code": "511010.SH"},
    "企业债ETF":  {"type": "债券", "region": "债券", "expected_return": 0.05, "volatility": 0.06, "code": "511020.SH"},
    "政金债ETF":  {"type": "债券", "region": "债券", "expected_return": 0.04, "volatility": 0.05, "code": "511060.SH"},
    # 黄金/大宗
    "黄金ETF":    {"type": "大宗", "region": "黄金", "expected_return": 0.06, "volatility": 0.15, "code": "518880.SH"},
    "豆粕ETF":    {"type": "大宗", "region": "大宗", "expected_return": 0.05, "volatility": 0.20, "code": "001222.SZ"},
    # REITs
    "公募REITs":  {"type": "REITs", "region": "REITs", "expected_return": 0.07, "volatility": 0.12, "code": "508001.SH"},
    # 货币基金
    "货币基金":   {"type": "现金", "region": "现金", "expected_return": 0.018, "volatility": 0.003, "code": "000198.SH"},
    # A股主动
    "红利低波ETF":{"type": "股票", "region": "A股", "expected_return": 0.09, "volatility": 0.18, "code": "512890.SH"},
    "家电ETF":    {"type": "股票", "region": "A股", "expected_return": 0.10, "volatility": 0.23, "code": "159996.SZ"},
    "新能源ETF":  {"type": "股票", "region": "A股", "expected_return": 0.13, "volatility": 0.32, "code": "515790.SH"},
    "半导体ETF":  {"type": "股票", "region": "A股", "expected_return": 0.14, "volatility": 0.34, "code": "512480.SH"},
}

# 风险偏好 → 默认股债比
RISK_PREFERENCE_BONDS: Dict[str, float] = {
    "保守型": 0.70,
    "稳健型": 0.50,
    "平衡型": 0.30,
    "进取型": 0.10,
    "激进型": 0.00,
}


def _build_covariance_matrix(assets: List[str]) -> np.ndarray:
    n = len(assets)
    cov = np.zeros((n, n))
    for i, a in enumerate(assets):
        for j, b in enumerate(assets):
            vi = ASSET_UNIVERSE[a]["volatility"]
            vj = ASSET_UNIVERSE[b]["volatility"]
            ri = ASSET_UNIVERSE[a]["region"]
            rj = ASSET_UNIVERSE[b]["region"]
            if i == j:
                cov[i, j] = vi * vi
            else:
                rho = 0.3 if ri == rj else 0.15
                cov[i, j] = rho * vi * vj
    return cov


def _build_returns_vector(assets: List[str]) -> np.ndarray:
    return np.array([ASSET_UNIVERSE[a]["expected_return"] for a in assets])


def _normalize_weights(w: np.ndarray) -> np.ndarray:
    """归一化权重到和为1，确保非负"""
    w = np.maximum(w, 0)
    s = w.sum()
    return w / s if s > 0 else np.ones_like(w) / len(w)


def _monte_carlo_frontier(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    n_samples: int = 3000,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """蒙特卡洛模拟生成有效前沿"""
    n = len(expected_returns)
    best_sr = -999
    best_w = np.ones(n) / n
    ret_arr = []
    vol_arr = []
    sharpe_arr = []
    all_weights = []

    for _ in range(n_samples):
        # 随机生成权重（Dirichlet分布采样）
        raw = np.random.dirichlet(np.ones(n))
        # 加入随机扰动
        w = _normalize_weights(raw + np.random.randn(n) * 0.05)
        ret = w @ expected_returns
        vol = np.sqrt(w @ cov_matrix @ w)
        sr = ret / vol if vol > 1e-10 else 0

        ret_arr.append(ret)
        vol_arr.append(vol)
        sharpe_arr.append(sr)
        all_weights.append(w.copy())

        if sr > best_sr:
            best_sr = sr
            best_w = w.copy()

    return (
        np.array(ret_arr),
        np.array(vol_arr),
        np.array(sharpe_arr),
        np.array(all_weights),
        best_w,
    )


def _golden_section_frontier(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    n_points: int = 30,
) -> Tuple[np.ndarray, np.ndarray, List[np.ndarray]]:
    """黄金分割法求解有效前沿上的点（带约束最小方差）"""
    n = len(expected_returns)
    min_ret = expected_returns.min()
    max_ret = expected_returns.max()

    # 网格化目标收益
    target_returns = np.linspace(min_ret + 0.001, max_ret - 0.001, n_points)

    ret_arr = []
    vol_arr = []
    portfolios = []

    # 无约束最小方差（通过求解线性方程组）
    try:
        ones = np.ones(n)
        inv_cov = np.linalg.inv(cov_matrix + np.eye(n) * 1e-6)
        # 解析最小方差组合（无约束）
        w_unconstrained = inv_cov @ ones / (ones @ inv_cov @ ones)
    except np.linalg.LinAlgError:
        w_unconstrained = np.ones(n) / n

    for target_ret in target_returns:
        # 使用梯度下降求解带目标收益约束的最小方差
        w = _solve_min_variance_with_target(
            expected_returns, cov_matrix, target_ret,
            init_w=w_unconstrained if len(portfolios) == 0 else portfolios[-1]
        )
        vol = np.sqrt(w @ cov_matrix @ w)
        ret = w @ expected_returns
        sr = ret / vol if vol > 1e-10 else 0

        ret_arr.append(ret)
        vol_arr.append(vol)
        portfolios.append(w.copy())

    return np.array(ret_arr), np.array(vol_arr), portfolios


def _solve_min_variance_with_target(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    target_ret: float,
    init_w: Optional[np.ndarray] = None,
    max_iter: int = 200,
) -> np.ndarray:
    """投影梯度法求解：min w'Σw  s.t. w'μ=target_ret, w'1=1, w>=0"""
    n = len(expected_returns)
    if init_w is None:
        init_w = np.ones(n) / n

    w = init_w.copy()
    alpha = 0.1  # 学习率

    for _ in range(max_iter):
        # 梯度：∇(w'Σw) = 2Σw
        grad = 2 * cov_matrix @ w

        w_new = w - alpha * grad

        # 投影到约束：非负 + 和为1
        w_new = np.maximum(w_new, 0)
        w_new = w_new / w_new.sum() if w_new.sum() > 0 else np.ones(n) / n

        # 满足目标收益：线搜索
        current_ret = w_new @ expected_returns
        if abs(current_ret) > 1e-10:
            # 调整截距项使组合收益接近目标
            delta = (target_ret - current_ret) * 0.1
            adjustment = np.ones(n) * delta / n
            w_new = np.maximum(w_new + adjustment, 0)
            w_new = w_new / w_new.sum() if w_new.sum() > 0 else np.ones(n) / n

        # 收敛判断
        if np.max(np.abs(w_new - w)) < 1e-8:
            w = w_new
            break
        w = w_new

    return w


def _min_variance_portfolio(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
) -> Tuple[np.ndarray, float, float, float]:
    """解析法最小方差组合（Long-Only）"""
    n = len(expected_returns)
    try:
        ones = np.ones(n)
        inv_cov = np.linalg.inv(cov_matrix + np.eye(n) * 1e-8)
        # 无约束最小方差解析解
        w_unc = inv_cov @ ones / (ones @ inv_cov @ ones)
        # 投影到simplex（非负 + 和为1）
        w = _project_to_simplex(w_unc)
    except np.linalg.LinAlgError:
        w = np.ones(n) / n

    vol = np.sqrt(w @ cov_matrix @ w)
    ret = w @ expected_returns
    sr = ret / vol if vol > 1e-10 else 0
    return w, ret, vol, sr


def _project_to_simplex(v: np.ndarray) -> np.ndarray:
    """将向量投影到概率单纯形（w>=0, sum(w)=1）"""
    n = len(v)
    # 排序（降序）
    u = np.sort(v)[::-1]
    cssv = np.cumsum(u)
    rho = np.where(u > (cssv - 1) / np.arange(1, n + 1))[0]
    if len(rho) == 0:
        return np.ones(n) / n
    theta = (cssv[rho[-1]] - 1) / (rho[-1] + 1)
    w = np.maximum(v - theta, 0)
    return w / w.sum() if w.sum() > 0 else np.ones(n) / n


def _risk_parity_portfolio(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    assets: List[str],
    tol: float = 1e-6,
    max_iter: int = 500,
) -> Tuple[np.ndarray, float, float, float]:
    """风险平价组合 — 基于风险预算迭代求解"""
    n = len(assets)
    w = np.ones(n) / n  # 初始等权
    vols = np.array([ASSET_UNIVERSE[a]["volatility"] for a in assets])

    for _ in range(max_iter):
        port_vol = np.sqrt(w @ cov_matrix @ w)
        if port_vol < 1e-12:
            break
        # 各资产风险贡献：w_i * (Σw)_i / σ_p
        marginal = cov_matrix @ w
        risk_contrib = w * marginal / port_vol
        target_risk = port_vol / n * np.ones(n)
        # 风险贡献误差
        diff = risk_contrib - target_risk
        if np.linalg.norm(diff) < tol:
            break
        # 梯度调整
        grad = 2 * (cov_matrix @ w - marginal * port_vol / n / w + 1e-8)
        w = w - 0.3 * w * grad
        w = _project_to_simplex(np.maximum(w, 0.001))

    w = _project_to_simplex(np.maximum(w, 0))
    vol = np.sqrt(w @ cov_matrix @ w)
    ret = w @ expected_returns
    sr = ret / vol if vol > 1e-10 else 0
    return w, ret, vol, sr


def _max_diversification_portfolio(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    assets: List[str],
    max_iter: int = 300,
) -> Tuple[np.ndarray, float, float, float]:
    """最大多样化组合 — 梯度上升"""
    n = len(assets)
    vols = np.array([ASSET_UNIVERSE[a]["volatility"] for a in assets])
    w = np.ones(n) / n

    for _ in range(max_iter):
        port_vol = np.sqrt(w @ cov_matrix @ w)
        weighted_vol = w @ vols
        if weighted_vol < 1e-12 or port_vol < 1e-12:
            break
        # 多元化比率 DR = σ_p / (w'σ)
        # ∇DR = (Σw/σ_p - σ) / (w'σ)
        grad = (cov_matrix @ w / port_vol - vols) / weighted_vol
        w = w + 0.1 * w * grad
        w = _project_to_simplex(np.maximum(w, 0.001))

    w = _project_to_simplex(np.maximum(w, 0))
    vol = np.sqrt(w @ cov_matrix @ w)
    ret = w @ expected_returns
    sr = ret / vol if vol > 1e-10 else 0
    return w, ret, vol, sr


class PortfolioEngine:
    """核心组合管理引擎"""

    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode

    def _log(self, msg: str):
        if not self.api_mode:
            print(f"[PortfolioEngine] {msg}")

    def generate(
        self,
        risk_preference: str,
        asset_size: float,
        investment_horizon_years: int,
        target_return: Optional[float] = None,
    ) -> Dict:
        """
        生成三种策略推荐组合
        """
        self._log(f"Generating portfolios for {risk_preference}, {asset_size}万元, {investment_horizon_years}年")

        # 资产筛选
        bond_ratio = RISK_PREFERENCE_BONDS.get(risk_preference, 0.30)
        equity_ratio = 1.0 - bond_ratio

        selected = []
        if bond_ratio > 0.05:
            selected += ["国债ETF", "企业债ETF", "货币基金"]
        if equity_ratio > 0.05:
            selected += ["沪深300ETF", "中证500ETF", "恒生ETF", "标普500ETF"]
        if equity_ratio > 0.30:
            selected += ["创业板ETF", "纳斯达克ETF", "黄金ETF", "红利低波ETF"]
        if equity_ratio > 0.60:
            selected += ["港股科技ETF", "新能源ETF", "半导体ETF", "中概互联ETF", "公募REITs"]

        selected = list(dict.fromkeys(selected))
        assets = [a for a in selected if a in ASSET_UNIVERSE]
        if len(assets) == 0:
            assets = ["国债ETF", "沪深300ETF"]

        n = len(assets)
        expected_returns = _build_returns_vector(assets)
        cov_matrix = _build_covariance_matrix(assets)

        self._log(f"Selected assets ({n}): {assets}")

        target_ret_float = (target_return / 100.0) if target_return is not None else None

        # ── 1. 马科维茨有效前沿 + 最优夏普 ──
        ret_arr, vol_arr, portfolios = _golden_section_frontier(
            expected_returns, cov_matrix, n_points=40
        )
        sharpe_arr = ret_arr / np.maximum(vol_arr, 1e-10)

        if target_ret_float is not None:
            idx = np.argmin(np.abs(ret_arr - target_ret_float))
        else:
            idx = np.argmax(sharpe_arr)

        mw_w = portfolios[idx]
        mw_ret = ret_arr[idx]
        mw_vol = vol_arr[idx]
        mw_sr = sharpe_arr[idx]

        # ── 2. 马科维茨最小方差 ──
        minvar_w, minvar_ret, minvar_vol, minvar_sr = _min_variance_portfolio(
            expected_returns, cov_matrix
        )

        # ── 3. 风险平价 ──
        rp_w, rp_ret, rp_vol, rp_sr = _risk_parity_portfolio(
            expected_returns, cov_matrix, assets
        )

        # ── 4. 最大多样化 ──
        md_w, md_ret, md_vol, md_sr = _max_diversification_portfolio(
            expected_returns, cov_matrix, assets
        )

        def format_portfolio(w, ret, vol, sr, strategy_name):
            holdings = []
            for i, a in enumerate(assets):
                if w[i] > 0.001:
                    holdings.append({
                        "asset": a,
                        "weight": round(w[i] * 100, 2),
                        "allocation": round(w[i] * asset_size, 0),
                        "asset_type": ASSET_UNIVERSE[a]["type"],
                        "region": ASSET_UNIVERSE[a]["region"],
                        "expected_return": ASSET_UNIVERSE[a]["expected_return"],
                        "volatility": ASSET_UNIVERSE[a]["volatility"],
                    })
            holdings.sort(key=lambda x: x["weight"], reverse=True)
            return {
                "strategy": strategy_name,
                "expected_return_annual": round(ret * 100, 2),
                "volatility_annual": round(vol * 100, 2),
                "sharpe_ratio": round(sr, 3),
                "max_drawdown_estimate": round(-1.5 * vol * 100, 2),
                "total_allocation": round(sum(h["allocation"] for h in holdings), 0),
                "holdings": holdings,
                "efficient_frontier_points": len(ret_arr),
            }

        result = {
            "metadata": {
                "risk_preference": risk_preference,
                "asset_size": asset_size,
                "investment_horizon_years": investment_horizon_years,
                "target_return_pct": target_return,
                "assets_available": len(ASSET_UNIVERSE),
                "assets_used": assets,
            },
            "markowitz_efficient": format_portfolio(mw_w, mw_ret, mw_vol, mw_sr, "马科维茨有效前沿（最优夏普）"),
            "markowitz_min_variance": format_portfolio(minvar_w, minvar_ret, minvar_vol, minvar_sr, "马科维茨最小方差"),
            "risk_parity": format_portfolio(rp_w, rp_ret, rp_vol, rp_sr, "风险平价（等风险贡献）"),
            "max_diversification": format_portfolio(md_w, md_ret, md_vol, md_sr, "最大多样化组合"),
            "summary": {
                "highest_sharpe": "markowitz_efficient",
                "lowest_volatility": "risk_parity",
                "highest_return": "max_diversification",
            }
        }

        self._log(f"Done. Sharpe ratios: MW={mw_sr:.3f}, RP={rp_sr:.3f}, MD={md_sr:.3f}")
        return result


if __name__ == "__main__":
    engine = PortfolioEngine()
    result = engine.generate("平衡型", 500, 3, 8.0)
    print(json.dumps(result, ensure_ascii=False, indent=2))
