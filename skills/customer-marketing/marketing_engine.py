#!/usr/bin/env python3
"""
客户经理营销话术生成引擎
核心逻辑：基于客户画像 + 营销目标 + 渠道 + 风格，生成专业话术
"""
import json
import random
from pathlib import Path
from typing import Dict, List, Optional


class MarketingEngine:
    """营销话术生成引擎"""

    # 话术风格定义
    STYLES = {
        "formal": {
            "tone": "正式专业",
            "greeting": "{name}您好，我是{bank}的客户经理{manager}。",
            "transition": "关于贵公司的{topic}，我们有以下方案供您参考：",
            "closing": "以上方案供您参考，如有任何问题欢迎随时联系。",
        },
        "friendly": {
            "tone": "亲切自然",
            "greeting": "{name}，好久不见！最近生意怎么样？",
            "transition": "对了，最近有个产品特别适合您这种情况：",
            "closing": "您先考虑考虑，有需要随时找我！",
        },
        "professional": {
            "tone": "数据驱动",
            "greeting": "{name}您好，根据我们对{industry}行业的最新研究...",
            "transition": "基于贵公司的{scale}和{news}，我们推荐以下方案：",
            "closing": "该方案预计可为贵公司节省{cost_save}，提升{benefit}。",
        },
        "concise": {
            "tone": "简洁明了",
            "greeting": "{name}您好，",
            "transition": "推荐{product}：",
            "closing": "详情可回复了解。",
        },
    }

    # 渠道适配
    CHANNELS = {
        "phone": {"max_length": 300, "format": "口语化，适合朗读"},
        "wechat": {"max_length": 500, "format": "分段清晰，适合阅读"},
        "face-to-face": {"max_length": 800, "format": "完整详细，可展开讲解"},
        "sms": {"max_length": 150, "format": "极度精简，核心卖点"},
    }

    # 行业-产品映射
    INDUSTRY_PRODUCTS = {
        "制造业": ["供应链金融", "设备融资租赁", "订单融资", "厂房抵押贷款"],
        "零售业": ["POS流水贷", "进货周转贷", "信用卡", "商户收单"],
        "科技": ["知识产权质押贷", "股权融资", "科创贷", "人才贷"],
        "房地产": ["开发贷", "按揭贷", "经营性物业贷", "工程保函"],
        "餐饮": ["装修贷", "食材供应链融资", "POS流水贷", "信用卡"],
        "医疗": ["医疗器械融资租赁", "医保应收账款融资", "医院建设贷", "人才贷"],
        "教育": ["学费应收账款融资", "校园建设贷", "教育分期", "人才贷"],
        "物流": ["运费保理", "车辆融资租赁", "仓储质押贷", "ETC信用卡"],
    }

    # 常见异议及应答
    OBJECTIONS = {
        "利率太高": [
            "张总，这个利率相比民间借贷已经低很多了，而且我们还能根据您的流水情况申请利率优惠。",
            "理解您的顾虑。其实您可以算一笔账，如果这笔资金能帮您在旺季多接几单，收益远大于利息成本。",
            "我们最近有针对优质客户的利率折扣活动，我可以帮您申请一下。",
        ],
        "已有合作银行": [
            "完全理解，多一家银行合作其实对贵公司更有利，可以分散风险，也能获得更多授信额度。",
            "我们银行在{industry}行业有专门的优惠政策，很多客户都是在我们这里获得了更好的条件。",
            "没关系，您可以先了解一下我们的方案，做个对比，反正也不吃亏。",
        ],
        "不需要": [
            "明白，不过最近{industry}行业很多企业在扩张期都遇到了资金周转问题，提前了解有备无患。",
            "即使现在不需要，了解一下最新的金融政策也是好的，说不定以后用得上。",
            "那您目前主要用什么方式解决资金周转呢？也许我能给您一些建议。",
        ],
        "考虑一下": [
            "好的，这是应该的。我把详细资料发给您，您和财务商量一下。",
            "没问题。我给您准备一份对比方案，您看看哪种更适合贵公司。",
            "理解，这种决策确实需要慎重。我下周再联系您，看看有什么需要补充的。",
        ],
        "手续太麻烦": [
            "现在我们的流程已经简化很多了，很多材料可以线上提交，最快当天就能放款。",
            "您放心，我会全程协助您准备材料，其实只需要提供基本的证照和流水就行。",
            "对于像您这样的优质客户，我们还有绿色通道，审批速度比普通客户快一倍。",
        ],
    }

    def __init__(self, templates_dir: Optional[str] = None):
        self.templates_dir = Path(templates_dir) if templates_dir else Path(__file__).parent / "templates"
        self._load_templates()

    def _load_templates(self):
        """加载话术模板"""
        self.templates = {
            "opening": {},
            "product": {},
            "closing": {},
        }
        # 如果模板文件存在则加载，否则使用内置模板
        for key in self.templates:
            template_file = self.templates_dir / f"{key}_templates.json"
            if template_file.exists():
                with open(template_file, "r", encoding="utf-8") as f:
                    self.templates[key] = json.load(f)

    def generate_script(
        self,
        customer_name: str,
        industry: str,
        company_scale: str = "",
        recent_news: str = "",
        marketing_goal: str = "",
        channel: str = "face-to-face",
        style: str = "professional",
        bank_name: str = "我行",
        manager_name: str = "",
    ) -> Dict:
        """
        生成营销话术

        Args:
            customer_name: 客户姓名/称呼
            industry: 客户行业
            company_scale: 企业规模（如"年营收5000万"）
            recent_news: 客户近期动态（如"刚获得大额订单"）
            marketing_goal: 营销目标（如"推荐供应链金融产品"）
            channel: 渠道（phone/wechat/face-to-face/sms）
            style: 风格（formal/friendly/professional/concise）
            bank_name: 银行名称
            manager_name: 客户经理姓名

        Returns:
            包含开场白、产品介绍、促成话术、异议处理的话术字典
        """
        style_config = self.STYLES.get(style, self.STYLES["professional"])
        channel_config = self.CHANNELS.get(channel, self.CHANNELS["face-to-face"])

        # 确定推荐产品
        products = self.INDUSTRY_PRODUCTS.get(industry, ["综合金融服务"])
        recommended_product = products[0] if products else "综合金融服务"

        # 生成话术各部分
        script = {
            "customer_name": customer_name,
            "industry": industry,
            "channel": channel,
            "style": style,
            "opening": self._generate_opening(
                customer_name, industry, recent_news, style_config, bank_name, manager_name
            ),
            "product_intro": self._generate_product_intro(
                industry, company_scale, recent_news, recommended_product, marketing_goal, style_config
            ),
            "benefits": self._generate_benefits(industry, recommended_product),
            "closing": self._generate_closing(style_config, customer_name),
            "objections": self._generate_objections(industry, marketing_goal),
            "recommended_product": recommended_product,
        }

        return script

    def _generate_opening(
        self,
        customer_name: str,
        industry: str,
        recent_news: str,
        style_config: Dict,
        bank_name: str,
        manager_name: str,
    ) -> str:
        """生成开场白"""
        greeting = style_config["greeting"].format(
            name=customer_name,
            bank=bank_name,
            manager=manager_name or "",
            industry=industry,
        )

        # 如果有近期动态，加入寒暄
        if recent_news:
            news_hook = f"听说贵公司最近{recent_news}，恭喜啊！"
            return f"{greeting}\n{news_hook}"

        return greeting

    def _generate_product_intro(
        self,
        industry: str,
        company_scale: str,
        recent_news: str,
        product: str,
        marketing_goal: str,
        style_config: Dict,
    ) -> str:
        """生成产品介绍"""
        transition = style_config["transition"].format(
            topic=marketing_goal or product,
            industry=industry,
            scale=company_scale or "",
            news=recent_news or "",
        )

        product_desc = f"我们这款{product}专门针对{industry}企业设计"
        if company_scale:
            product_desc += f"，特别适合像贵公司这样{company_scale}的企业"
        product_desc += "。"

        features = self._get_product_features(product)
        feature_text = "主要优势包括：" + "、".join(features)

        return f"{transition}\n{product_desc}\n{feature_text}"

    def _get_product_features(self, product: str) -> List[str]:
        """获取产品特点"""
        features_map = {
            "供应链金融": ["无需抵押", "随借随还", "利率优惠", "审批快速"],
            "设备融资租赁": ["保留现金流", "税务优化", "设备更新快", "手续简便"],
            "POS流水贷": ["纯信用", "按日计息", "额度循环", "线上申请"],
            "知识产权质押贷": ["盘活无形资产", "额度高", "利率低", "政府贴息"],
            "厂房抵押贷款": ["额度大", "期限长", "利率低", "可循环使用"],
            "信用卡": ["免息期长", "权益丰富", "分期灵活", "积分兑换"],
            "综合金融服务": ["一站式解决", "方案定制", "专属服务", "费率优惠"],
        }
        return features_map.get(product, ["专业定制", "费率优惠", "服务便捷"])

    def _generate_benefits(self, industry: str, product: str) -> str:
        """生成价值说明"""
        benefits_map = {
            "制造业": f"使用{product}后，预计可帮助您：缩短账期30%、降低融资成本15%、提升资金周转效率。",
            "零售业": f"使用{product}后，预计可帮助您：扩大进货规模、抓住旺季商机、提升客户满意度。",
            "科技": f"使用{product}后，预计可帮助您：加速研发投入、抢占市场先机、吸引优秀人才。",
            "餐饮": f"使用{product}后，预计可帮助您：快速扩张门店、优化食材供应链、提升翻台率。",
        }
        return benefits_map.get(industry, f"使用{product}后，预计可帮助您提升经营效率、降低融资成本。")

    def _generate_closing(self, style_config: Dict, customer_name: str) -> str:
        """生成促成话术"""
        closing = style_config["closing"].format(
            name=customer_name,
            cost_save="20%",
            benefit="资金周转效率",
        )
        return closing

    def _generate_objections(self, industry: str, marketing_goal: str) -> List[Dict]:
        """生成常见异议及应答"""
        objections = []
        for obj_key, responses in self.OBJECTIONS.items():
            # 随机选择一条应答，并替换行业变量
            response = random.choice(responses)
            response = response.replace("{industry}", industry)
            objections.append({
                "objection": obj_key,
                "response": response,
            })
        return objections

    def generate_objections_training(
        self,
        marketing_goal: str,
        industry: str = "",
        difficulty: str = "medium",
    ) -> Dict:
        """
        生成异议处理训练场景

        Args:
            marketing_goal: 营销目标
            industry: 客户行业
            difficulty: 难度（easy/medium/hard）

        Returns:
            训练场景字典
        """
        scenarios = {
            "easy": ["考虑一下", "不需要"],
            "medium": ["利率太高", "手续太麻烦"],
            "hard": ["已有合作银行", "对你们银行不了解", "需要董事会决议"],
        }

        selected_objections = scenarios.get(difficulty, scenarios["medium"])

        training = {
            "scenario": f"您正在向一位{industry or '企业'}客户推荐{marketing_goal}",
            "difficulty": difficulty,
            "objections": [],
        }

        for obj in selected_objections:
            if obj in self.OBJECTIONS:
                response = random.choice(self.OBJECTIONS[obj])
                response = response.replace("{industry}", industry or "该")
                training["objections"].append({
                    "objection": obj,
                    "response": response,
                    "tips": self._get_response_tips(obj),
                })

        return training

    def _get_response_tips(self, objection: str) -> str:
        """获取应答技巧提示"""
        tips_map = {
            "利率太高": "技巧：不要直接反驳，而是引导客户计算综合收益。",
            "已有合作银行": "技巧：强调互补性而非替代性，突出差异化优势。",
            "不需要": "技巧：先了解客户真实需求，再针对性推荐。",
            "考虑一下": "技巧：给客户提供决策辅助材料，约定跟进时间。",
            "手续太麻烦": "技巧：强调简化流程和全程协助，降低客户心理门槛。",
        }
        return tips_map.get(objection, "技巧：倾听客户顾虑，针对性回应。")


