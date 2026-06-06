"""
WeCom Template Card Builder — 企业微信卡片构建器

提供金融场景常用的 template_card 模板:
- 尽调摘要卡 (due_diligence_card)
- 行情快讯卡 (stock_alert_card)
- 风险预警卡 (risk_warning_card)
- 图文报告卡 (news_report_card)
- 交互确认卡 (confirm_card)

支持发送函数 send_template_card，失败时可 fallback 到 markdown。
"""

from datetime import datetime
from typing import Dict, Any, Optional
import httpx


class WeComCardBuilder:
    """企微 template_card 构建器"""

    # 风险等级 → 颜色语义映射 (供 H5/文档参考，企微 text_notice 自动着色)
    RISK_COLOR_MAP = {
        "AAA": "green", "AA": "green", "A": "green",
        "BBB": "orange", "BB": "orange",
        "B": "red", "CCC": "red", "CC": "red", "C": "red",
    }

    def __init__(self, source_name: str = "龙马金融AI"):
        self.source_name = source_name

    # ------------------------------------------------------------------
    # 1. 尽调摘要卡 (text_notice)
    # ------------------------------------------------------------------
    def due_diligence_card(
        self,
        company: str,
        code: str,
        risk_level: str,
        score: int,
        change_percent: float = 0.0,
        sentiment: str = "未知",
        sentiment_score: int = 50,
        h5_url: str = "",
        sources: Optional[list] = None,
    ) -> Dict[str, Any]:
        """构建尽调报告摘要卡片

        布局:
        - 来源: 龙马金融AI
        - 主标题: {company} 尽调报告
        - 副标题: {code} | {time}
        - 核心高亮: {risk_level} (风险等级)
        - 次标题: 得分 {score} | 💹 {change} | 舆情{sentiment}
        - 跳转: 查看完整报告
        """
        change_str = f"+{change_percent:.2f}%" if change_percent > 0 else f"{change_percent:.2f}%"
        sentiment_emoji = "🟢" if sentiment_score >= 70 else "🟡" if sentiment_score >= 40 else "🔴"
        sub_title = f"得分 {score}  |  💹 {change_str}  |  {sentiment_emoji}舆情{sentiment}"

        card = {
            "card_type": "text_notice",
            "source": {
                "desc": self.source_name,
                "desc_color": 0
            },
            "main_title": {
                "title": f"{company} 尽调报告",
                "desc": f"{code if code else '未找到'}  |  {datetime.now().strftime('%m-%d %H:%M')}"
            },
            "emphasis_content": {
                "title": risk_level,
                "desc": "风险等级"
            },
            "sub_title_text": sub_title,
        }

        if h5_url:
            card["jump_list"] = [
                {
                    "type": 1,
                    "url": h5_url,
                    "title": "📄 查看完整报告"
                }
            ]

        return card

    # ------------------------------------------------------------------
    # 2. 行情快讯卡 (text_notice)
    # ------------------------------------------------------------------
    def stock_alert_card(
        self,
        company: str,
        code: str,
        price: float,
        change_percent: float,
        alert_type: str = "行情异动",
        h5_url: str = "",
    ) -> Dict[str, Any]:
        """构建行情快讯卡片"""
        change_str = f"+{change_percent:.2f}%" if change_percent > 0 else f"{change_percent:.2f}%"
        emoji = "📈" if change_percent > 0 else "📉" if change_percent < 0 else "➖"

        card = {
            "card_type": "text_notice",
            "source": {
                "desc": self.source_name,
                "desc_color": 0
            },
            "main_title": {
                "title": f"{emoji} {company} {alert_type}",
                "desc": f"{code}  |  {datetime.now().strftime('%H:%M')}"
            },
            "emphasis_content": {
                "title": f"¥{price}",
                "desc": f"涨跌幅 {change_str}"
            },
            "sub_title_text": f"最新价 ¥{price}  |  涨跌 {change_str}",
        }

        if h5_url:
            card["jump_list"] = [
                {"type": 1, "url": h5_url, "title": "查看行情详情"}
            ]

        return card

    # ------------------------------------------------------------------
    # 3. 风险预警卡 (text_notice + 红色强调)
    # ------------------------------------------------------------------
    def risk_warning_card(
        self,
        company: str,
        code: str,
        risk_level: str,
        warning: str,
        score: int,
        h5_url: str = "",
    ) -> Dict[str, Any]:
        """构建风险预警卡片"""
        card = {
            "card_type": "text_notice",
            "source": {
                "desc": self.source_name,
                "desc_color": 1  # 红色来源标签
            },
            "main_title": {
                "title": f"⚠️ {company} 风险预警",
                "desc": f"{code}  |  {datetime.now().strftime('%m-%d %H:%M')}"
            },
            "emphasis_content": {
                "title": risk_level,
                "desc": "风险等级"
            },
            "sub_title_text": f"预警: {warning}  |  得分 {score}",
        }

        if h5_url:
            card["jump_list"] = [
                {"type": 1, "url": h5_url, "title": "查看风险详情"}
            ]

        return card

    # ------------------------------------------------------------------
    # 4. 图文报告卡 (news_notice)
    # ------------------------------------------------------------------
    def news_report_card(
        self,
        company: str,
        code: str,
        title: str,
        summary: str,
        cover_image_url: str,
        h5_url: str = "",
    ) -> Dict[str, Any]:
        """构建图文展示型卡片 (适合带封面图的深度报告)"""
        card = {
            "card_type": "news_notice",
            "source": {
                "desc": self.source_name,
                "desc_color": 0
            },
            "main_title": {
                "title": title,
                "desc": f"{company} ({code})"
            },
            "card_image": {
                "url": cover_image_url,
                "aspect_ratio": 2.25
            },
            "quote_area": {
                "type": 1,
                "url": h5_url or "https://work.weixin.qq.com",
                "title": "报告摘要",
                "quote_text": summary[:128]  # 企微建议不超过128字
            },
            "sub_title_text": f"生成时间 {datetime.now().strftime('%m-%d %H:%M')}",
        }

        if h5_url:
            card["jump_list"] = [
                {"type": 1, "url": h5_url, "title": "阅读完整报告"}
            ]
            card["card_action"] = {
                "type": 1,
                "url": h5_url
            }

        return card

    # ------------------------------------------------------------------
    # 5. 交互确认卡 (button_interaction)
    # ------------------------------------------------------------------
    def confirm_card(
        self,
        title: str,
        description: str,
        question: str,
        task_id: str,
        button_text: str = "确认",
    ) -> Dict[str, Any]:
        """构建按钮交互型卡片 (适合审批/确认场景)

        注意: button_interaction 需要配合回调处理，仅做卡片构建。
        """
        card = {
            "card_type": "button_interaction",
            "source": {
                "desc": self.source_name,
                "desc_color": 0
            },
            "main_title": {
                "title": title,
                "desc": description
            },
            "task_id": task_id,
            "button_selection": {
                "question_key": "confirm",
                "title": question,
                "option_list": [
                    {
                        "id": "yes",
                        "text": button_text,
                        "style": 1  # 主按钮样式
                    }
                ],
                "selected_id": "yes"
            },
            "button_replace_text": "已确认",
        }
        return card


