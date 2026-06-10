"""
企微卡片集成
将智能客服结果渲染为企微消息卡片
"""

import json
from typing import Dict, Optional


# 意图颜色映射
INTENT_COLORS = {
    1: "#3498db",   # 开户咨询 - 蓝色
    2: "#e74c3c",   # 贷款申请 - 红色
    3: "#2ecc71",   # 理财产品 - 绿色
    4: "#9b59b6",   # 信用卡 - 紫色
    5: "#f39c12",   # 保险业务 - 橙色
    6: "#e74c3c",   # 投诉建议 - 红色
    7: "#1abc9c",   # 信息查询 - 青色
    8: "#34495e",   # 转人工 - 深灰
    9: "#95a5a6",   # 判断失误 - 灰色
    10: "#7f8c8d",  # 闲聊 - 浅灰
}


def build_cs_card(result: Dict, user_name: str = "用户") -> Dict:
    """
    将客服结果构建为企微卡片

    Args:
        result: SmartCustomerServiceEngine.process() 返回的结果
        user_name: 用户名称（可选）

    Returns:
        企微卡片element数组
    """
    intent_id = result.get("intent_id", 10)
    intent_name = result.get("intent_name", "未知")
    confidence = result.get("confidence", 0.0)
    should_transfer = result.get("should_transfer", False)
    transfer_reason = result.get("transfer_reason", "")
    answer = result.get("answer", "")
    faq_match = result.get("faq_match")

    color = INTENT_COLORS.get(intent_id, "#7f8c8d")

    # 构建卡片内容
    elements = []

    # 头部：意图标签
    elements.append({
        "tag": "markdown",
        "content": f"**🎯 意图识别** | <font color='{color}'>**{intent_name}**</font> | 置信度: {confidence:.0%}"
    })

    # 转人工提示
    if should_transfer:
        elements.append({
            "tag": "markdown",
            "content": f"⚠️ **建议转人工**\n{transfer_reason}"
        })

    # FAQ匹配提示
    if faq_match:
        elements.append({
            "tag": "markdown",
            "content": f"📖 **匹配FAQ**: {faq_match.get('question', '')}"
        })

    # 回答内容
    elements.append({
        "tag": "markdown",
        "content": f"💬 **回答**:\n{answer}"
    })

    # 底部操作按钮
    if should_transfer:
        actions = [
            {
                "tag": "button",
                "text": "转接人工",
                "type": "primary",
                "value": "transfer_to_human"
            }
        ]
    else:
        actions = [
            {
                "tag": "button",
                "text": "满意",
                "type": "primary",
                "value": "satisfied"
            },
            {
                "tag": "button",
                "text": "转人工",
                "type": "secondary",
                "value": "transfer_to_human"
            }
        ]

    card = {
        "msgtype": "interactive",
        "interactive": {
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "text": "📞 智能客服小e"
                    },
                    "prompt": {
                        "tag": "plain_text",
                        "text": f"{user_name} 的咨询"
                    }
                },
                "elements": elements,
                "action_card": {
                    "card_filter": {
                        "exclude_count": 0
                    },
                    "actions": actions
                }
            }
        }
    }

    return card


def build_simple_text_card(result: Dict) -> Dict:
    """构建简单的文本消息（备用）"""
    intent_name = result.get("intent_name", "未知")
    confidence = result.get("confidence", 0.0)
    answer = result.get("answer", "")
    should_transfer = result.get("should_transfer", False)

    text = f"🎯 意图: {intent_name} (置信度: {confidence:.0%})\n\n"
    if should_transfer:
        text += f"⚠️ {result.get('transfer_reason', '建议转人工')}\n\n"
    text += f"💬 {answer}"

    return {
        "msgtype": "text",
        "text": {
            "content": text
        }
    }


def card_to_json(card: Dict, pretty: bool = True) -> str:
    """将卡片转为JSON字符串"""
    if pretty:
        return json.dumps(card, ensure_ascii=False, indent=2)
    return json.dumps(card, ensure_ascii=False)


# 企微应用消息发送示例
def send_card_to_wecom(card: Dict, agent_id: str, secret: str,
                        user_id: str = "@all") -> Dict:
    """
    发送卡片到企微（需要access_token）

    这是一个示例函数，实际使用时需要：
    1. 获取应用的 access_token
    2. 调用企微消息发送接口
    """
    import requests

    # 获取access_token（示例）
    # token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={agent_id}&corpsecret={secret}"
    # resp = requests.get(token_url)
    # access_token = resp.json().get("access_token")

    # 发送消息（示例）
    # url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
    # payload = {
    #     "touser": user_id,
    #     "msgtype": "interactive",
    #     "agentid": agent_id,
    "interactive": card["interactive"]
    # }
    # resp = requests.post(url, json=payload)
    # return resp.json()

    return {"error": "请实现完整的access_token获取和消息发送逻辑"}


# 快捷调用函数
def render(result: Dict) -> str:
    """渲染结果为企微卡片JSON"""
    card = build_cs_card(result)
    return card_to_json(card)


if __name__ == "__main__":
    # 测试
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from cs_engine import SmartCustomerServiceEngine

    engine = SmartCustomerServiceEngine()

    # 测试用例
    test_texts = [
        "我想投诉 银行卡被盗刷了",
        "如何申请贷款",
        "你好",
    ]

    for text in test_texts:
        print(f"\n{'='*60}")
        print(f"输入: {text}")
        result = engine.process(text)
        card = build_cs_card(result)
        print(card_to_json(card))
