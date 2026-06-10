"""
家族信托方案引擎
================
输入：客户画像/资产规模/传承目标
输出：家族信托设立方案（架构+资产配置+税务筹划+受益人安排+风险隔离）
"""
from __future__ import annotations
import json
import os
import re
import random
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Any

HERE = os.path.dirname(os.path.abspath(__file__))


@dataclass
class FamilyTrustPlan:
    """家族信托方案。"""
    title: str
    client_profile: Dict       # {age, asset_scale, citizenship, goals}
    trust_structure: Dict     # 信托架构设计
    asset_allocation: Dict    # 资产配置建议
    tax_planning: List[Dict]  # 税务筹划要点
    beneficiary_arrangement: Dict  # 受益人安排
    risk_isolation: Dict       # 风险隔离分析
    timeline: List[Dict]      # 设立时间表
    fee_estimate: Dict        # 费用估算
    risks_and_notes: List[str]
    generated_at: str


# 客户画像模板
CLIENT_PROFILES = {
    "民营企业主": {
        "characteristics": ["企业债务需隔离", "传承规划需求强", "税务居民身份复杂"],
        "suggested_trust_type": "他益信托+防火墙",
        "asset_priority": ["股权", "不动产", "金融资产的顺序进行资产置入"],
    },
    "高净值家族": {
        "characteristics": ["资产规模大", "境内境外配置均有", "传承规划明确"],
        "suggested_trust_type": "离岸信托+境内信托双层架构",
        "asset_priority": ["金融资产先行", "不动产", "股权"],
    },
    "上市公司高管": {
        "characteristics": ["限售股解禁需求", "税务筹划需求", "风险分散"],
        "suggested_trust_type": "股票期权信托+税务优化架构",
        "asset_priority": ["股权激励", "金融资产的顺序"],
    },
    "准备上市企业主": {
        "characteristics": ["股权增值预期大", "上市前税务筹划", "家族成员利益分配"],
        "suggested_trust_type": "上市前股权代持+信托化安排",
        "asset_priority": ["股权先行", "知识产权", "金融资产"],
    },
}

# 资产规模分段
ASSET_TIER = {
    "3000万-1亿": {"tier": "基础版", "trust_type": "单一他益信托", "fee": "20-50万"},
    "1亿-5亿": {"tier": "标准版", "trust_type": "结构化他益信托", "fee": "50-150万"},
    "5亿以上": {"tier": "定制版", "trust_type": "离岸+境内双层信托", "fee": "150万+"},
}


def parse_input(text: str) -> Dict[str, Any]:
    """解析输入文本。"""
    text = text.strip()

    # 提取年龄
    age_match = re.search(r"(\d+)\s*岁", text)
    age = int(age_match.group(1)) if age_match else 50

    # 提取资产规模
    asset_match = re.search(r"(\d+)\s*亿", text)
    if asset_match:
        asset_scale = int(asset_match.group(1)) * 10000  # 转为万
    else:
        m_match = re.search(r"(\d+)\s*万", text)
        asset_scale = int(m_match.group(1)) if m_match else 10000

    # 识别客户类型
    client_type = "高净值家族"
    for ct in CLIENT_PROFILES:
        if ct in text:
            client_type = ct
            break

    # 识别客户需求
    goals = []
    if any(w in text for w in ["传承", "子女", "后代"]):
        goals.append("代际传承")
    if any(w in text for w in ["隔离", "债务", "风险"]):
        goals.append("风险隔离")
    if any(w in text for w in ["税务", "税", "CRS"]):
        goals.append("税务筹划")
    if any(w in text for w in ["海外", "出境", "移民"]):
        goals.append("海外配置")
    if not goals:
        goals = ["资产保护", "传承规划"]

    # 识别税务居民身份
    tax_resident = "中国"
    if any(w in text for w in ["美国", "美籍", "绿卡"]):
        tax_resident = "美国"
    elif any(w in text for w in ["香港", "港籍"]):
        tax_resident = "香港"
    elif any(w in text for w in ["新加坡", "永居"]):
        tax_resident = "新加坡"

    return {
        "age": age,
        "asset_scale": asset_scale,
        "client_type": client_type,
        "goals": goals,
        "tax_resident": tax_resident,
        "raw_text": text,
    }


def determine_trust_structure(parsed: Dict) -> Dict:
    """确定信托架构。"""
    asset_scale = parsed["asset_scale"]

    # 确定资产段
    tier_key = "3000万-1亿"
    if asset_scale >= 50000:
        tier_key = "5亿以上"
    elif asset_scale >= 10000:
        tier_key = "1亿-5亿"

    tier_info = ASSET_TIER[tier_key]
    client_type = parsed["client_type"]
    client_info = CLIENT_PROFILES.get(client_type, CLIENT_PROFILES["高净值家族"])

    trust_type = tier_info["trust_type"]
    if client_type == "准备上市企业主":
        trust_type = "上市前股权信托+员工持股平台"
    elif client_type == "上市公司高管":
        trust_type = "股权激励信托+税务优化"
    elif "海外" in parsed["goals"]:
        trust_type = "离岸信托（BVI/开曼）+境内信托双层"

    return {
        "recommended_type": trust_type,
        "tier": tier_info["tier"],
        " onshore_location": "上海/深圳/海南",
        "offshore_location": "BVI/开曼/新加坡" if "海外" in parsed["goals"] else "暂无",
        "structure_diagram": (
            "委托人 → 信托财产 → 受托人 → 受益人\n"
            "                    ↓\n"
            "              保护人/监察人"
        ),
        "key_terms": [
            "信托期限：不超过50年（视具体方案）",
            "受益人：委托人家属及其后代",
            "保护人：委托人或指定家族成员",
            "投资权：保留或不保留，视方案而定",
        ],
    }