# ----------------------------------------------------------------------
# 发送函数
# ----------------------------------------------------------------------

async def send_template_card(
    access_token: str,
    to_user: str,
    agent_id: int,
    card: Dict[str, Any],
    timeout: float = 15.0,
) -> Dict[str, Any]:
    """发送企微 template_card 消息

    Args:
        access_token: 企微 access_token
        to_user: 接收者 userid
        agent_id: 应用 agentid
        card: template_card 字典 (由 WeComCardBuilder 构建)
        timeout: 请求超时秒数

    Returns:
        企微 API 返回的 JSON 字典
    """
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
    payload = {
        "touser": to_user,
        "msgtype": "template_card",
        "agentid": agent_id,
        "template_card": card,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, timeout=timeout)
        return resp.json()


async def send_card_with_fallback(
    access_token: str,
    to_user: str,
    agent_id: int,
    card: Dict[str, Any],
    markdown_content: str,
    logger=None,
) -> Dict[str, Any]:
    """发送卡片，失败时自动 fallback 到 Markdown

    这是生产环境推荐的发送模式:
    1. 先尝试发送 template_card (视觉效果好)
    2. 若失败 (如卡片格式不支持、超长度限制)，自动降级为 markdown
    """
    result = await send_template_card(access_token, to_user, agent_id, card)

    if result.get("errcode") == 0:
        return result

    # Fallback to markdown
    if logger:
        logger.warning(f"卡片发送失败({result}), fallback到Markdown")

    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
    payload = {
        "touser": to_user,
        "msgtype": "markdown",
        "agentid": agent_id,
        "markdown": {"content": markdown_content[:4096]},
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, timeout=15)
        return resp.json()


# ----------------------------------------------------------------------
# 快捷函数 (针对常见场景的 one-liner)
# ----------------------------------------------------------------------

def quick_dd_card(
    company: str,
    code: str,
    risk_level: str,
    score: int,
    change_percent: float = 0.0,
    sentiment: str = "未知",
    h5_url: str = "",
) -> Dict[str, Any]:
    """快速构建尽调卡片 (无需实例化 Builder)"""
    builder = WeComCardBuilder()
    return builder.due_diligence_card(
        company=company,
        code=code,
        risk_level=risk_level,
        score=score,
        change_percent=change_percent,
        sentiment=sentiment,
        h5_url=h5_url,
    )


def quick_alert_card(
    company: str,
    code: str,
    price: float,
    change_percent: float,
    h5_url: str = "",
) -> Dict[str, Any]:
    """快速构建行情预警卡片"""
    builder = WeComCardBuilder()
    return builder.stock_alert_card(
        company=company,
        code=code,
        price=price,
        change_percent=change_percent,
        h5_url=h5_url,
    )
