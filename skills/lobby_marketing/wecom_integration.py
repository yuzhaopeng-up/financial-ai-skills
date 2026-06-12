"""
企微（企业微信）卡片集成模块

将厅堂营销引擎的输出格式化为企业微信消息卡片，
支持通过企微 API 发送至客户群或个人。

用法：
    from wecom_integration import LobbyMarketingWecom

    wecom = LobbyMarketingWecom(corp_id="xxx", corp_secret="xxx", agent_id="xxx")
    result = engine.generate(raw_input="厅堂营销 40岁企业主 等候15分钟 资产200万")
    card = wecom.build_card(result)
    wecom.send_to_user(user_id="ou_xxx", card=card)
"""

import json
import os
import urllib.request
import urllib.error
from typing import Any, Optional


class LobbyMarketingWecom:
    """企微卡片发送器"""

    API_BASE = "https://qyapi.weixin.qq.com"

    def __init__(
        self,
        corp_id: str = "",
        corp_secret: str = "",
        agent_id: str = "",
        token_cache: Optional[dict] = None,
    ):
        self.corp_id = corp_id or os.getenv("WECOM_CORP_ID", "")
        self.corp_secret = corp_secret or os.getenv("WECOM_CORP_SECRET", "")
        self.agent_id = agent_id or os.getenv("WECOM_AGENT_ID", "")
        self._token_cache = token_cache or {}
        self._token_expiry = 0

    # ------------------------------------------------------------------
    # Token 管理
    # ------------------------------------------------------------------

    def _get_token(self) -> str:
        """获取 Access Token（带内存缓存）"""
        import time, os

        now = time.time()
        if self._token_cache.get("expire", 0) > now:
            return self._token_cache["token"]

        url = (
            f"{self.API_BASE}/cgi-bin/gettoken"
            f"?corpid={self.corp_id}&corpsecret={self.corp_secret}"
        )
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
            if data.get("errcode", 0) != 0:
                raise RuntimeError(f"获取Token失败: {data}")
            token = data["access_token"]
            self._token_cache = {
                "token": token,
                "expire": now + data.get("expires_in", 7200) - 60,
            }
            return token
        except urllib.error.URLError as e:
            raise RuntimeError(f"网络请求失败: {e}")

    # ------------------------------------------------------------------
    # 卡片构建
    # ------------------------------------------------------------------

    def build_card(
        self,
        engine_result: dict[str, Any],
        theme: str = "blue",
    ) -> dict:
        """
        将引擎输出构建为企微交互卡片格式（Markdown 卡片）。

        engine_result: LobbyMarketingEngine.generate() 的返回值
        theme: 卡片主题色 blue/green/red/primary

        Returns:
            企微消息卡片 dict，可直接用于 send_to_user / send_to_chat
        """
        cp = engine_result["customer_profile"]
        products = engine_result["recommended_products"]
        script = engine_result["script"]
        timing = engine_result["timing_signal"]

        theme_color = {
            "blue": "#576B95",
            "green": "#53A867",
            "red": "#E02424",
            "primary": "#1890FF",
        }.get(theme, "#1890FF")

        # 产品列表（最多4个）
        product_md = "\n".join(
            f"- **{p['product']}**（{p['type']}）匹配度 {int(p['match_score']*100)}%\n  > {p['reason']}"
            for p in products[:4]
        )

        # 异议处理（最多2个）
        objections_md = ""
        for obj in script["objection_handling"][:2]:
            objections_md += (
                f"\n#### 💬 {obj['objection']}\n"
                f"{obj['response'][:100]}...\n"
            )

        card = {
            "msgtype": "interactive",
            "agentid": int(self.agent_id) if self.agent_id else 0,
            "interactive": {
                "tag": "markdown",
                "content": (
                    f"<header>{theme_color}> 🎯 厅堂精准营销辅助</header>\n\n"
                    f"## 📋 客户画像\n"
                    f"- **年龄/职业**：{cp['age']}岁 | {cp['occupation']}\n"
                    f"- **资产级别**：{cp['asset_level']} | **风险偏好**：{cp['risk_preference']}\n"
                    f"- **等候时间**：{cp['waiting_minutes']}分钟\n"
                    f"- **已持产品**：{', '.join(cp['history_products']) or '无'}\n\n"
                    f"---\n\n"
                    f"## 💰 推荐产品\n"
                    f"{product_md}\n\n"
                    f"---\n\n"
                    f"## 🗣️ 营销话术\n"
                    f"> {script['opening'][:150]}{'...' if len(script['opening']) > 150 else ''}\n\n"
                    f"**需求挖掘**\n"
                    f"{script['need_discovery'][:200]}{'...' if len(script['need_discovery']) > 200 else ''}\n\n"
                    f"**产品呈现**\n"
                    f"{script['product_presentation'][:200]}{'...' if len(script['product_presentation']) > 200 else ''}\n\n"
                    f"---\n\n"
                    f"## ⏱️ 促成时机\n"
                    f"**{'✅ 建议立即切入' if timing['ready'] else '⏳ 继续培养'}** "
                    f"(置信度 {int(timing['confidence']*100)}%)\n\n"
                    + ("\n".join(f"- {r}" for r in timing['reasons']) if timing['reasons'] else "") + "\n\n"
                    f"---\n\n"
                    f"## 💬 异议处理{objections_md}\n\n"
                    f"## 🎯 促成话术\n"
                    f">{script['closing'][:200]}{'...' if len(script['closing']) > 200 else ''}\n"
                ),
                "card": {
                    "header": {
                        "title": {"tag": "plain_text", "content": "🎯 厅堂精准营销辅助方案"},
                        "palette": theme_color,
                    },
                    "theme": theme,
                },
            },
        }
        return card

    def build_text_card(self, engine_result: dict[str, Any]) -> dict:
        """
        构建纯文本消息卡片（兼容不支持 Markdown 的场景）
        """
        wecom_card = engine_result.get("wecom_card", {})
        content = wecom_card.get("text", {}).get("content", "")

        return {
            "msgtype": "textcard",
            "agentid": int(self.agent_id) if self.agent_id else 0,
            "textcard": {
                "title": "🎯 厅堂精准营销辅助方案",
                "description": content,
                "btntxt": "更多",
                "url": "",
            },
        }

    # ------------------------------------------------------------------
    # 消息发送
    # ------------------------------------------------------------------

    def _post(self, url: str, payload: dict) -> dict:
        """POST 请求"""
        import os

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read())
            if result.get("errcode", 0) != 0:
                raise RuntimeError(f"企微API错误: {result}")
            return result
        except urllib.error.URLError as e:
            raise RuntimeError(f"网络请求失败: {e}")

    def send_to_user(
        self,
        user_id: str,
        card: dict,
        message_type: str = "interactive",
    ) -> dict:
        """
        发送卡片消息给单个用户

        Args:
            user_id: 用户的 open_id（ou_xxx）
            card: build_card() 的返回值
            message_type: interactive（交互卡片）或 textcard（文本卡片）

        Returns:
            企微 API 响应
        """
        token = self._get_token()
        url = f"{self.API_BASE}/cgi-bin/message/send?access_token={token}"

        payload = {
            "touser": user_id,
            "msgtype": message_type,
        }
        if message_type == "interactive":
            payload["agentid"] = int(self.agent_id) if self.agent_id else 0
            payload["interactive"] = card["interactive"]
        else:
            payload["textcard"] = card["textcard"]

        return self._post(url, payload)

    def send_to_chat(
        self,
        chat_id: str,
        card: dict,
        message_type: str = "interactive",
    ) -> dict:
        """发送卡片消息到群聊"""
        token = self._get_token()
        url = f"{self.API_BASE}/cgi-bin/chatid/{chat_id}/send_card?access_token={token}"

        payload = {
            "chatid": chat_id,
            "msgtype": message_type,
        }
        if message_type == "interactive":
            payload["agentid"] = int(self.agent_id) if self.agent_id else 0
            payload["interactive"] = card["interactive"]
        else:
            payload["textcard"] = card["textcard"]

        return self._post(url, payload)


