"""
厅堂精准营销引擎（Lobby Marketing Engine）

基于客户画像（年龄/职业/资产级别/历史产品/等候时间），
实时生成营销话术推荐、产品匹配、促成时机判断及异议处理预案。
"""

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CustomerProfile:
    """客户画像"""
    age: int
    occupation: str          # 企业主/上班族/退休/自由职业/高管
    waiting_minutes: int
    asset_level: str          # 20万以下/20-100万/100-500万/500万以上
    history_products: list[str] = field(default_factory=list)
    risk_preference: str = ""  # 保守型/稳健型/积极型/未评估

    def infer_risk_preference(self) -> str:
        """根据历史产品推断风险偏好"""
        if self.risk_preference:
            return self.risk_preference
        if not self.history_products:
            return "未评估"
        product_mapping = {
            "定期": "保守型",
            "保险": "保守型",
            "大额存单": "保守型",
            "理财": "稳健型",
            "基金": "积极型",
            "股票": "积极型",
            "私募": "积极型",
        }
        scores = {"保守型": 0, "稳健型": 0, "积极型": 0}
        for p in self.history_products:
            for k, v in product_mapping.items():
                if k in p:
                    scores[v] += 1
        if max(scores.values()) == 0:
            return "未评估"
        return max(scores, key=scores.get)


@dataclass
class ProductRecommendation:
    """产品推荐"""
    product: str
    product_type: str         # 存款/理财/保险/基金
    match_score: float         # 0.0-1.0
    reason: str
    key_selling_points: list[str] = field(default_factory=list)


@dataclass
class LobbyScript:
    """营销话术"""
    opening: str = ""              # 开场白
    need_discovery: str = ""        # 需求挖掘
    product_presentation: str = ""  # 产品呈现
    objection_handling: list[dict] = field(default_factory=list)
    closing: str = ""              # 促成话术


@dataclass
class TimingSignal:
    """促成时机"""
    ready: bool
    confidence: float         # 0.0-1.0
    reasons: list[str] = field(default_factory=list)


