"""
企业微信卡片集成
WecomCard: 生成企微消息卡片格式的财报提取报告
"""

from typing import Optional


WECOM_CARD_TEMPLATE = {
    "msgtype": "interactive",
    "interactive": {
        "card_type": "template_card",
        "source": {
            "icon_url": "https://gw.alipay.com/logo.png",
            "desc": "财报智能提取"
        },
        "card_header": {
            "title": "📊 {company} 财报提取报告",
            "palette": "blue"
        },
        "card_elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "text",
                    "content": "**核心财务指标**",
                    "color": "#1890ff"
                }
            },
            {
                "tag": "column_set",
                "flex_mode": "right",
                "elements": [
                    {
                        "tag": "column",
                        "width": "weighted",
                        "weight": 1,
                        "widgets": [
                            {
                                "tag": "text",
                                "text": {"tag": "text", "content": "毛利率", "color": "#999999"}
                            },
                            {
                                "tag": "text",
                                "text": {"tag": "text", "content": "{gross_margin}", "color": "#333333", "size": "lg"}
                            }
                        ]
                    },
                    {
                        "tag": "column",
                        "width": "weighted",
                        "weight": 1,
                        "widgets": [
                            {
                                "tag": "text",
                                "text": {"tag": "text", "content": "净利率", "color": "#999999"}
                            },
                            {
                                "tag": "text",
                                "text": {"tag": "text", "content": "{net_margin}", "color": "#333333", "size": "lg"}
                            }
                        ]
                    },
                    {
                        "tag": "column",
                        "width": "weighted",
                        "weight": 1,
                        "widgets": [
                            {
                                "tag": "text",
                                "text": {"tag": "text", "content": "ROE", "color": "#999999"}
                            },
                            {
                                "tag": "text",
                                "text": {"tag": "text", "content": "{roe}", "color": "#333333", "size": "lg"}
                            }
                        ]
                    }
                ]
            },
            {
                "tag": "div",
                "text": {
                    "tag": "text",
                    "content": "**杜邦分析** {dupont_breakdown}",
                    "color": "#1890ff"
                }
            },
            {
                "tag": "div",
                "text": {
                    "tag": "text",
                    "content": "**同业对比**",
                    "color": "#1890ff"
                }
            },
            {
                "tag": "table",
                "columns": [
                    {"header": "指标", "value": "某公司", "color": "#999999"},
                    {"header": "行业均值", "value": "行业均值", "color": "#999999"},
                    {"header": "参考值", "value": "参考值", "color": "#999999"}
                ],
                "rows": []
            },
            {
                "tag": "note",
                "elements": [
                    {"tag": "text", "content": "⚠️ {alerts}", "color": "#FF3B30"}
                ]
            },
            {
                "tag": "hint",
                "elements": [
                    {
                        "icon_url": "https://gw.alipay.com/logo.png",
                        "text": {
                            "tag": "text",
                            "content": "由 AI财报智能提取引擎 生成 | 数据仅供参考"
                        }
                    }
                ]
            }
        ]
    }
}


def build_wecom_card(result: dict) -> dict:
    """
    将 extract() 返回的 result 转换为企微卡片格式
    """
    ind = result["indicators"]
    dupont = result["dupont"]
    alerts = result["alerts"]
    company = result["company"]

    # 填充同业对比表格
    rows = []
    for row in result["industry_comparison"]:
        rows.append({
            "header": row["指标"],
            "value": row["某公司"],
            "color": "#333333"
        })

    # 预警信息
    alert_text = " | ".join(alerts) if alerts else "无异常预警"

    card = {
        "msgtype": "interactive",
        "interactive": {
            "card_type": "template_card",
            "source": {
                "icon_url": "https://img.icons8.com/color/96/analytics.png",
                "desc": "财报智能提取"
            },
            "card_header": {
                "title": f"📊 {company} 财报提取报告",
                "palette": "blue"
            },
            "card_elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "text",
                        "content": "**📈 核心财务指标**",
                        "color": "#1890ff"
                    }
                },
                {
                    "tag": "column_set",
                    "flex_mode": "right",
                    "elements": [
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "widgets": [
                                {
                                    "tag": "text",
                                    "text": {"tag": "text", "content": "毛利率", "color": "#999999"}
                                },
                                {
                                    "tag": "text",
                                    "text": {"tag": "text", "content": ind["毛利率"], "color": "#333333", "size": "lg"}
                                }
                            ]
                        },
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "widgets": [
                                {
                                    "tag": "text",
                                    "text": {"tag": "text", "content": "净利率", "color": "#999999"}
                                },
                                {
                                    "tag": "text",
                                    "text": {"tag": "text", "content": ind["净利率"], "color": "#333333", "size": "lg"}
                                }
                            ]
                        },
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "widgets": [
                                {
                                    "tag": "text",
                                    "text": {"tag": "text", "content": "ROE", "color": "#999999"}
                                },
                                {
                                    "tag": "text",
                                    "text": {"tag": "text", "content": ind["ROE"], "color": "#333333", "size": "lg"}
                                }
                            ]
                        }
                    ]
                },
                {
                    "tag": "column_set",
                    "flex_mode": "right",
                    "elements": [
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "widgets": [
                                {
                                    "tag": "text",
                                    "text": {"tag": "text", "content": "资产负债率", "color": "#999999"}
                                },
                                {
                                    "tag": "text",
                                    "text": {"tag": "text", "content": ind["资产负债率"], "color": "#333333", "size": "lg"}
                                }
                            ]
                        },
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "widgets": [
                                {
                                    "tag": "text",
                                    "text": {"tag": "text", "content": "股东权益", "color": "#999999"}
                                },
                                {
                                    "tag": "text",
                                    "text": {"tag": "text", "content": ind["股东权益"], "color": "#333333", "size": "lg"}
                                }
                            ]
                        }
                    ]
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "text",
                        "content": f"**🔬 杜邦分析**\n{dupont['ROE分解']}",
                        "color": "#1890ff"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "text",
                        "content": "**⚠️ 异常预警**",
                        "color": "#FF3B30"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "text",
                        "content": alert_text,
                        "color": "#333333"
                    }
                },
                {
                    "tag": "hint",
                    "elements": [
                        {
                            "icon_url": "https://img.icons8.com/color/96/analytics.png",
                            "text": {
                                "tag": "text",
                                "content": "由 AI财报智能提取引擎 生成 | 数据仅供参考"
                            }
                        }
                    ]
                }
            ]
        }
    }

    return card


def print_card_json(result: dict):
    """打印企微卡片的 JSON，方便调试和接入"""
    import json
    card = build_wecom_card(result)
    print(json.dumps(card, ensure_ascii=False, indent=2))