# ------------------------------------------------------------------
# 便捷函数（无需实例化）
# ------------------------------------------------------------------


def send_lobby_mkt_to_wecom(
    engine_result: dict,
    user_id: str,
    corp_id: str = None,
    corp_secret: str = None,
    agent_id: str = None,
    theme: str = "blue",
) -> dict:
    """
    一键发送营销方案到企微用户

    所需凭据可从环境变量读取：
        WECOM_CORP_ID / WECOM_CORP_SECRET / WECOM_AGENT_ID
    """
    wecom = LobbyMarketingWecom(
        corp_id=corp_id or os.getenv("WECOM_CORP_ID"),
        corp_secret=corp_secret or os.getenv("WECOM_CORP_SECRET"),
        agent_id=agent_id or os.getenv("WECOM_AGENT_ID"),
    )
    card = wecom.build_card(engine_result, theme=theme)
    return wecom.send_to_user(user_id=user_id, card=card)


if __name__ == "__main__":
    # 演示模式（无需企微凭据）
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from lobby_mkt_engine import LobbyMarketingEngine

    engine = LobbyMarketingEngine()
    result = engine.generate(
        raw_input="厅堂营销 40岁企业主 等候15分钟 资产200万 持有定期"
    )

    wecom = LobbyMarketingWecom()
    card = wecom.build_card(result)
    print("=== 企微卡片内容 ===")
    print(json.dumps(card, ensure_ascii=False, indent=2))
