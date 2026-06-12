"""
企业微信卡片集成 (WeCom Integration)

将大宗交易分析结果以富媒体卡片形式推送到企业微信群
"""

import json
from typing import Dict, Any, Optional

from block_engine import BlockTradeResult


def build_wecom_card(result: BlockTradeResult, agent_id: str = "") -> Dict[str, Any]:
    """
    构建企业微信消息卡片

    Args:
        result: BlockTradeResult 分析结果
        agent_id: 企微 agent_id（可选）

    Returns:
        企微卡片 JSON 结构
    """
    # 折溢价率颜色和标签
    pd_rate = result.premium_discount_rate
    if pd_rate > 0:
        rate_color = "red"
        rate_emoji = "📈"
        rate_label = f"溢价 {pd_rate*100:.2f}%"
    elif pd_rate < 0:
        rate_color = "green"
        rate_emoji = "📉"
        rate_label = f"折价 {abs(pd_rate)*100:.2f}%"
    else:
        rate_color = "grey"
        rate_emoji = "➖"
        rate_label = "平价"

    # 风险等级颜色
    risk_color_map = {"低": "green", "中": "yellow", "高": "red"}
    risk_color = risk_color_map.get(result.risk_level, "grey")

    # 市场冲击颜色
    impact = result.market_impact_score
    if impact <= 3:
        impact_color = "green"
    elif impact <= 6:
        impact_color = "yellow"
    else:
        impact_color = "red"

    # 流动性颜色
    liq = result.liquidity_score
    if liq >= 7:
        liq_color = "green"
    elif liq >= 4:
        liq_color = "yellow"
    else:
        liq_color = "red"

    # 严重合规项
    severe_alerts = [a for a in result.compliance_alerts if a["level"] == "🔴 严重"]
    warning_alerts = [a for a in result.compliance_alerts if a["level"] == "⚠️ 警告"]

    # 相似案例摘要（最多3条）
    cases_content = ""
    for i, c in enumerate(result.similar_cases[:3], 1):
        cases_content += (
            f"{i}. **{c['stock']}**（{c['year']}）\n"
            f"   {c['buyer_type']}接手 | 折价{c['discount_rate']} | {c['note'][:20]}\n"
        )

    card = {
        "msgtype": "interactive",
        "agentid": agent_id,
        "interactive": {
            "tag": "card",
            "header": {
                "title": {
                    "tag": "plain_text",
                    "text": f"📊 大宗交易分析 | {result.stock_name}",
                    "emoji": True,
                },
                "template": "blue",
            },
            "elements": [
                # 基本信息
                {
                    "tag": "markdown",
                    "content": (
                        f"**股票：** {result.stock_name}  \n"
                        f"**成交数量：** {result.quantity:,} 股  \n"
                        f"**成交价格：** {result.price:.2f} 元  \n"
                        f"**当日收盘：** {result.closing_price:.2f} 元  \n"
                        f"**总成交额：** {result.total_amount:,.2f} 元"
                    ),
                },
                {"tag": "hr"},
                # 折溢价 + 风险等级
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
                                                f"**{rate_emoji} 折溢价率**  \n"
                                                f"[{rate_label}]({rate_color})"
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
                                                f"**⚠️ 风险等级**  \n"
                                                f"[{result.risk_level}]({risk_color})"
                                            ),
                                        }
                                    ],
                                },
                            ],
                        }
                    ],
                },
                # 市场冲击 + 流动性
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
                                                f"**📉 市场冲击**  \n"
                                                f"[{impact}/10]({impact_color}) "
                                                f"（估算冲击{result.estimated_price_impact*100:.2f}%）"
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
                                                f"**💧 流动性评分**  \n"
                                                f"[{liq}/10]({liq_color})"
                                            ),
                                        }
                                    ],
                                },
                            ],
                        }
                    ],
                },
                {"tag": "hr"},
                # 合规警示
                {
                    "tag": "markdown",
                    "content": _build_compliance_md(severe_alerts, warning_alerts),
                },
                {"tag": "hr"},
                # 相似案例
                {
                    "tag": "markdown",
                    "content": (
                        f"**📋 相似历史案例**\n\n{cases_content}"
                    ),
                },
                # 锁定期提示
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "text": (
                                f"【锁定期】{result.lockup_warning[:80]}..."
                                if len(result.lockup_warning) > 80
                                else f"【锁定期】{result.lockup_warning}"
                            ),
                        }
                    ],
                },
            ],
        },
    }
    return card


def _build_compliance_md(severe: list, warnings: list) -> str:
    """构建合规警示 markdown 内容"""
    lines = ["**⚖️ 合规要点**\n"]
    if severe:
        lines.append("🔴 **严重风险：**")
        for a in severe:
            lines.append(f"  • {a['rule']}：{a['description'][:40]}")
    if warnings:
        lines.append("⚠️ **需关注：**")
        for a in warnings[:3]:
            lines.append(f"  • {a['rule']}：{a['description'][:40]}")
    if not severe and not warnings:
        lines.append("✅ 暂未发现严重合规问题")
    return "\n".join(lines)


def build_wecom_text_summary(result: BlockTradeResult) -> str:
    """构建企微文本摘要（用于普通消息）"""
    pd_rate = result.premium_discount_rate
    if pd_rate > 0:
        rate_str = f"溢价 {pd_rate*100:.2f}%"
    elif pd_rate < 0:
        rate_str = f"折价 {abs(pd_rate)*100:.2f}%"
    else:
        rate_str = "平价"

    lines = [
        f"📊 大宗交易分析：{result.stock_name}",
        f"───────────────────────────────────",
        f"成交数量：{result.quantity:,} 股",
        f"成交价格：{result.price:.2f} 元（收盘 {result.closing_price:.2f} 元）",
        f"总成交额：{result.total_amount:,.2f} 元",
        f"",
        f"折溢价率：{rate_str}",
        f"风险等级：{result.risk_level}",
        f"市场冲击：{result.market_impact_score}/10（估算{result.estimated_price_impact*100:.2f}%）",
        f"流动性：{result.liquidity_score}/10",
        f"",
        f"【相似案例】",
    ]
    for c in result.similar_cases[:2]:
        lines.append(
            f"• {c['stock']}（{c['year']}）| "
            f"{c['buyer_type']}接手 | 折价{c['discount_rate']}"
        )
    lines.append(f"")
    lines.append(f"⚠️ {result.lockup_warning[:60]}...")
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
def push_block_trade_result(result: BlockTradeResult, webhook_url: str) -> Dict[str, Any]:
    """推送大宗交易分析结果到企微群（便捷函数）"""
    card = build_wecom_card(result)
    return send_wecom_card(card, webhook_url)
