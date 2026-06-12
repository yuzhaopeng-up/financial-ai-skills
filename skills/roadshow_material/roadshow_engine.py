"""
路演材料生成引擎
================
输入：产品信息+目标客户+时长
输出：PPT大纲+完整讲稿
"""
from __future__ import annotations
import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Any

HERE = os.path.dirname(os.path.abspath(__file__))


@dataclass
class RoadshowMaterial:
    """路演材料。"""
    title: str
    product_name: str
    target_audience: str        # 客群类型
    duration: int               # 时长（分钟）
    ppt_outline: List[Dict]     # PPT大纲 {page, title, key_points, duration}
    speech_script: List[Dict]   # 讲稿 {section, content, duration, tips}
    comparison_table: List[Dict] # 竞品对比
    risk_disclosure: str         # 风险揭示文本
    qa_prep: List[Dict]         # Q&A准备
    generated_at: str


# 产品模板
PRODUCT_TEMPLATES = {
    "固收理财": {
        "type": "固定收益类",
        "risk_level": "R2-R3",
        "expected_return": "4-5%",
        "min_investment": "1万",
        "key_features": ["刚性兑付历史", "收益稳健", "期限灵活"],
        "risks": ["信用风险", "流动性风险", "市场风险"],
        "competitors": ["工商e理财", "招行稳盈系列", "建行乾元"],
    },
    "私募股权": {
        "type": "股权类",
        "risk_level": "R5",
        "expected_return": "8-12%",
        "min_investment": "100万",
        "key_features": ["长期复利", "分散投资", "专业管理"],
        "risks": ["本金损失风险", "锁定期长", "流动性差"],
        "competitors": ["高瓴资本", "红杉中国", "IDG资本"],
    },
    "家族信托": {
        "type": "财富传承",
        "risk_level": "R2",
        "expected_return": "视资产配置",
        "min_investment": "1000万",
        "key_features": ["风险隔离", "定向传承", "税务优化"],
        "risks": ["受托人风险", "法律变更风险"],
        "competitors": ["平安信托", "中信信托", "外贸信托"],
    },
    "公募基金": {
        "type": "权益类/混合类",
        "risk_level": "R3-R4",
        "expected_return": "视市场",
        "min_investment": "100",
        "key_features": ["门槛低", "流动性好", "透明规范"],
        "risks": ["市场风险", "管理风险"],
        "competitors": ["易方达", "华夏", "嘉实"],
    },
    "保险理财": {
        "type": "寿险+理财",
        "risk_level": "R2",
        "expected_return": "3-4%",
        "min_investment": "5000",
        "key_features": ["保障+理财", "复利增值", "税务优惠"],
        "risks": ["退保损失", "利率风险"],
        "competitors": ["平安金瑞人生", "国寿鑫享今生", "太保长相伴"],
    },
}

# 受众话术风格
AUDIENCE_STYLES = {
    "保守型": {"tone": "稳健", "focus": "本金安全+稳定收益", "avoid": "激进表述"},
    "稳健型": {"tone": "平衡", "focus": "风险收益比+流动性", "avoid": "夸大收益"},
    "成长型": {"tone": "进取", "focus": "超额收益+成长空间", "avoid": "过度保守"},
    "激进型": {"tone": "积极", "focus": "高收益机会+分散配置", "avoid": "过度强调保本"},
}


def parse_input(text: str) -> Dict[str, Any]:
    """解析输入文本。"""
    text = text.strip()

    # 提取产品类型
    product_type = "固收理财"
    for pt in PRODUCT_TEMPLATES:
        if pt in text or any(kw in text for kw in ["理财", "固收", "基金", "信托", "保险", "股权"]):
            product_type = pt
            break

    # 提取目标客户
    audience = "稳健型"
    for aud in AUDIENCE_STYLES:
        if aud in text:
            audience = aud
            break
    if "50岁以上" in text or "老年" in text or "养老" in text:
        audience = "保守型"
    if "高净值" in text or "私行" in text or "1亿" in text:
        audience = "稳健型"

    # 提取时长
    duration_match = re.search(r"(\d+)\s*分钟", text)
    duration = int(duration_match.group(1)) if duration_match else 30

    # 提取年龄偏好
    age_keywords = re.findall(r"(\d+)\s*岁", text)
    age_note = f"目标客群约{age_keywords[0]}岁" if age_keywords else ""

    return {
        "product_type": product_type,
        "audience": audience,
        "duration": duration,
        "age_note": age_note,
        "raw_text": text,
    }


