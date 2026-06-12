"""
企微机器人卡片集成
wecom_integration - 企微群机器人消息卡片推送
"""

import json
import os
import re
from typing import Optional

# 可选依赖检查
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def build_fraud_alert_card(result) -> dict:
    """
    构建企微机器人消息卡片

    Args:
        result: FraudDetectionResult 检测结果

    Returns:
        dict: 企微卡片 JSON
    """
    # 风险等级 → 颜色 + emoji
    level_cfg = {
        "低":    {"color": "34", "emoji": "🟢", "bg": "#D4EDDA"},
        "中":    {"color": "33", "emoji": "🟡", "bg": "#FFF3CD"},
        "高":    {"color": "15", "emoji": "🟠", "bg": "#FFE5CC"},
        "极高":  {"color": "34", "emoji": "🔴", "bg": "#F8D7DA"},
    }
    cfg = level_cfg.get(result.level, level_cfg["低"])

    # 触发规则摘要（最多5条）
    top_rules = sorted(result.rules, key=lambda r: -r.confidence)[:5]
    rule_lines = []
    for r in top_rules:
        conf_pct = f"{r.confidence:.0%}"
        rule_lines.append({
            "tag": "text",
            "text": f"• [{r.id}] {r.name} {cfg['emoji']} {conf_pct}\n"
        })

    # 建议行动
    action_lines = []
    for i, action in enumerate(result.actions[:3], 1):
        action_lines.append({
            "tag": "text",
            "text": f"{i}. {action}\n"
        })

    # 组装卡片
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
                    "text": f"🚨 反欺诈预警 [{result.level}风险]",
                    "lang": "zh_cn"
                },
                "prompt": {
                    "tag": "plain_text",
                    "text": "金融反欺诈检测",
                    "lang": "zh_cn"
                },
                "color": cfg["color"]
            },
            "elements": [
                # 风险评分区
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**风险评分**\n{result.score}/100 {cfg['emoji']}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**风险等级**\n{cfg['emoji']} {result.level}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**触发规则**\n{len(result.rules)}条"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**建议行动**\n{len(result.actions)}项"
                            }
                        }
                    ]
                },
                {"tag": "hr"},
                # 摘要
                {
                    "tag": "section",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**📋 检测摘要**\n{result.summary}"
                    }
                },
                # 触发规则详情
                {
                    "tag": "section",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**⚠️ 触发规则** ({len(result.rules)}条)"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "".join(f"• [{r.id}] {r.name} 置信度:{r.confidence:.0%} | {r.detail or ''}\n" for r in top_rules)
                    }
                },
                # 建议行动
                {
                    "tag": "section",
                    "text": {
                        "tag": "lark_md",
                        "content": "**✅ 建议行动**"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "".join(f"{i}. {a}\n" for i, a in enumerate(result.actions[:3], 1))
                    }
                },
                {"tag": "hr"},
                # 底部时间戳
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "text": f"生成时间: "
                        },
                        {
                            "tag": "lark_md",
                            "content": "<cds>」<lkc>」</lkc></cds>",
                            "i18n": {
                                "zh_cn": ""
                            }
                        }
                    ]
                }
            ]
        }
    }

    return card


def build_simple_text_card(result) -> dict:
    """构建简单的文本消息卡片（兼容性更好）"""
    level_cfg = {
        "低": "🟢",
        "中": "🟡",
        "高": "🟠",
        "极高": "🔴",
    }
    emoji = level_cfg.get(result.level, "⚪")

    content_lines = [
        f"🚨 **反欺诈预警报告**",
        f"",
        f"风险评分: **{result.score}/100** {emoji}",
        f"风险等级: {emoji} **{result.level}风险**",
        f"",
    ]

    if result.rules:
        content_lines.append(f"**⚠️ 触发规则** ({len(result.rules)}条):")
        for r in sorted(result.rules, key=lambda x: -x.confidence)[:5]:
            content_lines.append(f"  • [{r.id}] {r.name} (置信度:{r.confidence:.0%})")
        content_lines.append("")

    content_lines.append("**✅ 建议行动**:")
    for i, action in enumerate(result.actions[:3], 1):
        content_lines.append(f"  {i}. {action}")
    content_lines.append("")
    content_lines.append(f"📋 {result.summary}")

    return {
        "msgtype": "text",
        "text": {
            "content": "\n".join(content_lines)
        }
    }


def send_alert(result, webhook_url: str = None, use_card: bool = True) -> dict:
    """
    发送企微告警消息

    Args:
        result: FraudDetectionResult 检测结果
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

    if use_card:
        payload = build_fraud_alert_card(result)
    else:
        payload = build_simple_text_card(result)

    try:
        import requests
        resp = requests.post(webhook_url, json=payload, timeout=10)
        return resp.json()
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}


# -------------------- CLI --------------------

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    from fraud_engine import FraudDetectionEngine

    engine = FraudDetectionEngine()
    test_texts = [
        "反欺诈 交易金额50万 时间凌晨2点 对方是新客户",
        "反欺诈 交易金额100万 时间节假日 对方是高风险地区",
        "反欺诈 交易金额1000元 时间正常工作日 对方是老客户",
    ]

    print("=" * 50)
    print("  企微卡片预览")
    print("=" * 50)

    for text in test_texts:
        result = engine.detect_from_nl(text)
        print(f"\n输入: {text}")
        print(f"评分: {result.score} [{result.level}]")
        print(f"触发: {[r.id for r in result.rules]}")
        card = build_fraud_alert_card(result)
        print(f"卡片结构: msgtype={card['msgtype']}")
        print("-" * 40)
