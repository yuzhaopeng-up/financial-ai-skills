"""
全球资产配置引擎
================
输入：客户风险偏好/资产规模/配置目标
输出：全球资产配置方案（区域分布+资产类别+货币对冲+再平衡策略）
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
class GlobalAssetAllocation:
    """全球资产配置方案。"""
    title: str
    client_profile: Dict       # {risk_level, asset_scale, goal}
    regional_allocation: List[Dict]  # 区域配置
    asset_class_allocation: List[Dict]  # 资产类别配置
    currency_hedge: Dict       # 货币对冲策略
    rebalancing: Dict          # 再平衡策略
    compliance_notes: List[str]  # 合规提示
    product_recommendations: List[Dict]  # 产品建议
    generated_at: str


# 风险等级配置
RISK_PROFILES = {
    "R1": {"name": "保守型", "max_loss": -5, "equity_max": 10, "bond_min": 60, "description": "本金保护优先"},
    "R2": {"name": "稳健型", "max_loss": -10, "equity_max": 25, "bond_min": 40, "description": "稳健增值"},
    "R3": {"name": "平衡型", "max_loss": -20, "equity_max": 50, "bond_min": 20, "description": "收益与风险平衡"},
    "R4": {"name": "成长型", "max_loss": -30, "equity_max": 70, "bond_min": 10, "description": "追求较高收益"},
    "R5": {"name": "激进型", "max_loss": -50, "equity_max": 90, "bond_min": 0, "description": "充分参与市场"},
}

# 区域配置模板
REGIONAL_TEMPLATES = {
    "A股": {"base": 30, "currency": "CNY", "hedge_needed": False},
    "港股": {"base": 15, "currency": "HKD", "hedge_needed": True},
    "美股": {"base": 20, "currency": "USD", "hedge_needed": True},
    "欧股": {"base": 10, "currency": "EUR", "hedge_needed": True},
    "日本": {"base": 5, "currency": "JPY", "hedge_needed": True},
    "新兴市场": {"base": 10, "currency": "Mixed", "hedge_needed": True},
    "黄金": {"base": 5, "currency": "USD", "hedge_needed": False},
    "REITs": {"base": 5, "currency": "USD", "hedge_needed": True},
}

# 资产类别
ASSET_CLASSES = {
    "权益类": ["A股大盘蓝筹", "美股科技", "港股高股息", "欧股价值", "日本股票"],
    "固收类": ["国债", "高等级信用债", "可转债", "美元债", "新兴市场债"],
    "另类资产": ["黄金", "商品", "私募股权", "对冲基金"],
    "实物资产": ["核心城市写字楼REITs", "物流仓储REITs", "基础设施REITs"],
    "现金类": ["货币基金", "短期理财", "结构性存款"],
}


def parse_input(text: str) -> Dict[str, Any]:
    """解析输入文本。"""
    text = text.strip()

    # 识别风险等级
    risk_level = "R3"
    for r in ["R1", "R2", "R3", "R4", "R5"]:
        if r in text or any(w in text for w in ["保守", "稳健", "平衡", "成长", "激进"]):
            risk_level = r
            break
    risk_map = {"保守": "R1", "稳健": "R2", "平衡": "R3", "成长": "R4", "激进": "R5"}
    for kw, rl in risk_map.items():
        if kw in text:
            risk_level = rl
            break

    # 提取资产规模
    asset_match = re.search(r"(\d+)\s*亿", text)
    if asset_match:
        asset_scale = int(asset_match.group(1)) * 10000  # 转为万
    else:
        m_match = re.search(r"(\d+)\s*万", text)
        asset_scale = int(m_match.group(1)) if m_match else 10000

    # 识别配置目标
    goals = []
    if any(w in text for w in ["养老", "退休"]):
        goals.append("养老规划")
    if any(w in text for w in ["教育", "子女", "留学"]):
        goals.append("子女教育")
    if any(w in text for w in ["传承", "传承"]):
        goals.append("财富传承")
    if any(w in text for w in ["增值", "收益", "投资"]):
        goals.append("资产增值")
    if not goals:
        goals = ["资产增值"]

    return {
        "risk_level": risk_level,
        "asset_scale": asset_scale,
        "goals": goals,
        "raw_text": text,
    }


def generate_regional_allocation(risk_level: str, asset_scale: int) -> List[Dict]:
    """生成区域配置。"""
    risk = RISK_PROFILES.get(risk_level, RISK_PROFILES["R3"])
    random.seed(asset_scale % 1000)

    if risk_level in ["R1", "R2"]:  # 保守/稳健
        regional = {
            "A股": 40, "港股": 15, "美股": 10,
            "欧股": 5, "日本": 5, "新兴市场": 5,
            "黄金": 10, "REITs": 5, "现金": 5,
        }
    elif risk_level == "R3":  # 平衡
        regional = {
            "A股": 25, "港股": 15, "美股": 20,
            "欧股": 10, "日本": 5, "新兴市场": 10,
            "黄金": 5, "REITs": 5, "现金": 5,
        }
    elif risk_level == "R4":  # 成长
        regional = {
            "A股": 20, "港股": 15, "美股": 25,
            "欧股": 10, "日本": 5, "新兴市场": 15,
            "黄金": 5, "REITs": 5,
        }
    else:  # 激进
        regional = {
            "A股": 15, "港股": 15, "美股": 30,
            "欧股": 10, "日本": 5, "新兴市场": 15,
            "黄金": 5, "REITs": 5,
        }

    result = []
    for region, pct in regional.items():
        if pct <= 0:
            continue
        template = REGIONAL_TEMPLATES.get(region, {"currency": "USD", "hedge_needed": True})
        result.append({
            "区域": region,
            "配置比例": f"{pct}%",
            "主要货币": template["currency"],
            "对冲建议": "是" if template["hedge_needed"] else "否（人民币资产）",
            "核心逻辑": _get_regional_logic(region, risk_level),
        })

    result.sort(key=lambda x: int(x["配置比例"].replace("%", "")), reverse=True)
    return result


def _get_regional_logic(region: str, risk_level: str) -> str:
    logics = {
        "A股": "国内经济复苏，政策支持，估值处于历史低位",
        "港股": "高股息标的吸引全球配置资金，估值修复机会",
        "美股": "AI科技浪潮持续，创新动能强，美联储降息预期",
        "欧股": "价值股股息率具吸引力，欧洲央行转向宽松",
        "日本": "日央行维持宽松，日元贬值利于出口企业",
        "新兴市场": "全球经济复苏，新兴市场增长潜力大",
        "黄金": "避险资产，对冲尾部风险和通胀",
        "REITs": "稳定现金流，抗通胀，收益分散化",
    }
    return logics.get(region, "区域配置")


def generate_asset_class_allocation(risk_level: str) -> List[Dict]:
    """生成资产类别配置。"""
    risk = RISK_PROFILES.get(risk_level, RISK_PROFILES["R3"])

    if risk_level == "R1":
        allocation = [("权益类", 5), ("固收类", 75), ("另类资产", 5), ("实物资产", 5), ("现金类", 10)]
    elif risk_level == "R2":
        allocation = [("权益类", 15), ("固收类", 60), ("另类资产", 5), ("实物资产", 10), ("现金类", 10)]
    elif risk_level == "R3":
        allocation = [("权益类", 35), ("固收类", 40), ("另类资产", 10), ("实物资产", 10), ("现金类", 5)]
    elif risk_level == "R4":
        allocation = [("权益类", 55), ("固收类", 20), ("另类资产", 15), ("实物资产", 10)]
    else:
        allocation = [("权益类", 75), ("固收类", 5), ("另类资产", 15), ("实物资产", 5)]

    return [
        {
            "资产类别": asset,
            "配置比例": f"{pct}%",
            "代表品种": "、".join(ASSET_CLASSES.get(asset, [])[:3]),
            "风险收益特征": _get_class_feature(asset),
        }
        for asset, pct in allocation if pct > 0
    ]


def _get_class_feature(asset: str) -> str:
    features = {
        "权益类": "高风险高收益，长期增值潜力大",
        "固收类": "中低风险稳定收益，现金流保障",
        "另类资产": "与传统资产相关性低，分散化效果",
        "实物资产": "抗通胀，稳定现金流",
        "现金类": "高流动性，收益低，防御性配置",
    }
    return features.get(asset, "")


def generate_currency_hedge(risk_level: str, asset_scale: int) -> Dict:
    """生成货币对冲策略。"""
    hedge_ratio = {
        "R1": {"USD": 30, "EUR": 20, "HKD": 20, "JPY": 10},
        "R2": {"USD": 40, "EUR": 25, "HKD": 20, "JPY": 10},
        "R3": {"USD": 50, "EUR": 30, "HKD": 15, "JPY": 5},
        "R4": {"USD": 60, "EUR": 25, "HPY": 10, "JPY": 5},
        "R5": {"USD": 70, "EUR": 15, "HKD": 10, "JPY": 5},
    }

    ratios = hedge_ratio.get(risk_level, hedge_ratio["R3"])
    total_foreign = sum(ratios.values())

    return {
        "对冲策略": "建议对冲主要敞口货币，降低汇率波动影响",
        "货币敞口分布": {f"{k}资产": f"{v}%" for k, v in ratios.items()},
        "人民币资产": f"{100 - total_foreign}%",
        "对冲工具": ["远期外汇合约", "外汇期权", "货币互换"],
        "对冲比例建议": "建议30-50%的外币资产进行对冲",
    }


def generate_rebalancing(risk_level: str) -> Dict:
    """生成再平衡策略。"""
    thresholds = {
        "R1": {"equity": 5, "bond": 10},
        "R2": {"equity": 7, "bond": 8},
        "R3": {"equity": 10, "bond": 7},
        "R4": {"equity": 12, "bond": 5},
        "R5": {"equity": 15, "bond": 5},
    }

    t = thresholds.get(risk_level, thresholds["R3"])

    return {
        "触发条件": [
            f"任一资产类别偏离目标配置超过{t['equity']}%（权益类）",
            f"任一资产类别偏离目标配置超过{t['bond']}%（固收类）",
            "每年定期调整（建议每年1月和7月）",
        ],
        "执行方式": ["小幅偏离时买入低配资产", "大幅偏离时卖出高配资产同时买入低配资产"],
        "税费考虑": "避免频繁交易，注意交易成本和税费对净收益的影响",
        "注意事项": [
            "再平衡不影响原有投资逻辑",
            "特殊市场环境下可适当灵活调整阈值",
            "大额资金建议分批执行",
        ],
    }


def generate_compliance_notes(risk_level: str, asset_scale: int) -> List[str]:
    """生成合规提示。"""
    notes = [
        "外汇管制提示：个人每年等值5万美元便利化购汇额度，实际需求需合规申报",
        "CRS合规：境外金融账户信息可能交换至中国税务机关，请确保申报合规",
        "反洗钱：投资资金来源需合法合规，大额资金需提供资金来源证明",
    ]

    if asset_scale >= 50000:
        notes.append("大额资产配置建议配合专业税务顾问进行跨境税务筹划")

    if risk_level in ["R4", "R5"]:
        notes.append("高风险等级产品仅适合具备相应风险承受能力的投资者，请如实评估自身风险等级")

    notes.append("投资有风险，配置需谨慎，过往业绩不预示未来表现")

    return notes


def generate_product_recommendations(risk_level: str) -> List[Dict]:
    """生成产品建议。"""
    products = {
        "R1": [
            {"产品": "国债", "特点": "国家信用背书，零信用风险", "适合比例": "40-60%"},
            {"产品": "大额存单", "特点": "利率优于普通存款，流动性好", "适合比例": "20-30%"},
            {"产品": "货币基金", "特点": "高流动性，净值稳定", "适合比例": "10-20%"},
        ],
        "R2": [
            {"产品": "固收+理财", "特点": "固收为主，适度权益增强", "适合比例": "40-50%"},
            {"产品": "高等级信用债", "特点": "收益高于国债，信用风险可控", "适合比例": "20-30%"},
            {"产品": "港股高股息ETF", "特点": "稳定分红，对冲汇率", "适合比例": "10-20%"},
        ],
        "R3": [
            {"产品": "A股指数增强", "特点": "跟踪指数，超额收益", "适合比例": "20-25%"},
            {"产品": "美股QDII基金", "特点": "分享美股科技红利", "适合比例": "15-20%"},
            {"产品": "全球股债平衡", "特点": "跨资产分散", "适合比例": "20-25%"},
            {"产品": "黄金ETF", "特点": "避险对冲", "适合比例": "5-10%"},
        ],
        "R4": [
            {"产品": "美股科技基金", "特点": "AI/云计算长期赛道", "适合比例": "25-30%"},
            {"产品": "新兴市场股票", "特点": "高增长潜力", "适合比例": "15-20%"},
            {"产品": "A股成长股", "特点": "国内创新动能", "适合比例": "20-25%"},
            {"产品": "私募股权", "特点": "长期高回报", "适合比例": "10-15%"},
        ],
        "R5": [
            {"产品": "纳斯达克ETF", "特点": "全球科技龙头", "适合比例": "30-40%"},
            {"产品": "A股创业板", "特点": "高成长高波动", "适合比例": "20-25%"},
            {"产品": "加密货币", "特点": "极高风险", "适合比例": "5-10%"},
            {"产品": "私募股权", "特点": "长期高回报", "适合比例": "15-20%"},
        ],
    }

    return products.get(risk_level, products["R3"])


class GlobalAssetAllocationEngine:
    """全球资产配置引擎。"""

    def generate(self, source) -> GlobalAssetAllocation:
        if isinstance(source, str):
            parsed = parse_input(source)
        elif isinstance(source, dict):
            parsed = {**parse_input(source.get("text", "")), **source}
        else:
            raise TypeError(f"unsupported input: {type(source)}")

        risk_level = parsed["risk_level"]
        asset_scale = parsed["asset_scale"]
        risk_info = RISK_PROFILES.get(risk_level, RISK_PROFILES["R3"])

        title = f"全球资产配置方案 - {risk_info['name']} 资产规模{asset_scale//10000}亿"

        return GlobalAssetAllocation(
            title=title,
            client_profile={
                "风险等级": f"{risk_level}（{risk_info['name']}）",
                "资产规模": f"{asset_scale}万",
                "配置目标": "/".join(parsed["goals"]),
                "最大可承受回撒": f"{risk_info['max_loss']}%",
            },
            regional_allocation=generate_regional_allocation(risk_level, asset_scale),
            asset_class_allocation=generate_asset_class_allocation(risk_level),
            currency_hedge=generate_currency_hedge(risk_level, asset_scale),
            rebalancing=generate_rebalancing(risk_level),
            compliance_notes=generate_compliance_notes(risk_level, asset_scale),
            product_recommendations=generate_product_recommendations(risk_level),
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )


if __name__ == "__main__":
    eng = GlobalAssetAllocationEngine()
    r = eng.generate("全球配置 高净值客户 风险等级R3 资产1亿 子女海外教育")
    print(json.dumps(asdict(r), ensure_ascii=False, indent=2))
