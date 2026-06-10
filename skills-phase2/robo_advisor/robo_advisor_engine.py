"""
Robo Advisor Engine - 智能投顾核心引擎
基于 Modern Portfolio Theory (MPT) 和 Black-Litterman 模型框架
"""

import json
import math
import random
import uuid
from datetime import datetime, timedelta
from typing import Any


# ─── 资产类别定义 ────────────────────────────────────────────────────────────

ASSET_CLASSES = {
    "stocks_china_a": {
        "name": "A股股票",
        "expected_return": 0.08,   # 8% 年化预期收益
        "volatility": 0.22,        # 22% 年化波动率
        "color": "rgb(239,68,68)",
    },
    "stocks_hk": {
        "name": "港股",
        "expected_return": 0.09,
        "volatility": 0.25,
        "color": "rgb(234,179,8)",
    },
    "stocks_us": {
        "name": "美股",
        "expected_return": 0.10,
        "volatility": 0.18,
        "color": "rgb(59,130,246)",
    },
    "bonds_gov": {
        "name": "利率债",
        "expected_return": 0.025,
        "volatility": 0.03,
        "color": "rgb(34,197,94)",
    },
    "bonds_credit": {
        "name": "信用债",
        "expected_return": 0.04,
        "volatility": 0.05,
        "color": "rgb(168,85,247)",
    },
    "alternatives_gold": {
        "name": "黄金",
        "expected_return": 0.04,
        "volatility": 0.15,
        "color": "rgb(251,191,36)",
    },
    "alternatives_reits": {
        "name": "REITs",
        "expected_return": 0.06,
        "volatility": 0.14,
        "color": "rgb(20,184,166)",
    },
    "cash": {
        "name": "现金及等价物",
        "expected_return": 0.015,
        "volatility": 0.005,
        "color": "rgb(156,163,175)",
    },
}

# 相关性矩阵（简化版）
CORRELATION_MATRIX = {
    ("stocks_china_a", "stocks_hk"): 0.65,
    ("stocks_china_a", "stocks_us"): 0.25,
    ("stocks_china_a", "bonds_gov"): -0.15,
    ("stocks_china_a", "bonds_credit"): 0.05,
    ("stocks_china_a", "alternatives_gold"): 0.05,
    ("stocks_china_a", "alternatives_reits"): 0.25,
    ("stocks_china_a", "cash"): 0.0,
    ("stocks_hk", "stocks_us"): 0.40,
    ("stocks_hk", "bonds_gov"): -0.10,
    ("stocks_hk", "bonds_credit"): 0.10,
    ("stocks_hk", "alternatives_gold"): 0.10,
    ("stocks_hk", "alternatives_reits"): 0.30,
    ("stocks_hk", "cash"): 0.0,
    ("stocks_us", "bonds_gov"): -0.20,
    ("stocks_us", "bonds_credit"): 0.05,
    ("stocks_us", "alternatives_gold"): 0.05,
    ("stocks_us", "alternatives_reits"): 0.35,
    ("stocks_us", "cash"): 0.0,
    ("bonds_gov", "bonds_credit"): 0.70,
    ("bonds_gov", "alternatives_gold"): 0.05,
    ("bonds_gov", "alternatives_reits"): 0.10,
    ("bonds_gov", "cash"): 0.20,
    ("bonds_credit", "alternatives_gold"): 0.0,
    ("bonds_credit", "alternatives_reits"): 0.15,
    ("bonds_credit", "cash"): 0.10,
    ("alternatives_gold", "alternatives_reits"): 0.15,
    ("alternatives_gold", "cash"): 0.0,
    ("alternatives_reits", "cash"): 0.0,
}


def get_correlation(a1: str, a2: str) -> float:
    if a1 == a2:
        return 1.0
    key = (a1, a2) if (a1, a2) in CORRELATION_MATRIX else (a2, a1)
    return CORRELATION_MATRIX.get(key, 0.0)


# ─── 风险类型映射 ────────────────────────────────────────────────────────────

