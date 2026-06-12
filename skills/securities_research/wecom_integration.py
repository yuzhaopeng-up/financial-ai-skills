"""
wecom_integration.py — 企微卡片推送

将投研报告格式化为企微消息卡片（Markdown/文本混合），
通过企微 Webhook 或企微应用 Agent 推送。
"""

from __future__ import annotations

import json
from typing import Any


def build_research_card(report: Any) -> dict:
    """
    将 ResearchReport 格式化为企微交互卡片 JSON

    Args:
        report: SecuritiesResearchEngine.generate() 返回的 ResearchReport 对象

    Returns:
        企微卡片 JSON dict（用于 feishu_im_user_message / wecom send 等渠道）
    """
    # 评级颜色映射
    rating_color = {
        "强烈推荐": "#00C853",  # 绿色
        "推荐": "#64DD17",      # 浅绿
        "中性": "#FFC107",      # 黄色
        "谨慎": "#FF9100",      # 橙色
        "回避": "#F44336",      # 红色
    }
    color = rating_color.get(report.rating, "#9E9E9E")

    # 核心观点摘要（取前3个拼成一段）
    core_views_text = "".join(report.core_views[:3])
    if len(core_views_text) > 200:
        core_views_text = core_views_text[:200] + "..."

    # 风险提示（取前3条）
    risks_text = "\n".join(
        f"• {r}" for r in report.risk_factors[:3]
    )

    # 财务数据摘要（取前3项）
    fin_items = list(report.financial_data.items())[:3]
    fin_text = "\n".join(
        f"• {k}: {' / '.join(str(v) for v in d.values())}"
        for k, d in fin_items
    )

    card = {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "header": {
                "title": {
                    "tag": "plain_text",
                    "text": f"📊 {report.company} — {report.report_type}",
                },
                "color": color,
            },
            "elements": [
                # 评级区
                {
                    "tag": "column_set",
                    "flex_mode": "none",
                    "elements": [
                        {
                            "tag": "column",
                            "width": "auto",
                            "elements": [
                                {
                                    "tag": "markdown",
                                    "content": f"**行业**\n{report.industry}",
                                },
                            ],
                        },
                        {
                            "tag": "column",
                            "width": "auto",
                            "elements": [
                                {
                                    "tag": "markdown",
                                    "content": f"**评级**\n{report.rating}",
                                },
                            ],
                        },
                        {
                            "tag": "column",
                            "width": "stretch",
                            "elements": [
                                {
                                    "tag": "markdown",
                                    "content": f"**评级依据**\n{report.rating_basis[:30]}...",
                                },
                            ],
                        },
                    ],
                },
                {"tag": "hr"},  # 分隔线
                # 核心观点
                {
                    "tag": "section",
                    "text": {
                        "tag": "markdown",
                        "content": f"**📌 核心观点**\n{core_views_text}",
                    },
                },
                {"tag": "hr"},
                # 财务数据摘要
                {
                    "tag": "section",
                    "text": {
                        "tag": "markdown",
                        "content": f"**📈 财务数据（脱敏模拟）**\n{fin_text}",
                    },
                },
                {"tag": "hr"},
                # 投资建议
                {
                    "tag": "section",
                    "text": {
                        "tag": "markdown",
                        "content": f"**💡 投资建议**\n{report.investment_advice}",
                    },
                },
                {"tag": "hr"},
                # 风险提示
                {
                    "tag": "section",
                    "text": {
                        "tag": "markdown",
                        "content": f"**⚠️ 风险提示**\n{risks_text}",
                    },
                },
                # 底部备注
                {
                    "tag": "note",
                    "elements": [
                        {"tag": "plain_text", "text": "本报告数据为脱敏模拟数据，仅供内部研究参考，不构成投资建议。　　生成时间：2026年"},
                    ],
                },
            ],
        },
    }
    return card


def build_simple_text_card(report: Any) -> dict:
    """
    构建纯文本企微消息（用于不支持卡片的场景）

    Returns:
        text 消息 dict
    """
    core_views_text = "".join(report.core_views[:2])
    if len(core_views_text) > 150:
        core_views_text = core_views_text[:150] + "..."

    text = (
        f"📊 {report.company} — {report.report_type}\n"
        f"行业：{report.industry}  |  评级：{report.rating}\n"
        f"评级依据：{report.rating_basis}\n"
        f"\n"
        f"📌 核心观点：{core_views_text}\n"
        f"\n"
        f"💡 投资建议：{report.investment_advice[:100]}...\n"
        f"\n"
        f"⚠️ 风险提示：\n"
    )
    for r in report.risk_factors[:3]:
        text += f"• {r}\n"

    text += f"\n> 本报告数据为脱敏模拟数据，仅供内部研究参考，不构成投资建议。"

    return {"msgtype": "text", "text": {"content": text}}


def send_to_wecom(
    report: Any,
    webhook_url: str | None = None,
    use_card: bool = True,
) -> dict:
    """
    推送投研报告到企微 Webhook

    Args:
        report: ResearchReport 对象
        webhook_url: 企微群机器人的 Webhook URL（不传则只返回卡片内容）
        use_card: 是否使用卡片格式（False 则用纯文本）

    Returns:
        {"card": dict}  或  {"response": requests.Response}
    """
    card = build_research_card(report) if use_card else build_simple_text_card(report)

    if webhook_url is None:
        return {"card": card}

    try:
        import requests
        resp = requests.post(
            webhook_url,
            json=card,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        return {"response": resp}
    except Exception as e:
        return {"error": str(e), "card": card}


# ──────────────────────────────────────────────
# CLI 入口
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import argparse, sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    from sec_research_engine import SecuritiesResearchEngine

    parser = argparse.ArgumentParser(description="企微卡片推送工具")
    parser.add_argument("command", help='命令字符串，如 "投研报告 某新能源公司 深度报告"')
    parser.add_argument("--webhook", "-w", help="企微 Webhook URL（可选）")
    parser.add_argument("--text", "-t", action="store_true", help="使用纯文本格式代替卡片")
    args = parser.parse_args()

    engine = SecuritiesResearchEngine()
    parsed = engine.parse_command(args.command)
    report = engine.generate(
        company=parsed["company"],
        industry=parsed["industry"],
        report_type=parsed["report_type"],
    )

    result = send_to_wecom(report, webhook_url=args.webhook, use_card=not args.text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
