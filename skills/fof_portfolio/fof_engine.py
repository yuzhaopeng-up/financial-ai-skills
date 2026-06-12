"""
FOF Portfolio Engine - 基金中基金组合管理引擎
根据客户风险偏好、组合规模、投资目标和持有期限，
从内池基金中筛选构建最优基金组合
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import json
from datetime import datetime


@dataclass
class Fund:
    """基金数据结构"""
    code: str
    name: str
    fund_type: str  # 股票型/混合型/债券型/货币型/指数型/QDII
    risk_level: str  # 激进型/积极型/平衡型/稳健型/保守型
    # 业绩指标
    annual_return_1y: float = 0.0  # 近1年化收益
    annual_return_3y: float = 0.0  # 近3年化收益
    annual_return_5y: float = 0.0  # 近5年化收益
    sharpe_ratio: float = 0.0  # 夏普比率
    max_drawdown: float = 0.0  # 最大回撤
    # 基金经理信息
    manager_name: str = ""
    manager_tenure_years: float = 0.0  # 任职年限
    manager_change_freq: int = 0  # 变更频率(次/年)
    # 规模与费率
    aum: float = 0.0  # 规模(亿元)
    fee_rate: float = 0.0  # 费率(%)
    # 标签
    tags: List[str] = field(default_factory=list)


# 内池基金池 (20+只代表性基金)
INTERNAL_FUND_POOL: List[Fund] = [
    # 股票型
    Fund(code="000001", name="景顺长城内需增长", fund_type="股票型", risk_level="激进型",
         annual_return_1y=8.5, annual_return_3y=12.3, annual_return_5y=15.2, sharpe_ratio=0.85,
         max_drawdown=-28.5, manager_name="刘彦春", manager_tenure_years=8.2, manager_change_freq=0,
         aum=120.5, fee_rate=1.5, tags=["内需", "消费", "龙头"]),
    Fund(code="000011", name="华夏大盘精选", fund_type="股票型", risk_level="激进型",
         annual_return_1y=6.2, annual_return_3y=9.8, annual_return_5y=11.5, sharpe_ratio=0.72,
         max_drawdown=-32.1, manager_name="陈伟彦", manager_tenure_years=6.5, manager_change_freq=1,
         aum=85.2, fee_rate=1.5, tags=["大盘", "价值"]),
    Fund(code="260101", name="景顺长城优选", fund_type="股票型", risk_level="积极型",
         annual_return_1y=10.2, annual_return_3y=14.5, annual_return_5y=16.8, sharpe_ratio=0.92,
         max_drawdown=-25.3, manager_name="杨锐文", manager_tenure_years=5.8, manager_change_freq=0,
         aum=95.8, fee_rate=1.5, tags=["成长", "科技"]),
    # 混合型
    Fund(code="110011", name="易方达中小盘", fund_type="混合型", risk_level="积极型",
         annual_return_1y=5.8, annual_return_3y=10.2, annual_return_5y=13.5, sharpe_ratio=0.78,
         max_drawdown=-22.8, manager_name="张坤", manager_tenure_years=7.2, manager_change_freq=0,
         aum=180.3, fee_rate=1.5, tags=["中小盘", "价值", "长期持有"]),
    Fund(code="270008", name="广发稳健增长", fund_type="混合型", risk_level="平衡型",
         annual_return_1y=4.2, annual_return_3y=7.5, annual_return_5y=9.8, sharpe_ratio=0.68,
         max_drawdown=-15.6, manager_name="傅友兴", manager_tenure_years=4.5, manager_change_freq=1,
         aum=110.2, fee_rate=1.2, tags=["稳健", "消费", "医药"]),
    Fund(code="162201", name="泰达宏利先锋", fund_type="混合型", risk_level="积极型",
         annual_return_1y=7.5, annual_return_3y=11.2, annual_return_5y=14.5, sharpe_ratio=0.82,
         max_drawdown=-20.5, manager_name="张勋", manager_tenure_years=3.8, manager_change_freq=1,
         aum=65.5, fee_rate=1.5, tags=["成长", "轮动"]),
    Fund(code="519697", name="交银优势行业", fund_type="混合型", risk_level="平衡型",
         annual_return_1y=3.8, annual_return_3y=6.8, annual_return_5y=8.5, sharpe_ratio=0.62,
         max_drawdown=-12.5, manager_name="何帅", manager_tenure_years=5.2, manager_change_freq=0,
         aum=88.9, fee_rate=1.2, tags=["优势行业", "绝对收益"]),
    # 债券型
    Fund(code="480012", name="嘉实纯债债券", fund_type="债券型", risk_level="稳健型",
         annual_return_1y=3.2, annual_return_3y=4.5, annual_return_5y=5.2, sharpe_ratio=1.25,
         max_drawdown=-2.8, manager_name="曲扬", manager_tenure_years=3.2, manager_change_freq=1,
         aum=45.2, fee_rate=0.6, tags=["纯债", "低风险"]),
    Fund(code="110008", name="易方达稳健收益", fund_type="债券型", risk_level="稳健型",
         annual_return_1y=3.5, annual_return_3y=5.0, annual_return_5y=5.8, sharpe_ratio=1.35,
         max_drawdown=-3.5, manager_name="胡剑", manager_tenure_years=4.8, manager_change_freq=0,
         aum=55.8, fee_rate=0.6, tags=["稳健", "一级债"]),
    Fund(code="217022", name="招商产业债券", fund_type="债券型", risk_level="稳健型",
         annual_return_1y=3.8, annual_return_3y=5.2, annual_return_5y=6.0, sharpe_ratio=1.42,
         max_drawdown=-2.5, manager_name="姚邻居", manager_tenure_years=5.5, manager_change_freq=0,
         aum=72.3, fee_rate=0.6, tags=["产业债", "高等级信用"]),
    Fund(code="000104", name="华安纯债债券", fund_type="债券型", risk_level="保守型",
         annual_return_1y=2.8, annual_return_3y=3.8, annual_return_5y=4.2, sharpe_ratio=1.18,
         max_drawdown=-1.5, manager_name="苏玉平", manager_tenure_years=2.8, manager_change_freq=1,
         aum=38.5, fee_rate=0.5, tags=["纯债", "利率债"]),
    # 货币型
    Fund(code="000001", name="易方达货币", fund_type="货币型", risk_level="保守型",
         annual_return_1y=2.1, annual_return_3y=2.3, annual_return_5y=2.5, sharpe_ratio=0.0,
         max_drawdown=0.0, manager_name="石大怿", manager_tenure_years=3.5, manager_change_freq=0,
         aum=250.8, fee_rate=0.3, tags=["货币", "流动性管理"]),
    Fund(code="163802", name="中银货币", fund_type="货币型", risk_level="保守型",
         annual_return_1y=2.0, annual_return_3y=2.2, annual_return_5y=2.4, sharpe_ratio=0.0,
         max_drawdown=0.0, manager_name="范静", manager_tenure_years=4.2, manager_change_freq=0,
         aum=320.5, fee_rate=0.3, tags=["货币", "低风险"]),
    # 指数型
    Fund(code="159915", name="易方达创业板ETF", fund_type="指数型", risk_level="激进型",
         annual_return_1y=12.5, annual_return_3y=15.8, annual_return_5y=18.2, sharpe_ratio=0.68,
         max_drawdown=-35.5, manager_name="成曦", manager_tenure_years=2.5, manager_change_freq=1,
         aum=145.2, fee_rate=0.5, tags=["创业板", "成长", "ETF"]),
    Fund(code="510300", name="华泰柏瑞沪深300ETF", fund_type="指数型", risk_level="积极型",
         annual_return_1y=5.5, annual_return_3y=8.5, annual_return_5y=10.2, sharpe_ratio=0.58,
         max_drawdown=-28.5, manager_name="柳军", manager_tenure_years=5.8, manager_change_freq=0,
         aum=380.5, fee_rate=0.5, tags=["沪深300", "大盘", "蓝筹"]),
    Fund(code="510500", name="南方中证500ETF", fund_type="指数型", risk_level="积极型",
         annual_return_1y=8.2, annual_return_3y=11.5, annual_return_5y=13.8, sharpe_ratio=0.72,
         max_drawdown=-30.2, manager_name="罗文杰", manager_tenure_years=4.2, manager_change_freq=0,
         aum=280.3, fee_rate=0.5, tags=["中证500", "中小盘"]),
    Fund(code="588000", name="华夏科创板50ETF", fund_type="指数型", risk_level="激进型",
         annual_return_1y=15.8, annual_return_3y=18.5, annual_return_5y=0.0, sharpe_ratio=0.65,
         max_drawdown=-40.2, manager_name="荣膺", manager_tenure_years=1.8, manager_change_freq=0,
         aum=120.5, fee_rate=0.5, tags=["科创板", "科技", "硬科技"]),
    # QDII
    Fund(code="000041", name="华夏全球精选", fund_type="QDII", risk_level="激进型",
         annual_return_1y=18.5, annual_return_3y=22.8, annual_return_5y=25.5, sharpe_ratio=0.78,
         max_drawdown=-25.5, manager_name="李湘杰", manager_tenure_years=5.2, manager_change_freq=1,
         aum=65.8, fee_rate=1.6, tags=["全球", "美股", "港股"]),
    Fund(code="270023", name="广发纳斯达克100ETF", fund_type="QDII", risk_level="激进型",
         annual_return_1y=25.2, annual_return_3y=28.5, annual_return_5y=30.2, sharpe_ratio=0.88,
         max_drawdown=-22.5, manager_name="刘杰", manager_tenure_years=3.5, manager_change_freq=0,
         aum=85.5, fee_rate=1.3, tags=["纳斯达克", "美股", "科技"]),
    Fund(code="001691", name="南方香港优选", fund_type="QDII", risk_level="积极型",
         annual_return_1y=12.8, annual_return_3y=15.5, annual_return_5y=18.5, sharpe_ratio=0.75,
         max_drawdown=-28.5, manager_name="黄亮", manager_tenure_years=4.2, manager_change_freq=1,
         aum=45.2, fee_rate=1.5, tags=["港股", "香港", "中概股"]),
]


# 风险偏好与股债比例映射
RISK_ALLOCATION_MAP = {
    "保守型": {"股票型": 0, "混合型": 5, "债券型": 60, "货币型": 30, "指数型": 0, "QDII": 5},
    "稳健型": {"股票型": 10, "混合型": 15, "债券型": 50, "货币型": 15, "指数型": 5, "QDII": 5},
    "平衡型": {"股票型": 20, "混合型": 25, "债券型": 35, "货币型": 5, "指数型": 10, "QDII": 5},
    "积极型": {"股票型": 30, "混合型": 30, "债券型": 15, "货币型": 0, "指数型": 15, "QDII": 10},
    "激进型": {"股票型": 40, "混合型": 25, "债券型": 5, "货币型": 0, "指数型": 15, "QDII": 15},
}

# 投资目标与持有期限调整
GOAL_HOLDING_ADJUSTMENTS = {
    "养老规划": {"期限5年以上": 1.1, "期限3-5年": 1.05, "期限1-3年": 1.0, "期限1年以下": 0.95},
    "教育金": {"期限5年以上": 1.1, "期限3-5年": 1.05, "期限1-3年": 1.0, "期限1年以下": 0.9},
    "财富增值": {"期限5年以上": 1.15, "期限3-5年": 1.1, "期限1-3年": 1.0, "期限1年以下": 0.85},
    "资产保值": {"期限5年以上": 1.0, "期限3-5年": 1.0, "期限1-3年": 0.95, "期限1年以下": 0.9},
}


@dataclass
class ScreeningResult:
    """筛选结果"""
    fund: Fund
    score: float
    match_reasons: List[str]


@dataclass
class SAAConfig:
    """战略资产配置"""
    total_allocations: Dict[str, float]  # 各类型基金比例
    target_return: float  # 目标年化收益
    expected_volatility: float  # 预期波动率
    max_drawdown_limit: float  # 最大回撤限制


@dataclass
class TAAAdjustment:
    """战术资产调整"""
    asset_type: str
    current_weight: float
    recommended_weight: float
    adjustment_reason: str
    macro_factor: str  # 宏观因素
    valuation_factor: str  # 估值因素
    sentiment_factor: str  # 情绪因素


@dataclass
class WeightOptimization:
    """权重优化结果"""
    fund: Fund
    weight: float
    rationale: str


@dataclass
class DueDiligencePoint:
    """基金尽调要点"""
    fund_code: str
    fund_name: str
    strength_points: List[str]
    concern_points: List[str]
    monitoring_indicators: List[str]


class FOFEngine:
    """FOF组合管理引擎"""

    def __init__(self, fund_pool: Optional[List[Fund]] = None):
        self.fund_pool = fund_pool or INTERNAL_FUND_POOL

    def _parse_holding_period(self, holding_period: str) -> str:
        """解析持有期限为标准化描述"""
        if "5年" in holding_period or "5年" in holding_period or "长期" in holding_period:
            return "期限5年以上"
        elif "3年" in holding_period or "4年" in holding_period:
            return "期限3-5年"
        elif "1年" in holding_period or "2年" in holding_period:
            return "期限1-3年"
        else:
            return "期限1年以下"

    def _parse_portfolio_size(self, size_str: str) -> float:
        """解析组合规模(亿元)"""
        size_str = size_str.replace("，", "").replace(",", "")
        if "亿" in size_str:
            return float(size_str.replace("亿", "").strip())
        elif "万" in size_str:
            return float(size_str.replace("万", "").strip()) / 10000
        return 1.0  # 默认1亿

    def screen_funds(self, risk_preference: str, investment_goal: str,
                     holding_period: str, max_funds_per_type: int = 3) -> List[ScreeningResult]:
        """基金筛选"""
        # 目标持有期限分类
        period_key = self._parse_holding_period(holding_period)
        goal_adjustment = 1.0
        for goal_key, period_map in GOAL_HOLDING_ADJUSTMENTS.items():
            if goal_key in investment_goal:
                goal_adjustment = period_map.get(period_key, 1.0)
                break

        results = []
        # 按类型筛选
        for fund in self.fund_pool:
            # 风险等级匹配
            risk_rank = {"保守型": 1, "稳健型": 2, "平衡型": 3, "积极型": 4, "激进型": 5}
            target_rank = risk_rank.get(risk_preference, 3)
            fund_rank = risk_rank.get(fund.risk_level, 3)

            # 允许±1档差异
            if abs(fund_rank - target_rank) > 1:
                continue

            # 计算综合评分
            score = 0.0
            reasons = []

            # 业绩评分 (权重50%)
            return_score = (fund.annual_return_3y * 0.5 + fund.annual_return_1y * 0.3 +
                          fund.annual_return_5y * 0.2) * goal_adjustment
            score += return_score * 0.5
            if return_score > 10:
                reasons.append(f"历史业绩优异(3年化{return_score:.1f}%)")

            # 夏普比率评分 (权重20%)
            sharpe_score = fund.sharpe_ratio * 10
            score += sharpe_score * 0.2
            if sharpe_score > 8:
                reasons.append(f"风险调整收益优秀(夏普{sharpe_score:.1f})")

            # 最大回撤评分 (权重15%)
            dd_penalty = abs(fund.max_drawdown) / 100 * 0.5
            dd_score = max(0, 10 - dd_penalty)
            score += dd_score * 0.15
            if abs(fund.max_drawdown) < 20:
                reasons.append(f"回撤控制良好({fund.max_drawdown:.1f}%)")

            # 基金经理稳定性 (权重10%)
            manager_score = min(10, fund.manager_tenure_years * 2 -
                               fund.manager_change_freq * 2)
            score += manager_score * 0.1
            if fund.manager_tenure_years > 5:
                reasons.append(f"基金经理{fund.manager_name}任职{fund.manager_tenure_years:.1f}年稳定")

            # 规模合理性 (权重5%)
            if 20 < fund.aum < 300:
                score += 8 * 0.05
            elif fund.aum >= 300:
                score += 6 * 0.05
            else:
                score += 5 * 0.05

            results.append(ScreeningResult(fund=fund, score=score, match_reasons=reasons))

        # 按评分排序，每类取前N只
        results.sort(key=lambda x: x.score, reverse=True)
        type_count = {}
        final_results = []
        for r in results:
            ft = r.fund.fund_type
            if type_count.get(ft, 0) < max_funds_per_type:
                final_results.append(r)
                type_count[ft] = type_count.get(ft, 0) + 1

        return final_results

    def calculate_saa(self, risk_preference: str, investment_goal: str,
                     holding_period: str) -> SAAConfig:
        """计算战略资产配置"""
        # 基础配置
        base_alloc = RISK_ALLOCATION_MAP.get(risk_preference, RISK_ALLOCATION_MAP["平衡型"]).copy()

        # 根据投资目标和期限微调
        period_key = self._parse_holding_period(holding_period)

        # 养老规划和教育金更偏重稳健
        if "养老" in investment_goal or "教育" in investment_goal:
            # 增加债券和货币比例
            base_alloc["债券型"] = min(65, base_alloc["债券型"] + 10)
            base_alloc["混合型"] = max(10, base_alloc["混合型"] - 5)
            base_alloc["股票型"] = max(0, base_alloc["股票型"] - 5)

        # 财富增值目标更偏重权益
        if "增值" in investment_goal:
            base_alloc["股票型"] = min(50, base_alloc["股票型"] + 10)
            base_alloc["混合型"] = min(35, base_alloc["混合型"] + 5)
            base_alloc["债券型"] = max(20, base_alloc["债券型"] - 15)

        # 期限越长可承受更高权益仓位
        if "5年" in period_key or "长期" in holding_period:
            base_alloc["股票型"] = min(50, base_alloc["股票型"] + 5)
            base_alloc["混合型"] = min(35, base_alloc["混合型"] + 3)

        # 计算预期收益和波动
        target_return = 0.0
        expected_vol = 0.0
        for ft, pct in base_alloc.items():
            if ft == "股票型":
                target_return += pct * 0.12
                expected_vol += pct * 0.25
            elif ft == "混合型":
                target_return += pct * 0.08
                expected_vol += pct * 0.15
            elif ft == "债券型":
                target_return += pct * 0.04
                expected_vol += pct * 0.03
            elif ft == "货币型":
                target_return += pct * 0.02
                expected_vol += pct * 0.005
            elif ft == "指数型":
                target_return += pct * 0.10
                expected_vol += pct * 0.22
            elif ft == "QDII":
                target_return += pct * 0.15
                expected_vol += pct * 0.20

        target_return /= 100
        expected_vol /= 100
        max_dd_limit = expected_vol * 1.5

        return SAAConfig(
            total_allocations=base_alloc,
            target_return=target_return * 100,
            expected_volatility=expected_vol * 100,
            max_drawdown_limit=max_dd_limit * 100
        )

    def calculate_taa(self, saa: SAAConfig) -> List[TAAAdjustment]:
        """计算战术资产调整"""
        adjustments = []

        # 模拟当前宏观环境 (实际应用中应接入实时数据)
        adjustments.append(TAAAdjustment(
            asset_type="股票型",
            current_weight=saa.total_allocations.get("股票型", 0),
            recommended_weight=saa.total_allocations.get("股票型", 0) + 5,
            adjustment_reason="估值处于历史低位，政策暖风频吹",
            macro_factor="经济复苏预期增强，PMI重回扩张区间",
            valuation_factor="股债相对吸引力指标显示股票低估10%",
            sentiment_factor="A股情绪指数从低位回升，外资持续流入"
        ))

        adjustments.append(TAAAdjustment(
            asset_type="债券型",
            current_weight=saa.total_allocations.get("债券型", 0),
            recommended_weight=saa.total_allocations.get("债券型", 0) - 3,
            adjustment_reason="债券收益率偏低，利率进一步下行空间有限",
            macro_factor="通胀预期回升，货币政策可能边际收紧",
            valuation_factor="债券估值偏贵，股债性价比向股票倾斜",
            sentiment_factor="机构配置需求减弱，外资减持人民币债券"
        ))

        adjustments.append(TAAAdjustment(
            asset_type="QDII",
            current_weight=saa.total_allocations.get("QDII", 0),
            recommended_weight=saa.total_allocations.get("QDII", 0) + 3,
            adjustment_reason="全球配置可分散单一市场风险，美联储降息预期",
            macro_factor="美联储加息周期接近尾声，美元可能走弱",
            valuation_factor="标普500估值合理，纳斯达克科技股估值偏高",
            sentiment_factor="海外资金增配新兴市场，中国资产吸引力提升"
        ))

        return adjustments

    def optimize_weights(self, screened: List[ScreeningResult],
                        saa: SAAConfig, portfolio_size: float) -> List[WeightOptimization]:
        """优化基金权重"""
        # 按类型分组
        type_groups = {}
        for s in screened:
            ft = s.fund.fund_type
            if ft not in type_groups:
                type_groups[ft] = []
            type_groups[ft].append(s)

        weights = []
        allocated = 0

        for ft, candidates in type_groups.items():
            # 该类型目标配置比例
            target_pct = saa.total_allocations.get(ft, 0)

            # 同一类型内按评分分配
            total_score = sum(c.score for c in candidates)
            for i, c in enumerate(candidates):
                # 同类型内评分占比
                inner_weight = c.score / total_score if total_score > 0 else 1.0 / len(candidates)
                # 该类型分配给这只基金的权重
                weight = target_pct * inner_weight / 100

                rationale = f"{ft}类中评分最高({c.score:.1f}分)"
                if c.match_reasons:
                    rationale += f"，{c.match_reasons[0]}"

                weights.append(WeightOptimization(
                    fund=c.fund,
                    weight=weight,
                    rationale=rationale
                ))

        # 按权重降序排列
        weights.sort(key=lambda x: x.weight, reverse=True)
        return weights

    def generate_due_diligence(self, optimized: List[WeightOptimization]) -> List[DueDiligencePoint]:
        """生成基金尽调要点"""
        points = []

        for opt in optimized:
            fund = opt.fund
            strength_points = []
            concern_points = []
            monitoring = []

            # 优势点
            if fund.manager_tenure_years > 5:
                strength_points.append(f"基金经理{fund.manager_name}任职时间较长({fund.manager_tenure_years}年)，投资风格稳定")
            if fund.sharpe_ratio > 0.8:
                strength_points.append(f"夏普比率{fund.sharpe_ratio}，风险调整收益表现优异")
            if fund.annual_return_3y > 10:
                strength_points.append(f"3年年化收益{fund.annual_return_3y}%，穿越牛熊能力强")
            if fund.aum > 100:
                strength_points.append(f"管理规模{fund.aum}亿，流动性充裕")

            # 关注点
            if abs(fund.max_drawdown) > 30:
                concern_points.append(f"历史最大回撤{fund.max_drawdown}%，需关注极端行情下的风控能力")
            if fund.manager_change_freq > 0:
                concern_points.append(f"基金经理历史变更{fund.manager_change_freq}次，存在风格漂移风险")
            if fund.aum > 300:
                concern_points.append(f"规模较大({fund.aum}亿)，可能影响灵活调仓")
            if fund.fee_rate > 1.2:
                concern_points.append(f"管理费率{fund.fee_rate}%偏高，长期持有成本需关注")

            # 监控指标
            monitoring.append(f"季度收益率 vs 业绩比较基准超额收益")
            monitoring.append(f"基金规模变化(警惕大额赎回)")
            monitoring.append(f"持仓集中度变化(前十大重仓股)")
            if fund.fund_type in ["股票型", "混合型", "指数型"]:
                monitoring.append("换手率变化")
                monitoring.append("重仓股估值分位")
            monitoring.append(f"基金经理公开言论与实际持仓一致性")

            points.append(DueDiligencePoint(
                fund_code=fund.code,
                fund_name=fund.name,
                strength_points=strength_points,
                concern_points=concern_points,
                monitoring_indicators=monitoring
            ))

        return points

    def generate_portfolio(self, risk_preference: str, portfolio_size: str,
                          investment_goal: str, holding_period: str) -> Dict[str, Any]:
        """生成完整FOF组合方案"""
        # 1. 基金筛选
        screened = self.screen_funds(risk_preference, investment_goal, holding_period)

        # 2. 战略资产配置
        saa = self.calculate_saa(risk_preference, investment_goal, holding_period)

        # 3. 战术资产调整
        taa = self.calculate_taa(saa)

        # 4. 权重优化
        size_value = self._parse_portfolio_size(portfolio_size)
        optimized = self.optimize_weights(screened, saa, size_value)

        # 5. 尽调要点
        due_diligence = self.generate_due_diligence(optimized)

        # 组装结果
        return {
            "portfolio_id": f"FOF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input_params": {
                "risk_preference": risk_preference,
                "portfolio_size": portfolio_size,
                "investment_goal": investment_goal,
                "holding_period": holding_period
            },
            "strategic_asset_allocation": {
                "allocations": saa.total_allocations,
                "target_annual_return": f"{saa.target_return:.2f}%",
                "expected_volatility": f"{saa.expected_volatility:.2f}%",
                "max_drawdown_limit": f"{saa.max_drawdown_limit:.2f}%"
            },
            "tactical_adjustments": [
                {
                    "asset_type": a.asset_type,
                    "current_weight": f"{a.current_weight:.1f}%",
                    "recommended_weight": f"{a.recommended_weight:.1f}%",
                    "adjustment": f"+{a.recommended_weight - a.current_weight:.1f}%" if a.recommended_weight > a.current_weight else f"{a.recommended_weight - a.current_weight:.1f}%",
                    "reason": a.adjustment_reason,
                    "macro_factor": a.macro_factor,
                    "valuation_factor": a.valuation_factor,
                    "sentiment_factor": a.sentiment_factor
                }
                for a in taa
            ],
            "fund_screening": [
                {
                    "fund_code": s.fund.code,
                    "fund_name": s.fund.name,
                    "fund_type": s.fund.fund_type,
                    "risk_level": s.fund.risk_level,
                    "score": round(s.score, 2),
                    "match_reasons": s.match_reasons,
                    "key_metrics": {
                        "annual_return_1y": f"{s.fund.annual_return_1y}%",
                        "annual_return_3y": f"{s.fund.annual_return_3y}%",
                        "sharpe_ratio": s.fund.sharpe_ratio,
                        "max_drawdown": f"{s.fund.max_drawdown}%",
                        "manager": s.fund.manager_name,
                        "manager_tenure": f"{s.fund.manager_tenure_years}年",
                        "aum": f"{s.fund.aum}亿"
                    }
                }
                for s in screened
            ],
            "weight_optimization": [
                {
                    "fund_code": o.fund.code,
                    "fund_name": o.fund.name,
                    "weight": f"{o.weight * 100:.2f}%",
                    "amount_100m": f"{size_value * o.weight:.4f}亿" if size_value >= 1 else f"{size_value * o.weight * 10000:.2f}万",
                    "rationale": o.rationale
                }
                for o in optimized if o.weight > 0.001
            ],
            "due_diligence": [
                {
                    "fund_code": d.fund_code,
                    "fund_name": d.fund_name,
                    "strength_points": d.strength_points,
                    "concern_points": d.concern_points,
                    "monitoring_indicators": d.monitoring_indicators
                }
                for d in due_diligence
            ]
        }

    def generate_report(self, result: Dict[str, Any]) -> str:
        """生成可读报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("📊 FOF组合方案报告")
        lines.append("=" * 60)
        lines.append(f"组合ID: {result['portfolio_id']}")
        lines.append(f"生成时间: {result['generated_at']}")
        lines.append("")
        lines.append("【输入参数】")
        params = result['input_params']
        lines.append(f"  风险偏好: {params['risk_preference']}")
        lines.append(f"  组合规模: {params['portfolio_size']}")
        lines.append(f"  投资目标: {params['investment_goal']}")
        lines.append(f"  持有期限: {params['holding_period']}")
        lines.append("")

        lines.append("【战略资产配置 SAA】")
        saa = result['strategic_asset_allocation']
        lines.append(f"  目标年化收益: {saa['target_annual_return']}")
        lines.append(f"  预期波动率: {saa['expected_volatility']}")
        lines.append(f"  最大回撤限制: {saa['max_drawdown_limit']}")
        lines.append("  资产配置比例:")
        for k, v in saa['allocations'].items():
            if v > 0:
                lines.append(f"    {k}: {v}%")
        lines.append("")

        lines.append("【战术调整建议 TAA】")
        for adj in result['tactical_adjustments']:
            lines.append(f"  ▶ {adj['asset_type']}: {adj['current_weight']} → {adj['recommended_weight']} ({adj['adjustment']})")
            lines.append(f"    理由: {adj['reason']}")
        lines.append("")

        lines.append("【基金筛选与权重】")
        for w in result['weight_optimization']:
            lines.append(f"  {w['fund_name']}({w['fund_code']})")
            lines.append(f"    权重: {w['weight']} | 金额: {w['amount_100m']}")
            lines.append(f"    理由: {w['rationale']}")
        lines.append("")

        lines.append("【基金尽调要点】")
        for dd in result['due_diligence']:
            lines.append(f"  ▶ {dd['fund_name']}({dd['fund_code']})")
            if dd['strength_points']:
                lines.append(f"    ✅ 优势: {'; '.join(dd['strength_points'])}")
            if dd['concern_points']:
                lines.append(f"    ⚠️ 关注: {'; '.join(dd['concern_points'])}")
            lines.append(f"    📊 监控指标: {', '.join(dd['monitoring_indicators'][:2])}")
        lines.append("")
        lines.append("=" * 60)
        lines.append("⚠️ 风险提示: 基金过往业绩不代表未来表现，本方案仅供参考。")
        lines.append("=" * 60)

        return "\n".join(lines)


