"""
Fixed Income Plus Engine
固收+策略核心引擎:收益分解 + 久期管理 + 信用风险管理 + 类属配置优化
"""

import json
import math
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum


# ============ 常量定义 ============

# 债券类属
class BondType(Enum):
    RATE_GOV = "利率债"        # 国债、政策性金融债
    RATE_BANK = "政金债"       # 政策性银行债
    CREDIT_HIGH = "高等级信用债"  # AAA
    CREDIT_MID = "中等级信用债"   # AA+/AA
    CREDIT_LOW = "低等级信用债"   # AA-/A+
    CB = "可转债"             # 可转换债券
    ABS_SENIOR = "ABS优先档"    # 资产支持证券优先档
    ABS_JUNIOR = "ABS劣后档"    # 资产支持证券劣后档
    SUBordinated = "二级资本债"   # 银行二级资本债


# 评级映射
RATING_MAP = {
    "AAA": 1, "AA+": 2, "AA": 3, "AA-": 4, "A+": 5, "A": 6, "A-": 7,
    "BBB+": 8, "BBB": 9, "BBB-": 10, "BB+": 11, "BB": 12, "B": 13
}

# 各评级的历史违约率(年化,%)
HISTORICAL_DEFAULT_RATES = {
    "AAA": 0.01, "AA+": 0.03, "AA": 0.05, "AA-": 0.10,
    "A+": 0.20, "A": 0.35, "A-": 0.50,
    "BBB+": 0.80, "BBB": 1.20, "BBB-": 1.80,
    "BB+": 4.00, "BB": 6.00, "B": 12.00
}

# 各评级的信用利差(bp)
CREDIT_SPREADS = {
    "AAA": 30, "AA+": 45, "AA": 60, "AA-": 80,
    "A+": 110, "A": 140, "A-": 180,
    "BBB+": 250, "BBB": 320, "BBB-": 400
}

# 各资产的基准收益率(%)
BENCHMARK_YIELD = {
    BondType.RATE_GOV: 2.0,
    BondType.RATE_BANK: 2.2,
    BondType.CREDIT_HIGH: 2.6,
    BondType.CREDIT_MID: 3.0,
    BondType.CREDIT_LOW: 4.5,
    BondType.CB: 1.5,       # 可转债债底收益
    BondType.ABS_SENIOR: 3.2,
    BondType.ABS_JUNIOR: 6.5,
    BondType.SUBordinated: 3.5,
}


# ============ 数据结构 ============

@dataclass
class BondPosition:
    """单个债券持仓"""
    name: str
    bond_type: str
    rating: str
    amount: float          # 金额(万元)
    ytm: float              # 到期收益率(%)
    duration: float         # 久期(年)
    convexity: float        # 凸性
    price: float            # 净价(元)
    maturity: float         # 剩余期限(年)


@dataclass
class ReturnDecomposition:
    """收益分解"""
    total_return: float           # 总收益(%)
    carry_return: float           # 票息收入(%)
    capital_gain: float            # 资本利得(%)
    cb_option_value: float        # 可转债期权价值(%)
    abs_structured_return: float  # ABS分层收益(%)

    # 分解明细
    carry_detail: Dict[str, float] = field(default_factory=dict)
    capital_gain_detail: Dict[str, float] = field(default_factory=dict)


@dataclass
class DurationStrategy:
    """久期管理策略"""
    strategy_name: str            # 策略名称
    description: str
    duration_target: float         # 目标久期
    duration_actual: float         # 实际久期
    duration_gap: float            # 久期缺口
    allocation_by_tenor: Dict[str, float] = field(default_factory=dict)  # 期限分布
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class CreditRiskAnalysis:
    """信用风险管理"""
    dvcs: float                    # Duration × Credit Spread Sensitivity
    pd_annual: float               # 年化违约概率（%)
    el_annual: float               # 年化预期损失（%)
    credit_var_99: float           # 99% VaR 信用风险
    rating_distribution: Dict[str, float] = field(default_factory=dict)
    high_risk_exposure: float = 0.0     # 高风险敞口（%）
    warning_flag: bool = False
    warning_message: str = ""