def generate_asset_allocation(parsed: Dict) -> Dict:
    """生成资产配置建议。"""
    asset_scale = parsed["asset_scale"]
    goals = parsed["goals"]

    # 按规模确定配置比例
    if asset_scale >= 50000:  # 5亿以上
        allocation = {
            "金融资产（境内）": "30%",
            "金融资产（境外）": "25%",
            "不动产（境内）": "20%",
            "不动产（境外）": "10%",
            "股权/私募": "10%",
            "另类资产": "5%",
        }
    elif asset_scale >= 10000:  # 1亿-5亿
        allocation = {
            "金融资产（境内）": "40%",
            "金融资产（境外）": "15%",
            "不动产（境内）": "25%",
            "股权/私募": "15%",
            "另类资产": "5%",
        }
    else:  # 3000万-1亿
        allocation = {
            "金融资产（境内）": "50%",
            "不动产（境内）": "30%",
            "股权/私募": "15%",
            "现金及等价物": "5%",
        }

    return {
        "recommended_allocation": allocation,
        "asset_separation_order": [
            "第一步：置入金融资产（流动性好、易估值）",
            "第二步：置入不动产（需评估、可能涉及税费）",
            "第三步：置入股权（如有企业股权）",
            "注：资产置入顺序需综合考虑税费和监管要求",
        ],
        "currency_hedge": "建议30-50%资产配置非人民币计价的全球化资产",
    }


def generate_tax_planning(parsed: Dict) -> List[Dict]:
    """生成税务筹划要点。"""
    tax_resident = parsed["tax_resident"]
    goals = parsed["goals"]

    planning = []

    if tax_resident == "中国":
        planning.append({
            "税种": "企业所得税",
            "要点": "信托财产置入环节可能涉及所得税、印花税；建议通过无偿转让方式设立",
            "注意事项": "需保留完整的资产原值凭证，避免重复征税",
        })
        planning.append({
            "税种": "个人所得税",
            "要点": "信托分配给受益人时，受益人需缴纳个人所得税（20%税率）",
            "注意事项": "可通过设立慈善信托进行税前抵扣",
        })
        if "海外" in goals:
            planning.append({
                "税种": "CRS申报",
                "要点": "中国税务居民在境外的金融账户信息将于2028年前逐步被交换",
                "注意事项": "建议合法合规申报，避免双重不征税风险",
            })
    elif tax_resident == "美国":
        planning.append({
            "税种": "联邦所得税",
            "要点": "美国税务居民需就全球收入缴纳联邦所得税（含信托收入）",
            "注意事项": "委托人权利保留可能被视为Red迎还原",
        })
    elif tax_resident == "香港":
        planning.append({
            "税种": "薪俸税/利得税",
            "要点": "香港信托一般不征资本利得税，但信托收入可能需要纳税",
            "注意事项": "需根据受益人身份判断纳税义务",
        })

    # 通用筹划
    planning.append({
        "税种": "传承税（遗产税/赠与税）",
        "要点": "中国目前暂无遗产税和赠与税，但需关注政策变化",
        "注意事项": "建议提前规划，避免政策变动带来的不确定性",
    })

    return planning


def generate_beneficiary_arrangement(parsed: Dict) -> Dict:
    """生成受益人安排。"""
    age = parsed["age"]
    goals = parsed["goals"]

    beneficiary_rules = []

    if "传承" in goals:
        beneficiary_rules.append({
            "类型": "直系后代",
            "安排": "子女及未出生后代均为受益人",
            "分配规则": "成年后可获得分配权，特殊情况可申请提前分配",
        })
        beneficiary_rules.append({
            "类型": "代际传承",
            "安排": "若受益人先于信托终止，由其直系后代继承受益权",
            "分配规则": "防止家族成员因婚变/债务丧失传承权益",
        })

    protection_clauses = [
        "受益人离婚，配偶不得分割信托财产",
        "受益人涉及重大债务，债权人不得强制执行信托财产",
        "受益人涉及刑事犯罪，部分受益权可能被暂停",
        "设立保护人监督受托人履职",
    ]

    return {
        "beneficiary_list": beneficiary_rules if beneficiary_rules else [{"类型": "待确认", "安排": "根据委托人意愿确定"}],
        "distribution_rules": [
            "教育金：年满18岁一次性获得基础教育金",
            "创业金：年满25岁可申请创业支持资金",
            "婚嫁金：结婚时一次性获得婚嫁金",
            "养老金：年满60岁每年获得养老金支持",
        ],
        "protection_clauses": protection_clauses,
    }


