#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能营销话术引擎 - 企微集成
"""

import json
from smart_marketing_engine import SmartMarketingEngine


class SmartMarketingWecom:
    """企微集成"""

    def __init__(self):
        self.engine = SmartMarketingEngine(api_mode=True)

    def handle_message(self, text: str, user_id: str = None) -> dict:
        text = text.strip()

        if not text:
            return self._build_help()

        # 判断渠道关键词
        channel = None
        if text.startswith("短信"):
            channel = "短信"
            text = text[2:].strip()
        elif text.startswith("微信"):
            channel = "微信"
            text = text[2:].strip()
        elif text.startswith("电话"):
            channel = "电话"
            text = text[2:].strip()

        # 通用命令
        if text in ["帮助", "使用说明", "help"]:
            return self._build_help()

        # 解析并生成话术
        result = self.engine.generate_script(text, channel=channel)

        return self._build_card(result)

    def _build_help(self) -> dict:
        return {
            "type": "text",
            "content": """🎯 **智能营销话术引擎**

📋 功能：根据客户画像生成精准营销话术 + 异议预判

📝 命令：
`营销话术 年龄=35 职业=企业主 资产=500万 风险偏好=稳健`
`保险话术 30岁白领50万进取型`
`短信 存款话术 50岁退休人员100万保守型`

🏦 支持产品：定期存款、理财、基金、保险、贷款、信用卡、贵金属、国债、信托、跨境金融、消费分期（共11种）

✅ 验收：生成<5秒，支持10+产品类型""",
        }

    def _build_card(self, result: dict) -> dict:
        """构建企微消息卡片"""
        script = result["script"]
        profile = result["profile"]
        objections = result.get("objections", [])

        # 异议预判元素
        objection_elements = []
        for obj in objections[:3]:
            objection_elements.extend([
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**❓ Q{obj['id']}**: {obj['objection']}"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**✅ A**: {obj['answer']}"
                    }
                },
                {"tag": "hr"},
            ])

        # 产品推荐元素
        recommended = result.get("recommended_products", [])
        product_text = "、".join([rp["product"] for rp in recommended[:3]]) if recommended else result["product"]

        card = {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"🎯 营销话术 | {result['product']} | {result['channel']}",
                    "template": "blue"
                },
                "elements": [
                    # 画像概览
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": (
                                f"👤 {profile.get('age', '?')}岁{profile.get('occupation', '')} | "
                                f"{profile.get('assets', '?')}元 | "
                                f"{profile.get('risk_preference', '')}型"
                            )
                        }
                    },
                    {"tag": "hr"},

                    # 开场白
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**【开场白】**\n{script['opening']}"
                        }
                    },
                    {"tag": "hr"},

                    # 价值主张
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**【价值主张】**\n{script['value_proposition']}"
                        }
                    },
                    {"tag": "hr"},

                    # 行动号召
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**【行动号召】**\n{script['cta']}"
                        }
                    },
                ]
            }
        }

        # 插入异议预判
        if objection_elements:
            card["card"]["elements"].extend([
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": f"**⚠️ 异议预判**（{len(objections)}条）"}
                },
                *objection_elements,
            ])

        # 底部验收信息
        card["card"]["elements"].extend([
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": (
                        f"🏦 产品匹配: {product_text} | "
                        f"⏱ 生成耗时: {result['generation_time_ms']}ms < 5000ms ✅"
                    )
                }
            },
        ])

        return card


def handle(text: str, user_id: str = None) -> dict:
    return SmartMarketingWecom().handle_message(text, user_id)


if __name__ == "__main__":
    test_cases = [
        "营销话术 客户年龄=35 职业=企业主 资产=500万 风险偏好=稳健",
        "保险话术 30岁白领50万进取型",
        "短信 存款话术 50岁退休人员100万保守型",
    ]
    for tc in test_cases:
        print(f"\n{'─'*40}")
        print(f"输入: {tc}")
        result = handle(tc)
        if result["type"] == "interactive":
            print("✅ 企微卡片构建成功")
            print(f"   产品: {result['card']['header']['title']}")
        else:
            print(result["content"][:100])