# CLI入口
if __name__ == "__main__":
    import sys

    def main():
        engine = FOFEngine()

        if len(sys.argv) > 1 and sys.argv[1] == "generate":
            # 解析输入: "FOF组合 平衡型 规模1亿 养老规划 持有5年"
            cmd = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            # 简单解析
            risk_pref = "平衡型"
            size = "1亿"
            goal = "养老规划"
            period = "5年"

            for kw in ["保守型", "稳健型", "平衡型", "积极型", "激进型"]:
                if kw in cmd:
                    risk_pref = kw
                    break

            for kw in ["亿", "万"]:
                if kw in cmd:
                    idx = cmd.find(kw)
                    size = cmd[max(0, idx-3):idx+1].strip()
                    if "规模" not in size:
                        size = cmd[max(0, idx-2):idx+1].strip()
                    break

            for kw in ["养老", "教育", "增值", "保值"]:
                if kw in cmd:
                    goal = kw + ("规划" if kw in ["养老", "教育"] else "")
                    break

            for kw in ["5年", "3年", "4年", "2年", "1年", "长期"]:
                if kw in cmd:
                    period = kw
                    break

            result = engine.generate_portfolio(risk_pref, size, goal, period)
            print(engine.generate_report(result))
        else:
            print("Usage: python fof_engine.py generate \"FOF组合 平衡型 规模1亿 养老规划 持有5年\"")

    main()
