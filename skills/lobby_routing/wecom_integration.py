"""
企微卡片 - 厅堂智能分流结果推送
"""

import json
from typing import Dict, Any, List, Optional

from lobby_routing import LobbyRoutingEngine, RoutingResult


def build_routing_card(result: RoutingResult, customer_name: Optional[str] = None) -> Dict[str, Any]:
    """
    构建企微消息卡片 - 厅堂智能分流结果

    Args:
        result: 分流结果
        customer_name: 客户姓名（可选）

    Returns:
        企微卡片 JSON 结构
    """
    # 优先级映射
    priority_map = {
        1: {"label": "最高", "color": "red"},
        2: {"label": "高", "color": "orange"},
        3: {"label": "中", "color": "yellow"},
        4: {"label": "较低", "color": "blue"},
        5: {"label": "普通", "color": "grey"},
    }
    priority_info = priority_map.get(result.service_priority, {"label": "普通", "color": "grey"})

    # 拥堵等级映射
    congestion_map = {
        "green": {"emoji": "🟢", "label": "畅通"},
        "yellow": {"emoji": "🟡", "label": "繁忙"},
        "orange": {"emoji": "🟠", "label": "拥挤"},
        "red": {"emoji": "🔴", "label": "拥堵"},
    }
    congestion_info = congestion_map.get(result.congestion_level, {"emoji": "⚪", "label": "未知"})

    # 推荐产品
    products_md = ""
    if result.recommended_products:
        products_md = "、".join(result.recommended_products)
    else:
        products_md = "暂无"

    # 备选方案
    alt_md = ""
    if result.alternative_routes:
        alt_lines = []
        for alt in result.alternative_routes[:2]:
            alt_lines.append(f"• {alt['counter']}（{alt['wait']}）：{alt['reason']}")
        alt_md = "\n".join(alt_lines)
    else:
        alt_md = "暂无"

    card = {
        "msgtype": "interactive",
        "interactive": {
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "text": f"🏧 智能分流方案 {'- ' + customer_name if customer_name else ''}"
                    },
                    "subtitle": {
                        "tag": "plain_text",
                        "text": f"推荐窗口：{result.recommended_counter}"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "markdown",
                            "content": f"**⏱️ 预计等候**：约 **{result.estimated_wait_minutes} 分钟**（当前排队 **{result.wait_queue_count} 人**）"
                        }
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "markdown",
                            "content": f"**🎯 服务优先级**：<font color=\"{priority_info['color']}\">{priority_info['label']}</font>"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "markdown",
                            "content": f"{congestion_info['emoji']} **{congestion_info['label']}**：{result.congestion_advice}"
                        }
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "markdown",
                            "content": f"**🚶 动线建议**：{result.movement_suggestion}"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "markdown",
                            "content": f"**💡 推荐产品**：{products_md}"
                        }
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "markdown",
                            "content": f"**🔄 备选方案**：\n{alt_md}"
                        }
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "text": f"📋 决策依据：{result.reasoning}"
                            }
                        ]
                    }
                ]
            }
        }
    }
    return card


def build_congestion_alert_card(
    location: str,
    cash_queue: int,
    non_cash_queue: int,
    self_service_queue: int,
    financial_queue: int,
) -> Dict[str, Any]:
    """
    构建厅堂拥堵预警卡片

    Args:
        location: 网点名称/位置
        cash_queue: 现金柜口排队人数
        non_cash_queue: 非现金柜口排队人数
        self_service_queue: 自助设备使用人数
        financial_queue: 理财室等候人数
    """
    # 计算总体拥堵等级
    max_queue = max(cash_queue, non_cash_queue)
    if max_queue <= 5:
        level = "green"
        emoji = "🟢"
        level_label = "畅通"
    elif max_queue <= 10:
        level = "yellow"
        emoji = "🟡"
        level_label = "繁忙"
    elif max_queue <= 15:
        level = "orange"
        emoji = "🟠"
        level_label = "拥挤"
    else:
        level = "red"
        emoji = "🔴"
        level_label = "拥堵"

    # 建议措施
    advice_map = {
        "green": "正常运营，保持观察",
        "yellow": "建议开启1-2个弹性窗口，引导客户使用自助设备",
        "orange": "启动客流疏导机制，全员上岗，限制非必要业务等候",
        "red": "发布橙色预警，开启全部窗口，联系相邻网点支援",
    }

    card = {
        "msgtype": "interactive",
        "interactive": {
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "text": f"⚠️ 厅堂拥堵预警 - {location}"
                    },
                    "subtitle": {
                        "tag": "plain_text",
                        "text": f"{emoji} {level_label}"
                    },
                    "template": "red" if level in ["orange", "red"] else "orange"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "markdown",
                            "content": "**实时队列状况**"
                        }
                    },
                    {
                        "tag": "columns",
                        "fields": [
                            {
                                "tag": "plain_text",
                                "text": f"💵 现金柜口\n**{cash_queue}人**"
                            },
                            {
                                "tag": "plain_text",
                                "text": f"💳 非现金柜口\n**{non_cash_queue}人**"
                            },
                            {
                                "tag": "plain_text",
                                "text": f"🏧 自助设备\n**{self_service_queue}人**"
                            },
                            {
                                "tag": "plain_text",
                                "text": f"📈 理财室\n**{financial_queue}人**"
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
                            "content": f"**📌 处置建议**：{advice_map[level]}"
                        }
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "text": f"生成时间：自动生成 | 请值班经理确认并采取对应措施"
                            }
                        ]
                    }
                ]
            }
        }
    }
    return card


def send_wecom_card(card: Dict[str, Any], agent_id: Optional[str] = None) -> bool:
    """
    发送企微卡片（需配合企业微信机器人或应用消息接口）

    Args:
        card: 卡片 JSON 结构
        agent_id: 应用 agent_id（可选）

    Returns:
        是否发送成功
    """
    # 此处为占位实现，实际调用需要企业微信 API
    # 企业微信应用消息发送参考：
    # POST https://qyapi.weixin.qq.com/cgi-bin/message/send
    # {
    #     "touser": "USERID",
    #     "msgtype": "interactive",
    #     "agentid": AGENT_ID,
    #     "interactive": card
    # }
    print("[Wecom Card] 卡片内容：")
    print(json.dumps(card, ensure_ascii=False, indent=2))
    return True


def demo():
    """演示"""
    engine = LobbyRoutingEngine()

    test_query = "智能分流 60岁老人 办理存款 等候20分钟 普通客户"
    print(f"输入：{test_query}\n")

    result = engine.route_from_text(test_query)
    card = build_routing_card(result, "张三")
    print("生成的企微卡片：")
    print(json.dumps(card, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60 + "\n")

    # 拥堵预警卡片
    alert_card = build_congestion_alert_card(
        location="北京朝阳支行营业部",
        cash_queue=12,
        non_cash_queue=8,
        self_service_queue=3,
        financial_queue=2,
    )
    print("拥堵预警卡片：")
    print(json.dumps(alert_card, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    demo()
