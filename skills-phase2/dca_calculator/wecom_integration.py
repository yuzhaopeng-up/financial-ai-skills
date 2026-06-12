"""
企业微信卡片集成 (WeCom Integration)

将定投计算结果以富媒体卡片形式推送到企业微信群
"""

import json
from typing import Dict, Any, Optional

from dca_engine import DCAResult


def build_wecom_card(result: DCAResult, agent_id: str = "") -> Dict[str, Any]:
    """
    构建企业微信消息卡片

    Args:
        result: DCAResult 计算结果
        agent_id: 企微 agent_id（可选）

    Returns:
        企微卡片 JSON 结构
    """
    s_opt = result.scenario_analysis.get("optimistic", {})
    s_neu = result.scenario_analysis.get("neutral", {})
    s_pes = result.scenario_analysis.get("pessimistic", {})

    # 计算高亮值
    return_rate = result.total_return_rate
    if return_rate > 0:
        emoji_return = "📈"
        color_return = "green"
    elif return_rate < 0:
        emoji_return = "📉"
        color_return = "red"
    else:
        emoji_return = "➖"
        color_return = "grey"

    card = {
        "msgtype": "interactive",
        "agentid": agent_id,
        "interactive": {
            "tag": "card",
            "header": {
                "title": {
                    "tag": "plain_text",
                    "text": f"📊 定投计算报告 | {result.fund_name}",
                    "emoji": True,
                },
                "template": "blue",
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": (
                        f"**基金：** {result.fund_name}（{result.fund_code}）  \n"
                        f"**类型：** {result.fund_type}  \n"
                        f"**方案：** {result.frequency} · {result.amount:,}元  \n"
                        f"**期限：** {result.years}年（共{result.total_months}期）"
                    ),
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "fields": [
                        {
                            "tag": "column_set",
                            "flex_mode": "center",
                            "vertical_align": "center",
                            "fields": [
                                {
                                    "tag": "column",
                                    "width": "auto",
                                    "fields": [
                                        {
                                            "tag": "markdown",
                                            "content": (
                                                f"**累计投入**  \n"
                                                f"{result.total_invested:,.2f} 元"
                                            ),
                                        }
                                    ],
                                },
                                {
                                    "tag": "column",
                                    "width": "auto",
                                    "fields": [
                                        {
                                            "tag": "markdown",
                                            "content": (
                                                f"**期末资产**  \n"
                                                f"{result.final_value:,.2f} 元"
                                            ),
                                        }
                                    ],
                                },
                            ],
                        }
                    ],
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "tag": "column_set",
                            "flex_mode": "center",
                            "vertical_align": "center",
                            "fields": [
                                {
                                    "tag": "column",
                                    "width": "auto",
                                    "fields": [
                                        {
                                            "tag": "markdown",
                                            "content": (
                                                f"**累计收益**  \n"
                                                f"{emoji_return} {result.total_return:+,.2f} 元"
                                            ),
                                        }
                                    ],
                                },
                                {
                                    "tag": "column",
                                    "width": "auto",
                                    "fields": [
                                        {
                                            "tag": "markdown",
                                            "content": (
                                                f"**年化收益率**  \n"
                                                f"{emoji_return} {result.annualized_return*100:+.2f}%"
                                            ),
                                        }
                                    ],
                                },
                            ],
                        }
                    ],
                },
                {"tag": "hr"},
                {
                    "tag": "markdown",
                    "content": (
                        "**📊 收益率情景分析**\n\n"
                        f"🟢 **乐观**（年化15%）："
                        f"资产 {s_opt.get('final_value', 0):,.2f} 元 | "
                        f"收益 {s_opt.get('total_return', 0):+,.2f} 元 | "
                        f"{s_opt.get('return_rate', 0)*100:+.2f}%\n\n"
                        f"🔵 **中性**（年化8%）："
                        f"资产 {s_neu.get('final_value', 0):,.2f} 元 | "
                        f"收益 {s_neu.get('total_return', 0):+,.2f} 元 | "
                        f"{s_neu.get('return_rate', 0)*100:+.2f}%\n\n"
                        f"🔴 **悲观**（年化-5%）："
                        f"资产 {s_pes.get('final_value', 0):,.2f} 元 | "
                        f"收益 {s_pes.get('total_return', 0):+,.2f} 元 | "
                        f"{s_pes.get('return_rate', 0)*100:+.2f}%"
                    ),
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "text": (
                                "⚠️ 以上为模拟数据，仅供参考，不构成投资建议。"
                                "实际收益受市场波动、费率、分红等因素影响。"
                            ),
                        }
                    ],
                },
            ],
        },
    }
    return card


def build_wecom_text_summary(result: DCAResult) -> str:
    """构建企微文本摘要（用于普通消息）"""
    s_neu = result.scenario_analysis.get("neutral", {})
    lines = [
        f"📊 定投计算报告：{result.fund_name}",
        f"─────────────────────────────",
        f"基金：{result.fund_name}（{result.fund_code}）",
        f"方案：{result.frequency} {result.amount:,}元 × {result.total_months}期",
        f"期限：{result.years}年",
        f"",
        f"累计投入：{result.total_invested:,.2f} 元",
        f"期末资产：{result.final_value:,.2f} 元",
        f"累计收益：{result.total_return:+,.2f} 元",
        f"年化收益：{result.annualized_return*100:+.2f}%",
        f"",
        f"【情景分析】",
        f"🟢 乐观(15%)：{s_neu.get('final_value', 0):,.2f}元 → "
        f"收益 {s_neu.get('total_return', 0):+,.2f}元",
        f"⚠️ 仅供参考，不构成投资建议",
    ]
    return "\n".join(lines)


def send_wecom_card(
    card: Dict[str, Any],
    webhook_url: str,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    通过 webhook 发送企微卡片

    Args:
        card: 卡片 JSON 结构
        webhook_url: 企业微信群机器人的 webhook 地址
        timeout: 超时秒数

    Returns:
        API 响应
    """
    import urllib.request

    payload = json.dumps(card).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}


# 导出便捷函数
def push_dca_result(result: DCAResult, webhook_url: str) -> Dict[str, Any]:
    """推送定投结果到企微群（便捷函数）"""
    card = build_wecom_card(result)
    return send_wecom_card(card, webhook_url)
