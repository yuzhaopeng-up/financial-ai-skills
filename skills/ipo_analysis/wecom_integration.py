"""
企微卡片集成 - IPO分析报告
用于通过企业微信发送卡片消息
"""

import json
from typing import Dict, Optional


def build_wecom_card(result) -> Dict:
    """
    将IPOAnalysisResult转换为企微卡片格式

    Args:
        result: IPOAnalysisResult对象

    Returns:
        企微卡片JSON结构
    """
    amount_billion = result.fundraising_amount / 1e8

    # 解析定价区间
    price_low, price_high = result.price_range

    card = {
        "msgtype": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "text": f"📋 IPO分析报告 | {result.company_name}"
                },
                "prompt": {
                    "tag": "plain_text",
                    "text": f"{result.board} · {result.industry} · 募资{amount_billion:.1f}亿"
                },
                "style": {
                    "bg_color": "#1A56DB"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "markdown",
                        "content": (
                            f"### 🏷️ 公司信息\n"
                            f"- **公司名称：** {result.company_name}\n"
                            f"- **所属行业：** {result.industry}\n"
                            f"- **上市板块：** {result.board}\n"
                            f"- **预计募资：** {amount_billion:.1f}亿元"
                        )
                    }
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "markdown",
                        "content": (
                            f"### 💰 综合定价建议\n"
                            f"▶ **建议发行价区间：** `{price_low} ~ {price_high} 元`\n"
                            f"▶ **中位建议价格：** `{result.mid_price} 元`"
                        )
                    }
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "markdown",
                        "content": (
                            f"### 📊 三种估值结果\n\n"
                            f"**① PE估值（市盈率法）**\n"
                            f"行业PE均值：{result.pe_valuation['industry_avg_pe']} | "
                            f"预测EPS：{result.pe_valuation['estimated_eps']}元\n"
                            f"估值区间：`{result.pe_valuation['low_price']} ~ {result.pe_valuation['high_price']}元`\n\n"
                            f"**② PB估值（市净率法）**\n"
                            f"行业PB均值：{result.pb_valuation['industry_avg_pb']} | "
                            f"每股净资产：{result.pb_valuation['estimated_nav']}元\n"
                            f"估值区间：`{result.pb_valuation['low_price']} ~ {result.pb_valuation['high_price']}元`\n\n"
                            f"**③ PS估值（市销率法）**\n"
                            f"行业PS均值：{result.ps_valuation['industry_avg_ps']} | "
                            f"每股营收：{result.ps_valuation['estimated_revenue_per_share']}元\n"
                            f"估值区间：`{result.ps_valuation['low_price']} ~ {result.ps_valuation['high_price']}元`"
                        )
                    }
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "markdown",
                        "content": (
                            f"### 🎯 中签率估算\n"
                            f"▶ 估算中签率：**{result.winning_rate}%**\n"
                            f"📝 {result.winning_rate_note}"
                        )
                    }
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "markdown",
                        "content": (
                            f"### 📈 上市后表现预测\n\n"
                            f"**首日涨幅预测**\n"
                            f"区间：{result.first_day_prediction['predicted_first_day_change_low']}% ~ "
                            f"{result.first_day_prediction['predicted_first_day_change_high']}%\n"
                            f"中位预测：**{result.first_day_prediction['predicted_first_day_change_mid']}%**\n\n"
                            f"**一年期展望**\n"
                            f"{result.long_term_outlook['one_year_outlook']}"
                        )
                    }
                },
                {"tag": "hr"},
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "text": "⚠️ 本报告仅供参考，不构成投资建议。数据基于历史案例推演，实际结果受市场环境影响。"
                        }
                    ]
                }
            ],
            "file_ids": []
        }
    }

    return card


def build_wecom_text_card(text: str) -> Dict:
    """构建纯文本企微卡片"""
    return {
        "msgtype": "textcard",
        "textcard": {
            "title": "IPO分析报告",
            "description": text,
            "btntxt": "更多",
            "btntarget": ""
        }
    }


# 示例用法
if __name__ == "__main__":
    # 测试
    import sys
    sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

    from ipo_engine import IPOAnalysisEngine

    engine = IPOAnalysisEngine()
    result = engine.analyze(
        company_name="某芯片设计公司",
        industry="半导体设计",
        board="科创板",
        fundraising_amount=55_000_000_000
    )

    card = build_wecom_card(result)
    print(json.dumps(card, ensure_ascii=False, indent=2))