RISK_TYPE_MAP = {
    "保守型": {
        "risk_score_range": (0, 30),
        "stocks_pct": 0.10,
        "bonds_pct": 0.55,
        "alternatives_pct": 0.05,
        "cash_pct": 0.30,
        "investment_horizon": "短期(1年以内)",
        "liquidity_need": "高",
        "description": "低风险偏好，以保本为首要目标，资产安全性优先",
    },
    "稳健型": {
        "risk_score_range": (31, 55),
        "stocks_pct": 0.25,
        "bonds_pct": 0.45,
        "alternatives_pct": 0.10,
        "cash_pct": 0.20,
        "investment_horizon": "中期(1-3年)",
        "liquidity_need": "中",
        "description": "追求稳健增值，可承受有限波动，兼顾收益与安全",
    },
    "平衡型": {
        "risk_score_range": (56, 75),
        "stocks_pct": 0.45,
        "bonds_pct": 0.30,
        "alternatives_pct": 0.15,
        "cash_pct": 0.10,
        "investment_horizon": "中长期(3-5年)",
        "liquidity_need": "中低",
        "description": "追求资产增值，可承受中等波动，风险收益均衡",
    },
    "进取型": {
        "risk_score_range": (76, 90),
        "stocks_pct": 0.65,
        "bonds_pct": 0.15,
        "alternatives_pct": 0.15,
        "cash_pct": 0.05,
        "investment_horizon": "长期(5年以上)",
        "liquidity_need": "低",
        "description": "追求高收益，可承受较大波动，资产增值为首要目标",
    },
    "激进型": {
        "risk_score_range": (91, 100),
        "stocks_pct": 0.80,
        "bonds_pct": 0.05,
        "alternatives_pct": 0.12,
        "cash_pct": 0.03,
        "investment_horizon": "超长期(10年以上)",
        "liquidity_need": "极低",
        "description": "最大化收益潜力，可承受剧烈波动，适合长期投资",
    },
}

INVESTMENT_GOAL_KEYWORDS = {
    "养老": {"horizon_weight": "long", "liquidity_weight": "low", "income_focus": 0.3},
    "教育": {"horizon_weight": "medium", "liquidity_weight": "medium", "income_focus": 0.2},
    "购房": {"horizon_weight": "short", "liquidity_weight": "high", "income_focus": 0.1},
    "保值": {"horizon_weight": "medium", "liquidity_weight": "high", "income_focus": 0.4},
    "增值": {"horizon_weight": "long", "liquidity_weight": "low", "income_focus": 0.1},
    "传承": {"horizon_weight": "ultra_long", "liquidity_weight": "very_low", "income_focus": 0.2},
}


# ─── 核心引擎类 ──────────────────────────────────────────────────────────────

