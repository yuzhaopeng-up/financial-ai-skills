"""
企微红色预警卡片集成
wecom_integration - 企业微信红色预警卡片推送（fraud_alert专用）
"""

import json
import os
import re
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def build_red_alert_card(result) -> dict:
    """
    构建企微红色预警卡片（fraud_alert专用）

    Args:
        result: FraudAlertResult 预警结果

    Returns:
        dict: 企微卡片 JSON
    """
    # 预警等级 → 颜色/emoji
    level_cfg = {
        "红色": {"color": "34", "emoji": "🔴", "level_tag": "🚨 红色预警"},
        "橙色": {"color": "15", "emoji": "🟠", "level_tag": "⚠️ 橙色预警"},
        "黄色": {"color": "33", "emoji": "🟡", "level_tag": "📌 黄色预警"},
        "正常": {"color": "0", "emoji": "✅", "level_tag": "✔️ 正常"},
    }
    cfg = level_cfg.get(result.level, level_cfg["正常"])

    # 紧急程度颜色
    urgency_color = {
        "高": {"color": "34", "label": "高"},
        "中": {"color": "15", "label": "中"},
        "低": {"color": "33", "label": "低"},
        "无": {"color": "0", "label": "无"},
    }.get(result.review_urgency, {"color": "0", "label": "无"})

    # 触发规则摘要
    top_rules = sorted(result.rules, key=lambda r: ({"A": 0, "B": 1, "C": 2}[r.severity], -r.confidence))[:6]

    # 按严重程度分组
    groups = {"A": [], "B": [], "C": []}
    for r in result.rules:
        groups[r.severity].append(r)

    # 规则摘要行
    rule_summary = []
    if groups["A"]:
        rule_summary.append(f"🔴 高危{len(groups['A'])}条")
    if groups["B"]:
        rule_summary.append(f"🟠 中危{len(groups['B'])}条")
    if groups["C"]:
        rule_summary.append(f"🟡 低危{len(groups['C'])}条")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 卡片元素
    elements = [
        # ===== 预警头部 =====
        {
            "tag": "div",
            "fields": [
                {
                    "is_short": True,
                    "text": {
                        "tag": "lark_md",
                        "content": f"**预警等级**\n{cfg['emoji']} {result.level}"
                    }
                },
                {
                    "is_short": True,
                    "text": {
                        "tag": "lark_md",
                        "content": f"**风险评分**\n{result.score}/100"
                    }
                },
                {
                    "is_short": True,
                    "text": {
                        "tag": "lark_md",
                        "content": f"**复核紧迫度**\n{result.review_urgency}"
                    }
                },
                {
                    "is_short": True,
                    "text": {
                        "tag": "lark_md",
                        "content": f"**触发规则**\n{len(result.rules)}条"
                    }
                },
            ]
        },
        {"tag": "hr"},

        # ===== 规则触发情况 =====
        {
            "tag": "section",
            "text": {
                "tag": "lark_md",
                "content": f"**⚠️ 规则触发情况**  {' | '.join(rule_summary) if rule_summary else '无'}"
            }
        },
    ]

    # 详细规则列表
    if top_rules:
        rule_detail_lines = []
        sev_icons = {"A": "🔴", "B": "🟠", "C": "🟡"}
        for r in top_rules:
            icon = sev_icons.get(r.severity, "⚪")
            rule_detail_lines.append(
                f"{icon} **[{r.id}] {r.name}** 置信度:{r.confidence:.0%}\n   └ {r.detail}"
            )

        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "\n".join(rule_detail_lines)
            }
        })

    elements.append({"tag": "hr"})

    # ===== 紧急处置建议 =====
    elements.append({
        "tag": "section",
        "text": {
            "tag": "lark_md",
            "content": "**🚨 紧急处置建议**"
        }
    })

    action_lines = []
    for i, action in enumerate(result.actions[:5], 1):
        action_lines.append(f"{i}. {action}")

    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": "\n".join(action_lines)
        }
    })

    elements.append({"tag": "hr"})

    # ===== 摘要 =====
    elements.append({
        "tag": "section",
        "text": {
            "tag": "lark_md",
            "content": f"**📋 检测摘要**\n{result.summary}"
        }
    })

    # ===== 底部 =====
    elements.append({
        "tag": "note",
        "elements": [
            {"tag": "plain_text", "text": f"生成时间: {now_str}  |  fraud_alert 实时预警系统"},
        ]
    })

    card = {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "config": {
                "wide_screen_mode": True,
                "enable_forward": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "text": f"{cfg['level_tag']} - 实时欺诈预警",
                    "lang": "zh_cn"
                },
                "prompt": {
                    "tag": "plain_text",
                    "text": "fraud_alert 实时交易预警",
                    "lang": "zh_cn"
                },
                "color": cfg["color"]
            },
            "elements": elements
        }
    }

    return card


