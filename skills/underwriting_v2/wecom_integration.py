"""
企微/飞书两融核保卡片集成

生成适用于企微机器人卡片或飞书消息卡片的两融核保报告JSON
"""

import json
import datetime
from typing import Dict, Any, Optional

from .underwriting_v2_engine import UnderwritingV2Engine


def generate_wecom_card(result: Dict[str, Any],
                       title: str = "券商两融智能核保报告") -> Dict[str, Any]:
    """
    生成企微/飞书卡片格式的两融核保报告

    Args:
        result: UnderwritingV2Engine.underwrite() 返回的核保结果
        title: 卡片标题

    Returns:
        企微/飞书卡片JSON结构
    """
    admission = result["准入评估"]
    collateral = result["担保物折算"]
    quota = result["额度建议"]
    rate = result["利率建议"]
    customer = result["客户信息"]

    # 决策颜色映射
    decision_colors = {
        "可开": "green",
        "有条件开": "yellow",
        "不开": "red"
    }
    color = decision_colors.get(admission["决定"], "grey")

    # 决策图标
    decision_icons = {
        "可开": "✅",
        "有条件开": "⚠️",
        "不开": "❌"
    }
    icon = decision_icons.get(admission["决定"], "📋")

    # 利率等级颜色
    rate_level = rate.get("信用等级", "良好")
    rate_colors = {
        "极优": "#53D395",
        "优秀": "#53D395",
        "良好": "#4299E1",
        "一般": "#ECC94B",
        "较差": "#F56565"
    }
    rate_color = rate_colors.get(rate_level, "#718096")

    # 卡片元素
    elements = []

    # 1. 核心结论区
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": (
                f"**准入决定：** {admission['决定']} {icon}\n"
                f"**最高可借：** {quota['最高可借金额(万)']}万\n"
                f"**融资利率：** {rate['融资年化利率']}（{rate['信用等级']}）"
            )
        }
    })

    elements.append({"tag": "hr"})

    # 2. 客户信息区
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": (
                f"**【客户信息】**\n"
                f"• 总资产：{customer['总资产(万)']}万\n"
                f"• 持仓市值：{customer['持仓市值(万)']}万（{customer['持仓类型']}）\n"
                f"• 信用评分：{customer['信用评分']} | 信用记录：{customer['信用记录']}\n"
                f"• 风险等级：{customer['风险等级']} | 持股：{customer['持股月数']}个月\n"
                f"• 负债状态：{customer['负债状态']}"
            )
        }
    })

    elements.append({"tag": "hr"})

    # 3. 准入条件明细
    qual_lines = "\n".join([f"• {r}" for r in admission["条件明细"]])
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": (
                f"**【准入评估】** {admission['资质评分']}（{admission['满足条件']}）\n"
                f"{qual_lines}"
            )
        }
    })

    elements.append({"tag": "hr"})

    # 4. 担保物折算
    collateral_lines = []
    for detail in collateral.get("明细", []):
        collateral_lines.append(
            f"• {detail['asset_type']}：{detail['market_value']/10000:.0f}万 × {detail['discount_rate']:.0%} = {detail['collateral_value']/10000:.0f}万"
        )
    coll_text = "\n".join(collateral_lines)

    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": (
                f"**【担保物折算】**\n"
                f"• 总市值：{collateral['总市值(万)']}万 → 折算价值：{collateral['折算价值(万)']}万（{collateral['综合折算率']:.0%}）\n"
                f"{coll_text}"
            )
        }
    })

    # 5. 额度建议
    elements.append({"tag": "hr"})
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": (
                f"**【额度建议】**\n"
                f"• 最高可借金额：**{quota['最高可借金额(万)']}万**\n"
                f"• 维持担保比例：{quota['维持担保比例']} | 警戒线：{quota['警戒线']} | 平仓线：{quota['平仓线']}"
            )
        }
    })

    # 6. 风险提示
    if result["风险提示"]:
        elements.append({"tag": "hr"})
        warning_lines = []
        for w in result["风险提示"]:
            level_icon = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(w["级别"], "⚪")
            warning_lines.append(f"{level_icon} [{w['级别']}] {w['类型']}：{w['说明']}")
        warning_text = "\n".join(warning_lines)

        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**【风险提示】**\n{warning_text}"
            }
        })

    # 7. 时间戳
    elements.append({
        "tag": "note",
        "elements": [
            {
                "tag": "plain_text",
                "text": f"报告时间：{result['报告时间']} | 两融核保v2"
            }
        ]
    })

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "text": f"{icon} {title}",
                    "lang": "zh_cn"
                },
                "template": color
            },
            "elements": elements
        }
    }

    return card


