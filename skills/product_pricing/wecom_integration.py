#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品定价 - 企微集成
"""

import json
from product_pricing_engine import ProductPricingEngine


class ProductPricingWecom:
    def __init__(self):
        self.engine = ProductPricingEngine(api_mode=True)

    def handle_message(self, text: str, user_id: str = None) -> dict:
        text = text.strip()

        if not text:
            return self._build_help()

        # 解析输入
        parsed = self.engine.parse_input(text)

        if not parsed["product_type"]:
            return {"type": "text", "content": "请指定产品类型（存款/贷款/汇兑/理财），例如：`产品定价 贷款 稳健型 3.6%`"}

        if not parsed["risk_level"]:
            return {"type": "text", "content": "请指定客户风险等级（保守型/稳健型/进取型），例如：`产品定价 贷款 稳健型 3.6%`"}

        if not parsed["market_rate"]:
            return {"type": "text", "content": "请指定市场利率（数字+%%），例如：`产品定价 贷款 稳健型 3.6%`"}

        result = self.engine.price(
            product_type=parsed["product_type"],
            risk_level=parsed["risk_level"],
            market_rate=parsed["market_rate"],
            sub_product=parsed.get("sub_product"),
        )

        return self._build_card(result)

    def _build_help(self) -> dict:
        return {
            "type": "text",
            "content": """💰 **产品定价引擎**

📋 功能：输入产品类型+客户风险等级+市场利率，输出定价方案+敏感性分析

📝 命令：`产品定价 [类型] [风险等级] [利率]`

💰 产品类型：存款 / 贷款 / 汇兑 / 理财
👤 风险等级：保守型 / 稳健型 / 进取型

**示例：**
`产品定价 贷款 稳健型 3.6%`
`存款 保守型 2.0%`
`理财 进取型 2.5%`

🔢 返回：执行利率 + 风险溢价 + 银行利润 + 竞争力评估 + 利率敏感性分析（±25/50/75/100bp）"""
        }

    def _build_card(self, result: dict) -> dict:
        if "error" in result:
            return {"type": "text", "content": f"❌ {result['error']}"}

        competitiveness = result.get("competitiveness", {})
        comp_label = competitiveness.get("label", "")

        # 利率敏感性摘要
        sensitivity = result.get("sensitivity", [])
        # 取上行(+50bp)和下行(-50bp)两个关键情景
        scenarios_display = []
        for s in sensitivity:
            if s["bp"] in [-50, 0, 50]:
                scenarios_display.append({
                    "bp": s["bp"],
                    "scenario": s["scenario"],
                    "customer_rate": s["customer_rate"],
                    "rate_diff": s["rate_diff"],
                })

        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": (
                        f"**产品**: {result['product_type']} / {result['sub_product']}\n"
                        f"**风险等级**: {result['risk_level']}\n"
                        f"**市场利率**: {result['market_rate']:.2f}%"
                    ),
                },
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": (
                        f"💎 **执行利率**: **{result['offered_rate']:.2f}%**\n"
                        f"利差: {result['spread']:.2f}% | "
                        f"风险溢价: {result['risk_premium']:.2f}% | "
                        f"银行利润: {result['bank_margin']:.2f}%"
                    ),
                },
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": (
                        f"🏆 竞争力: {comp_label}\n"
                        f"较{competitiveness.get('benchmark_name', '基准')}"
                        f"{vp_pct_str(competitiveness.get('vs_benchmark_pct', 0))}"
                    ),
                },
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"💡 {result.get('recommendation', '')}",
                },
            },
        ]

        # 添加敏感性分析
        if scenarios_display:
            sens_lines = ["**📉 利率敏感性分析**"]
            for s in scenarios_display:
                diff_str = f"{s['rate_diff']:+.2f}%" if s["bp"] != 0 else "基准"
                sens_lines.append(
                    f"{s['scenario']}: {s['customer_rate']:.2f}% ({diff_str})"
                )
            elements.append({"tag": "hr"})
            elements.append({
                "tag": "div",
                "text": {"tag": "lark_md", "content": "\n".join(sens_lines)},
            })

        template_map = {"excellent": "purple", "good": "blue", "fair": "gray", "poor": "red"}
        template = template_map.get(competitiveness.get("level", "gray"), "gray")

        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"💰 产品定价 - {result['sub_product']}",
                    "template": template,
                },
                "elements": elements,
            },
        }


def vp_pct_str(pct: float) -> str:
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


def handle(text: str, user_id: str = None) -> dict:
    return ProductPricingWecom().handle_message(text, user_id)


if __name__ == "__main__":
    # 测试
    result = handle("产品定价 贷款 稳健型 3.6%")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:800])
