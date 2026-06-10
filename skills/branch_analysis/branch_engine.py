"""
网点分析引擎 (Branch Analysis Engine)

基于多维度数据的银行网点竞争力分析引擎
"""

import random
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class CustomerProfile:
    primary: str       # 主要客群
    secondary: str     # 次要客群
    potential: str     # 潜在客群
    age_distribution: Dict[str, float] = field(default_factory=dict)
    income_level: str = "中等"


@dataclass
class TrafficEstimate:
    daily_visitors: int           # 日均来访人数
    peak_hours: List[str]         # 高峰时段
    conversion_rate: float        # 转化率
    weekend_multiplier: float = 1.3


@dataclass
class SWOT:
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]


@dataclass
class YearForecast:
    year: int
    revenue: float       # 万元
    customers: int      # 有效客户数
    market_share: float  # 预期市场份额


@dataclass
class ResourceAllocation:
    staff_front_desk: int
    staff_sales: int
    staff_back_office: int
    equipment: List[str]
    marketing_budget: float  # 万元/年


@dataclass
class InputOutputRecommendation:
    initial_investment: float    # 万元
    expected_roi: float          # %
    payback_period: int          # 月
    risk_level: str              # 低/中/高


@dataclass
class BranchAnalysisResult:
    branch_id: str
    zone_type: str
    area: float
    staff_count: int
    competitor_count: int
    local_enterprise_count: int
    swot: SWOT
    customer_profile: CustomerProfile
    traffic_estimate: TrafficEstimate
    service_radius_km: float
    production_capacity_index: float
    business_focus: List[str]
    three_year_forecast: List[YearForecast]
    resource_allocation: ResourceAllocation
    input_output_recommendation: InputOutputRecommendation

    def to_dict(self) -> Dict[str, Any]:
        def _flatten(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {k: _flatten(v) for k, v in asdict(obj).items()}
            elif isinstance(obj, list):
                return [_flatten(i) for i in obj]
            return obj
        return _flatten(self)


class BranchAnalysisEngine:
    """
    网点分析引擎
    
    输入：网点数据（所在区域/面积/员工数/周边竞争网点数/本地企业数）
    输出：网点竞争力分析（SWOT/客群画像/经营建议/资源配置建议）
    """

    ZONE_CONFIGS = {
        "商业区": {
            "daily_base_visitors": 350,
            "peak_hours": ["09:00-11:00", "14:00-16:00", "19:00-21:00"],
            "conversion_rate": 0.15,
            "avg_transaction": 2800,
            "service_radius_km": 1.5,
            "production_base": 180,  # 万元/人/年
            "customer_age": {"18-30": 0.35, "31-45": 0.40, "46-60": 0.20, "60+": 0.05},
            "customer_income": "中高",
            "primary_customer": "都市白领、商务人士",
            "secondary_customer": "个体工商户",
            "potential_customer": "年轻家庭",
        },
        "住宅区": {
            "daily_base_visitors": 120,
            "peak_hours": ["08:00-09:00", "17:00-19:00", "周末全天"],
            "conversion_rate": 0.25,
            "avg_transaction": 1500,
            "service_radius_km": 2.5,
            "production_base": 100,
            "customer_age": {"18-30": 0.20, "31-45": 0.35, "46-60": 0.30, "60+": 0.15},
            "customer_income": "中等",
            "primary_customer": "家庭户主、中老年居民",
            "secondary_customer": "年轻夫妇",
            "potential_customer": "社区商户",
        },
        "工业区": {
            "daily_base_visitors": 80,
            "peak_hours": ["07:30-08:30", "12:00-13:00", "17:30-18:30"],
            "conversion_rate": 0.30,
            "avg_transaction": 4500,
            "service_radius_km": 3.0,
            "production_base": 220,
            "customer_age": {"18-30": 0.40, "31-45": 0.35, "46-60": 0.20, "60+": 0.05},
            "customer_income": "中等偏下",
            "primary_customer": "工厂职工、企业主",
            "secondary_customer": "物流从业者",
            "potential_customer": "上下游供应商",
        },
        "大学区": {
            "daily_base_visitors": 200,
            "peak_hours": ["11:00-13:00", "16:00-18:00", "20:00-22:00"],
            "conversion_rate": 0.12,
            "avg_transaction": 800,
            "service_radius_km": 2.0,
            "production_base": 60,
            "customer_age": {"18-30": 0.90, "31-45": 0.07, "46-60": 0.02, "60+": 0.01},
            "customer_income": "低",
            "primary_customer": "在校学生、青年教师",
            "secondary_customer": "学生家长",
            "potential_customer": "校园商户",
        },
    }

    def __init__(self):
        self._random = random.Random()
        self._random.seed(42)

    def analyze(
        self,
        zone_type: str,
        area: float,
        staff_count: int,
        competitor_count: int,
        local_enterprise_count: int,
        branch_name: Optional[str] = None,
    ) -> BranchAnalysisResult:
        """
        分析网点竞争力
        
        Args:
            zone_type: 区域类型（商业区/住宅区/工业区/大学区）
            area: 网点面积（平方米）
            staff_count: 员工人数
            competitor_count: 周边竞争网点数量
            local_enterprise_count: 本地企业数量
        
        Returns:
            BranchAnalysisResult: 完整的分析结果
        """
        zone_type = self._normalize_zone_type(zone_type)
        config = self.ZONE_CONFIGS.get(zone_type, self.ZONE_CONFIGS["住宅区"])
        
        branch_id = str(uuid.uuid4())[:8].upper()
        
        # 客流量估算
        traffic = self._estimate_traffic(
            zone_type, area, staff_count, competitor_count, config
        )
        
        # SWOT分析
        swot = self._analyze_swot(
            zone_type, area, staff_count, competitor_count, 
            local_enterprise_count, config, traffic
        )
        
        # 客群画像
        customer_profile = self._build_customer_profile(config)
        
        # 产能潜力
        production_index = self._calc_production_index(
            zone_type, area, staff_count, competitor_count, config
        )
        
        # 业务重点方向
        business_focus = self._determine_business_focus(
            zone_type, competitor_count, customer_profile
        )
        
        # 三年经营预测
        forecast = self._forecast_three_years(
            zone_type, staff_count, production_index, traffic
        )
        
        # 资源配置建议
        resources = self._allocate_resources(
            zone_type, area, staff_count, business_focus
        )
        
        # 投入产出建议
        io_recommendation = self._calc_input_output(
            zone_type, area, staff_count, resources
        )
        
        return BranchAnalysisResult(
            branch_id=f"BR{branch_id}",
            zone_type=zone_type,
            area=area,
            staff_count=staff_count,
            competitor_count=competitor_count,
            local_enterprise_count=local_enterprise_count,
            swot=swot,
            customer_profile=customer_profile,
            traffic_estimate=traffic,
            service_radius_km=config["service_radius_km"],
            production_capacity_index=production_index,
            business_focus=business_focus,
            three_year_forecast=forecast,
            resource_allocation=resources,
            input_output_recommendation=io_recommendation,
        )

    def _normalize_zone_type(self, zone_type: str) -> str:
        mapping = {
            "商业": "商业区", "CBD": "商业区", "商区": "商业区",
            "住宅": "住宅区", "小区": "住宅区", "居民": "住宅区",
            "工业": "工业区", "厂区": "工业区", "产业园": "工业区",
            "大学": "大学区", "高校": "大学区", "校园": "大学区",
        }
        for key, val in mapping.items():
            if key in zone_type:
                return val
        if zone_type in self.ZONE_CONFIGS:
            return zone_type
        return "住宅区"

    def _estimate_traffic(
        self, zone_type: str, area: float, staff_count: int,
        competitor_count: int, config: Dict
    ) -> TrafficEstimate:
        base = config["daily_base_visitors"]
        
        # 面积修正
        area_factor = min(1.5, max(0.5, area / 200))
        
        # 竞争修正
        if competitor_count == 0:
            comp_factor = 1.3
        elif competitor_count <= 2:
            comp_factor = 1.0
        elif competitor_count <= 5:
            comp_factor = 0.8
        else:
            comp_factor = 0.6
        
        # 人力修正
        staff_factor = min(1.2, max(0.7, staff_count / 8))
        
        daily = int(base * area_factor * comp_factor * staff_factor)
        
        return TrafficEstimate(
            daily_visitors=daily,
            peak_hours=config["peak_hours"],
            conversion_rate=config["conversion_rate"],
            weekend_multiplier=1.3 if zone_type == "商业区" else 1.15,
        )

    def _analyze_swot(
        self, zone_type: str, area: float, staff_count: int,
        competitor_count: int, local_enterprise_count: int,
        config: Dict, traffic: TrafficEstimate
    ) -> SWOT:
        
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []
        
        # 优势
        if area > 250:
            strengths.append("网点面积较大，可提供更完善的客户服务空间")
        if staff_count >= 10:
            strengths.append("人员配置充足，可实现较好的客户服务")
        if competitor_count <= 2:
            strengths.append("周边竞争压力较小，市场空间充裕")
        if zone_type == "商业区":
            strengths.append("商业区客流量大，品牌曝光度高")
        if traffic.daily_visitors > 200:
            strengths.append(f"日均来访量{traffic.daily_visitors}人，客流充沛")
        strengths.append(f"{zone_type}客群特点鲜明，需求明确")
        
        # 劣势
        if area < 150:
            weaknesses.append("网点面积受限，空间布局受限")
        if staff_count < 6:
            weaknesses.append("人员配置偏紧，高峰时段服务能力不足")
        if competitor_count > 5:
            weaknesses.append("周边竞争激烈，市场分流严重")
        if zone_type == "大学区":
            weaknesses.append("客群消费能力有限，附加值业务开发难度大")
        weaknesses.append("数字化服务能力待提升")
        weaknesses.append("特色业务竞争力不明显")
        
        # 机会
        if local_enterprise_count > 30:
            opportunities.append(f"周边有{local_enterprise_count}家企业，对公业务潜力大")
        if zone_type in ["住宅区", "大学区"]:
            opportunities.append("深耕社区/校园生态，积累年轻客户群体")
        opportunities.append("数字化转型带来服务效率提升机会")
        opportunities.append("消费金融需求持续增长")
        
        # 威胁
        if competitor_count > 3:
            threats.append("周边竞争网点密集，价格竞争加剧")
        threats.append("互联网金融分流传统客群")
        threats.append("监管政策趋严影响部分业务发展")
        threats.append("人力成本持续上升压缩利润空间")
        
        return SWOT(
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            threats=threats,
        )

    def _build_customer_profile(self, config: Dict) -> CustomerProfile:
        return CustomerProfile(
            primary=config.get("primary_customer", ""),
            secondary=config.get("secondary_customer", ""),
            potential=config.get("potential_customer", ""),
            age_distribution=config.get("customer_age", {}),
            income_level=config.get("customer_income", "中等"),
        )

    def _calc_production_index(
        self, zone_type: str, area: float, staff_count: int,
        competitor_count: int, config: Dict
    ) -> float:
        base = config["production_base"]
        # 面积效率
        area_eff = min(1.4, max(0.6, area / 200))
        # 人员效率
        staff_eff = min(1.3, max(0.7, staff_count / 8))
        # 竞争压力
        comp_factor = 1.0 if competitor_count <= 2 else 0.85
        
        index = base * area_eff * staff_eff * comp_factor
        return round(index, 2)

    def _determine_business_focus(
        self, zone_type: str, competitor_count: int,
        customer: CustomerProfile
    ) -> List[str]:
        focus_map = {
            "商业区": [
                "财富管理及私人银行业务",
                "商户收单及结算服务",
                "消费信贷与信用卡业务",
                "企业开户及对公业务",
                "跨境金融服务",
            ],
            "住宅区": [
                "住房贷款及装修分期",
                "家庭综合理财服务",
                "子女教育金规划",
                "社区商户结算服务",
                "代发工资及养老金业务",
            ],
            "工业区": [
                "企业贷款及供应链金融",
                "现金管理及对公结算",
                "设备融资租赁",
                "员工代发工资业务",
                "进出口结算服务",
            ],
            "大学区": [
                "校园一卡通及电子银行业务",
                "学生信用卡及消费分期",
                "创业贷款及启动金服务",
                "教育培训分期",
                "年轻客户长期财富积累计划",
            ],
        }
        base_focus = focus_map.get(zone_type, focus_map["住宅区"])
        
        if competitor_count > 4:
            base_focus = base_focus[1:]  # 去掉竞争激烈的首项
        
        return base_focus[:4]

    def _forecast_three_years(
        self, zone_type: str, staff_count: int,
        production_index: float, traffic: TrafficEstimate
    ) -> List[YearForecast]:
        base_revenue = staff_count * production_index
        base_customers = int(traffic.daily_visitors * traffic.conversion_rate * 365 * 0.3)
        
        growth_rates = {
            "商业区": (0.15, 0.12, 0.10),
            "住宅区": (0.12, 0.10, 0.08),
            "工业区": (0.10, 0.08, 0.08),
            "大学区": (0.20, 0.15, 0.12),
        }
        rates = growth_rates.get(zone_type, (0.10, 0.08, 0.08))
        
        market_shares = {
            "商业区": (0.08, 0.09, 0.10),
            "住宅区": (0.12, 0.13, 0.14),
            "工业区": (0.10, 0.11, 0.12),
            "大学区": (0.06, 0.08, 0.10),
        }
        shares = market_shares.get(zone_type, (0.10, 0.11, 0.12))
        
        forecasts = []
        cum_growth = 1.0
        cum_share = shares[0]
        
        for i, (gr, ms) in enumerate(zip(rates, shares), 1):
            cum_growth *= (1 + gr)
            rev = base_revenue * cum_growth
            cust = int(base_customers * cum_growth)
            forecasts.append(YearForecast(
                year=2026 + i,
                revenue=round(rev, 1),
                customers=cust,
                market_share=round(ms, 3),
            ))
        
        return forecasts

    def _allocate_resources(
        self, zone_type: str, area: float, staff_count: int,
        business_focus: List[str]
    ) -> ResourceAllocation:
        # 人员分配
        front_desk = max(2, int(staff_count * 0.35))
        sales = max(2, int(staff_count * 0.40))
        back_office = max(1, staff_count - front_desk - sales)
        
        # 设备配置
        equipment = ["智能柜员机(ATM/ITM)", "自助服务终端", "排队叫号系统"]
        if zone_type == "商业区":
            equipment.append("移动展业设备")
            equipment.append("外汇兑换机")
        if zone_type == "大学区":
            equipment.append("校园一卡通充值机")
            equipment.append("刷脸支付终端")
        if area > 250:
            equipment.append("贵宾服务区设备")
        
        # 营销预算
        budget_map = {
            "商业区": 45.0,
            "住宅区": 25.0,
            "工业区": 35.0,
            "大学区": 20.0,
        }
        base_budget = budget_map.get(zone_type, 25.0)
        budget = base_budget * (staff_count / 8)
        
        return ResourceAllocation(
            staff_front_desk=front_desk,
            staff_sales=sales,
            staff_back_office=back_office,
            equipment=equipment,
            marketing_budget=round(budget, 1),
        )

    def _calc_input_output(
        self, zone_type: str, area: float, staff_count: int,
        resources: ResourceAllocation
    ) -> InputOutputRecommendation:
        # 初始投资估算
        area_invest = area * 0.3  # 万元 (装修等)
        equip_invest = len(resources.equipment) * 3.0
        initial = area_invest + equip_invest + 20.0  # 其他
        
        # 年度运营成本
        annual_cost = staff_count * 12.0 + resources.marketing_budget + 30.0
        
        # 年度收益（基于资源配置反推）
        revenue_map = {
            "商业区": staff_count * 180,
            "住宅区": staff_count * 100,
            "工业区": staff_count * 220,
            "大学区": staff_count * 60,
        }
        annual_revenue = revenue_map.get(zone_type, staff_count * 100)
        
        net_profit_y1 = annual_revenue - annual_cost
        roi = (net_profit_y1 / initial) * 100 if initial > 0 else 0
        payback = int(initial / (net_profit_y1 / 12)) if net_profit_y1 > 0 else 36
        
        risk_map = {
            "商业区": "中",
            "住宅区": "低",
            "工业区": "中高",
            "大学区": "中",
        }
        
        return InputOutputRecommendation(
            initial_investment=round(initial, 1),
            expected_roi=round(roi, 1),
            payback_period=max(12, min(60, payback)),
            risk_level=risk_map.get(zone_type, "中"),
        )

    def generate_report(self, result: BranchAnalysisResult) -> str:
        """生成格式化分析报告"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"         网点竞争力分析报告  [{result.branch_id}]")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"【基本信息】")
        lines.append(f"  区域类型：{result.zone_type}")
        lines.append(f"  网点面积：{result.area} 平方米")
        lines.append(f"  员工人数：{result.staff_count} 人")
        lines.append(f"  竞争网点：{result.competitor_count} 个")
        lines.append(f"  本地企业：{result.local_enterprise_count} 家")
        lines.append("")
        
        lines.append("【SWOT分析】")
        lines.append(f"  ✓ 优势:")
        for s in result.swot.strengths:
            lines.append(f"    · {s}")
        lines.append(f"  ✗ 劣势:")
        for w in result.swot.weaknesses:
            lines.append(f"    · {w}")
        lines.append(f"  ★ 机会:")
        for o in result.swot.opportunities:
            lines.append(f"    · {o}")
        lines.append(f"  ⚠ 威胁:")
        for t in result.swot.threats:
            lines.append(f"    · {t}")
        lines.append("")
        
        lines.append("【客群画像】")
        lines.append(f"  主要客群：{result.customer_profile.primary}")
        lines.append(f"  次要客群：{result.customer_profile.secondary}")
        lines.append(f"  潜力客群：{result.customer_profile.potential}")
        lines.append(f"  收入水平：{result.customer_profile.income_level}")
        lines.append("")
        
        lines.append("【客流量预估】")
        lines.append(f"  日均来访：{result.traffic_estimate.daily_visitors} 人次")
        lines.append(f"  高峰时段：{', '.join(result.traffic_estimate.peak_hours)}")
        lines.append(f"  转化率：{result.traffic_estimate.conversion_rate*100:.1f}%")
        lines.append(f"  服务半径：{result.service_radius_km} km")
        lines.append("")
        
        lines.append("【产能潜力】")
        lines.append(f"  产能指数：{result.production_capacity_index} 万元/人/年")
        lines.append("")
        
        lines.append("【重点发展业务】")
        for i, bf in enumerate(result.business_focus, 1):
            lines.append(f"  {i}. {bf}")
        lines.append("")
        
        lines.append("【三年经营预测】")
        for f in result.three_year_forecast:
            lines.append(
                f"  {f.year}年：营收 {f.revenue} 万元，"
                f"有效客户 {f.customers} 户，份额 {f.market_share*100:.1f}%"
            )
        lines.append("")
        
        lines.append("【资源配置建议】")
        r = result.resource_allocation
        lines.append(f"  前台柜员：{r.staff_front_desk} 人")
        lines.append(f"  营销人员：{r.staff_sales} 人")
        lines.append(f"  后台支持：{r.staff_back_office} 人")
        lines.append(f"  营销预算：{r.marketing_budget} 万元/年")
        lines.append(f"  设备配置：{', '.join(r.equipment)}")
        lines.append("")
        
        lines.append("【投入产出建议】")
        io = result.input_output_recommendation
        lines.append(f"  初始投资：{io.initial_investment} 万元")
        lines.append(f"  预期ROI：{io.expected_roi}%")
        lines.append(f"  回收周期：{io.payback_period} 个月")
        lines.append(f"  风险等级：{io.risk_level}")
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)


def parse_cli_input(text: str) -> Dict[str, Any]:
    """解析CLI文本输入"""
    params = {}
    
    zone_map = {"商业区": "商业区", "商业": "商业区", "CBD": "商业区",
                "住宅区": "住宅区", "住宅": "住宅区", "小区": "住宅区",
                "工业区": "工业区", "工业": "工业区",
                "大学区": "大学区", "大学": "大学区", "校园": "大学区"}
    
    for kw, val in zone_map.items():
        if kw in text:
            params["zone_type"] = val
            break
    if "zone_type" not in params:
        params["zone_type"] = "住宅区"
    
    import re
    staff_match = re.search(r'(\d+)\s*[人人]', text)
    if staff_match:
        params["staff_count"] = int(staff_match.group(1))
    else:
        params["staff_count"] = 8
    
    comp_match = re.search(r'(\d+)\s*个?\s*竞争', text)
    if comp_match:
        params["competitor_count"] = int(comp_match.group(1))
    else:
        params["competitor_count"] = 2
    
    ent_match = re.search(r'(\d+)\s*[家家企]', text)
    if ent_match:
        params["local_enterprise_count"] = int(ent_match.group(1))
    else:
        params["local_enterprise_count"] = 20
    
    area_match = re.search(r'(\d+)\s*(平米|平方米|平)', text)
    if area_match:
        params["area"] = float(area_match.group(1))
    else:
        params["area"] = 200.0
    
    return params
