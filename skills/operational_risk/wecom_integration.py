"""
WeCom Integration - 企微卡片消息集成

将操作风险管理评估结果通过企业微信应用消息（卡片）推送给相关人员。

用法：
    from wecom_integration import send_risk_card, build_risk_card_content

    # 方式1：直接推送
    send_risk_card(result, webhook_url="https://qyapi.weixin.qq.com/...")

    # 方式2：获取卡片 JSON，手动发送
    card_data = build_risk_card_content(result)
"""

import json
from typing import Optional

# 可通过 wecom_mcp 工具发送，或直接通过 webhook
# 以下为构建企微卡片内容的核心函数


def build_risk_card_content(
    category: str,
    category_code: str,
    risk_level: str,
    possibility: int,
    impact: int,
    score: int,
    loss_direct: float,
    loss_indirect: float,
    loss_fine: float,
    loss_total: float,
    preventive: list[str],
    detective: list[str],
    corrective: list[str],
    next_action: str,
) -> dict:
    """
    构建操作风险企微卡片内容。

    Args:
        所有风险评估字段

    Returns:
        企微消息卡片 dict（符合企微 web_hook 格式）
    """

    # 风险等级颜色映射
    level_color = {
        "极高": "#FF0000",   # 红色
        "高":  "#FF6600",   # 橙色
        "中":  "#FFAA00",   # 黄色
        "低":  "#00AA00",   # 绿色
    }
    color = level_color.get(risk_level, "#666666")

    # 可能性/影响星级
    def star(n: int) -> str:
        return "★" * n + "☆" * (5 - n)

    # 管控建议截取（前3条）
    def truncate(lst: list[str], n: int = 3) -> str:
        return "、".join(lst[:n]) + ("..." if len(lst) > n else "")

    card = {
        "msgtype": "interactive",
        "interactive": {
            "tag": "markdown",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"⚠️ 操作风险预警 | {category}"
                    },
                    "description": {
                        "tag": "markdown",
                        "content": (
                            f"**风险等级：** {risk_level}　"
                            f"**类别：** {category_code}　"
                            f"**评分：** {score}/25"
                        )
                    },
                    "color": color,
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": (
                            "-----\n"
                            "**风险矩阵**\n"
                            f"> 可能性：{star(possibility)}（{possibility}/5）\n"
                            f"> 影响程度：{star(impact)}（{impact}/5）\n"
                            f"> 风险评分：**{score}**（{possibility} × {impact}）\n"
                            "-----\n"
                            "**损失估算（万元）**\n"
                            f"> 直接损失：{loss_direct:.1f} | "
                            f"间接损失：{loss_indirect:.1f} | "
                            f"监管罚款：{loss_fine:.1f}\n"
                            f"> **总损失估算：{loss_total:.1f}万元**\n"
                            "-----\n"
                            "**管控建议**\n"
                            f"> 🛡️ 预防：{truncate(preventive)}\n"
                            f"> 🔍 检测：{truncate(detective)}\n"
                            f"> 🔧 纠正：{truncate(corrective)}\n"
                            "-----\n"
                            f"> 📌 **处置建议：{next_action}**"
                        )
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "content": "由 ArkClaw 操作风险管理引擎自动生成"
                            }
                        ]
                    }
                ],
                "btn_configs": [
                    {
                        "text": "查看详情",
                        "action_type": "click",
                        "key": "view_detail"
                    },
                    {
                        "text": "确认处置",
                        "action_type": "click",
                        "key": "confirm_action"
                    }
                ]
            }
        }
    }

    return card


def build_risk_card_from_result(result) -> dict:
    """
    从 OperationalRiskResult 对象构建企微卡片。

    Args:
        result: OperationalRiskResult 实例

    Returns:
        企微卡片 dict
    """
    return build_risk_card_content(
        category=result.category,
        category_code=result.category_code,
        risk_level=result.risk_level,
        possibility=result.risk_matrix.possibility,
        impact=result.risk_matrix.impact,
        score=result.risk_matrix.score,
        loss_direct=result.loss_estimate.direct,
        loss_indirect=result.loss_estimate.indirect,
        loss_fine=result.loss_estimate.regulatory_fine,
        loss_total=result.loss_estimate.total,
        preventive=result.controls.preventive,
        detective=result.controls.detective,
        corrective=result.controls.corrective,
        next_action=result.next_action,
    )


def send_risk_card(
    card_data: dict,
    webhook_url: str,
) -> dict:
    """
    通过企业微信 webhook 发送卡片消息。

    Args:
        card_data: 卡片内容 dict
        webhook_url: 企业微信群机器人的 webhook 地址

    Returns:
        企微 API 响应 dict

    Note:
        企业微信 webhook 地址格式：
        https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx
    """
    import urllib.request
    import urllib.error

    payload = json.dumps(card_data).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            response = json.loads(resp.read().decode("utf-8"))
            return response
    except urllib.error.HTTPError as e:
        return {"errcode": -1, "errmsg": f"HTTP Error: {e.code}"}
    except urllib.error.URLError as e:
        return {"errcode": -1, "errmsg": f"URL Error: {e.reason}"}


# ---------------------------------------------------------------------------
# 入口（测试）
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

    from operational_risk.op_risk_engine import OperationalRiskEngine

    engine = OperationalRiskEngine()
    result = engine.analyze(
        scenario="员工伪造理财产品合同，涉嫌诈骗客户资金",
        loss_amount=200,
        frequency="未遂",
        operator="内部",
    )

    card = build_risk_card_from_result(result)
    print("=== 企微卡片 JSON ===")
    print(json.dumps(card, ensure_ascii=False, indent=2))