def build_ppt_outline(product_type: str, audience: str, duration: int) -> List[Dict]:
    """生成PPT大纲。"""
    product = PRODUCT_TEMPLATES.get(product_type, PRODUCT_TEMPLATES["固收理财"])
    style = AUDIENCE_STYLES.get(audience, AUDIENCE_STYLES["稳健型"])

    base_pages = [
        {
            "page": 1, "title": "开场", "subtitle": "感谢时间+自我介绍",
            "key_points": ["尊敬的各位客户", "感谢参会", "今日安排概览"],
            "time_pages": duration // 8,
        },
        {
            "page": 2, "title": "公司介绍", "subtitle": f"{style['focus']}专业机构",
            "key_points": ["机构背景", "核心优势", "行业排名"],
            "time_pages": duration // 6,
        },
        {
            "page": 3, "title": f"{product['type']}产品概览", "subtitle": "产品基本要素",
            "key_points": [
                f"风险等级：{product['risk_level']}",
                f"起投金额：{product['min_investment']}",
                f"预期收益：{product['expected_return']}",
                f"产品期限：见合同条款",
            ],
            "time_pages": duration // 4,
        },
        {
            "page": 4, "title": "核心亮点", "subtitle": "为什么选择我们",
            "key_points": [f"亮点{i+1}：{f}" for i, f in enumerate(product["key_features"][:3])],
            "time_pages": duration // 3,
        },
        {
            "page": 5, "title": "竞品对比", "subtitle": "我们的差异化优势",
            "key_points": ["收益对比", "风险控制", "服务优势", "历史业绩"],
            "time_pages": duration // 3,
        },
        {
            "page": 6, "title": "风险揭示", "subtitle": "产品风险说明",
            "key_points": [f"风险{i+1}：{r}" for i, r in enumerate(product["risks"][:3])],
            "time_pages": duration // 4,
        },
        {
            "page": 7, "title": "购买流程", "subtitle": "简单几步即可参与",
            "key_points": ["风险评估", "产品认购", "合同签署", "资金入账"],
            "time_pages": duration // 6,
        },
        {
            "page": 8, "title": "Q&A", "subtitle": "问答环节",
            "key_points": ["常见问题解答", "一对一沟通"],
            "time_pages": duration // 5,
        },
    ]

    # 根据时长调整页数
    if duration <= 20:
        base_pages = base_pages[::2]  # 精简版
    elif duration >= 45:
        # 插入更多细节页
        extra_page = {
            "page": 9, "title": "案例分享", "subtitle": "真实客户故事",
            "key_points": ["客户背景", "配置方案", "收益表现", "客户感言"],
            "time_pages": duration // 5,
        }
        base_pages.insert(-1, extra_page)

    # 重新编号
    for i, page in enumerate(base_pages, 1):
        page["page"] = i

    return base_pages


def build_speech_script(product_type: str, audience: str, duration: int) -> List[Dict]:
    """生成完整讲稿。"""
    product = PRODUCT_TEMPLATES.get(product_type, PRODUCT_TEMPLATES["固收理财"])
    style = AUDIENCE_STYLES.get(audience, AUDIENCE_STYLES["稳健型"])
    tone = style["tone"]

    opening_tones = {
        "稳健": "各位朋友大家好，感谢大家在百忙之中抽出时间。今天我想和大家分享一个兼顾收益与安全的理财方案。",
        "平衡": "各位好，感谢参会。今天和大家探讨如何在当前市场环境下把握机遇、实现财富稳健增值。",
        "进取": "各位好，感谢信任。今天分享的是一个能够助力财富快速增长的投资机会。",
        "积极": "各位投资界的朋友，感谢参会。在当前充满机遇的市场中，我想和大家分享一个极具潜力的投资赛道。",
    }

    scripts = [
        {
            "section": "开场白",
            "content": opening_tones.get(tone, opening_tones["平衡"]),
            "duration": f"{duration//10}分钟",
            "tips": "保持微笑，与客户眼神交流，营造轻松氛围",
        },
        {
            "section": "产品介绍",
            "content": (
                f"今天要介绍的是我行的【{product_type}】产品。"
                f"这是一款{product['type']}产品，风险等级{product['risk_level']}，"
                f"起投金额{product['min_investment']}，预期收益{product['expected_return']}。"
            ),
            "duration": f"{duration//4}分钟",
            "tips": f"重点强调{product['key_features'][0]}，语速适中",
        },
        {
            "section": "优势阐述",
            "content": (
                "相比同业，我们的产品有三大核心优势：\n"
                f"一、{product['key_features'][0]}；\n"
                f"二、{product['key_features'][1] if len(product['key_features']) > 1 else '历史业绩稳健'}；\n"
                f"三、{product['key_features'][2] if len(product['key_features']) > 2 else '专业团队管理'}。"
            ),
            "duration": f"{duration//4}分钟",
            "tips": "用具体数据说话，避免空洞形容词",
        },
        {
            "section": "风险揭示",
            "content": (
                f"投资有风险，选择需谨慎。本产品涉及{product['risks'][0]}，"
                f"请各位在购买前仔细阅读产品说明书和风险揭示书，"
                "如有疑问可随时与我行理财经理沟通。"
            ),
            "duration": f"{duration//8}分钟",
            "tips": "语气诚恳，不回避风险，体现专业与诚信",
        },
        {
            "section": "结语",
            "content": (
                "感谢各位的聆听。如果您对我们的产品感兴趣，"
                "可以现场与我沟通，也可以扫描二维码了解更多详情。"
                "祝各位投资顺利，生活愉快！"
            ),
            "duration": f"{duration//10}分钟",
            "tips": "主动递送名片，引导添加微信",
        },
    ]

    return scripts


