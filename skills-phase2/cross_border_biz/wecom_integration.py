"""
跨境业务技能 - 企微卡片集成
WeCom Card Integration for Cross-Border Business Skill
"""

import json
from typing import Optional
from crossborder_engine import CrossBorderEngine


class CrossBorderWecomCard:
    """跨境业务企微卡片生成器"""

    def __init__(self):
        self.engine = CrossBorderEngine()

    def generate_card(
        self,
        business_type: str,
        amount: float,
        currency: str,
        destination_country: str,
    ) -> dict:
        """生成企微消息卡片"""
        result = self.engine.generate(
            business_type=business_type,
            amount=amount,
            currency=currency,
            destination_country=destination_country,
        )
        return self._build_card_content(result)

    def _build_card_content(self, result: dict) -> dict:
        """构建卡片内容"""
        settlement = result["recommended_settlement"]
        fx = result["fx_hedging"]
        compliance = result["compliance"]
        crossborder_rmb = result["crossborder_rmb"]

        # 构建卡片elements
        elements = [
            {
                "tag": "markdown",
                "content": f"**📋 跨境业务方案建议**\n"
                          f"业务类型: {result['business_type']} | "
                          f"金额: {result['amount']} ({result['currency']})\n"
                          f"目的国: {result['destination_country']}"
            },
            {"tag": "hr"},
            {
                "tag": "markdown",
                "content": self._build_settlement_md(settlement),
            },
            {"tag": "hr"},
            {
                "tag": "markdown",
                "content": self._build_fx_md(fx),
            },
            {"tag": "hr"},
            {
                "tag": "markdown",
                "content": self._build_compliance_md(compliance),
            },
        ]

        card = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "🌐 跨境业务方案",
                    },
                    "template": "blue",
                },
                "elements": elements,
            },
        }

        return card

    def _build_settlement_md(self, settlement: dict) -> str:
        """构建结算方式markdown"""
        fees = settlement.get("estimated_fees", {})
        fees_str = "\n".join([f"• {k}: {v}" for k, v in fees.items()])

        flow_str = "\n".join([f"{i+1}. {s}" for i, s in enumerate(settlement["flow"])])

        return (
            f"**【结算方式】**\n"
            f"✦ 方法: **{settlement['method']}**\n"
            f"✦ 建议: {settlement['bank_recommendation']}\n"
            f"✦ 流程:\n{flow_str}\n"
            f"✦ 费用估算:\n{fees_str}"
        )

    def _build_fx_md(self, fx: dict) -> str:
        """构建外汇避险markdown"""
        return (
            f"**【外汇避险】**\n"
            f"✦ 推荐工具: **{fx['recommended']}**\n"
            f"✦ 方案结构: {fx['structure']}\n"
            f"✦ 预计成本: {fx['estimated_cost']}\n"
            f"✦ 风险等级: {fx['risk_level']}"
        )

    def _build_compliance_md(self, compliance: dict) -> str:
        """构建合规要点markdown"""
        regs = "\n".join([f"• {r}" for r in compliance["required_registrations"]])
        licenses = "\n".join([f"• {l}" for l in compliance["restricted_licenses"]]) if compliance["restricted_licenses"] else "无特殊许可证"
        benefits = "\n".join([f"• {b}" for b in compliance["tax_benefits"]]) if compliance["tax_benefits"] else "无专项优惠"

        return (
            f"**【合规要点】**\n"
            f"✦ 所需备案:\n{regs}\n"
            f"✦ 许可证件:\n{licenses}\n"
            f"✦ 税收优惠:\n{benefits}"
        )

    def generate_and_send(
        self,
        business_type: str,
        amount: float,
        currency: str,
        destination_country: str,
        chat_id: Optional[str] = None,
    ) -> dict:
        """生成卡片并返回发送格式"""
        card = self.generate_card(business_type, amount, currency, destination_country)
        return {
            "card": card,
            "suggestions": [
                {
                    "tag": "replace_internet",
                    "text": "查看更多详情",
                    "replace_text": "点击查看完整方案",
                }
            ],
        }


def format_wecom_card(result: dict) -> dict:
    """将engine结果转换为企微卡片格式"""
    card_generator = CrossBorderWecomCard()
    return card_generator._build_card_content(result)


if __name__ == "__main__":
    # 测试
    card_gen = CrossBorderWecomCard()
    result = card_gen.generate_card(
        business_type="出口企业",
        amount=1000000,
        currency="USD",
        destination_country="欧盟",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
