"""
Wecom Integration - 企微贸易融资消息卡片

生成符合企业微信应用消息卡片格式的贸易融资推荐内容，
可直接通过企微「应用消息」接口推送。
"""

from typing import Any


def generate_trade_finance_card(recommendation_result: dict) -> dict:
    """
    将推荐结果转换为企微消息卡片格式

    Args:
        recommendation_result: TradeFinanceEngine.recommend() 的返回结果

    Returns:
        企微消息卡片 dict，可直接作为发送消息的 content 参数
    """

    input_info = recommendation_result["input"]
    recommendations = recommendation_result["recommendations"]
    decision_advice = recommendation_result["decision_advice"]

    # 构建卡片元素
    elements = []

    # 1. 头部：标题
    elements.append({
        "tag": "title",
        "text": "🏦 贸易融资方案推荐",
        "lang": "zh_CN"
    })

    # 2. 简要参数
    param_lines = [
        f"🏢 企业类型：{input_info['company_type']}",
        f"💵 融资金额：{input_info['amount_usd']:,.0f} USD",
        f"📅 账期：{input_info['payment_terms_days']} 天",
    ]
    elements.append({
        "tag": "section",
        "text": "\n".join(param_lines)
    })

    # 3. 推荐方案列表
    rec_texts = []
    for rec in recommendations:
        score_bar = "█" * int(rec["match_score"] / 10) + "░" * (10 - int(rec["match_score"] / 10))
        rec_texts.append(
            f"#{rec['rank']} {rec['name_cn']}\n"
            f"   匹配度：{score_bar} {rec['match_score']:.0f}/100\n"
            f"   {rec['match_reason']}"
        )

    elements.append({
        "tag": "section",
        "text": "🏆 推荐方案\n" + "\n---\n".join(rec_texts)
    })

    # 4. 决策建议
    elements.append({
        "tag": "section",
        "text": "💡 " + decision_advice
    })

    # 5. 底部：查看详情（可接入知识库/文档链接）
    elements.append({
        "tag": "remark",
        "text": "📎 由龙马集群AI · 贸易融资智能推荐引擎生成\n点击上方卡片或联系客户经理获取完整方案对比表"
    })

    # 组装企微 interactive 卡片
    card = {
        "msgtype": "interactive",
        "interactive": {
            "card_type": "news",
            "source": {
                "icon_url": "https://cdn.example.com/trade-icon.png",
                "desc": "贸易融资推荐"
            },
            "title": "🏦 贸易融资方案推荐",
            "brief": {
                "title": "已为您生成融资方案",
                "desc": f"{input_info['company_type']} · {input_info['amount_usd']:,.0f} USD · {input_info['payment_terms_days']}天账期"
            },
            "primary_color": "#2979FF",
            "quote_area": {
                "type": "column",
                "items": [
                    {
                        "type": "item",
                        "title": recommendations[0]["name_cn"] if recommendations else "—",
                        "desc": f"匹配度 {recommendations[0]['match_score']:.0f}/100" if recommendations else ""
                    }
                ]
            },
            "elements": elements,
            "actions": [
                {
                    "tag": "button",
                    "text": "📋 查看完整对比",
                    "type": "url",
                    "url": "https://your-knowledge-base.example.com/trade-finance"
                },
                {
                    "tag": "button",
                    "text": "📞 联系客户经理",
                    "type": "url",
                    "url": "https://your-bank.example.com/contact"
                }
            ],
            "language": "zh_CN"
        }
    }

    return card


def generate_simple_text_card(recommendation_result: dict) -> dict:
    """
    生成纯文本格式的企微消息（兼容不支持卡片的场景）

    Returns:
        可直接发送的 text 消息 dict
    """
    input_info = recommendation_result["input"]
    recs = recommendation_result["recommendations"]
    advice = recommendation_result["decision_advice"]

    lines = [
        f"🏦 贸易融资方案推荐",
        f"",
        f"📋 参数：{input_info['company_type']} | {input_info['amount_usd']:,.0f} USD | {input_info['payment_terms_days']}天账期",
        f"",
        f"🏆 推荐方案：",
    ]
    for rec in recs:
        lines.append(
            f"  #{rec['rank']} {rec['name_cn']}（匹配度 {rec['match_score']:.0f}/100）"
        )
        lines.append(f"     {rec['match_reason']}")

    lines.extend([
        f"",
        f"💡 {advice}",
        f"",
        f"📎 由龙马集群AI · 贸易融资引擎生成"
    ])

    return {
        "msgtype": "text",
        "text": {
            "content": "\n".join(lines)
        }
    }


def send_wecom_card(
    card: dict,
    to_user: str | None = None,
    to_party: str | None = None,
    agent_id: str | None = None
) -> dict:
    """
    发送企微卡片的请求体封装

    Args:
        card: generate_trade_finance_card() 返回的卡片 dict
        to_user: 目标用户 ID 列表（逗号分隔），如 "zhangsan|lisi"
        to_party: 目标部门 ID 列表
        agent_id: 应用 agentId

    Returns:
        企微 API 请求体
    """
    payload = {
        "touser": to_user or "@all",
        "toparty": to_party or "",
        "agentid": agent_id or "",
    }
    payload.update(card)
    return payload