def build_comparison(product_type: str) -> List[Dict]:
    """生成竞品对比表。"""
    product = PRODUCT_TEMPLATES.get(product_type, PRODUCT_TEMPLATES["固收理财"])
    competitors = product.get("competitors", ["同业产品A", "同业产品B"])

    comparison = [
        {
            "维度": "预期收益",
            "我行产品": product["expected_return"],
            "竞品1": f"{float(product['expected_return'].split('-')[0].replace('%','')) - 0.5:.1f}%~{float(product['expected_return'].split('-')[1].replace('%','')) - 0.3:.1f}%" if '-' in product['expected_return'] else "相近",
            "竞品2": "相近",
        },
        {
            "维度": "风险等级",
            "我行产品": product["risk_level"],
            "竞品1": "相近",
            "竞品2": "相近",
        },
        {
            "维度": "起投金额",
            "我行产品": product["min_investment"],
            "竞品1": f"{int(product['min_investment'].replace('万','').replace('元','').replace('百','')) * 2}万" if '万' in product['min_investment'] else "相近",
            "竞品2": "相近",
        },
        {
            "维度": "历史业绩",
            "我行产品": "稳健",
            "竞品1": "良好",
            "竞品2": "良好",
        },
        {
            "维度": "服务响应",
            "我行产品": "24小时专属服务",
            "竞品1": "工作日服务",
            "竞品2": "7*12小时服务",
        },
    ]
    return comparison


class RoadshowEngine:
    """路演材料生成引擎。"""

    def generate(self, source) -> RoadshowMaterial:
        if isinstance(source, str):
            parsed = parse_input(source)
        elif isinstance(source, dict):
            parsed = {**parse_input(source.get("text", source.get("raw_text", ""))), **source}
        else:
            raise TypeError(f"unsupported input: {type(source)}")

        product_type = parsed["product_type"]
        audience = parsed["audience"]
        duration = parsed["duration"]

        product = PRODUCT_TEMPLATES.get(product_type, PRODUCT_TEMPLATES["固收理财"])
        title = f"{product['type']}产品路演材料"

        risk_disclosure = (
            f"【风险揭示】本产品为{product['type']}，风险等级{product['risk_level']}。"
            f"主要风险包括：{'/'.join(product['risks'])}。"
            "过往业绩不预示未来表现。本材料仅供参考，不构成投资建议。"
            "投资者应在充分了解产品风险后，自主做出投资决策。"
        )

        qa_prep = [
            {"question": f"{product_type}的收益是如何计算的？", "answer": "按产品说明书约定的收益计算方式，以实际持有天数计息。"},
            {"question": "产品到期后资金多久到账？", "answer": "通常在到期后3-5个工作日内返回客户指定账户。"},
            {"question": "可以提前赎回吗？", "answer": "部分产品支持提前赎回，但可能涉及赎回费率，具体以合同为准。"},
            {"question": f"{product['risks'][0]}是什么意思？", "answer": f"{product['risks'][0]}指产品可能面临的特定风险，具体说明请参阅产品说明书。"},
        ]

        return RoadshowMaterial(
            title=title,
            product_name=product_type,
            target_audience=audience,
            duration=duration,
            ppt_outline=build_ppt_outline(product_type, audience, duration),
            speech_script=build_speech_script(product_type, audience, duration),
            comparison_table=build_comparison(product_type),
            risk_disclosure=risk_disclosure,
            qa_prep=qa_prep,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )


if __name__ == "__main__":
    eng = RoadshowEngine()
    r = eng.generate("路演材料生成 固收类理财产品 目标客户是50岁以上保守型投资者 30分钟")
    print(json.dumps(asdict(r), ensure_ascii=False, indent=2))
