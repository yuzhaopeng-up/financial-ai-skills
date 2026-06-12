"""
企微/飞书智能核保卡片集成

生成适用于企微机器人卡片或飞书消息卡片的核保报告JSON
"""

import json
from typing import Dict, Any, Optional

from .underwriting_engine import SmartUnderwritingEngine


def generate_wecom_card(result: Dict[str, Any], title: str = "智能核保报告") -> Dict[str, Any]:
    """
    生成企微/飞书卡片格式的核保报告

    Args:
        result: SmartUnderwritingEngine.underwrite() 返回的核保结果
        title: 卡片标题

    Returns:
        企微/飞书卡片JSON结构
    """
    decision = result["核保决定"]
    level = result["风险分级"]
    factor = result["保费调整系数"]
    score = result["综合风险评分"]
    notes = result["核保建议"]

    # 决策颜色映射
    decision_colors = {
        "标准体": "green",
        "加费": "yellow",
        "除外": "orange",
        "拒保": "red"
    }
    color = decision_colors.get(decision, "grey")

    # 决策图标
    decision_icons = {
        "标准体": "✅",
        "加费": "⏸️",
        "除外": "⚠️",
        "拒保": "❌"
    }
    icon = decision_icons.get(decision, "📋")

    # 构建评估明细摘要
    details_summary = []
    for detail in result["评估明细"]:
        decision_tag = detail.get("结论", "通过")
        details_summary.append({
            "title": detail["评估项目"],
            "value": f"系数{detail['风险系数']} | {detail['说明']}",
            "type": "primary" if decision_tag == "通过" else "warning"
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
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**核保决定：** {decision}\n**风险分级：** {level}\n**保费系数：** {factor}\n**综合评分：** {score}"
                    }
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**【投保信息】**\n• 年龄：{result['投保信息']['年龄']}岁\n• 职业：{result['投保信息']['职业']}\n• 健康状况：{result['投保信息']['健康状况']}\n• 年收入：{result['投保信息']['年收入(万)']}万元\n• 保额：{result['投保信息']['保额(万)']}万元"
                    }
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**【评估明细】**"
                    }
                }
            ]
        }
    }

    # 添加评估明细
    for detail in result["评估明细"]:
        card["card"]["elements"].append({
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "text": f"【{detail['评估项目']}】系数{detail['风险系数']} - {detail['说明']}"
                }
            ]
        })

    # 添加拒保原因（如有）
    if result["拒保原因"]:
        reasons_text = "\n".join([f"⚠️ {r}" for r in result["拒保原因"]])
        card["card"]["elements"].append({"tag": "hr"})
        card["card"]["elements"].append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**【拒保原因】**\n{reasons_text}"
            }
        })

    # 添加核保建议
    card["card"]["elements"].append({"tag": "hr"})
    card["card"]["elements"].append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": f"**【核保建议】**\n{notes}"
        }
    })

    # 添加时间戳
    import datetime
    card["card"]["elements"].append({
        "tag": "note",
        "elements": [
            {
                "tag": "plain_text",
                "text": f"报告时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        ]
    })

    return card


def generate_wecom_card_simple(result: Dict[str, Any]) -> str:
    """
    生成简洁版企微卡片文本（用于text类型的消息）

    Returns:
        格式化文本字符串
    """
    lines = [
        "━━━━━━━━━━━━━━━━━━━━",
        f"  智能核保报告",
        "━━━━━━━━━━━━━━━━━━━━",
        "",
        f"核保决定：{result['核保决定']}",
        f"风险分级：{result['风险分级']}",
        f"保费系数：{result['保费调整系数']}",
        f"综合评分：{result['综合风险评分']}",
        "",
        "【投保信息】",
        f"年龄：{result['投保信息']['年龄']}岁",
        f"职业：{result['投保信息']['职业']}",
        f"健康：{result['投保信息']['健康状况']}",
        f"年收入：{result['投保信息']['年收入(万)']}万元",
        f"保额：{result['投保信息']['保额(万)']}万元",
        "",
        "【评估明细】",
    ]

    for detail in result["评估明细"]:
        lines.append(f"  {detail['评估项目']}：系数{detail['风险系数']}")

    if result["拒保原因"]:
        lines.append("")
        lines.append("【拒保原因】")
        for reason in result["拒保原因"]:
            lines.append(f"  ⚠ {reason}")

    lines.extend([
        "",
        f"【建议】{result['核保建议']}",
        "━━━━━━━━━━━━━━━━━━━━"
    ])

    return "\n".join(lines)


def underwrite_and_send_wecom(text: str, format: str = "card") -> Dict[str, Any]:
    """
    快捷函数：核保并生成企微卡片

    Args:
        text: 自然语言核保描述
        format: 输出格式（card=卡片JSON，text=纯文本，both=两者）

    Returns:
        核保结果和卡片内容
    """
    engine = SmartUnderwritingEngine()
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


# 企微WebHook发送（示例）
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
    test_text = "智能核保 年龄45 职业企业主 健康良好 年收入100万 寿险500万 20年"

    print("=" * 50)
    print("测试企微卡片生成")
    print("=" * 50)
    print(f"\n输入：{test_text}\n")

    output = underwrite_and_send_wecom(test_text, format="both")

    print("【文本格式】")
    print(output["text"])

    print("\n【卡片JSON】")
    print(json.dumps(output["card"], ensure_ascii=False, indent=2))