class MarketingFormatter:
    """营销话术格式化输出"""

    @staticmethod
    def format_script(script: Dict) -> str:
        """格式化输出完整话术"""
        lines = [
            f"{'='*60}",
            f"🎯 营销话术生成结果",
            f"{'='*60}",
            f"",
            f"📋 客户信息",
            f"  客户：{script['customer_name']}",
            f"  行业：{script['industry']}",
            f"  渠道：{script['channel']}",
            f"  风格：{script['style']}",
            f"  推荐产品：{script['recommended_product']}",
            f"",
            f"{'='*60}",
            f"💬 开场白",
            f"{'='*60}",
            f"{script['opening']}",
            f"",
            f"{'='*60}",
            f"📦 产品介绍",
            f"{'='*60}",
            f"{script['product_intro']}",
            f"",
            f"{'='*60}",
            f"✨ 价值说明",
            f"{'='*60}",
            f"{script['benefits']}",
            f"",
            f"{'='*60}",
            f"🔚 促成话术",
            f"{'='*60}",
            f"{script['closing']}",
            f"",
            f"{'='*60}",
            f"🛡️ 常见异议处理",
            f"{'='*60}",
        ]

        for obj in script['objections']:
            lines.extend([
                f"",
                f"❓ 客户：\"{obj['objection']}\"",
                f"💡 应答：{obj['response']}",
            ])

        lines.append(f"\n{'='*60}")
        return "\n".join(lines)

    @staticmethod
    def format_objections(objections: Dict) -> str:
        """格式化输出异议处理"""
        lines = [
            f"{'='*60}",
            f"🛡️ 异议处理训练",
            f"{'='*60}",
            f"",
            f"场景：{objections['scenario']}",
            f"难度：{objections['difficulty']}",
            f"",
        ]

        for i, obj in enumerate(objections['objections'], 1):
            lines.extend([
                f"{'-'*60}",
                f"异议 {i}：\"{obj['objection']}\"",
                f"",
                f"💡 推荐应答：",
                f"{obj['response']}",
                f"",
                f"📌 {obj['tips']}",
                f"",
            ])

        lines.append(f"{'='*60}")
        return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    engine = MarketingEngine()
    formatter = MarketingFormatter()

    print("=" * 60)
    print("测试1：基础话术生成")
    print("=" * 60)
    result = engine.generate_script(
        customer_name="张总",
        industry="制造业",
        company_scale="年营收5000万",
        recent_news="刚获得大额订单",
        marketing_goal="推荐供应链金融产品",
        channel="face-to-face",
        style="professional",
    )
    print(formatter.format_script(result))

    print("\n" + "=" * 60)
    print("测试2：异议处理训练")
    print("=" * 60)
    training = engine.generate_objections_training(
        marketing_goal="推荐供应链金融产品",
        industry="制造业",
        difficulty="medium",
    )
    print(formatter.format_objections(training))