class LobbyMarketingEngine:
    """
    厅堂精准营销引擎

    输入客户画像，返回：
    - 推荐产品列表（含匹配分）
    - 完整话术（开场/需求挖掘/产品呈现/异议处理/促成）
    - 促成时机判断
    """

    def __init__(self):
        self._product_rules = _ProductRules()
        self._script_templates = _ScriptTemplates()
        self._objection_handlers = _ObjectionHandlers()

    # ------------------------------------------------------------------
    # 公开接口
    # ------------------------------------------------------------------

    def generate(
        self,
        age: int = None,
        occupation: str = None,
        waiting_minutes: int = None,
        asset_level: str = None,
        history_products: list = None,
        risk_preference: str = "",
        raw_input: str = "",
    ) -> dict[str, Any]:
        """
        主生成接口。

        支持两种调用方式：
        1. 关键字参数：age=40, occupation="企业主", ...
        2. 原始文本：raw_input="厅堂营销 40岁企业主 等候15分钟 资产200万 持有定期"

        Returns:
            包含 customer_profile / recommended_products / script /
                timing_signal / wecom_card 的字典
        """
        # 解析输入
        if raw_input:
            profile = self._parse_raw_input(raw_input)
        else:
            profile = CustomerProfile(
                age=age or 35,
                occupation=occupation or "未知",
                waiting_minutes=waiting_minutes or 5,
                asset_level=asset_level or "20万以下",
                history_products=history_products or [],
                risk_preference=risk_preference,
            )

        # 推断风险偏好
        if not profile.risk_preference or profile.risk_preference == "未评估":
            profile.risk_preference = profile.infer_risk_preference()

        # 产品匹配
        products = self._match_products(profile)

        # 话术生成
        script = self._generate_script(profile, products)

        # 时机判断
        timing = self._judge_timing(profile, products)

        # 企微卡片（dict格式，供外部渲染）
        wecom_card = self._build_wecom_card(profile, products, script, timing)

        return {
            "customer_profile": {
                "age": profile.age,
                "occupation": profile.occupation,
                "waiting_minutes": profile.waiting_minutes,
                "asset_level": profile.asset_level,
                "history_products": profile.history_products,
                "risk_preference": profile.risk_preference,
            },
            "recommended_products": [
                {
                    "product": p.product,
                    "type": p.product_type,
                    "match_score": round(p.match_score, 2),
                    "reason": p.reason,
                    "key_selling_points": p.key_selling_points,
                }
                for p in products
            ],
            "script": {
                "opening": script.opening,
                "need_discovery": script.need_discovery,
                "product_presentation": script.product_presentation,
                "objection_handling": script.objection_handling,
                "closing": script.closing,
            },
            "timing_signal": {
                "ready": timing.ready,
                "confidence": round(timing.confidence, 2),
                "reasons": timing.reasons,
            },
            "wecom_card": wecom_card,
        }

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _parse_raw_input(self, raw: str) -> CustomerProfile:
        """解析自然语言输入"""
        raw = raw.strip()

        # 年龄
        age_m = re.search(r"(\d{2})\s*岁", raw)
        age = int(age_m.group(1)) if age_m else 35

        # 职业
        occ_map = {
            "企业主": "企业主",
            "老板": "企业主",
            "上班族": "上班族",
            "退休": "退休",
            "高管": "高管",
            "自由职业": "自由职业",
        }
        occupation = next((v for k, v in occ_map.items() if k in raw), "未知")

        # 等候时间
        wait_m = re.search(r"等[候|了]?(\d+)\s*分", raw)
        waiting_minutes = int(wait_m.group(1)) if wait_m else 5

        # 资产级别
        asset_map = [
            ("500万以上", ["500万以上", "500万+", "800万", "1000万", "1000万以上"]),
            ("100-500万", ["100-500万", "200万", "300万", "400万", "500万"]),
            ("20-100万", ["20-100万", "20万", "50万", "80万", "100万"]),
            ("20万以下", ["20万以下", "10万", "5万"]),
        ]
        asset_level = next((k for k, vals in asset_map if any(v in raw for v in vals)), "20万以下")

        # 历史产品
        prod_map = ["定期", "理财", "基金", "保险", "活期", "大额存单", "私募", "股票"]
        history_products = [p for p in prod_map if p in raw]

        return CustomerProfile(
            age=age,
            occupation=occupation,
            waiting_minutes=waiting_minutes,
            asset_level=asset_level,
            history_products=history_products,
        )

    def _match_products(self, profile: CustomerProfile) -> list[ProductRecommendation]:
        """产品匹配"""
        rules = self._product_rules
        recommendations = []

        # 1. 存款产品（基础款，所有人适用）
        if profile.asset_level in ("20万以下", "20-100万"):
            if "定期" not in profile.history_products:
                recommendations.append(ProductRecommendation(
                    product="个人定期存款",
                    product_type="存款",
                    match_score=0.85,
                    reason="资金安全有保障，适合保守型客户",
                    key_selling_points=["50万内存款保险保护", "利率稳定", "支取灵活"],
                ))

        # 大额存单
        if profile.asset_level in ("100-500万", "500万以上"):
            if "大额存单" not in "".join(profile.history_products):
                recommendations.append(ProductRecommendation(
                    product="大额存单",
                    product_type="存款",
                    match_score=0.90,
                    reason="利率上浮、资产隔离，适合高净值客户资产保值",
                    key_selling_points=["利率较普通定期上浮10-30%", "可转让", "资产隔离功能"],
                ))

        # 2. 银行理财
        if profile.risk_preference in ("稳健型", "积极型"):
            if "理财" not in profile.history_products:
                recommendations.append(ProductRecommendation(
                    product="固定收益类理财产品",
                    product_type="理财",
                    match_score=0.80,
                    reason="兼顾收益与稳健，满足资产稳定增值需求",
                    key_selling_points=["历史业绩稳健", "多种期限可选", "风险评级R2-R3"],
                ))

        # 3. 保险（传承/健康）
        if profile.age >= 35:
            insurance_type = "终身寿险/年金险" if profile.age >= 50 else "重疾险/年金险"
            recommendations.append(ProductRecommendation(
                product=insurance_type,
                product_type="保险",
                match_score=0.75 + (0.05 if profile.occupation == "企业主" else 0),
                reason="资产传承+风险保障，企业主尤适合资产隔离",
                key_selling_points=["指定受益人传承", "资产隔离保护", "复利增值"],
            ))

        # 4. 基金
        if profile.age < 50 and profile.risk_preference in ("稳健型", "积极型"):
            fund_type = "股票型/混合型基金" if profile.risk_preference == "积极型" else "债券型/混合基金"
            recommendations.append(ProductRecommendation(
                product=fund_type,
                product_type="基金",
                match_score=0.70,
                reason="长期持有分享经济增长红利，强制储蓄",
                key_selling_points=["专业管理", "分散风险", "定投平摊成本"],
            ))
        elif profile.age >= 50 and "基金" not in profile.history_products:
            recommendations.append(ProductRecommendation(
                product="债券型基金/基金定投",
                product_type="基金",
                match_score=0.65,
                reason="稳健增值，适合中长期资产配置",
                key_selling_points=["波动小", "专业打理", "定期投入平抑风险"],
            ))

        # 按匹配分排序，取前4
        recommendations.sort(key=lambda x: x.match_score, reverse=True)
        return recommendations[:4]

    def _generate_script(
        self,
        profile: CustomerProfile,
        products: list[ProductRecommendation],
    ) -> LobbyScript:
        """生成话术"""
        t = self._script_templates
        occ = profile.occupation
        age = profile.age
        asset = profile.asset_level

        # 开场白
        opening = t.opening(occ, age, profile.waiting_minutes)

        # 需求挖掘
        need_discovery = t.need_discovery(occ, age, asset)

        # 产品呈现（取top2产品）
        top_products = products[:2]
        product_presentation = t.product_presentation(top_products, profile)

        # 异议处理
        objection_handling = self._objection_handlers.get_handlers(profile, top_products)

        # 促成话术
        closing = t.closing(profile, top_products)

        return LobbyScript(
            opening=opening,
            need_discovery=need_discovery,
            product_presentation=product_presentation,
            objection_handling=objection_handling,
            closing=closing,
        )

    def _judge_timing(
        self,
        profile: CustomerProfile,
        products: list[ProductRecommendation],
    ) -> TimingSignal:
        """促成时机判断"""
        reasons = []
        score = 0.0

        # 等候时间
        if profile.waiting_minutes >= 15:
            reasons.append(f"等候时间{profile.waiting_minutes}分钟，客户耐心有限")
            score += 0.30
        elif profile.waiting_minutes >= 10:
            reasons.append(f"等候时间{profile.waiting_minutes}分钟，适时切入")
            score += 0.20

        # 资产级别
        if profile.asset_level in ("100-500万", "500万以上"):
            reasons.append("高净值客户，营销价值高")
            score += 0.25

        # 产品已有一定了解
        if profile.history_products:
            reasons.append("已有金融产品认知，需求明确")
            score += 0.20

        # 年龄适合
        if 30 <= profile.age <= 60:
            reasons.append("黄金年龄段，资产配置需求强")
            score += 0.15

        # 企业主
        if profile.occupation == "企业主":
            reasons.append("企业主有资产隔离/传承需求")
            score += 0.25

        score = min(score, 1.0)
        return TimingSignal(
            ready=score >= 0.40,
            confidence=score,
            reasons=reasons,
        )

    def _build_wecom_card(
        self,
        profile: CustomerProfile,
        products: list[ProductRecommendation],
        script: LobbyScript,
        timing: TimingSignal,
    ) -> dict:
        """构建企微卡片格式"""
        product_lines = "\n".join(
            f"▌{p.product}（{p.product_type}）匹配度{int(p.match_score*100)}%"
            for p in products[:3]
        )
        return {
            "msgtype": "text",
            "text": {
                "content": (
                    f"🎯 厅堂营销辅助\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"👤 客户画像：{profile.age}岁{profile.occupation} | "
                    f"{profile.asset_level} | 等候{profile.waiting_minutes}分钟\n"
                    f"💰 风险偏好：{profile.risk_preference}\n"
                    f"📦 已持产品：{', '.join(profile.history_products) or '无'}\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"📋 推荐产品：\n{product_lines}\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"🗣️ 开场话术：\n{script.opening[:80]}...\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"⏱️ 促成时机：{'✅ 建议立即切入' if timing.ready else '⏳ 继续培养'}\n"
                    f"    置信度：{int(timing.confidence*100)}%\n"
                    f"    {'；'.join(timing.reasons[:2])}\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"💡 异议处理首推：{script.objection_handling[0]['objection'] if script.objection_handling else '待评估'}\n"
                    f"    → {script.objection_handling[0]['response'][:50] if script.objection_handling else ''}..."
                )
            },
        }


