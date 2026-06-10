"""
wecom_integration.py - 企微机器人卡片预警集成

基于情绪识别结果，生成不同颜色的企微消息卡片：
  - 红色：愤怒（5级）/舆情高风险
  - 橙色：不满（4级）
  - 黄色：中性（3级）
  - 蓝色：满意（2级）
  - 绿色：非常满意（1级）

使用方法:
    from wecom_integration import WecomEmotionCard
    card = WecomEmotionCard()
    card.send(result, webhook_url="https://qyapi.weixin.qq.com/...")
"""

import json
import os
from typing import Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# 颜色映射：emotion_level -> (卡片主题色, 颜色描述)
EMOTION_COLORS = {
    1: ("info", "-green", "快速服务"),   # 非常满意 - 绿色
    2: ("info", "blue", "正常服务"),     # 满意 - 蓝色
    3: ("warning", "yellow", "关注服务"), # 中性 - 黄色
    4: ("warning", "orange", "预警服务"), # 不满 - 橙色
    5: ("danger", "red", "紧急处理"),     # 愤怒 - 红色
}

# 舆情风险色
RISK_COLORS = {
    "高": "red",
    "中": "orange",
    "低": "yellow",
    "无": "green",
}


class WecomEmotionCard:
    """
    企微情绪预警卡片生成器

    根据 LobbyEmotionEngine 的分析结果，
    生成带颜色的 Interactive 消息卡片，推送到企微群机器人。
    """

    def __init__(self):
        self.name = "WecomEmotionCard"
        self.version = "1.0.0"

    def build_card(self, result) -> dict:
        """
        根据情绪分析结果构建企微卡片

        Args:
            result: EmotionResult 对象

        Returns:
            dict: 企微卡片 JSON 结构
        """
        emotion = result.emotion
        level = result.emotion_level
        intensity = result.intensity_score
        strategy = result.service_strategy
        risk = result.public_sentiment_risk
        mgmt = result.management_intervention

        # 获取颜色配置
        color_tag, color_value, action_tag = EMOTION_COLORS.get(
            level, ("info", "gray", "未知")
        )
        risk_color = RISK_COLORS.get(risk["level"], "gray")

        # 情绪标签
        emotion_tags = {
            "非常满意": ("info", "🟢 非常满意"),
            "满意": ("info", "🔵 满意"),
            "中性": ("warning", "🟡 中性"),
            "不满": ("warning", "🟠 不满"),
            "愤怒": ("danger", "🔴 愤怒"),
        }
        tag_type, emotion_label = emotion_tags.get(emotion, ("info", "⚪ 未知"))

        # 构造卡片内容
        card_elements = []

        # 第1行：情绪状态（标题区）
        card_elements.append({
            "tag": "markdown",
            "content": f"### {emotion_label} <font color=\"{color_value}\">【{action_tag}】</font>\n"
                       f"**情绪强度：** {intensity}/5 级\n"
                       f"**情绪评分：** {intensity} 分"
        })

        # 第2行：服务策略
        card_elements.append({
            "tag": "markdown",
            "content": f"**📝 安抚话术：**\n{strategy['script']}"
        })

        card_elements.append({
            "tag": "markdown",
            "content": f"**⚡ 建议动作：**\n{strategy['action']}"
        })

        # 第3行：升级情况
        if strategy.get("escalation"):
            card_elements.append({
                "tag": "markdown",
                "content": f"<font color=\"red\">**🚨 需要升级**</font>\n" +
                           "\n".join([f"- {r}" for r in strategy.get("escalation_reasons", [])])
            })
        else:
            card_elements.append({
                "tag": "markdown",
                "content": "<font color=\"green\">**✅ 暂无需升级**</font>"
            })

        # 第4行：舆情风险
        card_elements.append({
            "tag": "markdown",
            "content": f"**🌐 舆情风险：** <font color=\"{risk_color}\">{risk['level']}</font>\n"
                       f"{risk['warning']}"
        })

        # 第5行：管理人员介入
        if mgmt.get("required"):
            card_elements.append({
                "tag": "markdown",
                "content": f"<font color=\"red\">**👔 请 {mgmt['suggested_person']} 介入**</font>\n"
                           f"原因：{mgmt['reason']}"
            })
        else:
            card_elements.append({
                "tag": "markdown",
                "content": f"**👔 管理人员：** {mgmt['suggested_person']}"
            })

        # 组装卡片
        card = {
            "msgtype": "interactive",
            "interactive": {
                "tag": "card",
                "color": color_value,
                "title": {
                    "tag": "plain_text",
                    "content": f"🎭 客户情绪预警 | {emotion} | 强度{intensity}级"
                },
                "emphasis": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"🚨 {emotion} | 强度 {intensity}/5 级 | {action_tag}"
                    }
                },
                "elements": card_elements
            }
        }

        return card

    def send(
        self,
        result,
        webhook_url: str,
        mentioned_list: Optional[list[str]] = None
    ) -> dict:
        """
        发送企微卡片消息

        Args:
            result: EmotionResult 对象
            webhook_url: 企微群机器人 Webhook URL
            mentioned_list: 需要 @ 的用户 open_id 列表

        Returns:
            dict: 发送结果 {"errcode": 0, "errmsg": "ok"}
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests 库未安装，请运行: pip install requests")

        card = self.build_card(result)

        payload = card
        if mentioned_list:
            payload["interactive"]["mentioned_list"] = mentioned_list

        headers = {"Content-Type": "application/json"}
        response = requests.post(webhook_url, headers=headers, json=payload, timeout=10)
        return response.json()

    def preview(self, result) -> str:
        """
        预览卡片 JSON（不发送，用于调试）
        """
        card = self.build_card(result)
        return json.dumps(card, ensure_ascii=False, indent=2)


def preview_from_result(emotion_result) -> str:
    """快捷预览函数"""
    card = WecomEmotionCard()
    return card.preview(emotion_result)


def send_card(emotion_result, webhook_url: str) -> dict:
    """快捷发送函数"""
    card = WecomEmotionCard()
    return card.send(emotion_result, webhook_url)


if __name__ == "__main__":
    # 测试：构造示例情绪结果并预览卡片
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from emotion_engine import LobbyEmotionEngine

    engine = LobbyEmotionEngine()
    result = engine.analyze(
        tone="急促",
        expression="皱眉",
        body_language="正常",
        wait_minutes=40,
        has_complaint_history=True,
        keywords=[]
    )

    card = WecomEmotionCard()
    print("=== 企微卡片预览 ===")
    print(card.preview(result))
