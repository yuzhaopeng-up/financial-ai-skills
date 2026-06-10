"""
企微卡片集成 (wecom_integration)
将基金对比结果渲染为企微机器人可发送的卡片消息
"""

import json
from typing import Optional

from .compare_engine import FundCompareEngine


class WecomCardSender:
    """企微卡片发送器（需要配合企微机器人 webhook 使用）"""

    def __init__(self, webhook_url: str = ""):
        self.webhook_url = webhook_url

    def send_fund_compare(self, inputs: list[str], webhook_url: Optional[str] = None) -> dict:
        """
        生成并发送基金对比卡片

        Args:
            inputs: 基金代码或名称列表
            webhook_url: 企微群机器人的 webhook 地址

        Returns:
            发送结果（包含 success 状态和响应）
        """
        url = webhook_url or self.webhook_url
        if not url:
            raise ValueError("必须提供 webhook_url")

        engine = FundCompareEngine()
        result = engine.compare(inputs)
        card = engine.render_wecom_card(result)

        # 构建企微卡片消息
        payload = self._build_card_payload(card, result)

        # 发送（需要调用者自行 POST 到 webhook）
        return {
            "success": True,
            "payload": payload,
            "recommendation": result["recommendation"],
            "scores": result["scores"],
        }

    def _build_card_payload(self, card: dict, result) -> dict:
        """构建企微卡片消息体"""
        profiles = result["profiles"]
        scores = result["scores"]

        # 生成对比表格行
        table_lines = []
        for i, p in enumerate(profiles):
            tag = "🏆" if i == 0 else f"  "
            table_lines.append(
                f"{tag}**{p.name}**（{p.code}）\n"
                f"   评分:{scores[p.code]}分 | 近1年:+{p.returns.y1:.1f}%"
                f" | 回撤:{p.risk.max_drawdown:.1f}% | 夏普:{p.risk.sharpe:.2f}"
            )

        # 推荐语
        best_code = max(scores, key=scores.get)
        best = next(pp for pp in profiles if pp.code == best_code)

        card_content = {
            "msgtype": "interactive",
            "interactive": {
                "card": {
                    "header": {
                        "title": {"tag": "plain_text", "text": f"🏆 基金对比报告 | 推荐 {best.name}"},
                        "color": "blue"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": "\n".join(table_lines)
                            }
                        },
                        {"tag": "hr"},
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": f"**综合推荐**：{best.name}（{best.code}）"
                                          f"评分 **{scores[best_code]}分** 位居首位"
                            }
                        },
                        {
                            "tag": "note",
                            "fields": [
                                {"is_short": True, "text": {
                                    "tag": "lark_md",
                                    "content": f"**近1年收益**\n{best.returns.y1:+.1f}%"
                                }},
                                {"is_short": True, "text": {
                                    "tag": "lark_md",
                                    "content": f"**夏普比率**\n{best.risk.sharpe:.2f}"
                                }},
                                {"is_short": True, "text": {
                                    "tag": "lark_md",
                                    "content": f"**最大回撤**\n-{best.risk.max_drawdown:.1f}%"
                                }},
                                {"is_short": True, "text": {
                                    "tag": "lark_md",
                                    "content": f"**基金类型**\n{best.info.fund_type}"
                                }},
                            ]
                        },
                        {"tag": "hr"},
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": result["analysis"]
                            }
                        }
                    ]
                }
            }
        }

        return card_content


def send_compare_card(inputs: list[str], webhook_url: str) -> dict:
    """
    便捷函数：直接发送基金对比卡片

    Args:
        inputs: 基金代码或名称，如 ["110011", "163402"]
        webhook_url: 企微群机器人 webhook 地址

    Returns:
        发送结果
    """
    sender = WecomCardSender(webhook_url=webhook_url)
    return sender.send_fund_compare(inputs, webhook_url)
