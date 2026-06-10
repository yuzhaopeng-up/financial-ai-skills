"""
Wecom Integration — 企微卡片输出集成

用于将AML评级结果以企微消息卡片形式发送给企业微信群或个人。
"""

import json
from typing import Optional


class WecomCardBuilder:
    """企微消息卡片构建器"""

    # 风险等级颜色映射
    LEVEL_COLORS = {
        "极低": "#36B759",   # 绿色
        "低": "#2196F3",    # 蓝色
        "中": "#FF9800",    # 橙色
        "高": "#FF5722",    # 橙红
        "极高": "#F44336",  # 红色
    }

    # 风险等级 emoji
    LEVEL_EMOJI = {
        "极低": "🟢",
        "低": "🔵",
        "中": "🟡",
        "高": "🟠",
        "极高": "🔴",
    }

    def __init__(self):
        pass

    def build_aml_card(self, result: dict) -> dict:
        """
        构建AML评级结果的企微消息卡片

        Args:
            result: AMLRatingEngine.rate() 返回的字典

        Returns:
            企微卡片 JSON 结构（用于发送 interactive 消息）
        """
        risk_level = result.get("risk_level", "未知")
        risk_score = result.get("risk_score", 0)
        color = self.LEVEL_COLORS.get(risk_level, "#999999")
        emoji = self.LEVEL_EMOJI.get(risk_level, "⚪")

        # 风险因素摘要
        risk_factors = result.get("risk_factors", {})
        factor_lines = []
        for dim, data in risk_factors.items():
            score = data.get("score", 0)
            factors = data.get("factors", [])
            if score > 0 or factors:
                factor_text = "、".join(factors[:2]) if factors else "无异常"
                factor_lines.append({
                    "tag": "markdown",
                    "content": f"**{dim}** {factor_text} `+{score}分`"
                })

        # 建议
        recommendations = result.get("recommendations", [])
        rec_lines = []
        for rec in recommendations[:3]:
            rec_lines.append({
                "tag": "markdown",
                "content": f"• {rec}"
            })

        card = {
            "msgtype": "interactive",
            "interactive": {
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "text": f"AML客户风险评级 {emoji} {risk_level}"
                        },
                        "subtitle": {
                            "tag": "plain_text",
                            "text": f"客户: {result.get('customer_name', '未知')} | 评分: {risk_score}/100"
                        },
                        "template": color.lstrip("#")
                    },
                    "elements": [
                        {
                            "tag": "markdown",
                            "content": "**风险因素拆解**"
                        },
                        *factor_lines,
                        {"tag": "hr"},
                        {
                            "tag": "markdown",
                            "content": "**管控措施建议**"
                        },
                        *rec_lines,
                        {
                            "tag": "note",
                            "elements": [
                                {
                                    "tag": "plain_text",
                                    "text": f"报告时间: 自动生成 | AML Rating System v1.0"
                                }
                            ]
                        }
                    ],
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "text": "查看详情"
                            },
                            "type": "primary"
                        }
                    ]
                }
            }
        }

        return card

    def build_simple_card(self, result: dict) -> str:
        """构建简化文本卡片（用于无法使用 interactive 的场景）"""
        risk_level = result.get("risk_level", "未知")
        risk_score = result.get("risk_score", 0)
        emoji = self.LEVEL_EMOJI.get(risk_level, "⚪")

        lines = [
            f"AML客户风险评级 {emoji}",
            f"客户: {result.get('customer_name', '未知')}",
            f"风险等级: {risk_level} ({risk_score}/100)",
            "",
            "风险因素:",
        ]

        risk_factors = result.get("risk_factors", {})
        for dim, data in risk_factors.items():
            score = data.get("score", 0)
            factors = data.get("factors", [])
            if factors:
                lines.append(f"  {dim}: {' '.join(factors)} (+{score})")

        lines.append("")
        lines.append("建议:")
        for rec in result.get("recommendations", [])[:3]:
            lines.append(f"  · {rec}")

        return "\n".join(lines)


def send_wecom_card(card: dict,
                    webhook_url: Optional[str] = None,
                    agent_id: Optional[str] = None) -> dict:
    """
    发送企微卡片消息

    Args:
        card: 卡片 JSON（由 WecomCardBuilder 构建）
        webhook_url: 企微机器人 webhook URL
        agent_id: 企业应用 agent_id

    Returns:
        API 响应
    """
    import urllib.request
    import urllib.error

    if not webhook_url:
        # 尝试从环境变量获取
        webhook_url = os.environ.get("WECOM_WEBHOOK_URL")

    if not webhook_url:
        raise ValueError("必须提供 webhook_url 或设置 WECOM_WEBHOOK_URL 环境变量")

    data = json.dumps(card).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"errcode": e.code, "errmsg": str(e)}
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}


# 便捷函数
def format_aml_for_wecom(result: dict) -> dict:
    """将 AML 结果格式化为企微卡片"""
    builder = WecomCardBuilder()
    return builder.build_aml_card(result)


# 导出
__all__ = ["WecomCardBuilder", "send_wecom_card", "format_aml_for_wecom"]
