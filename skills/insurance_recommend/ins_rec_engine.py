"""
Insurance Recommendation Engine - 保险产品智能推荐引擎
根据客户画像生成保险产品推荐方案
"""

from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class FamilyInfo:
    """家庭信息"""
    married: bool = False
    children: list = field(default_factory=list)
    dependents: int = 0  # 赡养父母数量


@dataclass
class Liabilities:
    """负债信息"""
    mortgage: float = 0.0
    car_loan: float = 0.0
    other_debt: float = 0.0

    @property
    def total(self) -> float:
        return self.mortgage + self.car_loan + self.other_debt


@dataclass
class ExistingPolicy:
    """已有保单"""
    type: str
    coverage: float
    annual_premium: float = 0.0


@dataclass
class CustomerProfile:
    """客户画像"""
    age: int
    gender: str  # male/female
    family: FamilyInfo = field(default_factory=FamilyInfo)
    annual_income: float = 0.0
    existing_policies: list = field(default_factory=list)
    liabilities: Liabilities = field(default_factory=Liabilities)
    budget_percent: float = 0.1  # 保费占年收入比例
    health_status: str = "good"  # good/average/poor

    @property
    def total_debt(self) -> float:
        return self.liabilities.total

    def has_policy_type(self, policy_type: str) -> bool:
        """检查是否已有某类保险"""
        for p in self.existing_policies:
            if policy_type in p.type:
                return True
        return False


@dataclass
class ProtectionGap:
    """保障缺口"""
    life_insurance_gap: float = 0.0
    critical_illness_gap: float = 0.0
    medical_gap: float = 0.0
    accident_gap: float = 0.0

    def total_gap(self) -> float:
        return (self.life_insurance_gap +
                self.critical_illness_gap +
                self.medical_gap +
                self.accident_gap)


@dataclass
class Recommendation:
    """单个推荐项"""
    priority: int
    insurance_type: str
    product_matching: str
    coverage: float
    annual_premium: float
    policy_term: str
    reason: str
    key_benefits: list


@dataclass
class FamilyProtectionOverview:
    """家庭保障全景"""
    total_coverage_needed: float
    current_coverage: float
    gap: float
    priority_order: list