# ------------------------------------------------------------------
# 内部类：话术模板
# ------------------------------------------------------------------

class _ScriptTemplates:

    def opening(self, occupation: str, age: int, wait_min: int) -> str:
        wait_note = f"非常感谢您今天等候了{wait_min}分钟" if wait_min >= 5 else ""
        templates = {
            "企业主": (
                f"{wait_note}，李总！看您气质不凡，想必事业做得非常出色。"
                "现在网点客户不多，正好可以给您介绍几个我们行的个性化金融服务，"
                "不知道您平时对资产配置、传承规划有没有关注？"
            ),
            "高管": (
                f"{wait_note}，张先生！您是我们行优质客户，"
                "针对您这个资产层级，我们有几款专属理财产品和保险规划，"
                "不知道您现在方便了解一下吗？"
            ),
            "上班族": (
                f"{wait_note}，您好！工作这么忙还要来网点办业务，真是辛苦了。"
                "我们行最近有一款非常适合上班族的储蓄+理财组合，"
                "每月定投几百元就能享受专业资管服务，您看要不要了解一下？"
            ),
            "退休": (
                f"{wait_note}，阿姨/叔叔您好！您气质真好，"
                "我们行针对您这个年龄段推出了高息定期存款和大额存单，"
                "安全又划算，您要不要听我介绍一下？"
            ),
        }
        base = templates.get(occupation, templates["上班族"])
        # 融入年龄信息
        if occupation in ("企业主", "高管") and age >= 45:
            base += "尤其像您这样事业稳定、家庭责任也相对重一些的，资产安全和传承就更值得关注了。"
        return base

    def need_discovery(self, occupation: str, age: int, asset: str) -> str:
        templates = {
            "企业主": (
                "【需求挖掘 - SPIN】\n"
                "▶ 现状：李总，您目前企业运营资金和家庭资产是怎么分配的？"
                "平时主要在哪几家银行打理？\n"
                "▶ 问题：这两年经济环境变化，有没有感觉到资产保值方面的压力？"
                "企业经营风险和家庭资产有没有做好隔离？\n"
                "▶ 影响：如果企业出现风险，您目前的家庭资产能保障生活质量吗？"
                "子女教育、养老有没有提前规划？\n"
                "▶ 解决：那正好，我们行有一款专门针对企业主的综合资产配置方案，"
                "集储蓄、理财、保险于一体，可以帮您把家庭资产和企业风险有效隔离。"
            ),
            "高管": (
                "【需求挖掘 - SPIN】\n"
                "▶ 现状：张先生，您目前的收入主要投向哪些渠道？"
                "平时的资产打理是自己做还是交给专业机构？\n"
                "▶ 问题：现在理财产品净值波动较大，您感觉收益和风险如何平衡？"
                "有没有考虑过用保险做底层资产配置？\n"
                "▶ 影响：如果出现意外或重大疾病，会不会影响家庭财务规划？\n"
                "▶ 解决：其实用一部分资金配置稳健型保险，作为家庭资产的'稳定器'，"
                "再配合一些浮动收益产品，整体风险更可控。"
            ),
            "退休": (
                "【需求挖掘 - SPIN】\n"
                "▶ 现状：叔叔/阿姨，您现在退休后的收入来源主要是什么？"
                "平时积蓄是存银行还是买了一些理财产品？\n"
                "▶ 问题：这两年存款利率一直在下降，您有没有感觉到利息收入减少了？\n"
                "▶ 影响：以后如果身体不好需要大笔医疗费，或者想给子女留点什么，"
                "现有的积蓄够不够？\n"
                "▶ 解决：其实我们有一款专门为老年人设计的大额存单，"
                "利率比普通定期高，而且50万以内受存款保险保护，非常安全。"
            ),
            "上班族": (
                "【需求挖掘 - SPIN】\n"
                "▶ 现状：小王，您好！平时工作忙，有没有关注过自己的财务规划？"
                "现在收入主要放在哪里打理？\n"
                "▶ 问题：随着年龄增长，家庭责任也在增加，"
                "万一遇到意外或生病，存款够不够应对？"
                "孩子的教育金、自己未来的养老钱有没有提前准备？\n"
                "▶ 影响：如果没有提前规划，到时候可能会比较被动，"
                "储蓄的速度往往赶不上通胀和支出增长。\n"
                "▶ 解决：我们有一款专门为上班族设计的'强制储蓄+轻理财'组合，"
                "每月投入不多，但长期坚持效果很好，而且不需要您花时间打理。"
            ),
        }
        return templates.get(occupation, templates["上班族"])

    def product_presentation(
        self,
        products: list[ProductRecommendation],
        profile: CustomerProfile,
    ) -> str:
        if not products:
            return "目前暂时没有特别推荐的产品，建议继续跟进。"

        lines = ["【产品呈现 - FAB法则】\n"]
        for i, p in enumerate(products[:2], 1):
            fab = (
                f"▌产品{i}：{p.product}\n"
                f"  🔸特征（F）：{p.key_selling_points[0] if p.key_selling_points else '暂无'}\n"
                f"  🔸优势（A）：{p.reason}\n"
                f"  🔸利益（B）："
            )
            if p.product_type == "存款":
                fab += "本金安全、利息稳定、50万内存款保险保护"
            elif p.product_type == "理财":
                fab += "资产稳健增值，历史业绩良好，流动性好"
            elif p.product_type == "保险":
                fab += "风险保障+资产传承，指定受益人，资产隔离"
            elif p.product_type == "基金":
                fab += "专业管理省心省力，定投平摊成本，长期复利效应"
            lines.append(fab)
        return "\n".join(lines)

    def closing(self, profile: CustomerProfile, products: list) -> str:
        """生成促成话术"""
        if not products:
            return "感谢您的来访，祝您生活愉快！"

        top_product = products[0].product if products else ""

        templates = {
            "企业主": (
                f"李总，跟您聊了这么多，感觉这款「{top_product}」"
                f"非常适合您目前的资产配置需求。"
                f"今天正好有专属活动，利率比平时更优惠，"
                f"您要不要先开一个账户把资金放进来，"
                f"后续我再帮您做一个完整的资产配置方案？"
                f"时间有限，今天签约还能额外获得一次免费的财务诊断服务。"
            ),
            "高管": (
                f"张先生，「{top_product}」这款产品非常契合您刚才提到的需求。"
                f"其实高净值客户都在用这种方式做资产'压舱石'，"
                f"您要不要今天就预约一个专属理财顾问，"
                f"详细帮您测算一下收益和配置比例？"
            ),
            "上班族": (
                f"这款「{top_product}」每月投入不多，长期坚持效果非常好。"
                f"像您这样的白领客户最看重的是'省心'，"
                f"签约后您只需要每月发工资时自动扣款，"
                f"完全不用操心，还能享受专业团队的持续打理。"
                f"要不要今天就开通一个账户试试？"
            ),
            "退休": (
                f"叔叔/阿姨，「{top_product}」安全性高、收益稳定，"
                f"特别适合咱们这个年龄段。"
                f"而且50万以内受存款保险保护，您完全不用担心资金安全。"
                f"要不要今天就把钱转进来？我帮您算一下到期能拿多少利息。"
            ),
        }
        return templates.get(
            profile.occupation,
            templates["上班族"],
        )