def build_simple_text(result) -> dict:
    """构建简单文本消息（兼容性版本）"""
    emoji_map = {"红色": "🔴", "橙色": "🟠", "黄色": "🟡", "正常": "✅"}
    emoji = emoji_map.get(result.level, "⚪")

    lines = [
        f"{emoji} **{emoji} fraud_alert 实时欺诈预警**",
        f"",
        f"预警等级: **{result.level}**  风险评分: **{result.score}/100**",
        f"人工复核: {'是' if result.review_required else '否'} (紧迫度: {result.review_urgency})",
        f"",
    ]

    if result.rules:
        lines.append(f"⚠️ 触发规则 ({len(result.rules)}条):")
        sev_icons = {"A": "🔴", "B": "🟠", "C": "🟡"}
        for r in sorted(result.rules, key=lambda x: -x.confidence)[:5]:
            icon = sev_icons.get(r.severity, "⚪")
            lines.append(f"  {icon} [{r.id}] {r.name} ({r.confidence:.0%})")
        lines.append("")

    if result.actions:
        lines.append("🚨 紧急处置建议:")
        for i, action in enumerate(result.actions[:4], 1):
            lines.append(f"  {i}. {action}")
        lines.append("")

    lines.append(f"📋 {result.summary}")

    return {
        "msgtype": "text",
        "text": {"content": "\n".join(lines)}
    }


def send_red_alert(result, webhook_url: str = None, use_card: bool = True) -> dict:
    """
    发送企微红色预警

    Args:
        result: FraudAlertResult 预警结果
        webhook_url: 企微群机器人 Webhook URL
                    若不传则尝试从环境变量 WECOM_WEBHOOK 获取
        use_card: 是否使用卡片消息（True=卡片，False=文本）

    Returns:
        dict: API 响应结果
    """
    if not HAS_REQUESTS:
        return {"errcode": -1, "errmsg": "requests 库未安装"}

    if not webhook_url:
        webhook_url = os.environ.get("WECOM_WEBHOOK", "")

    if not webhook_url:
        return {"errcode": -1, "errmsg": "未提供 webhook_url，请设置 WECOM_WEBHOOK 环境变量"}

    payload = build_red_alert_card(result) if use_card else build_simple_text(result)

    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        return resp.json()
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}


# -------------------- 调试预览 --------------------

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    from fraud_alert_engine import FraudAlertEngine

    engine = FraudAlertEngine()

    test_cases = [
        "fraud_alert 交易金额5万 时间22:00 地点异地 设备更换",
        "fraud_alert 交易金额100万 时间凌晨3点 对方是新客户",
        "fraud_alert 交易金额1000元 时间正常工作日",
    ]

    print("=" * 60)
    print("  fraud_alert 企微卡片预览")
    print("=" * 60)

    for text in test_cases:
        result = engine.alert_from_nl(text)
        print(f"\n输入: {text}")
        print(f"预警: {result.level} [{result.score}分]  复核:{result.review_required}")
        card = build_red_alert_card(result)
        print(f"卡片类型: {card['msgtype']}  颜色: {card['interactive']['header']['color']}")
        print("-" * 60)