def generate_risk_isolation(parsed: Dict) -> Dict:
    """生成风险隔离分析。"""
    client_type = parsed["client_type"]

    isolation_effects = []
    if "债务" in client_type or "企业主" in client_type:
        isolation_effects.append({
            "风险类型": "企业债务隔离",
            "有效性": "高",
            "原理": "信托设立后，信托财产与委托人财产分离，企业债务不能追索信托财产",
            "前提条件": [
                "信托设立时委托人不存在财务危机",
                "信托财产来源合法合规",
                "不存在虚假信托或逃债目的",
            ],
        })

    isolation_effects.extend([
        {
            "风险类型": "婚姻风险隔离",
            "有效性": "高",
            "原理": "子女作为受益人获得的信托分配不属于夫妻共同财产",
            "前提条件": "子女配偶不列为受益人",
        },
        {
            "风险类型": "身故传承风险",
            "有效性": "高",
            "原理": "避免遗嘱认证程序，保护隐私，定向传承",
            "前提条件": "信托条款明确约定受益人范围和分配规则",
        },
    ])

    limitations = [
        "信托设立前的已有债务可能无法隔离",
        "恶意逃债被认定无效的风险",
        "法律政策变化可能影响信托效力",
        "受托人违约风险（通过选择靠谱受托人和保护人机制降低）",
    ]

    return {
        "isolation_effects": isolation_effects,
        "effectiveness_summary": "家族信托是风险隔离的有效工具，但需确保信托合法有效设立",
        "limitations": limitations,
    }


def generate_timeline() -> List[Dict]:
    """生成设立时间表。"""
    return [
        {"阶段": "尽职调查", "内容": "客户背景调查、资产梳理、方案设计", "周期": "1-2周"},
        {"阶段": "方案确认", "内容": "信托架构、受益人安排、投资策略确认", "周期": "1-2周"},
        {"阶段": "法律文件", "内容": "信托契约起草、审核、签署", "周期": "2-4周"},
        {"阶段": "资产置入", "内容": "金融资产/不动产过户至信托", "周期": "2-8周"},
        {"阶段": "正式运营", "内容": "信托设立完成，受托人开始管理", "周期": "持续"},
    ]


def generate_fee_estimate(parsed: Dict) -> Dict:
    """生成费用估算。"""
    asset_scale = parsed["asset_scale"]

    if asset_scale >= 50000:
       设立费 = "80-200万"
       年度管理费 = "资产规模的0.3-0.5%"
    elif asset_scale >= 10000:
       设立费 = "30-80万"
       年度管理费 = "资产规模的0.4-0.6%"
    else:
       设立费 = "15-30万"
       年度管理费 = "资产规模的0.5-0.8%"

    return {
        "设立费": 设立费,
        "年度管理费": 年度管理费,
        "其他费用": ["资产审计费（视需要）", "法律顾问费（视需要）", "税务顾问费（视需要）"],
        "备注": "具体费用以信托公司报价为准，以上为市场参考价格",
    }


class FamilyTrustEngine:
    """家族信托方案引擎。"""

    def generate(self, source) -> FamilyTrustPlan:
        if isinstance(source, str):
            parsed = parse_input(source)
        elif isinstance(source, dict):
            parsed = {**parse_input(source.get("text", "")), **source}
        else:
            raise TypeError(f"unsupported input: {type(source)}")

        title = f"家族信托设立方案 - {parsed['client_type']} {parsed['asset_scale']//10000}亿资产规模"

        return FamilyTrustPlan(
            title=title,
            client_profile={
                "年龄": f"{parsed['age']}岁",
                "资产规模": f"{parsed['asset_scale']}万",
                "客户类型": parsed["client_type"],
                "核心需求": "/".join(parsed["goals"]),
                "税务居民身份": parsed["tax_resident"],
            },
            trust_structure=determine_trust_structure(parsed),
            asset_allocation=generate_asset_allocation(parsed),
            tax_planning=generate_tax_planning(parsed),
            beneficiary_arrangement=generate_beneficiary_arrangement(parsed),
            risk_isolation=generate_risk_isolation(parsed),
            timeline=generate_timeline(),
            fee_estimate=generate_fee_estimate(parsed),
            risks_and_notes=[
                "本方案仅供参考，具体以信托公司正式方案为准",
                "信托设立需满足监管要求和法律条件",
                "税务筹划需在专业税务顾问指导下进行",
                "信托效力取决于设立时的法律环境和资产来源合法性",
            ],
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )


if __name__ == "__main__":
    eng = FamilyTrustEngine()
    r = eng.generate("家族信托 客户50岁 资产3亿 想传承给子女 企业债务需隔离")
    print(json.dumps(asdict(r), ensure_ascii=False, indent=2))
