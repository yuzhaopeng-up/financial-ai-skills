"""
WeCom Integration - 企微卡片集成

用于将预算分析结果以企微消息卡片格式发送
"""

import json
from typing import Optional


def build_budget_card(
    dept: str,
    category: str,
    budget: float,
    spent: float,
    execution_rate: float,
    status: str,
    status_text: str,
    overrun_risk_text: str,
    projected_overrun: float,
    recommendations: list
) -> dict:
    """
    构建企微预算预警消息卡片
    
    Args:
        dept: 部门名称
        category: 费用科目
        budget: 预算金额
        spent: 已使用金额
        execution_rate: 执行率
        status: 预警状态
        status_text: 预警状态文本
        overrun_risk_text: 风险等级文本
        projected_overrun: 预测超支
        recommendations: 管控建议列表
    
    Returns:
        企微卡片JSON
    """
    # 状态颜色映射
    color_map = {
        "green": "00A86B",   # 绿色
        "yellow": "FFD700",  # 黄色
        "red": "FF4444"      # 红色
    }
    accent_color = color_map.get(status, "00A86B")
    
    # 构建建议文本
    rec_text = "\n".join([f"• {rec}" for rec in recommendations])
    
    card = {
        "msgtype": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True,
                "enable_forward": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "text": f"💰 预算执行预警 | {dept} {category}"
                },
                "template": status if status != "green" else "green"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**执行率：** `{execution_rate}%` {status_text}"
                    }
                },
                {"tag": "hr"},
                {
                    "tag": "column_set",
                    "flex_mode": "between",
                    "elements": [
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "vertical_align": "top",
                            "elements": [
                                {
                                    "tag": "markdown",
                                    "content": "**📊 预算金额**\n{RMB} 万元".format(RMB=f"{budget:.1f}")
                                }
                            ]
                        },
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "vertical_align": "top",
                            "elements": [
                                {
                                    "tag": "markdown",
                                    "content": "**💸 已使用**\n{RMB} 万元".format(RMB=f"{spent:.1f}")
                                }
                            ]
                        },
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "vertical_align": "top",
                            "elements": [
                                {
                                    "tag": "markdown",
                                    "content": "**📈 执行率**\n{RATE}%".format(RATE=f"{execution_rate:.1f}")
                                }
                            ]
                        }
                    ]
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**⚠️ 超支风险：** {overrun_risk_text}\n\n**📉 预测超支：** {projected_overrun:.1f} 万元"
                    }
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**💡 管控建议：**\n{rec_text}"
                    }
                },
                {
                    "tag": "note",
                    "elements": [
                        {"tag": "plain_text", "text": "预算管控系统自动生成"}
                    ]
                }
            ]
        }
    }
    
    return card


def build_budget_card_from_result(result: dict) -> dict:
    """从分析结果字典构建企微卡片"""
    return build_budget_card(
        dept=result["dept"],
        category=result["category"],
        budget=result["budget"],
        spent=result["spent"],
        execution_rate=result["execution_rate"],
        status=result["status"],
        status_text=result["status_text"],
        overrun_risk_text=result["overrun_risk_text"],
        projected_overrun=result["projected_overrun"],
        recommendations=result["recommendations"]
    )


def send_wecom_card(card: dict, webhook_url: str) -> dict:
    """
    发送企微卡片消息
    
    Args:
        card: 卡片JSON
        webhook_url: 企微机器人webhook地址
    
    Returns:
        发送结果
    """
    import urllib.request
    
    data = json.dumps(card).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


if __name__ == "__main__":
    # 测试卡片构建
    test_result = {
        "dept": "市场部",
        "category": "差旅费",
        "budget": 20.0,
        "spent": 18.0,
        "remaining": 2.0,
        "remaining_months": 2,
        "execution_rate": 90.0,
        "status": "yellow",
        "status_text": "🟡 需要关注",
        "overrun_risk": "medium",
        "overrun_risk_text": "🟡 中等风险",
        "monthly_burn_rate": 9.0,
        "projected_spend": 27.0,
        "projected_overrun": 7.0,
        "recommendations": [
            "⚠️ 市场部差旅费执行率达 90.0%，月均额度控制在 1.0 万元以内",
            "📋 严格审批后续报销，优先处理必要支出",
            "📈 每周跟踪执行进度，提前预警超支风险"
        ]
    }
    
    card = build_budget_card_from_result(test_result)
    print(json.dumps(card, ensure_ascii=False, indent=2))