@dataclass
class AllocationResult:
    """类属配置结果"""
    optimal_allocation: Dict[str, float]  # 最优配置比例(%)
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    risk_contribution: Dict[str, float] = field(default_factory=dict)


@dataclass
class PureBondComparison:
    """VS纯债对比"""
    fi_plus_return: float
    pure_bond_return: float
    excess_return: float
    fi_plus_volatility: float
    pure_bond_volatility: float
    return_per_volatility: float   # 单位波动收益
    max_drawdown_fi_plus: float
    max_drawdown_pure: float
    conclusion: str


@dataclass
class FIPlusReport:
    """固收+分析报告"""
    # 输入参数
    portfolio_amount: float        # 组合规模(万元)
    duration: float                # 组合久期
    rating: str                    # 信用评级
    target_return: float           # 目标收益(%)

    # 分析结果
    return_decomposition: Optional[ReturnDecomposition] = None
    duration_strategy: Optional[DurationStrategy] = None
    credit_risk: Optional[CreditRiskAnalysis] = None
    allocation: Optional[AllocationResult] = None
    pure_bond_comparison: Optional[PureBondComparison] = None

    # 元数据
    analysis_timestamp: str = ""
    model_version: str = "1.0.0"


# ============ 核心引擎类 ============

class FixedIncomePlusEngine:
    """
    固收+策略分析引擎

    输入:债券组合持仓、久期、信用分布、收益目标
    输出:收益分解、久期管理策略、信用风险管理、类属配置优化、VS纯债对比
    """

    def __init__(self):
        self.report = None

    def analyze(
        self,
        portfolio_amount: float,
        duration: float,
        rating: str,
        target_return: float,
        positions: Optional[List[BondPosition]] = None
    ) -> FIPlusReport:
        """
        主分析入口

        Args:
            portfolio_amount: 组合规模(万元)
            duration: 组合久期(年)
            rating: 组合评级(如 "AA")
            target_return: 目标收益(%)
            positions: 持仓列表(可选,不提供则使用默认配置)

        Returns:
            FIPlusReport: 完整的固收+分析报告
        """
        self.report = FIPlusReport(
            portfolio_amount=portfolio_amount,
            duration=duration,
            rating=rating,
            target_return=target_return,
            analysis_timestamp=self._get_timestamp()
        )

        # 1. 收益分解
        self.report.return_decomposition = self._decompose_return(
            portfolio_amount, duration, rating, target_return, positions
        )

        # 2. 久期管理策略
        self.report.duration_strategy = self._analyze_duration_strategy(
            portfolio_amount, duration, rating
        )

        # 3. 信用风险管理
        self.report.credit_risk = self._analyze_credit_risk(
            portfolio_amount, duration, rating, positions
        )

        # 4. 类属配置优化
        self.report.allocation = self._optimize_allocation(
            portfolio_amount, duration, rating, target_return
        )

        # 5. VS纯债对比
        self.report.pure_bond_comparison = self._compare_with_pure_bond(
            portfolio_amount, duration, rating, target_return
        )

        return self.report

    # ---------- 收益分解 ----------

    def _decompose_return(
        self,
        portfolio_amount: float,
        duration: float,
        rating: str,
        target_return: float,
        positions: Optional[List[BondPosition]]
    ) -> ReturnDecomposition:
        """
        收益分解:票息 + 资本利得 + 可转债期权价值 + ABS分层
        """
        # 如果没有提供持仓,使用默认配置
        if positions is None:
            positions = self._default_positions(portfolio_amount, duration, rating)

        total_base_yield = 0.0
        carry_detail = {}
        capital_gain_detail = {}

        # 按资产类型汇总
        type_yields = {}
        for pos in positions:
            bt = pos.bond_type
            if bt not in type_yields:
                type_yields[bt] = {"amount": 0, "ytm": 0, "weight_ytm": 0}
            type_yields[bt]["amount"] += pos.amount
            type_yields[bt]["weight_ytm"] += pos.ytm * pos.amount

        # 计算各类资产的加权收益
        total_amount = sum(v["amount"] for v in type_yields.values())
        weighted_yield = 0.0
        for bt, data in type_yields.items():
            if data["amount"] > 0:
                avg_ytm = data["weight_ytm"] / data["amount"]
                weight = data["amount"] / total_amount
                weighted_yield += avg_ytm * weight
                carry_detail[bt] = round(avg_ytm * weight * 100, 4)

        # 票息收入(年化)
        carry_return = weighted_yield

        # 资本利得(根据久期和利率预期)
        # 假设年度利率变动 0.2%,资本利得 = -Duration × ΔRate
        rate_change = 0.20  # 预期利率下行 20bp
        capital_gain = duration * rate_change * (-1)  # 利率下行,资本利得为正

        # 资本利得分项
        for bt in type_yields.keys():
            if bt in [BondType.CB.value, BondType.ABS_SENIOR.value, BondType.ABS_JUNIOR.value]:
                capital_gain_detail[bt] = round(capital_gain * 0.3, 4)
            else:
                capital_gain_detail[bt] = round(capital_gain * 0.7 / max(len(type_yields) - 3, 1), 4)

        # 可转债期权价值
        cb_weight = type_yields.get(BondType.CB.value, {}).get("amount", 0) / total_amount
        cb_option_value = cb_weight * 0.8  # 假设期权价值贡献

        # ABS分层收益
        abs_senior_weight = type_yields.get(BondType.ABS_SENIOR.value, {}).get("amount", 0) / total_amount
        abs_junior_weight = type_yields.get(BondType.ABS_JUNIOR.value, {}).get("amount", 0) / total_amount
        abs_structured_return = abs_senior_weight * 0.3 + abs_junior_weight * 1.2

        # 总收益
        total_return = carry_return + capital_gain + cb_option_value + abs_structured_return

        return ReturnDecomposition(
            total_return=round(total_return, 4),
            carry_return=round(carry_return, 4),
            capital_gain=round(capital_gain, 4),
            cb_option_value=round(cb_option_value, 4),
            abs_structured_return=round(abs_structured_return, 4),
            carry_detail={k: round(v, 4) for k, v in carry_detail.items()},
            capital_gain_detail={k: round(v, 4) for k, v in capital_gain_detail.items()}
        )

    # ---------- 久期管理 ----------

    def _analyze_duration_strategy(
        self,
        portfolio_amount: float,
        duration: float,
        rating: str
    ) -> DurationStrategy:
        """
        久期管理策略分析:子弹 vs 阶梯 vs 哑铃
        """
        # 子弹策略:集中于3-5年期
        bullet_tenor = {
            "1年以内": 10, "1-3年": 20, "3-5年": 50, "5-7年": 15, "7-10年": 5, "10年以上": 0
        }
        bullet_avg_duration = 3.5

        # 阶梯策略:均匀分布
        ladder_tenor = {
            "1年以内": 16, "1-3年": 17, "3-5年": 17, "5-7年": 17, "7-10年": 17, "10年以上": 16
        }
        ladder_avg_duration = 5.0

        # 哑铃策略:1年以内 + 7-10年
        dumbbell_tenor = {
            "1年以内": 35, "1-3年": 5, "3-5年": 5, "5-7年": 10, "7-10年": 35, "10年以上": 10
        }
        dumbbell_avg_duration = 4.5

        # 选择最优策略
        strategies = [
            ("子弹策略", bullet_tenor, bullet_avg_duration,
             ["收益较高", "管理简便"],
             ["流动性较差", "利率风险集中"]),
            ("阶梯策略", ladder_tenor, ladder_avg_duration,
             ["流动性好", "风险分散"],
             ["收益平平", "需要较多人力管理"]),
            ("哑铃策略", dumbbell_tenor, dumbbell_avg_duration,
             ["兼顾收益与流动性", "风险对冲"],
             ["两端波动大", "操作复杂"]),
        ]

        # 根据目标久期选择
        best_idx = 0
        if duration < 3.0:
            best_idx = 0  # 子弹偏短
        elif duration < 4.5:
            best_idx = 2  # 哑铃
        else:
            best_idx = 1  # 阶梯

        name, tenor, avg_dur, pros, cons = strategies[best_idx]

        # 计算久期缺口
        duration_gap = abs(duration - avg_dur)

        recommendation = ""
        if duration_gap < 0.5:
            recommendation = f"当前组合久期{duration}年与{name}匹配度良好,继续维持"
        else:
            recommendation = f"建议调整期限结构,目标久期{duration}年建议采用{name}"

        return DurationStrategy(
            strategy_name=name,
            description=f"{name}:久期集中于{avg_dur}年区间,通过期限配置实现稳健收益",
            duration_target=duration,
            duration_actual=avg_dur,
            duration_gap=round(duration_gap, 2),
            allocation_by_tenor=tenor,
            pros=pros,
            cons=cons,
            recommendation=recommendation
        )

    # ---------- 信用风险管理 ----------

    def _analyze_credit_risk(
        self,
        portfolio_amount: float,
        duration: float,
        rating: str,
        positions: Optional[List[BondPosition]]
    ) -> CreditRiskAnalysis:
        """
        信用风险管理:DVCS + 违约概率 + 预期损失
        """
        # DVCS = Duration × Credit Spread Change
        spread_change = CREDIT_SPREADS.get(rating, 100) / 10000  # 转换为小数
        dvcs = duration * spread_change * 10000  # 单位:bp

        # 年化违约概率
        pd_annual = HISTORICAL_DEFAULT_RATES.get(rating, 0.5)

        # 假设回收率 40%
        recovery_rate = 0.40
        lgd = 1 - recovery_rate

        # 年化预期损失 EL = PD × LGD
        el_annual = pd_annual * lgd

        # 99% VaR(基于正态分布近似)
        z_99 = 2.33
        credit_var_99 = z_99 * el_annual * math.sqrt(duration)

        # 评级分布(默认配置)
        rating_distribution = {
            "AAA": 15, "AA+": 25, "AA": 35, "AA-": 15, "A+": 5, "A": 3, "A-": 2
        }

        # 高风险敞口(评级低于A的占比)
        high_risk = sum(v for k, v in rating_distribution.items()
                       if k in ["A", "A-", "BBB+", "BBB", "BBB-", "BB+", "BB", "B"])
        high_risk_exposure = high_risk

        # 预警判断
        warning_flag = False
        warning_message = ""
        if duration * pd_annual > 0.5:
            warning_flag = True
            warning_message = f"久期×违约率 = {duration * pd_annual:.2f}%>0.5%,建议降低久期或提高评级"
        if dvcs > 200:
            warning_flag = True
            warning_message += f"\nDVCS={dvcs:.0f}bp>200bp,信用风险较高"

        return CreditRiskAnalysis(
            dvcs=round(dvcs, 2),
            pd_annual=round(pd_annual, 4),
            el_annual=round(el_annual, 4),
            credit_var_99=round(credit_var_99, 4),
            rating_distribution=rating_distribution,
            high_risk_exposure=round(high_risk_exposure, 2),
            warning_flag=warning_flag,
            warning_message=warning_message.strip()
        )

    # ---------- 类属配置优化 ----------

    def _optimize_allocation(
        self,
        portfolio_amount: float,
        duration: float,
        rating: str,
        target_return: float
    ) -> AllocationResult:
        """
        类属配置优化:利率债/信用债/可转债/ABS/二级债最优比例
        """
        # 简化的优化模型:基于目标收益和久期约束
        # 实际应用中可使用scipy.optimize或CVXPY

        base_weights = {
            "利率债": 20, "高等级信用债": 25, "中等级信用债": 20,
            "可转债": 10, "ABS优先档": 15, "ABS劣后档": 5, "二级资本债": 5
        }

        # 根据评级调整
        if rating in ["AAA", "AA+"]:
            base_weights = {
                "利率债": 25, "高等级信用债": 30, "中等级信用债": 15,
                "可转债": 10, "ABS优先档": 12, "ABS劣后档": 3, "二级资本债": 5
            }
        elif rating in ["AA-", "A+"]:
            base_weights = {
                "利率债": 15, "高等级信用债": 20, "中等级信用债": 30,
                "可转债": 10, "ABS优先档": 15, "ABS劣后档": 5, "二级资本债": 5
            }
        else:
            base_weights = {
                "利率债": 30, "高等级信用债": 25, "中等级信用债": 20,
                "可转债": 5, "ABS优先档": 12, "ABS劣后档": 3, "二级资本债": 5
            }

        # 计算预期收益
        expected_return = (
            base_weights["利率债"] / 100 * BENCHMARK_YIELD[BondType.RATE_GOV] +
            base_weights["高等级信用债"] / 100 * BENCHMARK_YIELD[BondType.CREDIT_HIGH] +
            base_weights["中等级信用债"] / 100 * BENCHMARK_YIELD[BondType.CREDIT_MID] +
            base_weights["可转债"] / 100 * BENCHMARK_YIELD[BondType.CB] +
            base_weights["ABS优先档"] / 100 * BENCHMARK_YIELD[BondType.ABS_SENIOR] +
            base_weights["ABS劣后档"] / 100 * BENCHMARK_YIELD[BondType.ABS_JUNIOR] +
            base_weights["二级资本债"] / 100 * BENCHMARK_YIELD[BondType.SUBordinated]
        )

        # 波动率(年化)
        expected_volatility = 2.5  # 简化估计

        # 夏普比率(假设无风险利率 2%)
        risk_free = 2.0
        sharpe_ratio = (expected_return - risk_free) / expected_volatility

        # 风险贡献
        risk_contribution = {
            "利率风险贡献": 30,
            "信用风险贡献": 45,
            "可转债风险贡献": 15,
            "ABS分层风险": 10
        }

        return AllocationResult(
            optimal_allocation=base_weights,
            expected_return=round(expected_return, 4),
            expected_volatility=round(expected_volatility, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            risk_contribution=risk_contribution
        )

    # ---------- VS纯债对比 ----------

    def _compare_with_pure_bond(
        self,
        portfolio_amount: float,
        duration: float,
        rating: str,
        target_return: float
    ) -> PureBondComparison:
        """
        固收+与纯债组合对比分析
        """
        # 固收+组合
        fi_plus_return = target_return
        fi_plus_volatility = 3.0  # 固收+波动率约3%

        # 纯债组合(降低久期、严控信用)
        pure_bond_return = min(target_return - 1.5, 3.5)  # 纯债收益通常低1-1.5%
        pure_bond_volatility = 1.2  # 纯债波动率约1.2%

        # 超额收益
        excess_return = fi_plus_return - pure_bond_return

        # 单位波动收益
        return_per_volatility = fi_plus_return / fi_plus_volatility

        # 最大回撤估算(基于波动率)
        max_drawdown_fi_plus = fi_plus_volatility * 2.5  # ~7.5%
        max_drawdown_pure = pure_bond_volatility * 2.0   # ~2.4%

        # 结论
        if excess_return > 1.0 and max_drawdown_fi_plus < 5.0:
            conclusion = f"固收+组合相比纯债超额收益{excess_return:.1f}%,回撤可控,建议配置"
        elif excess_return > 0.5:
            conclusion = f"固收+组合有适度超额收益{excess_return:.1f}%,风险收益比一般"
        else:
            conclusion = f"固收+超额收益{excess_return:.1f}%较低,需谨慎配置"

        return PureBondComparison(
            fi_plus_return=round(fi_plus_return, 4),
            pure_bond_return=round(pure_bond_return, 4),
            excess_return=round(excess_return, 4),
            fi_plus_volatility=round(fi_plus_volatility, 2),
            pure_bond_volatility=round(pure_bond_volatility, 2),
            return_per_volatility=round(return_per_volatility, 2),
            max_drawdown_fi_plus=round(max_drawdown_fi_plus, 2),
            max_drawdown_pure=round(max_drawdown_pure, 2),
            conclusion=conclusion
        )

    # ---------- 工具方法 ----------

    def _default_positions(
        self,
        portfolio_amount: float,
        duration: float,
        rating: str
    ) -> List[BondPosition]:
        """生成默认持仓配置"""
        total = portfolio_amount
        return [
            BondPosition("国债230023", BondType.RATE_GOV.value, "AAA",
                         total * 0.15, 2.0, 5.0, 30, 100.5, 7.2),
            BondPosition("农发债2303", BondType.RATE_BANK.value, "AAA",
                         total * 0.15, 2.2, 3.5, 15, 100.2, 3.5),
            BondPosition("铁建转债", BondType.CB.value, "AA+",
                         total * 0.12, 1.8, 2.5, 8, 105.0, 2.0),
            BondPosition("22电网MTN003", BondType.CREDIT_HIGH.value, "AAA",
                         total * 0.18, 2.6, 3.2, 12, 100.8, 3.2),
            BondPosition("22龙湖MTN001", BondType.CREDIT_MID.value, "AA+",
                         total * 0.15, 3.2, 4.0, 20, 98.5, 4.0),
            BondPosition("蚂蚁供应链ABS优先", BondType.ABS_SENIOR.value, "AA+",
                         total * 0.10, 3.3, 2.0, 5, 100.0, 1.5),
            BondPosition("蚂蚁供应链ABS劣后", BondType.ABS_JUNIOR.value, "AA",
                         total * 0.05, 6.5, 2.0, 5, 98.0, 1.5),
            BondPosition("20工行永续债01", BondType.SUBordinated.value, "AA+",
                         total * 0.10, 3.5, 4.5, 25, 99.0, 5.0),
        ]

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---------- 格式化输出 ----------

    def to_markdown(self, report: FIPlusReport) -> str:
        """生成 Markdown 格式报告"""
        lines = [
            f"# 固收+策略分析报告",
            f"",
            f"**分析时间**: {report.analysis_timestamp}",
            f"**组合规模**: {report.portfolio_amount:.0f} 万元",
            f"**组合久期**: {report.duration:.1f} 年",
            f"**信用评级**: {report.rating}",
            f"**目标收益**: {report.target_return:.1f}%",
            "",
            "---",
            "",
        ]

        # 收益分解
        rd = report.return_decomposition
        lines += [
            "## 1. 收益分解",
            "",
            "| 收益来源 | 贡献(%) |",
            "|---------|---------|",
            f"| 票息收入 (Carry) | {rd.carry_return:.2f} |",
            f"| 资本利得 (Capital Gain) | {rd.capital_gain:.2f} |",
            f"| 可转债期权价值 | {rd.cb_option_value:.2f} |",
            f"| ABS分层收益 | {rd.abs_structured_return:.2f} |",
            f"| **合计** | **{rd.total_return:.2f}** |",
            "",
            "**分项明细**:",
        ]
        for k, v in rd.carry_detail.items():
            lines.append(f"- {k}: {v:.2f}%")

        lines += ["", "---", ""]

        # 久期管理
        ds = report.duration_strategy
        lines += [
            "## 2. 久期管理策略",
            "",
            f"**推荐策略**: {ds.strategy_name}",
            f"**策略描述**: {ds.description}",
            "",
            f"| 指标 | 数值 |",
            "|-----|-----|",
            f"| 目标久期 | {ds.duration_target:.1f} 年 |",
            f"| 实际久期 | {ds.duration_actual:.1f} 年 |",
            f"| 久期缺口 | {ds.duration_gap:.2f} 年 |",
            "",
            "**期限分布**:",
        ]
        for tenor, pct in ds.allocation_by_tenor.items():
            lines.append(f"- {tenor}: {pct}%")
        lines += [
            "",
            f"**优势**: {', '.join(ds.pros)}",
            f"**劣势**: {', '.join(ds.cons)}",
            "",
            f"**建议**: {ds.recommendation}",
            "",
            "---",
            "",
        ]

        # 信用风险管理
        cr = report.credit_risk
        lines += [
            "## 3. 信用风险管理",
            "",
            f"| 风险指标 | 数值 |",
            "|---------|-----|",
            f"| DVCS(久期×信用利差) | {cr.dvcs:.1f} bp |",
            f"| 年化违约概率 (PD) | {cr.pd_annual:.4f}% |",
            f"| 年化预期损失 (EL) | {cr.el_annual:.4f}% |",
            f"| 99% VaR | {cr.credit_var_99:.4f}% |",
            f"| 高风险敞口 | {cr.high_risk_exposure:.1f}% |",
            "",
            "**评级分布**:",
        ]
        for rating, pct in cr.rating_distribution.items():
            lines.append(f"- {rating}: {pct}%")

        if cr.warning_flag:
            lines += ["", f"⚠️ **预警**: {cr.warning_message}", ""]

        lines += ["---", ""]

        # 类属配置
        al = report.allocation
        lines += [
            "## 4. 类属配置优化",
            "",
            f"| 配置类属 | 建议比例 |",
            "|---------|---------|",
        ]
        for asset, pct in al.optimal_allocation.items():
            lines.append(f"| {asset} | {pct}% |")
        lines += [
            "",
            f"| 预期收益 | {al.expected_return:.2f}% |",
            f"| 预期波动率 | {al.expected_volatility:.2f}% |",
            f"| 夏普比率 | {al.sharpe_ratio:.2f} |",
            "",
            "**风险贡献**:",
        ]
        for risk, contrib in al.risk_contribution.items():
            lines.append(f"- {risk}: {contrib}%")

        lines += ["---", ""]

        # VS纯债对比
        pc = report.pure_bond_comparison
        lines += [
            "## 5. VS纯债对比分析",
            "",
            f"| 对比维度 | 固收+ | 纯债 |",
            "|---------|------|-----|",
            f"| 预期收益 | {pc.fi_plus_return:.2f}% | {pc.pure_bond_return:.2f}% |",
            f"| 波动率 | {pc.fi_plus_volatility:.2f}% | {pc.pure_bond_volatility:.2f}% |",
            f"| 最大回撤 | {pc.max_drawdown_fi_plus:.2f}% | {pc.max_drawdown_pure:.2f}% |",
            f"| 单位波动收益 | {pc.return_per_volatility:.2f} | - |",
            "",
            f"**超额收益**: {pc.excess_return:.2f}%",
            "",
            f"**结论**: {pc.conclusion}",
            "",
            "---",
            "",
            f"*报告生成时间: {report.analysis_timestamp}*",
            f"*模型版本: {report.model_version}*",
        ]

        return "\n".join(lines)

    def to_json(self, report: FIPlusReport) -> str:
        """生成 JSON 格式报告"""
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(i) for i in d]
            elif hasattr(d, '__dict__'):
                return clean_dict(asdict(d))
            return d

        data = {
            "portfolio_amount": report.portfolio_amount,
            "duration": report.duration,
            "rating": report.rating,
            "target_return": report.target_return,
            "analysis_timestamp": report.analysis_timestamp,
            "model_version": report.model_version,
            "return_decomposition": asdict(report.return_decomposition) if report.return_decomposition else None,
            "duration_strategy": asdict(report.duration_strategy) if report.duration_strategy else None,
            "credit_risk": asdict(report.credit_risk) if report.credit_risk else None,
            "allocation": asdict(report.allocation) if report.allocation else None,
            "pure_bond_comparison": asdict(report.pure_bond_comparison) if report.pure_bond_comparison else None,
        }
        return json.dumps(data, ensure_ascii=False, indent=2)


def main():
    """测试入口"""
    engine = FixedIncomePlusEngine()

    # 测试用例:债券组合1亿,久期3.5,信用AA,目标收益4.5%
    report = engine.analyze(
        portfolio_amount=10000,  # 1亿 = 10000万
        duration=3.5,
        rating="AA",
        target_return=4.5
    )

    print(engine.to_markdown(report))


if __name__ == "__main__":
    main()
