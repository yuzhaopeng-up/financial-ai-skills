"""
企微卡片集成 (WeCom Card Integration)

生成飞书/企业微信格式的续保提醒卡片消息。
"""

from typing import Optional, Dict, Any


def generate_wecom_card(
    customer_name: str,
    product_type: str,
    priority: str,
    analysis_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    生成续保提醒企微卡片

    Args:
        customer_name: 客户姓名
        product_type: 险种
        priority: 优先级（紧急/重要/一般）
        analysis_result: 分析结果（可选）

    Returns:
        企微卡片消息体
    """
    # 优先级颜色映射
    priority_config = {
        "紧急": {"color": "red", "tag": "🔥 紧急" if "🔥" not in priority else priority},
        "重要": {"color": "orange", "tag": "⚠️ 重要" if "⚠️" not in priority else priority},
        "一般": {"color": "blue", "tag": "ℹ️ 一般" if "ℹ️" not in priority else priority},
    }

    config = priority_config.get(priority, priority_config["一般"])

    # 建议文本
    if analysis_result:
        recommendation = analysis_result.get("recommendation", "建议续保")
        retention_strategy = analysis_result.get("retention_strategy", "")
        renewal_script = analysis_result.get("renewal_script", "")
        analysis = analysis_result.get("analysis", {})
        paid_ratio = analysis.get("paid_ratio", 0)
        cash_value_ratio = analysis.get("cash_value_ratio", 0)
        risk_level = analysis.get("risk_level", "")
    else:
        recommendation = "建议续保"
        retention_strategy = "请与客户深入沟通，了解真实需求。"
        renewal_script = ""
        paid_ratio = 0
        cash_value_ratio = 0
        risk_level = ""

    # 构建企微卡片
    card = {
        "msgtype": "interactive",
        "interactive": {
            "card_type": "template_card",
            "source": {
                "icon_url": "https://example.com/insurance-icon.png",
                "desc": "续保提醒"
            },
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"📋 续保提醒 | {customer_name}"
                    },
                    "template": config["color"]
                },
                "elements": [
                    {
                        "tag": "div",
                        "fields": [
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "markdown",
                                    "content": f"**客户姓名**\n{customer_name}"
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "markdown",
                                    "content": f"**险种**\n{product_type}"
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "markdown",
                                    "content": f"**挽留优先级**\n{config['tag']}"
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "markdown",
                                    "content": f"**续保建议**\n**{recommendation}**"
                                }
                            }
                        ]
                    }
                ]
            }
        }
    }

    # 如果有分析结果，添加更多信息
    if analysis_result:
        # 添加分析详情
        card["interactive"]["card"]["elements"].append({
            "tag": "hr"
        })

        card["interactive"]["card"]["elements"].append({
            "tag": "div",
            "fields": [
                {
                    "is_short": True,
                    "text": {
                        "tag": "markdown",
                        "content": f"**已缴比例**\n{paid_ratio*100:.1f}%"
                    }
                },
                {
                    "is_short": True,
                    "text": {
                        "tag": "markdown",
                        "content": f"**现金价值比例**\n{cash_value_ratio*100:.1f}%"
                    }
                },
                {
                    "is_short": False,
                    "text": {
                        "tag": "markdown",
                        "content": f"**风险等级**: {risk_level}"
                    }
                }
            ]
        })

        # 添加挽留策略
        if retention_strategy:
            card["interactive"]["card"]["elements"].append({
                "tag": "div",
                "text": {
                    "tag": "markdown",
                    "content": f"**挽留策略**\n{retention_strategy}"
                }
            })

        # 添加续保话术
        if renewal_script:
            # 截取话术前200字
            script_preview = renewal_script[:200] + "..." if len(renewal_script) > 200 else renewal_script
            card["interactive"]["card"]["elements"].append({
                "tag": "note",
                "elements": [
                    {
                        "tag": "markdown",
                        "content": f"**续保话术（摘要）**\n{script_preview}"
                    }
                ]
            })

    # 添加底部按钮
    card["interactive"]["card"]["elements"].append({
        "tag": "hr"
    })

    card["interactive"]["card"]["elements"].append({
        "tag": "action",
        "actions": [
            {
                "tag": "button",
                "text": {
                    "tag": "plain_text",
                    "content": "📞 联系客户"
                },
                "type": "primary"
            },
            {
                "tag": "button",
                "text": {
                    "tag": "plain_text",
                    "content": "📝 标记已处理"
                },
                "type": "secondary"
            }
        ]
    })

    return card


def generate_wecom_text_card(
    customer_name: str,
    product_type: str,
    priority: str,
    analysis_result: Optional[Dict[str, Any]] = None
) -> str:
    """
    生成纯文本格式的企微消息（用于不支持卡片的场景）

    Returns:
        文本消息
    """
    if analysis_result:
        recommendation = analysis_result.get("recommendation", "建议续保")
        retention_strategy = analysis_result.get("retention_strategy", "")
        analysis = analysis_result.get("analysis", {})
        paid_ratio = analysis.get("paid_ratio", 0)
        cash_value_ratio = analysis.get("cash_value_ratio", 0)
    else:
        recommendation = "建议续保"
        retention_strategy = "请与客户深入沟通，了解真实需求。"
        paid_ratio = 0
        cash_value_ratio = 0

    lines = [
        f"📋 续保提醒 | {customer_name}",
        f"━━━━━━━━━━━━━━━━━━",
        f"险种：{product_type}",
        f"优先级：{priority}",
        f"建议：{recommendation}",
        f"已缴比例：{paid_ratio*100:.1f}%",
        f"现金价值：{cash_value_ratio*100:.1f}%",
    ]

    if retention_strategy:
        lines.append(f"━━━━━━━━━━━━━━━━━━")
        lines.append(f"挽留策略：{retention_strategy[:100]}")

    return "\n".join(lines)
