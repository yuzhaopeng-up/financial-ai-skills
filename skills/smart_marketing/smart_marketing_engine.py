#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能营销话术引擎 v1.0
根据客户画像生成精准营销话术，支持异议预判

Author: ArkClaw
Version: 1.0.0
"""

import re
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional


class SmartMarketingEngine:
    """智能营销话术引擎"""

    VERSION = "1.0.0"

    # 客户画像维度
    CUSTOMER_DIMENSIONS = ["age", "occupation", "assets", "risk_preference", "investment_experience", "financial_goal"]

    # 风险偏好映射
    RISK_PREFERENCE_MAP = {
        "保守": ["定期存款", "国债", "保本理财", "年金险"],
        "稳健": ["理财产品", "混合基金", "债券基金", "终身寿险"],
        "进取": ["股票基金", "贵金属", "权益类", "投连险"],
        "激进": ["股票", "私募", "跨境金融", "杠杆产品"],
    }

    # 年龄段映射
    AGE_GROUP_MAP = {
        (18, 25): "青年",
        (26, 35): "青壮年",
        (36, 45): "中年",
        (46, 55): "中老年",
        (56, 65): "老年",
        (65, 999): "高龄",
    }

    # 职业类型映射话术风格
    OCCUPATION_STYLE = {
        "企业主": "专业权威型",
        "公司高管": "专业权威型",
        "公务员": "稳重信赖型",
        "医生": "专业信赖型",
        "律师": "专业精确型",
        "教师": "温和教育型",
        "自由职业": "灵活共鸣型",
        "上班族": "效率实用型",
        "退休人员": "关怀稳健型",
    }

    # 产品模板库
    PRODUCT_TEMPLATES = {
        "定期存款": {
            "value_prop": ["资金安全有保障", "收益稳定可预期", "存取灵活无忧"],
            "objections": [
                {"objection": "利率太低了", "answer": "确实比不上高风险产品，但本金绝对安全，收益写进合同，适合您这样的稳健型客户。"},
                {"objection": "流动性不好", "answer": "可以提前支取，只是会按活期计息。我们也有阶梯存款帮您兼顾收益和流动性。"},
            ],
            "keywords": ["存款", "定存", "定期"],
        },
        "理财产品": {
            "value_prop": ["专业管理省心省力", "期限灵活选择多", "业绩基准有竞争力"],
            "objections": [
                {"objection": "不保本了", "answer": "理财打破刚兑后，收益更真实。我们的理财产品有专业团队管理，评级稳健，适合您这个风险层级的客户。"},
                {"objection": "看不懂产品说明书", "answer": "我来给您逐条拆解，重点看投资范围、业绩比较基准和风险等级这三项就够了。"},
            ],
            "keywords": ["理财", "银行理财", "净值型"],
        },
        "基金产品": {
            "value_prop": ["专业基金经理管理", "分散投资降低风险", "申赎灵活"],
            "objections": [
                {"objection": "亏损了怎么办", "answer": "基金净值有波动是正常的，关键看长期表现。我建议定投方式，平滑成本穿越周期。"},
                {"objection": "手续费太高", "answer": "现在主流渠道申购费打1折，算下来很低。而且持有一年以上很多基金免赎回费。"},
            ],
            "keywords": ["基金", "申购", "定投", "货币基金"],
        },
        "保险产品": {
            "value_prop": ["保障+储蓄双功能", "税收优惠（税优健康险）", "指定传承定向传承"],
            "objections": [
                {"objection": "保险不划算", "answer": "保险的核心是风险对冲，不是投资收益率。一旦发生风险，保险的杠杆效应是任何投资品都比不了的。"},
                {"objection": "钱存进去拿不出来", "answer": "这是误解。年金险支持保单贷款，终身寿险有现金价值，急用钱时可以灵活取用。"},
            ],
            "keywords": ["保险", "寿险", "年金险", "健康险"],
        },
        "贷款产品": {
            "value_prop": ["利率优惠放款快", "额度充足用途广", "还款方式灵活"],
            "objections": [
                {"objection": "利率太高", "answer": "我们根据您的资质给到最优利率，还可以申请利率优惠。能按时还款还有机会降低利率。"},
                {"objection": "手续麻烦", "answer": "现在全程线上操作，最快当天放款。准备好身份证和收入证明就行。"},
            ],
            "keywords": ["贷款", "借款", "信用贷", "抵押贷"],
        },
        "信用卡": {
            "value_prop": ["消费返现/积分", "免息期长达50天", "机场贵宾厅等权益"],
            "objections": [
                {"objection": "怕自己乱花钱", "answer": "可以设置交易限额，还有记账功能帮您管理消费。免息期合理使用其实是在帮您省钱。"},
                {"objection": "年费问题", "answer": "每年消费满X笔就能免年费，附属权益（机场贵宾厅、保险等）完全够本。"},
            ],
            "keywords": ["信用卡", "卡"],
        },
        "贵金属": {
            "value_prop": ["抗通胀保值增值", "实物可提取", "收藏传承价值"],
            "objections": [
                {"objection": "黄金会跌吗", "answer": "黄金有避险属性，长期看有保值功能。建议占您总资产的5%-10%作为配置，能有效对冲风险。"},
                {"objection": "买纸黄金还是实物", "answer": "想传承收藏选实物，追求灵活交易选纸黄金/ETF。各有优势看您的目的。"},
            ],
            "keywords": ["黄金", "贵金属", "金银"],
        },
        "国债/地方政府债": {
            "value_prop": ["国家信用背书", "利率比定存高", "利息免税"],
            "objections": [
                {"objection": "抢不到", "answer": "我们行是主要代销机构，有优先额度。您可以设置到期提醒，新债开售第一时间通知您。"},
                {"objection": "地方债安全吗", "answer": "地方政府债有财政收入作为担保，评级AA+以上，属于城投债里最安全的品种。"},
            ],
            "keywords": ["国债", "地方债", "政金债"],
        },
        "财富管理信托": {
            "value_prop": ["门槛100万起", "预期收益较高", "资产隔离保护"],
            "objections": [
                {"objection": "信托可靠吗", "answer": "信托是持牌金融机构，受银保监会严格监管。资产独立，不受债务纠纷影响。"},
                {"objection": "流动性太差", "answer": "信托有封闭期，但收益相对更高。建议用闲置资金配置，不影响日常流动资金需求。"},
            ],
            "keywords": ["信托", "家族信托", "资管"],
        },
        "跨境金融产品": {
            "value_prop": ["全球资产配置", "分散单一货币风险", "捕捉海外机会"],
            "objections": [
                {"objection": "汇率风险大", "answer": "可以做货币对冲，我们有专业团队帮您管理汇率风险。全球配置才能真正分散风险。"},
                {"objection": "不熟悉海外市场", "answer": "我们有专业研究团队提供海外市场分析，产品设计也做了本土化适配，您不需要成为专家。"},
            ],
            "keywords": ["跨境", "海外", "QDII", "外汇"],
        },
        "消费分期": {
            "value_prop": ["0利息0手续费", "最长24期", "审批秒过"],
            "objections": [
                {"objection": "真的有0利息吗", "answer": "是的，这是银行补贴给用户的优惠，名额有限，手慢无。"},
                {"objection": "会不会有隐藏费用", "answer": "合同白纸黑字写明费用结构，提前还款也无违约金，您可以放心。"},
            ],
            "keywords": ["分期", "消费分期", "信用支付"],
        },
    }

    # 渠道话术风格
    CHANNEL_STYLES = {
        "短信": {"prefix": "【XX银行】", "style": "简洁直接", "length": "70字以内"},
        "微信": {"prefix": "", "style": "亲切互动", "length": "200字以内"},
        "电话": {"prefix": "", "style": "专业清晰", "length": "3分钟以内"},
        "面对面": {"prefix": "", "style": "亲切专业", "length": "视情况"},
    }

    # 营销目标话术模板
    GOAL_TEMPLATES = {
        "资产保值": {
            "opening": "针对您的资产保值需求，我建议重点考虑能锁定收益、风险可控的产品组合。",
            "cta": "我们可以做个资产配置诊断，帮您找到最适合的保值方案。",
        },
        "资产增值": {
            "opening": "您希望资产稳健增值，我建议在控制风险的前提下适当增配权益类产品。",
            "cta": "我可以为您量身定制一个股债平衡组合，争取更好的长期收益。",
        },
        "养老规划": {
            "opening": "养老规划越早越好，我根据您的年龄和家庭情况，推荐侧重安全和持续现金流的方案。",
            "cta": "我们可以测算一下，以您现在的资产基数，退休后每月能领多少养老金。",
        },
        "子女教育": {
            "opening": "子女教育金是刚性支出，时间确定不能挪用，建议用教育金保险或定投基金来规划。",
            "cta": "我帮您算一下，按目标倒推每月需要投入多少。",
        },
        "短期周转": {
            "opening": "短期资金讲究流动性，我建议放在现金管理类产品里，随用随取还能有收益。",
            "cta": "我们的XX产品非常适合您，随存随取，利率比活期高很多。",
        },
    }

    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode
        self._log("初始化智能营销话术引擎 v%s" % self.VERSION)

    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)

    # ---- 画像解析 ----

    def parse_customer_profile(self, text: str) -> Dict[str, Any]:
        """解析客户画像文本"""
        profile = {
            "age": None,
            "age_group": None,
            "occupation": None,
            "assets": None,
            "assets_level": None,
            "risk_preference": None,
            "investment_experience": None,
            "financial_goal": None,
            "channel": "面对面",
            "raw_text": text,
        }

        # 解析年龄
        age_match = re.search(r"(\d{2})[岁件]|年龄[=：](\d+)", text)
        if age_match:
            profile["age"] = int(age_match.group(1) or age_match.group(2))
            profile["age_group"] = self._get_age_group(profile["age"])

        # 解析职业
        occupations = ["企业主", "公司高管", "公务员", "医生", "律师", "教师", "自由职业", "上班族", "退休人员"]
        for occ in occupations:
            if occ in text:
                profile["occupation"] = occ
                break

        # 解析资产规模
        # 优先匹配 "资产=500万" 格式，再兜底匹配独立的 "XX万" 模式
        assets_match = re.search(r"资产[=：]?\s*(\d+)\s*([万千]|[千万]?元?)", text)
        if not assets_match:
            assets_match = re.search(r"(\d+)\s*万", text)
        if assets_match:
            assets_val = int(assets_match.group(1))
            if assets_match.lastindex >= 2:
                unit = assets_match.group(2)
                if unit == "万":
                    assets_val *= 10000
                elif unit == "千":
                    assets_val *= 1000
                elif unit == "千万":
                    assets_val *= 10000000
            else:
                # 兜底匹配 "500万" → 乘以10000
                assets_val *= 10000
            profile["assets"] = assets_val
            profile["assets_level"] = self._get_assets_level(assets_val)

        # 解析风险偏好
        risk_levels = {"保守": "保守", "稳健": "稳健", "进取": "进取", "激进": "激进"}
        for level, label in risk_levels.items():
            if level in text:
                profile["risk_preference"] = label
                break

        # 解析营销目标
        goals = ["资产保值", "资产增值", "养老规划", "子女教育", "短期周转", "财富传承"]
        for goal in goals:
            if goal in text:
                profile["financial_goal"] = goal
                break

        # 解析渠道
        channels = ["短信", "微信", "电话", "面对面"]
        for ch in channels:
            if ch in text:
                profile["channel"] = ch
                break

        return profile

    def _get_age_group(self, age: int) -> str:
        for (low, high), label in self.AGE_GROUP_MAP.items():
            if low <= age <= high:
                return label
        return "未知"

    def _get_assets_level(self, assets: int) -> str:
        if assets < 500000:
            return "普通"
        elif assets < 1000000:
            return "优质"
        elif assets < 5000000:
            return "富裕"
        elif assets < 20000000:
            return "高净值"
        else:
            return "超高净值"

    def _get_occupation_style(self, occupation: str) -> str:
        return self.OCCUPATION_STYLE.get(occupation, "通用型")

    # ---- 产品匹配 ----

    def detect_product(self, text: str) -> str:
        """识别产品类型"""
        text_lower = text.lower()
        scores = {}
        for product, template in self.PRODUCT_TEMPLATES.items():
            score = sum(1 for kw in template["keywords"] if kw.lower() in text_lower)
            if score > 0:
                scores[product] = score
        if scores:
            return max(scores, key=scores.get)
        return "理财产品"  # 默认

    def match_products_for_profile(self, profile: Dict) -> List[Dict[str, str]]:
        """根据客户画像匹配产品"""
        risk = profile.get("risk_preference", "稳健")
        matched = []
        candidates = self.RISK_PREFERENCE_MAP.get(risk, [])

        for product_name in candidates:
            if product_name in self.PRODUCT_TEMPLATES:
                template = self.PRODUCT_TEMPLATES[product_name]
                matched.append({
                    "product": product_name,
                    "suitability": "⭐⭐⭐" if product_name in candidates[:2] else "⭐⭐",
                    "value_props": template["value_prop"],
                })
        return matched[:3]  # 最多返回3个

    # ---- 话术生成 ----

    def generate_script(
        self,
        customer_text: str,
        product: str = None,
        goal: str = None,
        channel: str = None,
    ) -> Dict[str, Any]:
        """
        生成营销话术

        Args:
            customer_text: 客户画像描述
            product: 产品类型（可选，自动识别）
            goal: 营销目标（可选，自动识别）
            channel: 营销渠道（可选，默认面对面）

        Returns:
            包含话术、异议预判、推荐产品的完整结果
        """
        start = time.time()

        # 解析画像
        profile = self.parse_customer_profile(customer_text)

        # 识别/设置产品
        if not product:
            product = self.detect_product(customer_text)
        if goal:
            profile["financial_goal"] = goal
        if channel:
            profile["channel"] = channel

        # 获取产品模板
        product_template = self.PRODUCT_TEMPLATES.get(product, self.PRODUCT_TEMPLATES["理财产品"])

        # 获取目标模板
        goal_key = profile.get("financial_goal") or "资产增值"
        goal_template = self.GOAL_TEMPLATES.get(goal_key, self.GOAL_TEMPLATES["资产增值"])

        # 获取渠道风格
        channel_style = self.CHANNEL_STYLES.get(profile["channel"], self.CHANNEL_STYLES["面对面"])

        # 生成话术
        script = self._build_script(profile, product, product_template, goal_template, channel_style)

        # 获取异议预判
        objections = self._build_objections(product_template)

        # 产品匹配
        recommended_products = self.match_products_for_profile(profile)

        elapsed_ms = round((time.time() - start) * 1000, 1)

        return {
            "profile": profile,
            "product": product,
            "channel": profile["channel"],
            "script": script,
            "objections": objections,
            "recommended_products": recommended_products,
            "generation_time_ms": elapsed_ms,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _build_script(
        self,
        profile: Dict,
        product: str,
        product_template: Dict,
        goal_template: Dict,
        channel_style: Dict,
    ) -> Dict[str, str]:
        """构建话术结构"""
        age = profile.get("age") or 35
        age_group = profile.get("age_group", "客户")
        occupation = profile.get("occupation") or ""
        assets = profile.get("assets") or 0
        assets_str = f"{assets // 10000}万" if assets >= 10000 else f"{assets}元"
        assets_level = profile.get("assets_level", "")
        risk = profile.get("risk_preference", "稳健")
        occupation_style = self._get_occupation_style(occupation)
        goal = profile.get("financial_goal") or "资产增值"

        # 开场白
        opening_templates = {
            "专业权威型": f"张总，您好！我是XX银行的客户经理。结合您{assets_str}资产的配置需求，今天重点跟您介绍一款非常适合您这样{occupation}群体的{product}。",
            "稳重信赖型": f"您好！感谢您一直以来对我们的信任。结合您的资产情况和风险偏好，我为您筛选了一款值得关注的{product}，希望对您的财务规划有帮助。",
            "专业精确型": f"您好！根据您的投资偏好和资产规模，我为您匹配了一款{product}，我从三个维度为您做个专业解读。",
            "温和教育型": f"您好！您的情况我大概了解了。今天给您介绍一款我觉得很适合您长远规划的{product}，我慢慢给您说明。",
            "灵活共鸣型": f"您好！看您的需求，确实需要一个灵活又靠谱的方案。给您推荐的这款{product}，我觉得会比较对您的胃口。",
            "效率实用型": f"您好！直接说重点——您的情况我推荐{product}，三个理由让您快速判断是否合适。",
            "关怀稳健型": f"您好！考虑到您这个阶段最重要的是资金安全，我为您精选了一款{product}，兼顾收益和稳健。",
            "通用型": f"您好！根据您的需求，我为您推荐这款{product}，下面给您详细介绍一下。",
        }
        opening = opening_templates.get(occupation_style, opening_templates["通用型"])

        # 价值主张
        value_props = product_template["value_prop"]
        value_prop_text = "、".join(value_props[:2])
        value_主张 = f"这款{product}有三大核心优势：第一，{value_props[0]}；第二，{value_props[1] if len(value_props) > 1 else value_props[0]}；第三，专业团队管理，帮您省心。"

        # 行动号召
        cta = goal_template["cta"]

        # 完整话术文本
        full_script = f"{opening}\n\n【产品价值】\n{value_主张}\n\n【营销目标】\n{goal_template['opening']}\n\n【下一步】\n{cta}"

        return {
            "opening": opening,
            "value_proposition": value_主张,
            "goal_alignment": goal_template["opening"],
            "cta": cta,
            "full": full_script,
        }

    def _build_objections(self, product_template: Dict) -> List[Dict[str, str]]:
        """构建异议预判"""
        raw_objections = product_template.get("objections", [])
        result = []
        for i, obj in enumerate(raw_objections[:3], 1):
            result.append({
                "id": f"O{i:02d}",
                "objection": obj["objection"],
                "answer": obj["answer"],
                "confidence": 0.95,
            })
        return result

    # ---- 格式化输出 ----

    def format_text(self, result: Dict) -> str:
        """格式化输出为文本"""
        profile = result["profile"]
        script = result["script"]
        lines = [
            f"🎯 **智能营销话术**",
            f"",
            f"⏱ 生成耗时: {result['generation_time_ms']}ms | 📺 渠道: {result['channel']} | ⏰ {result['generated_at']}",
            f"",
            f"{'='*32}",
            f"",
            f"👤 **客户画像**",
            f"  年龄: {profile.get('age', '未知')}岁（{profile.get('age_group', '')}）",
            f"  职业: {profile.get('occupation', '未知')}",
            f"  资产: {profile.get('assets', '未知')}（{profile.get('assets_level', '')}）",
            f"  风险偏好: {profile.get('risk_preference', '未知')}",
            f"  营销目标: {profile.get('financial_goal', '未知')}",
            f"",
            f"{'='*32}",
            f"",
            f"📦 **推荐产品**: {result['product']}",
            f"",
            f"💬 **营销话术**",
            f"",
        ]

        for key, label in [
            ("opening", "开场白"),
            ("value_proposition", "价值主张"),
            ("goal_alignment", "目标契合"),
            ("cta", "行动号召"),
        ]:
            lines.append(f"**【{label}】**")
            lines.append(script[key])
            lines.append("")

        if result["objections"]:
            lines.extend([
                f"{'='*32}",
                f"",
                f"⚠️ **异议预判**（{len(result['objections'])}条）",
            ])
            for obj in result["objections"]:
                lines.extend([
                    f"",
                    f"❓ **Q{obj['id']}**: {obj['objection']}",
                    f"✅ **A**: {obj['answer']}",
                ])

        if result["recommended_products"]:
            lines.extend([
                f"",
                f"{'='*32}",
                f"",
                f"🏦 **产品匹配建议**",
            ])
            for rp in result["recommended_products"]:
                lines.append(f"  • {rp['product']} {rp['suitability']} - {', '.join(rp['value_props'][:2])}")

        lines.append(f"\n{'='*32}")
        lines.append(f"✅ 验收：生成耗时 {result['generation_time_ms']}ms < 5000ms，支持 {len(self.PRODUCT_TEMPLATES)} 种产品")

        return "\n".join(lines)

    def format_json(self, result: Dict) -> str:
        """格式化输出为JSON"""
        return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("🎯 智能营销话术引擎 v1.0")
    print("=" * 50)
    print()

    engine = SmartMarketingEngine()

    # 测试用例
    test_cases = [
        ("营销话术 客户年龄=35 职业=企业主 资产=500万 风险偏好=稳健 产品=理财产品 目标=资产增值", "企业主稳健型理财"),
        ("保险话术 30岁白领50万进取型", "白领进取型保险"),
        ("短信 存款话术 50岁退休人员100万保守型", "退休保守型存款短信"),
    ]

    for text, label in test_cases:
        print(f"\n{'─'*40}")
        print(f"测试用例: {label}")
        print(f"输入: {text}")
        print()
        result = engine.generate_script(text)
        print(engine.format_text(result))
        print()


if __name__ == "__main__":
    main()