class RoboAdvisorEngine:
    """
    智能投顾核心引擎
    融合 Modern Portfolio Theory (MPT) 和 Black-Litterman 模型框架
    """

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.assets = ASSET_CLASSES

    # ── 工具方法 ────────────────────────────────────────────────────────────

    def _parse_asset_amount(self, text: str) -> float:
        """从自然语言提取资产规模（单位：万元）"""
        import re
        patterns = [
            r"资产\s*([0-9,.]+)\s*万",
            r"([0-9,.]+)\s*万",
            r"资产\s*([0-9,.]+)\s*亿",
            r"([0-9,.]+)\s*亿",
            r"([0-9,.]+)\s*百万",
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                val = float(m.group(1).replace(",", ""))
                if "亿" in p or "百万" in p:
                    val *= 100
                return val * 10000  # 统一转为万元
        return 100.0  # 默认100万

    def _parse_risk_type(self, text: str) -> str:
        """从自然语言识别风险偏好类型"""
        text_lower = text.lower()
        if any(k in text_lower for k in ["保守", "低风险", "保本", "安稳"]):
            return "保守型"
        if any(k in text_lower for k in ["稳健", "平衡", "中等"]):
            return "稳健型"
        if any(k in text_lower for k in ["平衡", "适中", "中庸"]):
            return "平衡型"
        if any(k in text_lower for k in ["进取", "积极", "成长", "高收益"]):
            return "进取型"
        if any(k in text_lower for k in ["激进", "冒险", "大胆", "max", "极端"]):
            return "激进型"
        return "稳健型"  # 默认

    def _parse_investment_goal(self, text: str) -> str:
        """识别投资目标"""
        for kw, val in INVESTMENT_GOAL_KEYWORDS.items():
            if kw in text:
                return kw
        return "增值"

    def _compute_risk_score(self, risk_type: str, goal: str) -> int:
        """基于风险类型和投资目标计算风险评分"""
        base_map = {
            "保守型": 20, "稳健型": 43, "平衡型": 65,
            "进取型": 83, "激进型": 95,
        }
        base = base_map.get(risk_type, 50)
        goal_boost = {
            "养老": -5, "教育": -3, "购房": -8,
            "保值": -5, "增值": +5, "传承": 0,
        }
        return max(0, min(100, base + goal_boost.get(goal, 0)))

    def _get_risk_config(self, risk_score: int) -> dict:
        """根据风险评分获取配置"""
        for rtype, cfg in RISK_TYPE_MAP.items():
            lo, hi = cfg["risk_score_range"]
            if lo <= risk_score <= hi:
                return cfg
        return RISK_TYPE_MAP["平衡型"]

    # ── 资产配置生成（BL模型框架） ──────────────────────────────────────────

    def _black_litterman_weights(self, market_weights: dict, risk_aversion: float) -> dict:
        """
        Black-Litterman 简化实现
        将市场均衡收益与投资者观点融合，返回最优权重
        """
        # 市场均衡权重（如股票60%债券40%）
        # 融合风险偏好后得到后验权重
        assets = list(market_weights.keys())
        weights = {}
        for a in assets:
            er = self.assets[a]["expected_return"]
            vol = self.assets[a]["volatility"]
            # 简化的 BL 权重公式：w ∝ (μ - λΣμ) / (λΣ²)
            # 这里用更直观的：权重与(预期收益/波动率²)正相关
            weight = (er / (vol ** 2)) if vol > 0 else 0
            weights[a] = weight
        total = sum(weights.values())
        return {a: w / total for a, w in weights.items()}

    def _generate_strategic_allocation(self, risk_config: dict, risk_score: int) -> dict:
        """生成战略资产配置（SAA）"""
        # 四大类配置
        stocks_pct = risk_config["stocks_pct"]
        bonds_pct = risk_config["bonds_pct"]
        alt_pct = risk_config["alternatives_pct"]
        cash_pct = risk_config["cash_pct"]

        # 区域内部分配（简化：股票内部分配）
        china_a = stocks_pct * 0.45
        hk = stocks_pct * 0.25
        us = stocks_pct * 0.30

        # 债券内部分配
        gov = bonds_pct * 0.60
        credit = bonds_pct * 0.40

        # 另类内部分配
        gold = alt_pct * 0.60
        reits = alt_pct * 0.40

        return {
            "stocks_china_a": round(china_a, 4),
            "stocks_hk": round(hk, 4),
            "stocks_us": round(us, 4),
            "bonds_gov": round(gov, 4),
            "bonds_credit": round(credit, 4),
            "alternatives_gold": round(gold, 4),
            "alternatives_reits": round(reits, 4),
            "cash": round(cash_pct, 4),
        }

    def _aggregate_allocation(self, alloc: dict) -> dict:
        """将详细配置聚合为四大类"""
        stocks = sum(v for k, v in alloc.items() if "stocks" in k)
        bonds = sum(v for k, v in alloc.items() if "bonds" in k)
        alts = sum(v for k, v in alloc.items() if "alternatives" in k)
        cash = alloc.get("cash", 0)
        return {
            "stocks": round(stocks, 4),
            "bonds": round(bonds, 4),
            "alternatives": round(alts, 4),
            "cash": round(cash, 4),
        }

    def _region_allocation(self, alloc: dict) -> dict:
        """区域配置"""
        return {
            "china_a": round(alloc.get("stocks_china_a", 0), 4),
            "hk": round(alloc.get("stocks_hk", 0), 4),
            "us": round(alloc.get("stocks_us", 0), 4),
            "other": round(alloc.get("alternatives_reits", 0) * 0.3, 4),
        }

    # ── 组合指标计算 ────────────────────────────────────────────────────────

    def _portfolio_expected_return(self, alloc: dict) -> float:
        """组合预期收益"""
        total = 0.0
        for asset, pct in alloc.items():
            if asset in self.assets:
                total += pct * self.assets[asset]["expected_return"]
        return round(total, 4)

    def _portfolio_volatility(self, alloc: dict) -> float:
        """组合波动率（简化：忽略相关性）"""
        # 简化：加权波动率
        total_var = 0.0
        for a1, p1 in alloc.items():
            if a1 not in self.assets:
                continue
            v1 = self.assets[a1]["volatility"]
            for a2, p2 in alloc.items():
                if a2 not in self.assets:
                    continue
                corr = get_correlation(a1, a2)
                v2 = self.assets[a2]["volatility"]
                total_var += p1 * p2 * v1 * v2 * corr
        return round(math.sqrt(max(total_var, 0)), 4)

    def _sharpe_ratio(self, er: float, vol: float, rf: float = 0.015) -> float:
        """夏普比率"""
        if vol == 0:
            return 0.0
        return round((er - rf) / vol, 3)

    def _var_95(self, vol: float, er: float = 0.0) -> float:
        """95% VaR（简化：1.65σ）"""
        return round(1.65 * vol, 4)

    def _max_drawdown_est(self, vol: float) -> float:
        """估计最大回撤（简化：2.5σ）"""
        return round(2.5 * vol, 4)

    def _portfolio_metrics(self, alloc: dict) -> dict:
        """计算组合关键指标"""
        er = self._portfolio_expected_return(alloc)
        vol = self._portfolio_volatility(alloc)
        sharpe = self._sharpe_ratio(er, vol)
        var95 = self._var_95(vol, er)
        mdd = self._max_drawdown_est(vol)
        return {
            "expected_return": f"{er*100:.2f}%",
            "expected_volatility": f"{vol*100:.2f}%",
            "sharpe_ratio": sharpe,
            "var_95": f"{var95*100:.2f}%",
            "max_drawdown_est": f"{mdd*100:.2f}%",
        }

    # ── 再平衡策略 ──────────────────────────────────────────────────────────

    def _rebalancing_plan(self, risk_config: dict, session_ts: datetime) -> dict:
        """生成再平衡计划"""
        horizon = risk_config.get("investment_horizon", "中期(1-3年)")
        if "短期" in horizon:
            freq = "月度"
            next_rb = session_ts + timedelta(days=30)
            threshold = 0.03  # 3%
        elif "长期" in horizon or "超长期" in horizon:
            freq = "年度"
            next_rb = session_ts + timedelta(days=365)
            threshold = 0.05  # 5%
        else:
            freq = "季度"
            next_rb = session_ts + timedelta(days=90)
            threshold = 0.04  # 4%

        return {
            "strategy": f"{freq}再平衡",
            "trigger_rule": f"任一资产偏离目标>{threshold*100:.0f}%时触发",
            "threshold": threshold,
            "next_rebalance_date": next_rb.strftime("%Y-%m-%d"),
            "cost_aware": True,
            "tax_considerations": "必要时使用线性再平衡减少税费",
        }

    # ── 合规提示 ────────────────────────────────────────────────────────────

    def _compliance_notes(self, risk_type: str, alloc: dict) -> dict:
        """生成合规提示"""
        notes = {
            "appropriateness": f"该配置适合【{risk_type}】投资者",
            "risk_disclosure": [
                "本配置方案仅供参考，不构成投资建议",
                "过往业绩不代表未来表现，市场有风险，投资需谨慎",
                "非保本理财：股票型、混合型基金不保证本金安全",
                "投资者需确认本人风险承受能力与产品风险等级匹配",
            ],
            "regulatory_references": [
                "《关于规范金融机构资产管理业务的指导意见》（资管新规）",
                "《证券期货投资者适当性管理办法》",
                "《公开募集证券投资基金销售机构监督管理办法》",
                "《商业银行理财业务监督管理办法》",
            ],
        }
        if alloc.get("stocks_china_a", 0) + alloc.get("stocks_hk", 0) > 0.5:
            notes["risk_disclosure"].append(
                "注意：权益类资产配置比例较高，需关注A股/港股市场波动风险"
            )
        if alloc.get("bonds_credit", 0) > 0.2:
            notes["risk_disclosure"].append(
                "信用债存在信用风险，建议关注发行主体资质"
            )
        return notes

    # ── 投资组合持仓建议 ─────────────────────────────────────────────────────

    def _generate_positions(self, alloc: dict, total_amount: float) -> list:
        """生成具体持仓建议"""
        positions = []
        for asset_key, pct in alloc.items():
            if pct < 0.001:
                continue
            amount = total_amount * pct
            asset_info = self.assets.get(asset_key, {})
            rationale_map = {
                "stocks_china_a": "A股核心资产，分享中国经济增长红利",
                "stocks_hk": "港股低估优势，配置稀缺标的",
                "stocks_us": "美股科技龙头，分散区域风险",
                "bonds_gov": "利率债提供稳定票息，对冲股市风险",
                "bonds_credit": "信用债增强收益，控制久期",
                "alternatives_gold": "黄金避险对冲，降低组合波动",
                "alternatives_reits": "REITs提供稳定现金流，抗通胀",
                "cash": "现金管理，应对流动性需求",
            }
            positions.append({
                "asset_key": asset_key,
                "asset_name": asset_info.get("name", asset_key),
                "target_pct": f"{pct*100:.1f}%",
                "amount_yuan": round(amount, 2),
                "rationale": rationale_map.get(asset_key, ""),
                "expected_return": f"{asset_info.get('expected_return', 0)*100:.1f}%",
                "risk_level": "高" if asset_info.get("volatility", 0) > 0.15 else
                              "中" if asset_info.get("volatility", 0) > 0.07 else "低",
            })
        return positions

    # ── 主入口 ──────────────────────────────────────────────────────────────

    def generate_advisory(self, user_input: str) -> dict:
        """
        主入口：解析用户输入，生成完整投顾方案
        """
        ts = datetime.now()

        # 1. 解析输入
        risk_type = self._parse_risk_type(user_input)
        total_amount = self._parse_asset_amount(user_input)  # 元
        goal = self._parse_investment_goal(user_input)

        # 2. 风险评分
        risk_score = self._compute_risk_score(risk_type, goal)
        risk_config = self._get_risk_config(risk_score)

        # 3. 战略资产配置
        strategic_alloc = self._generate_strategic_allocation(risk_config, risk_score)

        # 4. 战术配置（暂时与战略相同，可扩展）
        tactical_alloc = strategic_alloc.copy()

        # 5. 聚合配置
        agg_strategic = self._aggregate_allocation(strategic_alloc)
        agg_tactical = self._aggregate_allocation(tactical_alloc)

        # 6. 组合指标
        metrics = self._portfolio_metrics(strategic_alloc)

        # 7. 持仓建议
        positions = self._generate_positions(strategic_alloc, total_amount)

        # 8. 再平衡计划
        rebalancing = self._rebalancing_plan(risk_config, ts)

        # 9. 合规提示
        compliance = self._compliance_notes(risk_type, strategic_alloc)

        # 10. 投顾建议摘要
        advice_summary = self._generate_summary(risk_type, goal, metrics, agg_strategic)

        return {
            "session_id": self.session_id,
            "timestamp": ts.isoformat(),
            "risk_profile": {
                "risk_type": risk_type,
                "risk_score": risk_score,
                "investment_horizon": risk_config.get("investment_horizon", "中期"),
                "liquidity_need": risk_config.get("liquidity_need", "中"),
                "investment_goal": goal,
                "description": risk_config.get("description", ""),
            },
            "asset_allocation": {
                "strategic": {k: f"{v*100:.1f}%" for k, v in agg_strategic.items()},
                "tactical": {k: f"{v*100:.1f}%" for k, v in agg_tactical.items()},
                "detail": {k: f"{v*100:.1f}%" for k, v in strategic_alloc.items()},
                "region": {k: f"{v*100:.1f}%" for k, v in self._region_allocation(strategic_alloc).items()},
            },
            "portfolio": {
                "positions": positions,
                **metrics,
            },
            "rebalancing": rebalancing,
            "compliance": compliance,
            "summary": advice_summary,
        }

    def generate_advisory_from_questionnaire(
        self,
        age: int = None,
        annual_income: float = None,
        invest_experience_years: int = None,
        loss_tolerance_pct: float = None,
        investment_goal: str = "增值",
        investment_horizon: str = "中期",
        liquidity_need: str = "中",
    ) -> dict:
        """
        问卷模式：从结构化问卷数据生成投顾方案
        """
        # 基于问卷计算风险评分
        score = 50
        if age is not None:
            if age < 30:
                score += 10
            elif age < 45:
                score += 5
            elif age < 60:
                score -= 5
            else:
                score -= 10

        if annual_income is not None:
            if annual_income > 100:
                score += 8
            elif annual_income > 50:
                score += 4
            elif annual_income > 20:
                score += 0
            else:
                score -= 5

        if invest_experience_years is not None:
            if invest_experience_years >= 10:
                score += 10
            elif invest_experience_years >= 5:
                score += 6
            elif invest_experience_years >= 2:
                score += 2

        if loss_tolerance_pct is not None:
            if loss_tolerance_pct >= 30:
                score += 15
            elif loss_tolerance_pct >= 20:
                score += 8
            elif loss_tolerance_pct >= 10:
                score += 2
            else:
                score -= 5

        score = max(0, min(100, score))

        # 确定风险类型
        risk_type = "平衡型"
        for rt, cfg in RISK_TYPE_MAP.items():
            lo, hi = cfg["risk_score_range"]
            if lo <= score <= hi:
                risk_type = rt
                risk_config = cfg
                break

        ts = datetime.now()
        strategic_alloc = self._generate_strategic_allocation(risk_config, score)
        agg_strategic = self._aggregate_allocation(strategic_alloc)
        metrics = self._portfolio_metrics(strategic_alloc)
        rebalancing = self._rebalancing_plan(risk_config, ts)
        compliance = self._compliance_notes(risk_type, strategic_alloc)

        return {
            "session_id": self.session_id,
            "timestamp": ts.isoformat(),
            "risk_profile": {
                "risk_type": risk_type,
                "risk_score": score,
                "investment_horizon": risk_config.get("investment_horizon", investment_horizon),
                "liquidity_need": risk_config.get("liquidity_need", liquidity_need),
                "investment_goal": investment_goal,
                "description": risk_config.get("description", ""),
                "questionnaire_data": {
                    "age": age,
                    "annual_income": annual_income,
                    "invest_experience_years": invest_experience_years,
                    "loss_tolerance_pct": loss_tolerance_pct,
                },
            },
            "asset_allocation": {
                "strategic": {k: f"{v*100:.1f}%" for k, v in agg_strategic.items()},
                "detail": {k: f"{v*100:.1f}%" for k, v in strategic_alloc.items()},
            },
            "portfolio": {
                **metrics,
            },
            "rebalancing": rebalancing,
            "compliance": compliance,
        }

    def calculate_rebalance(self, current_alloc: dict, target_alloc: dict, total_value: float) -> dict:
        """
        再平衡计算：分析当前配置与目标配置的偏离
        """
        drift_alerts = []
        for asset_key in set(list(current_alloc.keys()) + list(target_alloc.keys())):
            cur = current_alloc.get(asset_key, 0)
            tgt = target_alloc.get(asset_key, 0)
            drift = cur - tgt
            if abs(drift) >= 0.01:  # 1%以上
                drift_alerts.append({
                    "asset_key": asset_key,
                    "asset_name": self.assets.get(asset_key, {}).get("name", asset_key),
                    "current_pct": f"{cur*100:.2f}%",
                    "target_pct": f"{tgt*100:.2f}%",
                    "drift": f"{drift*100:+.2f}%",
                    "action": "减配" if drift > 0 else "增配",
                    "amount_yuan": round(abs(drift) * total_value, 2),
                })

        return {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "rebalance_needed": len(drift_alerts) > 0,
            "drift_alerts": sorted(drift_alerts, key=lambda x: abs(float(x["drift"].rstrip("%"))), reverse=True),
            "threshold_default": 0.05,
        }

    def _generate_summary(self, risk_type: str, goal: str, metrics: dict, alloc: dict) -> str:
        """生成自然语言摘要"""
        return (
            f"根据您的【{risk_type}】风险偏好和【{goal}】投资目标，"
            f"建议股债比为 {alloc['stocks']}：{alloc['bonds']}，"
            f"预期年化收益 {metrics['expected_return']}，"
            f"组合波动率 {metrics['expected_volatility']}，"
            f"夏普比率 {metrics['sharpe_ratio']}，"
            f"风险调整后收益表现良好。"
        )


# ─── CLI 入口兼容函数 ────────────────────────────────────────────────────────

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 robo_advisor_engine.py generate '智能投顾 稳健型 资产100万 养老规划'")
        return

    cmd = sys.argv[1]
    engine = RoboAdvisorEngine()

    if cmd == "generate" and len(sys.argv) >= 3:
        result = engine.generate_advisory(sys.argv[2])
    elif cmd == "questionnaire" and len(sys.argv) >= 3:
        # 解析问卷参数
        import re
        text = sys.argv[2]
        age_m = re.search(r"年龄(\d+)", text)
        income_m = re.search(r"收入([0-9.]+)万", text)
        exp_m = re.search(r"投资经验(\d+)年", text)
        loss_m = re.search(r"亏损承受([0-9.]+)%", text)
        result = engine.generate_advisory_from_questionnaire(
            age=int(age_m.group(1)) if age_m else None,
            annual_income=float(income_m.group(1)) if income_m else None,
            invest_experience_years=int(exp_m.group(1)) if exp_m else None,
            loss_tolerance_pct=float(loss_m.group(1)) if loss_m else None,
        )
    else:
        result = {"error": "unknown command"}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