def generate_wecom_card_simple(result: Dict[str, Any]) -> str:
    """
    生成简洁版企微卡片文本（用于text类型的消息）

    Returns:
        格式化文本字符串
    """
    admission = result["准入评估"]
    collateral = result["担保物折算"]
    quota = result["额度建议"]
    rate = result["利率建议"]
    customer = result["客户信息"]

    decision_icons = {"可开": "✅", "有条件开": "⚠️", "不开": "❌"}
    icon = decision_icons.get(admission["决定"], "📋")

    lines = [
        "━━━━━━━━━━━━━━━━━━━━",
        f"  券商两融智能核保报告",
        "━━━━━━━━━━━━━━━━━━━━",
        "",
        f"【准入决定】{admission['决定']} {icon}",
        f"最高可借：{quota['最高可借金额(万)']}万 | 融资利率：{rate['融资年化利率']}",
        f"资质评分：{admission['资质评分']}（{admission['满足条件']}）",
        "",
        "【客户信息】",
        f"总资产：{customer['总资产(万)']}万 | 持仓：{customer['持仓市值(万)']}万（{customer['持仓类型']}）",
        f"信用评分：{customer['信用评分']} | 风险：{customer['风险等级']} | 持股：{customer['持股月数']}个月",
        f"负债：{customer['负债状态']}",
        "",
        "【担保物折算】",
        f"市值{collateral['总市值(万)']}万 → 折算{collateral['折算价值(万)']}万（{collateral['综合折算率']:.0%}）",
    ]

    for detail in collateral.get('明细', []):
        lines.append(f"  {detail['asset_type']}：{detail['market_value']/10000:.0f}万 × {detail['discount_rate']:.0%} = {detail['collateral_value']/10000:.0f}万")

    lines.extend([
        "",
        "【额度建议】",
        f"最高可借：{quota['最高可借金额(万)']}万 | 维持担保：{quota['维持担保比例']}",
        f"警戒线：{quota['警戒线']} | 平仓线：{quota['平仓线']}",
        "",
        f"【利率】融资{rate['融资年化利率']} | 融券{rate['融券年化利率']} | 信用{rate['信用等级']} {rate['利率调整']}",
    ])

    if result["风险提示"]:
        lines.append("")
        lines.append("【风险提示】")
        for w in result["风险提示"]:
            level_icon = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(w["级别"], "⚪")
            lines.append(f"  {level_icon}[{w['级别']}] {w['类型']}：{w['说明']}")

    lines.extend([
        "",
        f"报告时间：{result['报告时间']}",
        "━━━━━━━━━━━━━━━━━━━━"
    ])

    return "\n".join(lines)


def underwrite_and_send_wecom(text: str, format: str = "card") -> Dict[str, Any]:
    """
    快捷函数：核保并生成企微卡片

    Args:
        text: 自然语言两融核保描述
        format: 输出格式（card=卡片JSON，text=纯文本，both=两者）

    Returns:
        核保结果和卡片内容
    """
    engine = UnderwritingV2Engine()
    result = engine.underwrite(raw_input=text)

    output = {"result": result}

    if format == "card":
        output["card"] = generate_wecom_card(result)
    elif format == "text":
        output["text"] = generate_wecom_card_simple(result)
    else:
        output["card"] = generate_wecom_card(result)
        output["text"] = generate_wecom_card_simple(result)

    return output


def send_to_wecom_webhook(webhook_url: str, card: Dict[str, Any]) -> Dict[str, Any]:
    """
    发送卡片到企微WebHook

    Args:
        webhook_url: 企微群机器人的Webhook URL
        card: generate_wecom_card() 生成的卡片内容

    Returns:
        API响应结果
    """
    import urllib.request
    import urllib.error

    payload = json.dumps(card).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            response = resp.read().decode("utf-8")
            return json.loads(response)
    except urllib.error.URLError as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # 测试用例
    test_texts = [
        "两融核保 客户资产500万 持仓市值300万 信用评分80 无负债",
        "两融核保 客户资产1000万 持仓科创板500万 信用评分85 持股满12个月 风险C5",
    ]

    for test_text in test_texts:
        print("=" * 50)
        print(f"测试输入：{test_text}")
        print("=" * 50)

        output = underwrite_and_send_wecom(test_text, format="both")

        print("【文本格式】")
        print(output["text"])

        print("\n【卡片JSON摘要】")
        card = output["card"]
        print(f"卡片类型: {card['msg_type']}")
        print(f"卡片颜色: {card['card']['header']['template']}")
        print(f"元素数量: {len(card['card']['elements'])}")

        print()
