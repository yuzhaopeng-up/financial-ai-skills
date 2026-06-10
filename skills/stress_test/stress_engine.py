"""
银行压力测试引擎 (Stress Test Engine)
Bank Stress Testing Core Engine

基于宏观经济情景模拟银行资产负债表压力传导路径，
输出资本充足率、不良率、ROE、流动性缺口等关键指标。
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum


class StressScenario(Enum):
    """压力情景枚举"""
    BASE = "基准"
    MILD = "轻压"
    MODERATE = "中压"
    SEVERE = "重压"
    EXTREME = "极重压"


@dataclass
class ScenarioParams:
    """压力情景参数"""
    name: str
    gdp_change: float
    real_estate_change: float
    rate_change: float
    stock_change: float = 0.0
    external_shock: str = ""
    npl_multiplier: float = 1.0
    provision_ratio: float = 1.5
    liquidity_impact: float = 0.0


SCENARIO_PARAMS = {
    StressScenario.MILD: ScenarioParams(
        name="轻压", gdp_change=-1.0, real_estate_change=-10.0, rate_change=50,
        npl_multiplier=1.5, provision_ratio=1.4, liquidity_impact=-5.0
    ),
    StressScenario.MODERATE: ScenarioParams(
        name="中压", gdp_change=-3.0, real_estate_change=-20.0, rate_change=100,
        npl_multiplier=2.5, provision_ratio=1.3, liquidity_impact=-15.0
    ),
    StressScenario.SEVERE: ScenarioParams(
        name="重压", gdp_change=-5.0, real_estate_change=-30.0, rate_change=150,
        stock_change=-20.0, npl_multiplier=4.0, provision_ratio=1.2, liquidity_impact=-30.0
    ),
    StressScenario.EXTREME: ScenarioParams(
        name="极重压", gdp_change=-7.0, real_estate_change=-40.0, rate_change=200,
        stock_change=-40.0, external_shock="疫情/地缘冲突/制裁",
        npl_multiplier=6.0, provision_ratio=1.0, liquidity_impact=-50.0
    ),
}


@dataclass
class BankInput:
    """银行输入数据"""
    total_assets: float
    capital: float
    npl_ratio: float
    total_loans: Optional[float] = None
    total_liabilities: Optional[float] = None
    tier1_capital: Optional[float] = None
    core_tier1_capital: Optional[float] = None

    def __post_init__(self):
        if self.total_loans is None:
            self.total_loans = self.total_assets * 0.60
        if self.total_liabilities is None:
            self.total_liabilities = self.total_assets * 0.90
        if self.tier1_capital is None:
            self.tier1_capital = self.capital * 0.80
        if self.core_tier1_capital is None:
            self.core_tier1_capital = self.capital * 0.75


class StressTestEngine:
    """
    银行压力测试引擎
    基于宏观经济压力情景，模拟银行资产负债表的风险传导路径，
    计算各情景下的资本充足率、不良率、ROE、流动性缺口等指标。
    """

    def __init__(self):
        self.name = "BankStressTestEngine"
        self.version = "1.0.0"

    def run_stress_test(
        self,
        total_assets: float,
        capital: float,
        npl_ratio: float,
        liability_structure: Optional[Dict[str, float]] = None,
        scenarios: Optional[List[StressScenario]] = None
    ) -> Dict[str, Any]:
        """运行压力测试"""
        bank = BankInput(
            total_assets=total_assets,
            capital=capital,
            npl_ratio=npl_ratio
        )

        if scenarios is None:
            scenarios = [StressScenario.MILD, StressScenario.MODERATE,
                        StressScenario.SEVERE, StressScenario.EXTREME]

        base_result = self._calculate_base_scenario(bank)
        stress_results = {}
        for scenario in scenarios:
            params = SCENARIO_PARAMS[scenario]
            result = self._calculate_stress_scenario(bank, params, base_result)
            stress_results[scenario.value] = result

        return {
            "bank_info": {
                "total_assets": total_assets,
                "capital": capital,
                "npl_ratio": npl_ratio,
                "loan_amount": bank.total_loans
            },
            "baseline": base_result,
            "stress_scenarios": stress_results
        }

    def _calculate_base_scenario(self, bank: BankInput) -> Dict[str, Any]:
        """计算基准情景"""
        risk_weighted_assets = bank.total_loans * 0.60
        car = (bank.capital / risk_weighted_assets) * 100
        base_net_profit = bank.capital * 0.12
        roe = (base_net_profit / bank.capital) * 100

        return {
            "scenario": "基准",
            "car": round(car, 2),
            "tier1_car": round(car * 0.85, 2),
            "core_tier1_car": round(car * 0.75, 2),
            "npl_ratio": bank.npl_ratio,
            "npl_amount": round(bank.total_loans * bank.npl_ratio / 100, 2),
            "roe": round(roe, 2),
            "net_profit": round(base_net_profit, 2),
            "lcr": 120.0,
            "nsfr": 110.0,
            "liquidity_gap": 0.0
        }

    def _calculate_stress_scenario(
        self,
        bank: BankInput,
        params: ScenarioParams,
        base: Dict[str, Any]
    ) -> Dict[str, Any]:
        """计算压力情景"""
        stressed_npl = min(bank.npl_ratio * params.npl_multiplier, 30.0)
        npl_change = stressed_npl - bank.npl_ratio
        npl_amount = bank.total_loans * stressed_npl / 100

        provision_additional = npl_amount * (params.provision_ratio - 1.0) * 0.5
        stressed_capital = max(bank.capital - provision_additional, bank.capital * 0.5)

        risk_weighted_assets = bank.total_loans * 0.60 * (1 + params.npl_multiplier * 0.05)
        car = (stressed_capital / risk_weighted_assets) * 100
        car = max(min(car, 25.0), 2.0)

        tier1_car = car * 0.85
        core_tier1_car = car * 0.75

        profit_decline_ratio = (params.npl_multiplier - 1) * 0.15
        stressed_net_profit = base["net_profit"] * (1 - profit_decline_ratio)
        roe = (stressed_net_profit / stressed_capital) * 100

        lcr = max(base["lcr"] + params.liquidity_impact, 50.0)
        nsfr = max(base["nsfr"] + params.liquidity_impact * 0.8, 60.0)
        liquidity_gap = bank.total_liabilities * abs(params.liquidity_impact) / 100 * 0.3

        risk_channels = self._identify_risk_channels(params)
        risk_score = self._calculate_risk_score(params, car, stressed_npl, lcr)

        return {
            "scenario": params.name,
            "car": round(car, 2),
            "tier1_car": round(tier1_car, 2),
            "core_tier1_car": round(core_tier1_car, 2),
            "npl_ratio": round(stressed_npl, 2),
            "npl_amount": round(npl_amount, 2),
            "npl_change": round(npl_change, 2),
            "roe": round(roe, 2),
            "roe_change": round(roe - base["roe"], 2),
            "net_profit": round(stressed_net_profit, 2),
            "net_profit_change": round((stressed_net_profit / base["net_profit"] - 1) * 100, 2),
            "lcr": round(lcr, 2),
            "nsfr": round(nsfr, 2),
            "liquidity_gap": round(liquidity_gap, 2),
            "risk_channels": risk_channels,
            "risk_score": risk_score
        }

    def _identify_risk_channels(self, params: ScenarioParams) -> List[str]:
        """识别风险传导路径"""
        channels = []
        if params.real_estate_change < 0:
            channels.append("房地产抵押品价值↓ → 抵押贷款违约率↑")
        if params.gdp_change < 0:
            channels.append("GDP增速放缓 → 企业经营恶化 → 贷款违约↑")
        if params.rate_change > 0:
            channels.append("利率上行 → 利息支出↑ → 净息差收窄")
        if params.stock_change < 0:
            channels.append("股市下跌 → 股权投资收益↓ → 资本价值缩水")
        if params.liquidity_impact < 0:
            channels.append("储户信心下降 → 存款流失 → 流动性缺口扩大")
        channels.append("同业市场收紧 → 批发融资成本↑")
        if params.external_shock:
            channels.append(f"{params.external_shock} → 系统性风险上升")
        return channels

    def _calculate_risk_score(self, params: ScenarioParams, car: float,
                              npl_ratio: float, lcr: float) -> int:
        """计算综合风险评分 (1-10)"""
        score = 1.0
        if car < 8.0:
            score += 3.0
        elif car < 10.5:
            score += 2.0
        elif car < 12.0:
            score += 1.0
        if npl_ratio > 10:
            score += 3.0
        elif npl_ratio > 5:
            score += 2.0
        elif npl_ratio > 3:
            score += 1.0
        if lcr < 80:
            score += 2.0
        elif lcr < 100:
            score += 1.0
        if params.npl_multiplier >= 5:
            score += 2.0
        elif params.npl_multiplier >= 3:
            score += 1.0
        return min(int(score), 10)

    def format_report(self, results: Dict[str, Any]) -> str:
        """格式化压力测试报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("Bank Stress Test Report / 银行压力测试报告")
        lines.append("=" * 60)

        info = results["bank_info"]
        lines.append(f"\n[Bank Info]")
        lines.append(f"  Total Assets: {info['total_assets']:.2f} B CNY")
        lines.append(f"  Capital: {info['capital']:.2f} B CNY")
        lines.append(f"  Current NPL: {info['npl_ratio']:.2f}%")

        base = results["baseline"]
        lines.append(f"\n[Baseline]")
        lines.append(f"  CAR: {base['car']:.2f}%  |  NPL: {base['npl_ratio']:.2f}%")
        lines.append(f"  ROE: {base['roe']:.2f}%  |  LCR: {base['lcr']:.2f}%")

        lines.append(f"\n[Stress Scenarios]")
        for name, r in results["stress_scenarios"].items():
            car_flag = "!" if r["car"] < 10.5 else ""
            lines.append(f"\n  [{name}] Risk Score: {r['risk_score']}/10")
            lines.append(f"    CAR: {r['car']:.2f}%{car_flag}  |  NPL: {r['npl_ratio']:.2f}%")
            lines.append(f"    ROE: {r['roe']:.2f}%  |  Net Profit: {r['net_profit']:.2f}B")
            lines.append(f"    LCR: {r['lcr']:.2f}%  |  NSFR: {r['nsfr']:.2f}%")
            lines.append(f"    Liquidity Gap: {r['liquidity_gap']:.2f}B CNY")
        return "\n".join(lines)

    def format_wecom_card(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成企微卡片格式"""
        info = results["bank_info"]
        base = results["baseline"]
        scenarios = results["stress_scenarios"]

        card = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"""# 🏦 银行压力测试报告

## 基本信息
- 总资产: **{info['total_assets']:.0f}亿** | 资本金: **{info['capital']:.0f}亿**
- 当前不良率: **{info['npl_ratio']:.2f}%** | 资本充足率: **{base['car']:.2f}%**

## 压力测试结果

| 情景 | 资本充足率 | 不良率 | ROE | LCR | 风险评分 |
|:---:|:---:|:---:|:---:|:---:|:---:"""
            }
        }

        for name, r in scenarios.items():
            car_icon = "🔴" if r["car"] < 10.5 else "🟡"
            card["markdown"]["content"] += f"\n| {name} | {car_icon}{r['car']:.1f}% | {r['npl_ratio']:.1f}% | {r['roe']:.1f}% | {r['lcr']:.0f}% | {r['risk_score']}/10 |"

        card["markdown"]["content"] += "\n\n**风险传导路径:**"
        for name, r in scenarios.items():
            if r["risk_channels"]:
                card["markdown"]["content"] += f"\n\n**{name}:**"
                for ch in r["risk_channels"][:2]:
                    card["markdown"]["content"] += f"\n- {ch}"

        return card
