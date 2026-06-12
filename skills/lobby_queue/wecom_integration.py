"""
Lobby Queue WeCom Integration — 企业微信卡片通知

将排队预警分析结果通过企业微信机器人推送卡片消息。
"""

import json
import os
from typing import Optional, Dict, Any

try:
    from queue_engine import LobbyQueueEngine, QueueAnalysis
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from queue_engine import LobbyQueueEngine, QueueAnalysis


# 企业微信 Webhook URL（可通过环境变量配置）
WECOM_WEBHOOK_URL = os.environ.get("WECOM_WEBHOOK_URL", "")


def build_queue_card(analysis: QueueAnalysis) -> Dict[str, Any]:
    """
    构建企业微信卡片消息

    卡片格式：
    - 标题：🏧 大堂排队预警
    - 摘要：预警等级 + 排队指数
    - 详情信息：区域、人数、等候时间、开台建议等
    """

    data = analysis.queue_data

    # 预警颜色：0=灰色, 1=红, 2=黄, 3=绿
    level_color = {"green": 3, "yellow": 2, "red": 1}.get(analysis.alert_level, 0)
    level_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(analysis.alert_level, "⚪")

    card = {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "text": f"🏧 大堂排队预警 | {data.region}"
                    },
                    "description": {
                        "tag": "plain_text",
                        "text": f"{level_emoji} {analysis.alert_color} | 排队指数 {analysis.queue_index}/100"
                    },
                    "color": str(level_color)
                },
                "elements": [
                    {
                        "tag": "div",
                        "fields": [
                            {
                                "tag": "field",
                                "is_short": True,
                                "text": {
                                    "tag": "markdown",
                                    "content": f"**📍 业务区域**\n{data.region}"
                                }
                            },
                            {
                                "tag": "field",
                                "is_short": True,
                                "text": {
                                    "tag": "markdown",
                                    "content": f"**👥 当前等候**\n{data.waiting_count}人"
                                }
                            },
                            {
                                "tag": "field",
                                "is_short": True,
                                "text": {
                                    "tag": "markdown",
                                    "content": f"**⏱️ 最长等候**\n{data.max_wait}分钟"
                                }
                            },
                            {
                                "tag": "field",
                                "is_short": True,
                                "text": {
                                    "tag": "markdown",
                                    "content": f"**🏧 服务窗口**\n{data.service_windows}个"
                                }
                            },
                            {
                                "tag": "field",
                                "is_short": True,
                                "text": {
                                    "tag": "markdown",
                                    "content": f"**⏳ 平均办理**\n{data.avg_service_time}分钟"
                                }
                            },
                            {
                                "tag": "field",
                                "is_short": True,
                                "text": {
                                    "tag": "markdown",
                                    "content": f"**📊 排队指数**\n{analysis.queue_index}/100"
                                }
                            }
                        ]
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "markdown",
                            "content": f"**💡 开台建议**\n{analysis.suggestion}"
                        }
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "markdown",
                            "content": f"**⏰ 等候预估**\n{analysis.wait_estimate}"
                        }
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "markdown",
                            "content": f"**📈 历史对比**\n{analysis.history_compare}"
                        }
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "text": " Generated by Lobby Queue Engine  |  排队预警系统"
                            }
                        ]
                    }
                ]
            }
        }
    }

    return card


def send_wecom_card(card: Dict[str, Any], webhook_url: Optional[str] = None) -> bool:
    """
    发送企业微信卡片消息

    Args:
        card: 卡片消息内容
        webhook_url: Webhook地址（为空则使用环境变量）

    Returns:
        bool: 发送是否成功
    """
    import urllib.request
    import urllib.error

    url = webhook_url or WECOM_WEBHOOK_URL
    if not url:
        print("错误：未配置企业微信Webhook URL", file=__import__('sys').stderr)
        print("请设置环境变量 WECOM_WEBHOOK_URL 或传入 webhook_url 参数", file=__import__('sys').stderr)
        return False

    try:
        data = json.dumps(card, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(
            url=url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get("errcode") == 0:
                return True
            else:
                print(f"错误：企业微信返回错误 {result.get('errcode')}: {result.get('errmsg')}", file=__import__('sys').stderr)
                return False
    except urllib.error.URLError as e:
        print(f"错误：无法连接到企业微信 {e}", file=__import__('sys').stderr)
        return False
    except Exception as e:
        print(f"错误：{e}", file=__import__('sys').stderr)
        return False


def send_queue_alert(text: str, webhook_url: Optional[str] = None) -> bool:
    """
    快捷函数：将排队预警分析结果直接发送企业微信卡片

    Args:
        text: 自然语言输入
        webhook_url: Webhook地址

    Returns:
        bool: 发送是否成功
    """
    engine = LobbyQueueEngine()
    analysis = engine.analyze(text)
    if not analysis:
        print("错误：无法解析输入文本", file=__import__('sys').stderr)
        return False

    card = build_queue_card(analysis)
    return send_wecom_card(card, webhook_url)


# 命令行入口
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="发送排队预警到企业微信")
    parser.add_argument("text", nargs="?", help="排队预警文本，如：排队预警 非现金区3人等候 等待最长达25分钟")
    parser.add_argument("-w", "--webhook", dest="webhook", help="企业微信Webhook URL")
    parser.add_argument("-t", "--test", action="store_true", help="仅生成卡片内容，不发送")

    args = parser.parse_args()

    if not args.text:
        parser.print_help()
        sys.exit(1)

    engine = LobbyQueueEngine()
    analysis = engine.analyze(args.text)
    if not analysis:
        print("错误：无法解析输入文本", file=sys.stderr)
        sys.exit(1)

    card = build_queue_card(analysis)

    if args.test:
        print("=== 卡片内容预览 ===")
        print(json.dumps(card, ensure_ascii=False, indent=2))
    else:
        success = send_queue_alert(args.text, args.webhook)
        if success:
            print("✅ 消息已发送")
        else:
            print("❌ 发送失败")
            sys.exit(1)
