"""
360 度客户画像生成引擎
=========================

输入：自然语言客户描述 或 结构化字典
输出：CustomerPersona 数据类（含 RFM、生命周期、产品、渠道、话术钩子）

核心规则：
- RFM 标签 → 8 类客户分层（重要价值/重要发展/重要保持/重要挽留/一般价值/一般发展/一般保持/流失）
- 生命周期 → 5 阶段（潜在/新客户/成长/成熟/流失）
- 产品推荐 → 25 个银行常见产品 + 风险偏好/年龄/收入/婚姻/房贷/子女 多维匹配
- 触达渠道 → 5 类（电话/微信/短信/APP推送/线下面访）按年龄+客群优先级排序
- 营销话术 → 12 套钩子模板按生命周期+产品类型匹配
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


# ============== 数据类 ==============

@dataclass
class CustomerInput:
    """客户输入信息（标准化结构）。"""
    name: str = ""
    age: Optional[int] = None
    gender: str = ""  # male/female/unknown
    monthly_income: Optional[float] = None  # 元
    aum: Optional[float] = None  # 资产管理规模（元）
    marital_status: str = ""  # single/married/divorced/widowed
    has_mortgage: bool = False
    has_car_loan: bool = False
    has_children: bool = False
    children_count: int = 0
    risk_preference: str = ""  # conservative/steady/balanced/aggressive
    occupation: str = ""
    last_transaction_days: Optional[int] = None  # 最近一次交易距今天数
    transaction_frequency_year: Optional[int] = None  # 年交易次数
    products_held: List[str] = field(default_factory=list)
    city: str = ""
    raw_text: str = ""

    def is_high_net_worth(self) -> bool:
        return (self.aum or 0) >= 6_000_000

    def income_level(self) -> str:
        m = self.monthly_income or 0
        if m >= 100000: return "super_high"  # 月收入10万+
        if m >= 50000: return "high"        # 月收入5万+
        if m >= 20000: return "middle_high" # 月收入2万+
        if m >= 8000: return "middle"       # 月收入8k+
        return "low"


@dataclass
class CustomerPersona:
    """生成的画像结果。"""
    customer: CustomerInput
    rfm_segment: str  # 8 类客户分层
    rfm_score: Dict[str, int]  # {R: 1-5, F: 1-5, M: 1-5}
    life_cycle_stage: str  # 5 阶段
    recommended_products: List[Dict[str, Any]]  # [{name, reason, priority, expected_yield}]
    contact_channels: List[Dict[str, Any]]  # [{channel, priority, best_time, reason}]
    marketing_hooks: List[Dict[str, Any]]  # [{scenario, hook_text, expected_response}]
    value_tags: List[str]  # 标签集合
    risk_warnings: List[str]
    next_best_action: str  # 下一步最佳动作

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

# ============== RFM 评分模型 ==============

# 年龄分组 → R 默认分
AGE_R_SCORE = {
    (0, 25): 4,    # 年轻人触达敏感，R偏高
    (26, 35): 5,   # 主力客群，活跃
    (36, 50): 4,   # 中年稳定，活跃度中等
    (51, 65): 3,   # 临近退休，交易频率下降
    (66, 120): 2,  # 老年客群
}

# 月收入分组 → M 分数
INCOME_M_SCORE = {
    "super_high": 5,
    "high": 5,
    "middle_high": 4,
    "middle": 3,
    "low": 2,
}

# F 分数基准
FREQUENCY_SCORE = [
    (52, 5),   # 每周一次以上
    (24, 4),   # 每月两次
    (12, 3),   # 每月一次
    (4, 2),    # 每季一次
    (0, 1),    # 低频
]


def _score_r(c: CustomerInput) -> int:
    if c.last_transaction_days is not None:
        if c.last_transaction_days <= 7: return 5
        if c.last_transaction_days <= 30: return 4
        if c.last_transaction_days <= 90: return 3
        if c.last_transaction_days <= 180: return 2
        return 1
    age = c.age or 35
    for (lo, hi), s in AGE_R_SCORE.items():
        if lo <= age <= hi: return s
    return 3


def _score_f(c: CustomerInput) -> int:
    if c.transaction_frequency_year is not None:
        for min_f, s in FREQUENCY_SCORE:
            if c.transaction_frequency_year >= min_f: return s
        return 1
    return 4  # 未知时默认月中水平


def _score_m(c: CustomerInput) -> int:
    return INCOME_M_SCORE.get(c.income_level(), 3)


# RFM 8 类客户分层
RFM_SEGMENTS = {
    (5, 5, 5): "重要价值客户",  # 高R高F高M
    (5, 4, 5): "重要价值客户",
    (5, 5, 4): "重要发展客户",
    (5, 4, 4): "重要发展客户",
    (4, 5, 5): "重要保持客户",
    (4, 4, 5): "重要保持客户",
    (4, 5, 4): "重要保持客户",
    (3, 5, 5): "重要挽留客户",
    (3, 4, 5): "重要挽留客户",
    (5, 3, 3): "一般价值客户",
    (4, 3, 3): "一般发展客户",
    (5, 2, 2): "一般保持客户",
    (3, 2, 2): "一般保持客户",
}

def _rfm_segment(r: int, f: int, m: int) -> str:
    key = (r, f, m)
    if key in RFM_SEGMENTS:
        return RFM_SEGMENTS[key]
    total = r + f + m
    if total >= 12: return "重要价值客户"
    if total >= 10: return "重要发展客户"
    if total >= 8: return "一般发展客户"
    if total >= 6: return "一般保持客户"
    return "流失客户"


# ============== 生命周期 ==============

def _life_cycle(ci: CustomerInput, r: int) -> str:
    if not ci.products_held:
        return "潜在客户"
    if r >= 4 and len(ci.products_held) <= 2:
        return "新客户"
    if r >= 3 and len(ci.products_held) >= 3:
        return "成熟客户"
    if ci.is_high_net_worth() or ci.income_level() in ("super_high", "high"):
        return "成长客户"
    if r <= 2:
        return "流失客户"
    return "成熟客户"


# ============== 产品推荐系统 ==============

# 25 个产品定义
PRODUCT_CATALOG = [
    {
        "name": "灵活宝类活期理财",
        "type": "deposit",
        "risk": "conservative",
        "min_age": 0, "max_age": 999,
        "tags": ["low_barrier", "high_liquidity"],
        "score": 0,
    },
    {
        "name": "大额存单",
        "type": "deposit",
        "risk": "conservative",
        "min_age": 18, "max_age": 999,
        "tags": ["safe", "fixed_term", "high_amount"],
        "score": 0,
    },
    {
        "name": "结构性存款",
        "type": "deposit",
        "risk": "conservative",
        "min_age": 18, "max_age": 999,
        "tags": ["safe", "enhanced_yield"],
        "score": 0,
    },
    {
        "name": "固收+基金",
        "type": "fund",
        "risk": "steady",
        "min_age": 18, "max_age": 999,
        "tags": ["balanced", "mid_term"],
        "score": 0,
    },
    {
        "name": "指数定投",
        "type": "fund",
        "risk": "balanced",
        "min_age": 18, "max_age": 999,
        "tags": ["long_term", "regular_invest", "low_barrier"],
        "score": 0,
    },
    {
        "name": "混合偏股基金",
        "type": "fund",
        "risk": "balanced",
        "min_age": 18, "max_age": 999,
        "tags": ["equity", "mid_long_term"],
        "score": 0,
    },
    {
        "name": "纯债基金",
        "type": "fund",
        "risk": "steady",
        "min_age": 18, "max_age": 999,
        "tags": ["safe", "mid_term", "income"],
        "score": 0,
    },
    {
        "name": "股票型基金",
        "type": "fund",
        "risk": "aggressive",
        "min_age": 18, "max_age": 999,
        "tags": ["high_growth", "long_term", "high_risk"],
        "score": 0,
    },
    {
        "name": "货币基金",
        "type": "fund",
        "risk": "conservative",
        "min_age": 0, "max_age": 999,
        "tags": ["safe", "high_liquidity", "low_yield"],
        "score": 0,
    },
    {
        "name": "教育金规划",
        "type": "insurance",
        "risk": "conservative",
        "min_age": 18, "max_age": 999,
        "tags": ["has_children", "long_term", "education"],
        "score": 0,
    },
    {
        "name": "养老目标基金",
        "type": "fund",
        "risk": "steady",
        "min_age": 25, "max_age": 999,
        "tags": ["long_term", "retirement", "tax_deferred"],
        "score": 0,
    },
    {
        "name": "百万医疗保险",
        "type": "insurance",
        "risk": "conservative",
        "min_age": 0, "max_age": 65,
        "tags": ["health", "low_premium", "high_coverage"],
        "score": 0,
    },
    {
        "name": "重疾险",
        "type": "insurance",
        "risk": "conservative",
        "min_age": 18, "max_age": 55,
        "tags": ["health", "critical_illness", "family_protection"],
        "score": 0,
    },
    {
        "name": "终身寿险",
        "type": "insurance",
        "risk": "conservative",
        "min_age": 25, "max_age": 999,
        "tags": ["wealth_transfer", "asset_protection", "high_net_worth"],
        "score": 0,
    },
    {
        "name": "年金保险",
        "type": "insurance",
        "risk": "conservative",
        "min_age": 30, "max_age": 999,
        "tags": ["retirement", "stable_income", "long_term"],
        "score": 0,
    },
    {
        "name": "信用卡白金卡",
        "type": "credit",
        "risk": "balanced",
        "min_age": 22, "max_age": 999,
        "tags": ["spending", "benefits", "travel"],
        "score": 0,
    },
    {
        "name": "消费贷",
        "type": "loan",
        "risk": "balanced",
        "min_age": 22, "max_age": 999,
        "tags": ["short_term", "spending", "emergency"],
        "score": 0,
    },
    {
        "name": "住房按揭贷款",
        "type": "loan",
        "risk": "balanced",
        "min_age": 22, "max_age": 65,
        "tags": ["home", "large_amount", "long_term"],
        "score": 0,
    },
    {
        "name": "抵押经营贷",
        "type": "loan",
        "risk": "balanced",
        "min_age": 25, "max_age": 999,
        "tags": ["business", "mortgage", "self_employed"],
        "score": 0,
    },
    {
        "name": "小微企业贷",
        "type": "loan",
        "risk": "balanced",
        "min_age": 25, "max_age": 999,
        "tags": ["business", "micro_enterprise", "short_term"],
        "score": 0,
    },
    {
        "name": "家族信托",
        "type": "wealth",
        "risk": "conservative",
        "min_age": 40, "max_age": 999,
        "tags": ["high_net_worth", "wealth_transfer", "asset_protection", "tax"],
        "score": 0,
    },
    {
        "name": "私人银行服务",
        "type": "wealth",
        "risk": "balanced",
        "min_age": 30, "max_age": 999,
        "tags": ["high_net_worth", "concierge", "exclusive", "investment"],
        "score": 0,
    },
    {
        "name": "黄金积存",
        "type": "investment",
        "risk": "balanced",
        "min_age": 18, "max_age": 999,
        "tags": ["safe_haven", "hedge", "regular_invest"],
        "score": 0,
    },
    {
        "name": "券商收益凭证",
        "type": "investment",
        "risk": "steady",
        "min_age": 18, "max_age": 999,
        "tags": ["safe", "enhanced", "principal_protected"],
        "score": 0,
    },
    {
        "name": "海外基金(跨境理财通)",
        "type": "fund",
        "risk": "balanced",
        "min_age": 18, "max_age": 999,
        "tags": ["global", "diversification", "cross_border"],
        "score": 0,
    },
]


def _score_products(ci: CustomerInput) -> List[Dict]:
    """为所有产品评分，返回 Top 6。"""
    scored = []
    for p in PRODUCT_CATALOG:
        s = 0
        # 年龄
        if not (p["min_age"] <= (ci.age or 35) <= p["max_age"]):
            continue
        # 风险匹配
        risk_map = {"conservative": 0, "steady": 1, "balanced": 2, "aggressive": 3}
        pref = risk_map.get(ci.risk_preference, 2)
        p_risk = risk_map.get(p["risk"], 2)
        if abs(pref - p_risk) <= 1:
            s += 20
        elif pref >= 2:
            s += 5  # 可接受略高风险
        else:
            s += 0   # 不推荐
        # 收入匹配
        il = ci.income_level()
        if p["type"] == "wealth" and il in ("super_high", "high"):
            s += 30
        if p["type"] == "loan" and il in ("low", "middle") and p["risk"] != "aggressive":
            s += 10
        # 家庭状况
        if ci.has_children and "has_children" in p["tags"]:
            s += 25
        if ci.has_mortgage and "home" in p["tags"]:
            s += 20
        if ci.marital_status == "married" and "family_protection" in p["tags"]:
            s += 15
        # AUM
        if ci.is_high_net_worth():
            if "high_net_worth" in p["tags"]:
                s += 40
            if p["type"] in ("wealth", "insurance"):
                s += 20
        # 已有产品
        if p["name"] in ci.products_held:
            s = -1  # 已有则不推荐
        # 生命周期加分
        if ci.risk_preference in ("aggressive",) and "high_growth" in p["tags"]:
            s += 15
        if ci.risk_preference == "conservative" and "safe" in p["tags"]:
            s += 15
        p = dict(p)
        p["score"] = s
        if s > 0:
            scored.append(p)
    scored.sort(key=lambda x: -x["score"])
    return scored[:6]


# ============== 触达渠道建议 ==============

CHANNEL_CONFIG = [
    {"channel": "微信", "priority": 1, "best_time": "10:00-11:30;19:00-21:00",
     "suitable_for": ["20-55"]},
    {"channel": "电话", "priority": 2, "best_time": "10:00-11:30;14:00-16:30",
     "suitable_for": ["35-70"]},
    {"channel": "短信", "priority": 3, "best_time": "11:00-13:00",
     "suitable_for": ["25-80"]},
    {"channel": "APP推送", "priority": 4, "best_time": "08:00-09:00;18:00-20:00",
     "suitable_for": ["20-50"]},
    {"channel": "线下面访", "priority": 5, "best_time": "预约制",
     "suitable_for": ["40-70"]},
]


def _recommend_channels(ci: CustomerInput) -> List[Dict]:
    age = ci.age or 35
    # 高净值客户优先面访
    if ci.is_high_net_worth():
        return [
            {"channel": "线下面访", "reason": "高净值客户优先面访，展示专业度"},
            {"channel": "微信", "reason": "日常维护，推送市场资讯"},
            {"channel": "电话", "reason": "跟进产品到期/重要提醒"},
        ]
    # 普通客户
    channels = []
    for ch in CHANNEL_CONFIG:
        suitable = False
        for r in ch["suitable_for"]:
            lo, hi = r.split("-")
            if int(lo) <= age <= int(hi):
                suitable = True
                break
        if suitable:
            channels.append({
                "channel": ch["channel"],
                "priority": ch["priority"],
                "best_time": ch["best_time"],
                "reason": f"{ci.name or '客户'}年龄{age}岁，适合{ch['channel']}渠道"
            })
    # 营销目标附加
    if ci.has_mortgage:
        channels.insert(0, {
            "channel": "APP推送", "priority": 0, "best_time": "18:00-20:00",
            "reason": "有房贷客户，APP推送利率优惠敏感度最高"
        })
    return sorted(channels[:4], key=lambda x: x["priority"])


# ============== 营销话术钩子 ==============

HOOK_TEMPLATES = {
    "wealth_management": [
        '您最近的{amount}万理财即将到期，我们新上了一款年化{rate}%的{product}，方便给您介绍一下吗？',
        '根据您的风险偏好{risk}，我们最近推荐的{product}表现不错，年化收益{rate}%，要了解一下吗？',
    ],
    "loan_offer": [
        '好消息！目前我行消费贷利率降至{rate}%，额度最高{limit}万，您的资质预估可获批。',
        '您之前有意向的{product}现在有批量化优惠，利率低至{rate}%，想给您预留个名额。',
    ],
    "insurance": [
        '了解到您刚{event}，建议及时配置{product}，每天只需{cost}元，就能获得{coverage}万保障。',
        '您家庭的保险保障方案我们已经做好了，预计年缴{amount}元，覆盖重疾/意外/医疗。',
    ],
    "credit_card": [
        '您近期的消费场景适合用我们的{product}，开卡送{bonus}积分，年费可免。',
        '我行白金卡最近推出{benefit}权益，非常适合您的出行习惯。',
    ],
    "retirement": [
        '您的养老规划缺口约{gap}万，建议每月定投{product}，{years}年后预计积累{total}万。',
        '最近个人养老金账户可享税收优惠，每年最高節税{tax_save}元，建议您关注。',
    ],
    "children_education": [
        '了解到您孩子今年{child_age}岁，教育金规划现在启动，{years}年后预计储备{total}万。',
        '开学季教育金定投计划，每月500元起，助力孩子未来留学/深造。',
    ],
    "business": [
        '您的企业现金流管理建议使用我们的{product}，随借随还，年化低至{rate}%。',
        '贵公司账户流水优质，我们系统自动核定了一笔{biz_amount}万的信用额度待您激活。',
    ],
}


def _generate_hooks(ci: CustomerInput, products: List[Dict], stage: str) -> List[Dict]:
    """按生命周期+产品生成话术钩子。"""
    hooks = []
    top_product = products[0]["name"] if products else "智能推荐产品"
    # 确定情景
    scenario = None
    if products:
        t = products[0]["type"]
        if t == "deposit": scenario = "wealth_management"
        elif t == "fund": scenario = "wealth_management"
        elif t == "loan": scenario = "loan_offer"
        elif t == "insurance": scenario = "insurance"
        elif t == "credit": scenario = "credit_card"
        elif t == "wealth": scenario = "wealth_management"
        elif t == "investment": scenario = "wealth_management"
    if not scenario:
        scenario = "wealth_management"
    templates = HOOK_TEMPLATES.get(scenario, HOOK_TEMPLATES["wealth_management"])
    for tpl in templates[:2]:
        hook = tpl.format(
            name=ci.name or "",
            amount=ci.aum // 10000 if ci.aum else 10,
            biz_amount=50,
            rate="3.2",
            product=top_product,
            risk=ci.risk_preference or "稳健",
            limit=ci.monthly_income * 12 // 10000 if ci.monthly_income else 30,
            event="结婚" if ci.marital_status == "married" else "工作稳定",
            cost=5,
            coverage=200,
            bonus="10万",
            benefit="机场贵宾厅",
            gap=200,
            years=20,
            total=300,
            tax_save=5400,
            child_age=ci.children_count if ci.has_children else 8,
        )
        hooks.append({"scenario": scenario, "hook_text": hook,
                       "expected_response": "感兴趣" if stage != "流失客户" else "需重新建立信任"})
    # 生命周期附加
    if stage == "潜在客户":
        hooks.insert(0, {"scenario": "first_touch",
                         "hook_text": f"{ci.name or '客户'}您好，我是您的专属客户经理，"
                         f"我们近期有个非常适合您的金融方案，方便简单了解一下吗？",
                         "expected_response": "初步了解"})
    if stage == "流失客户":
        hooks.append({"scenario": "win_back",
                      "hook_text": f"{ci.name or '客户'}您好，好久不见！我们为您准备了一份专属回馈礼包，"
                      f"含{top_product}费率优惠，限时7天有效。",
                      "expected_response": "回馈活动关注"})
    return hooks[:4]


# ============== 标签提取 ==============

def _extract_tags(ci: CustomerInput) -> List[str]:
    tags = []
    il = ci.income_level()
    tags.append({"super_high": "超高净值", "high": "高收入",
                 "middle_high": "中高收入", "middle": "中等收入", "low": "普通收入"}.get(il, "未知"))
    tags.append({"conservative": "保守型", "steady": "稳健型",
                 "balanced": "平衡型", "aggressive": "进取型"}.get(ci.risk_preference, "未知"))
    if ci.has_mortgage: tags.append("有房贷")
    if ci.has_car_loan: tags.append("有车贷")
    if ci.has_children: tags.append("有子女")
    if ci.is_high_net_worth(): tags.append("高净值(髑AUM)")
    tags.append({"single": "单身", "married": "已婚", "divorced": "离异",
                 "widowed": "丧偶"}.get(ci.marital_status, "未知"))
    if ci.age:
        if ci.age < 30: tags.append("Z世代")
        elif ci.age < 40: tags.append("千禧一代")
        elif ci.age < 55: tags.append("中坚一代")
        else: tags.append("银发客群")
    return tags


# ============== 风险提示 ==============

def _risk_warnings(ci: CustomerInput, products: List[Dict]) -> List[str]:
    warns = []
    if ci.risk_preference in ("conservative", "steady"):
        risky = [p["name"] for p in products if p["risk"] in ("balanced", "aggressive")]
        if risky:
            warns.append(f"产品{risky[0]}的风险等级可能超出您的风险偏好，建议优先配置保守型产品")
    if ci.monthly_income and ci.monthly_income < 5000:
        loan_products = [p["name"] for p in products if p["type"] == "loan"]
        if loan_products:
            warns.append(f"月收入偏低，{loan_products[0]}的月供压力可能较大，建议合理评估还款能力")
    # 年龄匹配
    if ci.age and ci.age > 60:
        long_term = [p["name"] for p in products if p["type"] == "fund" and "long_term" in p.get("tags", [])]
        if long_term:
            warns.append(f"年龄{ci.age}岁，不建议长期封闭型产品，确保资金流动性")
    return warns


# ============== 下一步动作 ==============

def _next_best_action(ci: CustomerInput, stage: str, products: List[Dict]) -> str:
    if stage == "潜在客户":
        return f"首次触达：介绍万能账户概念，获取客户同意后续联系"
    if stage == "新客户":
        return f"产品配置：推荐{products[0]['name'] if products else '首款入门产品'}，完成开户激活"
    if stage == "成长客户":
        return f"交叉销售：结合{products[0]['name'] if products else '推荐产品'}，提升AUM"
    if stage == "成熟客户":
        return f"深度经营：邀约参加私人银行/财富沙龙活动，强化粘性"
    if stage == "流失客户":
        return f"流失预警：致电了解原因，送专属优惠权益争取回迁"
    return "常规维护"

# ============== 自然语言解析器 ==============

def parse_natural_language(text: str) -> CustomerInput:
    """从自然语言中提取客户字段。

    支持示例：
      '客户画像 张伟 35岁 月收入2万 已婚 有房贷 风险偏好稳健'
      '李华 女 42岁 月收入5万 已婚 2个孩子 有房贷 风险偏好平衡 高净值'
    """
    ci = CustomerInput(raw_text=text)
    # 去掉指令前缀
    text = re.sub(r"^客户画像\s+", "", text)
    text = re.sub(r"^画像\s+", "", text)
    tokens = text.split()

    # 提取姓名（首个非数字/非关键字 token）
    name_blacklist = {"男", "女", "已婚", "单身", "离异", "丧偶", "客户画像", "画像",
                      "有房贷", "无房贷", "有车贷", "有子女", "高净值", "退休", "无业"}
    for t in tokens[:3]:
        if t in name_blacklist: continue
        if re.search(r"\d", t): continue
        if "收入" in t or "岁" in t or "万" in t: continue
        if "风险" in t or "偏好" in t: continue
        ci.name = t
        break

    # 年龄
    m = re.search(r"(\d{1,3})\s*岁", text)
    if m:
        ci.age = int(m.group(1))

    # 性别
    if " 男 " in f" {text} " or "男性" in text:
        ci.gender = "male"
    if " 女 " in f" {text} " or "女性" in text:
        ci.gender = "female"

    # 月收入
    m = re.search(r"月收入\s*([\d\.]+)\s*([万千wWkK]?)", text)
    if m:
        n = float(m.group(1))
        unit = m.group(2).lower()
        if unit in ("万", "w"): n *= 10000
        elif unit in ("千", "k"): n *= 1000
        ci.monthly_income = n
    # 收入也可能直接
    m2 = re.search(r"(?<!月)收入\s*([\d\.]+)\s*万", text)
    if m2 and not ci.monthly_income:
        ci.monthly_income = float(m2.group(1)) * 10000

    # AUM 资产
    m = re.search(r"(?:AUM|资产|金融资产|管理规模)\s*([\d\.]+)\s*([万千亿]?)", text)
    if m:
        n = float(m.group(1))
        unit = m.group(2)
        if unit == "万": n *= 10000
        elif unit == "千": n *= 1000
        elif unit == "亿": n *= 100_000_000
        ci.aum = n
    if "高净值" in text and not ci.aum:
        ci.aum = 6_000_000

    # 婚姻
    if "已婚" in text: ci.marital_status = "married"
    elif "单身" in text or "未婚" in text: ci.marital_status = "single"
    elif "离异" in text or "离婚" in text: ci.marital_status = "divorced"
    elif "丧偶" in text: ci.marital_status = "widowed"

    # 房贷/车贷
    if "有房贷" in text or "房贷" in text and "无房贷" not in text:
        ci.has_mortgage = True
    if "有车贷" in text or "车贷" in text and "无车贷" not in text:
        ci.has_car_loan = True

    # 子女
    m = re.search(r"(\d+)\s*个?(?:孩子|子女|娃)", text)
    if m:
        ci.has_children = True
        ci.children_count = int(m.group(1))
    if ("有子女" in text or "有孩子" in text) and not ci.has_children:
        ci.has_children = True
        ci.children_count = 1

    # 风险偏好
    if "风险偏好" in text or "风险" in text:
        if "保守" in text or "厌恶风险" in text:
            ci.risk_preference = "conservative"
        elif "稳健" in text or "稳定" in text:
            ci.risk_preference = "steady"
        elif "平衡" in text:
            ci.risk_preference = "balanced"
        elif "进取" in text or "激进" in text or "高风险" in text:
            ci.risk_preference = "aggressive"

    # 职业
    for kw in ["医生", "教师", "公务员", "工程师", "律师", "企业主", "个体户",
               "经理", "总监", "CEO", "退休", "自由职业"]:
        if kw in text:
            ci.occupation = kw
            break

    # 城市
    for kw in ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "重庆",
               "武汉", "西安", "天津", "苏州", "厦门", "青岛"]:
        if kw in text:
            ci.city = kw
            break

    return ci


# ============== 主引擎 ==============

class PersonaEngine:
    """360 度客户画像生成引擎。"""

    def generate(self, customer_input) -> CustomerPersona:
        """生成画像。

        Args:
            customer_input: CustomerInput 实例 或 自然语言字符串 或 dict
        """
        if isinstance(customer_input, str):
            ci = parse_natural_language(customer_input)
        elif isinstance(customer_input, dict):
            ci = CustomerInput(**{k: v for k, v in customer_input.items()
                                  if k in CustomerInput.__dataclass_fields__})
        elif isinstance(customer_input, CustomerInput):
            ci = customer_input
        else:
            raise TypeError(f"unsupported input type: {type(customer_input)}")

        # RFM 评分
        r, f, m = _score_r(ci), _score_f(ci), _score_m(ci)
        segment = _rfm_segment(r, f, m)
        # 生命周期
        stage = _life_cycle(ci, r)
        # 产品推荐
        products = _score_products(ci)
        # 渠道推荐
        channels = _recommend_channels(ci)
        # 话术钩子
        hooks = _generate_hooks(ci, products, stage)
        # 标签
        tags = _extract_tags(ci)
        # 风险提示
        warns = _risk_warnings(ci, products)
        # 下一步动作
        nba = _next_best_action(ci, stage, products)

        return CustomerPersona(
            customer=ci,
            rfm_segment=segment,
            rfm_score={"R": r, "F": f, "M": m},
            life_cycle_stage=stage,
            recommended_products=products,
            contact_channels=channels,
            marketing_hooks=hooks,
            value_tags=tags,
            risk_warnings=warns,
            next_best_action=nba,
        )


if __name__ == "__main__":
    eng = PersonaEngine()
    persona = eng.generate("客户画像 张伟 35岁 月收入2万 已婚 有房贷 风险偏好稳健")
    print(json.dumps(persona.to_dict(), ensure_ascii=False, indent=2))