class InsuranceRecommendEngine:
    """
    保险产品智能推荐引擎

    推荐原则：
    1. 先保障后理财
    2. 先大人后小孩
    3. 先家庭经济支柱

    保额计算：
    - 寿险 = 10倍年收入 + 负债
    - 意外 = 10倍年收入
    - 医疗 = 300万+
    - 重疾 = 3~5倍年收入
    """

    # 产品知识库（示例）
    PRODUCT_DB = {
        "定期寿险": [
            {
                "name": "华贵大麦2024定期寿险",
                "min_age": 18,
                "max_age": 60,
                "coverage_range": (10, 400),
                "annual_premium_rate": 0.001,  # 每10万保额约100元
                "features": ["健康告知宽松", "免责条款少", "性价比高"],
                "suitable_for": ["家庭支柱", "有房贷者", "经济压力大的中年人"]
            },
            {
                "name": "中信保诚祯祥定期寿险",
                "min_age": 18,
                "max_age": 55,
                "coverage_range": (50, 300),
                "annual_premium_rate": 0.0012,
                "features": ["大品牌", "服务网络广", "核保相对宽松"],
                "suitable_for": ["高收入家庭", "企业主"]
            },
            {
                "name": "阳光人寿甜蜜家2024",
                "min_age": 18,
                "max_age": 50,
                "coverage_range": (100, 500),
                "annual_premium_rate": 0.0015,
                "features": ["夫妻共保", "双豁免", "专属保障"],
                "suitable_for": ["已婚夫妻", "双收入家庭"]
            }
        ],
        "终身寿险": [
            {
                "name": "同方全球传世荣耀终身寿险",
                "min_age": 18,
                "max_age": 65,
                "coverage_range": (30, 1000),
                "annual_premium_rate": 0.015,
                "features": ["现金价值增长快", "可贷款", "资产传承"],
                "suitable_for": ["高净值人群", "有传承需求", "企业主"]
            },
            {
                "name": "平安守护百分百2024",
                "min_age": 18,
                "max_age": 55,
                "coverage_range": (20, 500),
                "annual_premium_rate": 0.018,
                "features": ["大品牌", "附加重疾", "返还保费"],
                "suitable_for": ["中产家庭", "偏好返还型"]
            }
        ],
        "意外险": [
            {
                "name": "平安小顽童5号少儿意外险",
                "min_age": 0,
                "max_age": 17,
                "coverage_range": (10, 80),
                "annual_premium_rate": 0.002,
                "features": ["少儿专属", "含烧烫伤", "含骨折"],
                "suitable_for": ["0-17岁儿童"]
            },
            {
                "name": "人保大护甲6号成人意外险",
                "min_age": 18,
                "max_age": 60,
                "coverage_range": (30, 300),
                "annual_premium_rate": 0.0015,
                "features": ["含猝死", "含住院津贴", "交通额外赔"],
                "suitable_for": ["成人", "上班族", "出差族"]
            },
            {
                "name": "美亚畅游天下意外险",
                "min_age": 1,
                "max_age": 85,
                "coverage_range": (10, 100),
                "annual_premium_rate": 0.003,
                "features": ["含全球紧急救援", "含医疗送返"],
                "suitable_for": ["出境旅游", "海外务工"]
            }
        ],
        "医疗险": [
            {
                "name": "太平洋蓝医保长期医疗险",
                "min_age": 0,
                "max_age": 65,
                "coverage_range": (200, 400),
                "annual_premium_rate": 0.00075,
                "features": ["20年保证续保", "含质子重离子", "含CAR-T"],
                "suitable_for": ["全年龄段", "追求长期保障"]
            },
            {
                "name": "平安e生保长期医疗险",
                "min_age": 0,
                "max_age": 55,
                "coverage_range": (200, 400),
                "annual_premium_rate": 0.0008,
                "features": ["20年保证续保", "大品牌", "增值服务全"],
                "suitable_for": ["重视品牌", "追求稳定"]
            },
            {
                "name": "众安尊享e生2024版",
                "min_age": 0,
                "max_age": 70,
                "coverage_range": (100, 600),
                "annual_premium_rate": 0.001,
                "features": ["最高600万", "含赴日医疗", "含罕见病"],
                "suitable_for": ["追求高保额", "癌症高危人群"]
            }
        ],
        "重疾险": [
            {
                "name": "国联人寿明爱易心重大疾病保险",
                "min_age": 28,
                "max_age": 55,
                "coverage_range": (10, 100),
                "annual_premium_rate": 0.01,
                "features": ["重疾额外赔", "轻症不分组", "性价比高"],
                "suitable_for": ["成人", "追求高性价比"]
            },
            {
                "name": "信泰完美人生守护2024",
                "min_age": 28,
                "max_age": 50,
                "coverage_range": (30, 80),
                "annual_premium_rate": 0.012,
                "features": ["多次赔付", "癌症二次赔", "少儿特疾额外赔"],
                "suitable_for": ["少儿", "家族癌症史"]
            },
            {
                "name": "友邦友如意顺心版",
                "min_age": 18,
                "max_age": 55,
                "coverage_range": (20, 100),
                "annual_premium_rate": 0.015,
                "features": ["大品牌", "分组合理", "增值服务多"],
                "suitable_for": ["高收入家庭", "重视品牌服务"]
            }
        ],
        "年金险": [
            {
                "name": "太平岁岁金生年金保险",
                "min_age": 28,
                "max_age": 60,
                "min_premium": 12000,
                "annual_return_rate": 0.035,
                "features": ["对接养老社区", "万能账户", "养老金保证领取"],
                "suitable_for": ["养老规划", "中产以上家庭"]
            },
            {
                "name": "中国人寿鑫享今生",
                "min_age": 28,
                "max_age": 55,
                "min_premium": 10000,
                "annual_return_rate": 0.032,
                "features": ["大品牌", "短期交费", "固定返还"],
                "suitable_for": ["保守型", "短期理财替代"]
            }
        ],
        "防癌险": [
            {
                "name": "平安防癌卫士2024",
                "min_age": 45,
                "max_age": 80,
                "coverage_range": (10, 100),
                "annual_premium_rate": 0.008,
                "features": ["三高可投保", "原位癌可赔", "确诊即赔"],
                "suitable_for": ["老年人", "三高人群", "癌症高危"]
            }
        ]
    }

    def __init__(self):
        pass

    def calculate_protection_gap(self, profile: CustomerProfile) -> ProtectionGap:
        """计算保障缺口"""
        income = profile.annual_income

        # 寿险需求 = 10倍年收入 + 负债 - 已有寿险保额
        life_coverage_needed = income * 10 + profile.total_debt
        life_existing = self._get_existing_coverage(profile, ["寿险", "定期寿险", "终身寿险"])
        life_gap = max(0, life_coverage_needed - life_existing)

        # 重疾险 = 3~5倍年收入（取中间值4倍）
        ci_coverage_needed = income * 4
        ci_existing = self._get_existing_coverage(profile, ["重疾", "重大疾病"])
        ci_gap = max(0, ci_coverage_needed - ci_existing)

        # 医疗险 = 300万+
        medical_coverage_needed = 3000000
        medical_existing = self._get_existing_coverage(profile, ["医疗", "住院", "百万医疗"])
        medical_gap = max(0, medical_coverage_needed - medical_existing)

        # 意外险 = 10倍年收入
        accident_coverage_needed = income * 10
        accident_existing = self._get_existing_coverage(profile, ["意外"])
        accident_gap = max(0, accident_coverage_needed - accident_existing)

        return ProtectionGap(
            life_insurance_gap=life_gap,
            critical_illness_gap=ci_gap,
            medical_gap=medical_gap,
            accident_gap=accident_gap
        )

    def _get_existing_coverage(self, profile: CustomerProfile, types: list) -> float:
        """获取已有保单中某类保险的保额"""
        total = 0.0
        for policy in profile.existing_policies:
            for ptype in types:
                if ptype in policy.type:
                    total += policy.coverage
        return total

    def _get_priority_order(self, profile: CustomerProfile) -> list:
        """根据客户角色确定险种优先级"""
        age = profile.age
        has_children = len(profile.family.children) > 0
        is_married = profile.family.married

        # 未婚青年
        if not is_married:
            return ["意外险", "医疗险", "重疾险", "定期寿险"]

        # 已婚无孩子
        if not has_children:
            return ["定期寿险", "意外险", "医疗险", "重疾险"]

        # 已婚有孩子
        if has_children:
            return ["定期寿险", "意外险", "医疗险", "重疾险", "终身寿险"]

        # 中年家庭支柱
        if age >= 45:
            return ["医疗险", "意外险", "重疾险", "防癌险"]

        return ["定期寿险", "意外险", "医疗险", "重疾险"]

    def _match_product(self, insurance_type: str, profile: CustomerProfile,
                       coverage: float) -> tuple:
        """匹配最适合的产品"""
        products = self.PRODUCT_DB.get(insurance_type, [])

        if not products:
            return f"{insurance_type}（通用型）", coverage, [], "行业标准产品"

        # 筛选适合该客户的产品
        suitable = []
        for p in products:
            if p["min_age"] <= profile.age <= p["max_age"]:
                suitable.append(p)

        if not suitable:
            suitable = products  # 如果没有完全匹配的，退回全部

        # 选择第一个（最合适的）
        selected = suitable[0]

        # 根据目标保额调整
        if "coverage_range" in selected:
            min_cov, max_cov = selected["coverage_range"]
            actual_coverage = min(max_cov * 10000, max(min_cov * 10000, coverage))
        else:
            actual_coverage = coverage

        # 计算保费
        if "annual_premium_rate" in selected:
            annual_premium = actual_coverage / 10000 * selected["annual_premium_rate"] * 10000
        elif "min_premium" in selected:
            annual_premium = max(selected["min_premium"], coverage * selected.get("annual_return_rate", 0.03))
        else:
            annual_premium = actual_coverage * 0.01

        return (selected["name"], actual_coverage,
                selected.get("features", []), selected.get("suitable_for", []))

    def _generate_reason(self, insurance_type: str, profile: CustomerProfile,
                         coverage: float) -> str:
        """生成推荐理由"""
        reasons = {
            "定期寿险": f"您是家庭经济支柱，年收入{profile.annual_income/10000:.0f}万元，"
                       f"家庭负债{profile.total_debt/10000:.0f}万元。"
                       f"定期寿险保额{coverage/10000:.0f}万元可在不幸身故时保障家人生活。",
            "终身寿险": f"您有资产传承需求，终身寿险可在百年后留给家人确定资产，"
                       f"同时具备现金价值积累功能。",
            "意外险": f"意外风险无处不在，年收入{profile.annual_income/10000:.0f}万元的您"
                    f"需要{coverage/10000:.0f}万元的身价保障。",
            "医疗险": f"大病医疗费用高昂，社保外自付比例大。"
                     f"{coverage/10000:.0f}万元医疗险可覆盖绝大多数治疗费用。",
            "重疾险": f"重疾平均治疗费用30-50万元，加上康复期收入损失，"
                     f"建议配置{coverage/10000:.0f}万元重疾险。",
            "年金险": f"养老规划越早越好，通过年金险提前锁定未来品质生活。",
            "防癌险": f"癌症发病率随年龄增长而上升，{profile.age}岁人群需要重点防范，"
                     f"防癌险确诊即赔，保障更有针对性。"
        }
        return reasons.get(insurance_type, f"推荐配置{insurance_type}以完善家庭保障。")

    def _get_policy_term(self, insurance_type: str, profile: CustomerProfile) -> str:
        """确定保险期间"""
        remaining_working_years = max(0, 65 - profile.age)

        if insurance_type == "定期寿险":
            if profile.family.married and len(profile.family.children) > 0:
                # 有家庭责任，保障到孩子独立
                youngest_child = min([c["age"] for c in profile.family.children]) if profile.family.children else 0
                term = max(10, 22 - youngest_child)
                return f"{term}年"
            return f"{min(30, remaining_working_years)}年"

        if insurance_type == "终身寿险":
            return "终身"

        if insurance_type == "意外险":
            return "1年（续保）"

        if insurance_type in ["医疗险", "重疾险"]:
            return "长期/终身"

        if insurance_type == "年金险":
            return "至养老"

        return "根据需求"

    def _calculate_budget(self, profile: CustomerProfile) -> dict:
        """计算保费预算"""
        total_income = profile.annual_income
        total_budget = total_income * profile.budget_percent

        # 保障型保费上限（70%）
        protection_budget = total_budget * 0.7

        # 理财型保费上限（30%）
        investment_budget = total_budget * 0.3

        return {
            "total_annual": total_budget,
            "by_type": {
                "保障型": protection_budget,
                "理财型": investment_budget
            }
        }

    def generate_recommendation(self,
                                age: int,
                                gender: str,
                                annual_income: float,
                                family: dict = None,
                                existing_policies: list = None,
                                liabilities: dict = None,
                                budget_percent: float = 0.1,
                                health_status: str = "good",
                                **kwargs) -> dict:
        """
        生成保险推荐方案

        Args:
            age: 年龄
            gender: 性别 male/female
            annual_income: 年收入（元）
            family: 家庭结构 {"married": bool, "children": [{"age": int}], "dependents": int}
            existing_policies: 已有保单 [{"type": str, "coverage": float}]
            liabilities: 负债 {"mortgage": float, "car_loan": float, "other_debt": float}
            budget_percent: 保费占年收入比例
            health_status: 健康状况 good/average/poor

        Returns:
            dict: 完整的推荐方案
        """
        # 构建客户画像
        fam = FamilyInfo(
            married=family.get("married", False) if family else False,
            children=family.get("children", []) if family else [],
            dependents=family.get("dependents", 0) if family else 0
        )

        liab = Liabilities(
            mortgage=liabilities.get("mortgage", 0) if liabilities else 0,
            car_loan=liabilities.get("car_loan", 0) if liabilities else 0,
            other_debt=liabilities.get("other_debt", 0) if liabilities else 0
        )

        existing = []
        if existing_policies:
            for p in existing_policies:
                existing.append(ExistingPolicy(
                    type=p.get("type", ""),
                    coverage=p.get("coverage", 0),
                    annual_premium=p.get("annual_premium", 0)
                ))

        profile = CustomerProfile(
            age=age,
            gender=gender,
            family=fam,
            annual_income=annual_income,
            existing_policies=existing,
            liabilities=liab,
            budget_percent=budget_percent,
            health_status=health_status
        )

        # 计算保障缺口
        gap = self.calculate_protection_gap(profile)

        # 获取优先级
        priority_order = self._get_priority_order(profile)

        # 生成推荐列表
        recommendations = []
        priority = 1

        # 保额分配权重
        allocation = {
            "定期寿险": gap.life_insurance_gap,
            "意外险": gap.accident_gap,
            "医疗险": gap.medical_gap,
            "重疾险": gap.critical_illness_gap,
            "终身寿险": max(0, profile.annual_income * 5) if profile.age < 50 else 0,
            "年金险": 0,
            "防癌险": 500000 if profile.age >= 45 else 0
        }

        for ins_type in priority_order:
            coverage_needed = allocation.get(ins_type, 0)

            # 跳过已有充足保障的险种
            if ins_type == "定期寿险" and gap.life_insurance_gap <= 0:
                continue
            if ins_type == "意外险" and gap.accident_gap <= 0:
                continue
            if ins_type == "医疗险" and gap.medical_gap <= 0:
                continue
            if ins_type == "重疾险" and gap.critical_illness_gap <= 0:
                continue

            # 跳过不匹配的险种
            if ins_type == "防癌险" and profile.age < 45:
                continue
            if ins_type == "年金险" and profile.age > 55:
                continue

            product_name, coverage, features, suitable_for = self._match_product(
                ins_type, profile, coverage_needed
            )

            annual_premium = self._calculate_premium(ins_type, coverage, profile)

            recommendations.append(Recommendation(
                priority=priority,
                insurance_type=ins_type,
                product_matching=product_name,
                coverage=coverage,
                annual_premium=annual_premium,
                policy_term=self._get_policy_term(ins_type, profile),
                reason=self._generate_reason(ins_type, profile, coverage),
                key_benefits=features
            ))
            priority += 1

        # 计算总保额和当前覆盖
        total_needed = gap.life_insurance_gap + gap.critical_illness_gap + \
                      gap.medical_gap + gap.accident_gap
        current_cov = sum(p.coverage for p in profile.existing_policies)

        # 计算保费预算
        premium_budget = self._calculate_budget(profile)

        return {
            "customer_profile": {
                "age": profile.age,
                "gender": "男性" if profile.gender == "male" else "女性",
                "annual_income": f"{profile.annual_income/10000:.1f}万元",
                "family_status": self._describe_family(profile),
                "health_status": profile.health_status,
                "total_debt": f"{profile.total_debt/10000:.1f}万元",
                "existing_policies_count": len(profile.existing_policies)
            },
            "protection_gap": {
                "定期寿险缺口": f"{gap.life_insurance_gap/10000:.0f}万元",
                "重疾险缺口": f"{gap.critical_illness_gap/10000:.0f}万元",
                "医疗险缺口": f"{gap.medical_gap/10000:.0f}万元",
                "意外险缺口": f"{gap.accident_gap/10000:.0f}万元"
            },
            "recommendations": [
                {
                    "priority": r.priority,
                    "insurance_type": r.insurance_type,
                    "product_matching": r.product_matching,
                    "coverage": f"{r.coverage/10000:.0f}万元",
                    "annual_premium": f"{r.annual_premium:.0f}元",
                    "policy_term": r.policy_term,
                    "reason": r.reason,
                    "key_benefits": r.key_benefits
                }
                for r in recommendations
            ],
            "family_protection_overview": {
                "total_coverage_needed": f"{total_needed/10000:.0f}万元",
                "current_coverage": f"{current_cov/10000:.0f}万元",
                "gap": f"{(total_needed - current_cov)/10000:.0f}万元",
                "priority_order": priority_order
            },
            "premium_budget": {
                "total_annual": f"{premium_budget['total_annual']:.0f}元",
                "by_type": {
                    k: f"{v:.0f}元" for k, v in premium_budget["by_type"].items()
                },
                "note": f"占年收入{profile.budget_percent*100:.0f}%，符合行业标准（5%-20%）"
            }
        }

    def _calculate_premium(self, ins_type: str, coverage: float,
                          profile: CustomerProfile) -> float:
        """计算保费"""
        coverage_wan = coverage / 10000

        rates = {
            "定期寿险": 0.001,   # 每10万约100元
            "终身寿险": 0.015,
            "意外险": 0.0015,
            "医疗险": 0.001,     # 蓝医保约300元/400万
            "重疾险": 0.012,
            "年金险": 0.03,
            "防癌险": 0.008
        }

        rate = rates.get(ins_type, 0.01)

        if ins_type == "定期寿险":
            return coverage_wan * 100  # 简化计算
        elif ins_type == "医疗险":
            return 300 + (coverage_wan - 200) * 2 if coverage_wan > 200 else 300
        elif ins_type == "意外险":
            return coverage_wan * 10
        elif ins_type == "年金险":
            return min(20000, coverage_wan * 2000)
        else:
            return coverage_wan * 1000 * rate

    def _describe_family(self, profile: CustomerProfile) -> str:
        """描述家庭状况"""
        parts = []
        if profile.family.married:
            parts.append("已婚")
        else:
            parts.append("未婚")

        if profile.family.children:
            child_count = len(profile.family.children)
            child_ages = [c.get("age", 0) for c in profile.family.children]
            parts.append(f"{child_count}个孩子(年龄:{','.join(map(str, child_ages))})")
        else:
            parts.append("无孩子")

        if profile.family.dependents > 0:
            parts.append(f"需赡养父母{profile.family.dependents}位")

        return "".join(parts)

    @staticmethod
    def parse_natural_language(text: str) -> dict:
        """
        解析自然语言输入
        例如: "保险推荐 30岁男性 已婚 孩子1岁 年收入30万 已有医保"
        """
        result = {
            "age": 30,
            "gender": "male",
            "annual_income": 300000,
            "family": {"married": False, "children": [], "dependents": 0},
            "existing_policies": [],
            "liabilities": {"mortgage": 0, "car_loan": 0, "other_debt": 0},
            "health_status": "good"
        }

        text = text.strip()

        # 解析年龄
        age_match = re.search(r"(\d{2})岁", text)
        if age_match:
            result["age"] = int(age_match.group(1))

        # 解析性别
        if "女性" in text or "女" in text:
            result["gender"] = "female"
        elif "男性" in text or "男" in text:
            result["gender"] = "male"

        # 解析婚姻状态
        if "已婚" in text:
            result["family"]["married"] = True
        elif "未婚" in text:
            result["family"]["married"] = False

        # 解析孩子
        child_matches = re.findall(r"孩子(\d+)岁|孩子(\d+)个", text)
        for match in child_matches:
            if match[0]:  # 孩子X岁
                result["family"]["children"].append({"age": int(match[0])})
            elif match[1]:  # 孩子X个
                for _ in range(int(match[1])):
                    result["family"]["children"].append({"age": 0})

        # 解析年收入
        income_match = re.search(r"年收入?(\d+(?:\.\d+)?)\s*(万|元)", text)
        if income_match:
            value = float(income_match.group(1))
            unit = income_match.group(2)
            result["annual_income"] = value * 10000 if unit == "万" else value

        # 解析已有保单
        if "医保" in text:
            result["existing_policies"].append({"type": "医保", "coverage": 100000})
        if "社保" in text:
            result["existing_policies"].append({"type": "社保", "coverage": 50000})
        if "商业险" in text or "商业保险" in text:
            result["existing_policies"].append({"type": "商业医疗", "coverage": 1000000})
        if "寿险" in text:
            result["existing_policies"].append({"type": "寿险", "coverage": 500000})
        if "重疾" in text:
            result["existing_policies"].append({"type": "重疾险", "coverage": 300000})
        if "意外" in text:
            result["existing_policies"].append({"type": "意外险", "coverage": 500000})

        # 解析房贷
        mortgage_match = re.search(r"房贷(\d+(?:\.\d+)?)\s*(万|元)", text)
        if mortgage_match:
            value = float(mortgage_match.group(1))
            unit = mortgage_match.group(2)
            result["liabilities"]["mortgage"] = value * 10000 if unit == "万" else value

        return result