# ------------------------------------------------------------------
# 内部类：异议处理
# ------------------------------------------------------------------

class _ObjectionHandlers:

    def __init__(self):
        self._handlers = {
            "收益低": {
                "keywords": ["收益低", "利息低", "不合算", "不划算"],
                "response": "我理解您对收益的关注。其实我们这款产品综合考虑了安全性和收益性，"
                            "在同等风险级别里收益已经是很有竞争力的了。而且本金安全才是第一位的，"
                            "您说对吗？我们可以帮您做一个不同期限的收益对比，您看看就清楚了。",
                },
            "资金流动性": {
                "keywords": ["流动性", "急用", "取不出来", "锁定期"],
                "response": "这个您完全不用担心。我们的产品支持提前支取，"
                            "只是会按活期利率计算，这样既保证了您资金的灵活性，"
                            "又能让不动用的那部分享受更高的收益，一举两得。",
                },
            "不信任": {
                "keywords": ["不信任", "不可靠", "没听过", "小银行"],
                "response": "完全理解您的顾虑。我们银行是正规持牌金融机构，"
                            "产品都经过严格监管和审批。而且50万以内的存款都受存款保险制度保护，"
                            "即使银行出现问题，您的存款也是安全的。您可以随时通过官方渠道查询产品信息。",
                },
            "回去考虑": {
                "keywords": ["回去考虑", "想想", "商量", "不急"],
                "response": "李总，这完全理解，这么重要的决定确实需要慎重考虑。"
                            "不过我有个小小的建议：这类产品最近利率有调整趋势，"
                            "如果您有意向，可以先交一个'意向金'把今天的优惠利率锁定，"
                            "这样您回去考虑的时候也不会有压力。您看这样行吗？",
                },
            "已有类似产品": {
                "keywords": ["已经有了", "买过了", "已经有了"],
                "response": "那太好了，说明您非常有理财意识！不知道您目前配置的比例是怎样的？"
                            "其实合理的资产配置讲究'不把鸡蛋放在同一个篮子里'，"
                            "我们可以帮您做一个免费的资产配置诊断，看看有没有优化空间。",
                },
        }

    def get_handlers(
        self,
        profile: CustomerProfile,
        products: list[ProductRecommendation],
    ) -> list[dict]:
        """返回最相关的异议处理预案（取前3个）"""
        # 针对企业主优先返回传承/流动性/收益类异议
        if profile.occupation == "企业主":
            order = ["流动性", "收益低", "不信任", "已有类似产品", "回去考虑"]
        elif profile.occupation == "退休":
            order = ["不信任", "流动性", "收益低", "回去考虑", "已有类似产品"]
        else:
            order = ["收益低", "流动性", "回去考虑", "不信任", "已有类似产品"]

        result = []
        for key in order:
            if key in self._handlers:
                result.append({
                    "objection": key,
                    "response": self._handlers[key]["response"],
                })
            if len(result) >= 3:
                break
        return result


# ------------------------------------------------------------------
# 内部类：产品规则（占位，未来可扩展为数据库驱动）
# ------------------------------------------------------------------

class _ProductRules:
    """产品规则引擎"""
    pass
