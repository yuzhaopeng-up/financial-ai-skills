#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
税务筹划方案 - 企微集成
"""

import json
from tax_planning_engine import TaxPlanningEngine


class TaxPlanningWecom:
    def __init__(self):
        self.engine = TaxPlanningEngine(api_mode=True)

    def handle_message(self, text: str, user_id: str = None) -> dict:
        text = text.strip()

        # 税务筹划命令
        if any(text.startswith(kw) for kw in ["税务筹划", "税负分析", "税务分析", "税收筹划", "个税计算"]):
            content = text
            for kw in ["税务筹划", "税负分析", "税务分析", "税收筹划", "个税计算"]:
                content = content.replace(kw, "").strip()
            if content:
                result = self.engine.generate_tax_plan(content)
                return self._build_card(result)
            return {"type": "text", "content": "请输入收入信息，例如：`税务筹划 收入类型=工资 收入=30万 地区=北京`"}

        elif text in ["税务帮助", "帮助", "tax help"]:
            return self._build_help()

        return self._build_help()

    def _build_help(self) -> dict:
        return {
            "type": "text",
            "content": """💰 **税务筹划方案引擎**

📋 功能：输入收入类型、金额、地区，输出税负分析与节税方案

📝 命令：
`税务筹划 收入类型=工资 收入=30万 地区=北京`
`税负分析 收入=80万 收入类型=个体工商户 地区=深圳`
`个税计算 收入=50万 地区=上海`

💡 支持税种：个人所得税、企业所得税、增值税、房产税、契税

⚠️ 风险等级：🔴高 🟡中 🟢低"""
        }

    def _build_card(self, result: dict) -> dict:
        # 根据税负率决定颜色
        burden = result["total_tax_burden_rate"]
        if burden > 40:
            template = "red"
            burden_label = "🔴 高税负"
        elif burden > 20:
            template = "orange"
            burden_label = "🟡 中税负"
        else:
            template = "green"
            burden_label = "🟢 低税负"

        # 税种明细文本
        tax_lines = []
        for detail in result["tax_details"]:
            tax_lines.append(
                f"{detail['tax_name']}: ¥{detail['tax_amount']:,.0f} ({detail['effective_rate']:.1f}%)"
            )
        tax_summary = "\n".join(tax_lines)

        # 节税方案摘要
        saving_lines = []
        for plan in result["tax_saving_plans"][:3]:
            saving_lines.append(f"▪ **{plan['title']}**: {plan['estimated_saving']}")
        saving_summary = "\n".join(saving_lines)

        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"💰 税务筹划 - {burden_label}",
                    "template": template
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**收入类型**: {result['income_type']}  |  **地区**: {result['region']}\n"
                                       f"**总收入**: ¥{result['gross_income']:,.0f}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**总税额**: ¥{result['total_tax']:,.0f}\n"
                                       f"**综合税负率**: {result['total_tax_burden_rate']:.1f}%\n"
                                       f"**税后收入**: ¥{result['after_tax_income']:,.0f}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**税种明细**:\n{tax_summary}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**💡 节税方案**:\n{saving_summary}"
                        }
                    },
                ]
            }
        }


def handle(text: str, user_id: str = None) -> dict:
    return TaxPlanningWecom().handle_message(text, user_id)


if __name__ == "__main__":
    test_cases = [
        "税务筹划 收入类型=工资 收入=30万 地区=北京",
        "税务筹划 收入类型=个体工商户 收入=80万 地区=深圳",
    ]
    for tc in test_cases:
        print(f"Input: {tc}")
        result = handle(tc)
        print(json.dumps(result, ensure_ascii=False, indent=2)[:300])
        print("---")