def main():
    """CLI入口"""
    import sys
    import json

    if len(sys.argv) < 2:
        print("用法: python ins_rec_engine.py generate <描述>")
        print("示例: python ins_rec_engine.py generate '保险推荐 30岁男性 已婚 孩子1岁 年收入30万 已有医保'")
        sys.exit(1)

    command = sys.argv[1]

    if command == "generate":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if not text:
            print("请提供描述文本")
            sys.exit(1)

        engine = InsuranceRecommendEngine()
        params = engine.parse_natural_language(text)

        print(f"\n📋 解析客户信息: {json.dumps(params, ensure_ascii=False, indent=2)}\n")

        result = engine.generate_recommendation(**params)

        print("=" * 60)
        print("🛡️  保险产品智能推荐方案")
        print("=" * 60)

        print(f"\n【客户画像】")
        profile = result["customer_profile"]
        for k, v in profile.items():
            print(f"  {k}: {v}")

        print(f"\n【保障缺口分析】")
        for k, v in result["protection_gap"].items():
            print(f"  {k}: {v}")

        print(f"\n【推荐方案】(按优先级)")
        for rec in result["recommendations"]:
            print(f"\n  {rec['priority']}. {rec['insurance_type']} - {rec['product_matching']}")
            print(f"     保额: {rec['coverage']} | 年保费: {rec['annual_premium']} | 期间: {rec['policy_term']}")
            print(f"     理由: {rec['reason']}")
            if rec['key_benefits']:
                print(f"     亮点: {', '.join(rec['key_benefits'])}")

        print(f"\n【家庭保障全景】")
        overview = result["family_protection_overview"]
        for k, v in overview.items():
            if k != "priority_order":
                print(f"  {k}: {v}")
        print(f"  投保优先级: {' → '.join(overview['priority_order'])}")

        print(f"\n【保费预算】")
        budget = result["premium_budget"]
        print(f"  年度总保费: {budget['total_annual']}")
        for k, v in budget["by_type"].items():
            print(f"    {k}: {v}")
        print(f"  {budget['note']}")

        print("\n" + "=" * 60)
        print("⚠️  仅供参考，具体方案请咨询专业保险顾问")
        print("=" * 60)

    elif command == "parse":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if not text:
            print("请提供描述文本")
            sys.exit(1)

        engine = InsuranceRecommendEngine()
        result = engine.parse_natural_language(text)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {command}")
        print("可用命令: generate, parse")
        sys.exit(1)


if __name__ == "__main__":
    main()
