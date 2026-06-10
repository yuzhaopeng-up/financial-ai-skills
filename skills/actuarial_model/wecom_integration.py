#!/usr/bin/env python3
"""
企微卡片集成 - 精算模型
用法:
    python3 wecom_integration.py generate "精算模型 终身寿险 30岁男性 保额100万 20年缴"
    python3 wecom_integration.py card "精算模型 终身寿险 30岁男性 保额100万 20年缴"
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actuarial_model import ActuarialModelEngine


def build_card(result: dict) -> dict:
    """
    构建企微消息卡片

    Args:
        result: ActuarialModelEngine.calculate() 返回的字典

    Returns:
        企微卡片格式字典
    """
    insured = result.get("insured_info", {})
    premium = result.get("premium_pricing", {})
    reserve = result.get("reserve_evaluation", {})
    solvency = result.get("solvency_assessment", {})
    assumptions = result.get("actuarial_assumptions", {})

    # 判断偿付能力状态
    ratio = solvency.get("comprehensive_solvency_ratio", 0)
    if ratio >= 150:
        ratio_color = "green"
        ratio_emoji = "✅"
    elif ratio >= 100:
        ratio_color = "yellow"
        ratio_emoji = "⚠️"
    else:
        ratio_color = "red"
        ratio_emoji = "🔴"

    return {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"📊 精算模型报告 | {result.get('product_type', '终身寿险')}",
                },
                "color": "blue",
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": (
                        f"**👤 投保人信息**\n"
                        f"年龄：{insured.get('age', 'N/A')}岁　｜　"
                        f"性别：{insured.get('gender', 'N/A')}　｜　"
                        f"保额：**{insured.get('sum_insured', 0):,.0f}** 元"
                    ),
                },
                {"tag": "hr"},
                {
                    "tag": "markdown",
                    "content": (
                        f"**💰 保费定价**\n"
                        f"• 纯保费（趸交）：**{premium.get('net_premium_single', 0):,.2f}** 元\n"
                        f"• 纯保费（年缴）：**{premium.get('net_premium_per_year', 0):,.2f}** 元/年\n"
                        f"• 首年附加费用：**{premium.get('expense_first_year', 0):,.2f}** 元\n"
                        f"• 续年附加费用：**{premium.get('expense_renewal', 0):,.2f}** 元/年\n"
                        f"• **总保费（年缴）：{premium.get('gross_premium_per_year', 0):,.2f}** 元/年"
                    ),
                },
                {"tag": "hr"},
                {
                    "tag": "markdown",
                    "content": (
                        f"**📋 准备金评估**\n"
                        f"• 未决赔款准备金：{reserve.get('unpaid_claim_reserve', 0):,.2f} 元\n"
                        f"• 已赚保费准备金：{reserve.get('earned_premium_reserve', 0):,.2f} 元\n"
                        f"• **总准备金：{reserve.get('total_reserve', 0):,.2f}** 元"
                    ),
                },
                {"tag": "hr"},
                {
                    "tag": "markdown",
                    "content": (
                        f"**{ratio_emoji} 偿付能力评估**\n"
                        f"• 实际资本：{solvency.get('actual_capital', 0):,.2f} 元\n"
                        f"• 最低资本：{solvency.get('minimum_capital', 0):,.2f} 元\n"
                        f"• **核心偿付率：{solvency.get('core_solvency_ratio', 0):.2f}%**　｜　"
                        f"**综合偿付率：{solvency.get('comprehensive_solvency_ratio', 0):.2f}%**\n"
                        f"• 风险边际：{solvency.get('risk_margin', 0):,.2f} 元"
                    ),
                },
                {"tag": "hr"},
                {
                    "tag": "markdown",
                    "content": (
                        f"**📐 精算假设**\n"
                        f"死亡率表：{assumptions.get('mortality_table', 'N/A')}　｜　"
                        f"预定利率：{assumptions.get('interest_rate', 0) * 100:.1f}%　｜　"
                        f"首年费用率：{assumptions.get('first_year_expense_rate', 0) * 100:.1f}%"
                    ),
                },
                {
                    "tag": "note",
                    "elements": [
                        {"tag": "plain_text", "content": f"精算模型 Engine v1.0 | CL{assumptions.get('mortality_table', 'N/A')} 生命表"}
                    ],
                },
            ],
        },
    }


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "generate"
    text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

    if not text.strip():
        print("用法: python3 wecom_integration.py [card|generate] <产品描述>", file=sys.stderr)
        print("示例: python3 wecom_integration.py card 精算模型 终身寿险 30岁男性 保额100万 20年缴", file=sys.stderr)
        sys.exit(1)

    # 从文本解析参数
    import re

    def parse_gender(t):
        return "女性" if "女性" in t or "女" in t else "男性"

    def parse_age(t):
        m = re.search(r"(\d+)岁", t)
        return int(m.group(1)) if m else 30

    def parse_sum_insured(t):
        m = re.search(r"保额\s*(\d+(?:\.\d+)?)\s*万", t)
        if m:
            return float(m.group(1)) * 10000
        m = re.search(r"保额\s*(\d+)", t)
        if m:
            return float(m.group(1))
        return 1000000

    def parse_payment_term(t):
        m = re.search(r"(\d+)\s*年", t)
        return int(m.group(1)) if m else 20

    def parse_product_type(t):
        if "终身" in t:
            return "终身寿险"
        if "定期" in t:
            return "定期寿险"
        if "重疾" in t:
            return "重疾险"
        return "终身寿险"

    product_type = parse_product_type(text)
    gender = parse_gender(text)
    age = parse_age(text)
    sum_insured = parse_sum_insured(text)
    payment_term = parse_payment_term(text)

    engine = ActuarialModelEngine()
    result = engine.calculate(
        product_type=product_type,
        age=age,
        gender=gender,
        sum_insured=sum_insured,
        payment_term=payment_term,
    )

    if command == "card":
        card = build_card(result)
        print(json.dumps(card, ensure_ascii=False, indent=2))
    else:
        # 默认输出格式化报告
        print(engine.format_report(result))


if __name__ == "__main__":
    main()
