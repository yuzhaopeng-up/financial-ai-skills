# -*- coding: utf-8 -*-
"""
企微卡片集成
企业微信消息卡片格式化输出
"""

from typing import Optional
from manager_engine import FundManagerEngine


def format_wecom_card(name: str) -> dict:
    """
    生成基金经理企微消息卡片内容

    Args:
        name: 基金经理姓名

    Returns:
        企微卡片 JSON dict，包含以下字段：
        - title: 卡片标题
        - manager_name: 基金经理姓名
        - company: 所属公司
        - scale: 管理规模
        - experience: 从业年限
        - style_tags: 风格标签（逗号分隔）
        - annual_return: 5年年化收益
        - max_drawdown: 最大回撤
        - risk_level: 风险等级
        - rep_fund: 代表基金
        - success: 是否成功找到
        - error_msg: 未找到时的错误信息
    """
    engine = FundManagerEngine()
    matched_name = engine.search_manager(name)

    if not matched_name:
        return {
            "success": False,
            "error_msg": f"未找到基金经理「{name}」，请确认姓名是否正确。",
            "title": "❌ 未找到基金经理",
        }

    data = engine.managers[matched_name]
    perf = data["performance"]
    risk = data["risk特征"]

    # 风险等级评估
    vol = risk["volatility"]
    dd_control = risk["drawdown_control"]
    if vol == "低" or "优秀" in dd_control:
        risk_level = "🟢 低风险"
    elif vol == "中等偏低" or "较好" in dd_control:
        risk_level = "🟡 中低风险"
    elif vol == "中等":
        risk_level = "🟡 中风险"
    elif vol == "较高":
        risk_level = "🟠 中高风险"
    else:
        risk_level = "🔴 高风险"

    return {
        "success": True,
        "title": f"📊 {data['name']} — 基金经理画像",
        "manager_name": data["name"],
        "company": data["fund_company"].replace("基金管理有限公司", "").replace("股份有限公司", ""),
        "experience": f"{data['experience_years']}年",
        "scale": f"~{data['management_scale_bn']}亿",
        "style_tags": " / ".join(data["investment_style"]),
        "area": "、".join(data["area_expertise"][:5]),
        "annual_return": perf.get("annual_return_5y", "N/A"),
        "cumulative_return": perf.get("cumulative_return_5y", "N/A"),
        "max_drawdown": perf.get("max_drawdown", "N/A"),
        "sharpe": perf.get("sharpe_ratio", "N/A"),
        "risk_level": risk_level,
        "risk_volatility": vol,
        "risk_drawdown": dd_control,
        "rep_fund": data["representative_fund"],
        "holding_period": data["holding_preference"]["holding_period"],
        "top_holdings": "、".join(data["holding_preference"]["top_holdings"][:3]),
        "awards_count": len(data["awards"]),
        "top_awards": "；".join(data["awards"][:3]),
        "famous_saying": data["famous_saying"],
        "personality": data["personality"],
    }


def build_wecom_text_card(name: str) -> str:
    """
    生成企微富文本卡片内容（用于飞书/企微 text 类型的纯文本展示）
    格式化为简洁的分段文字
    """
    card = format_wecom_card(name)
    if not card["success"]:
        return card["error_msg"]

    lines = [
        f"{card['title']}",
        "─" * 40,
        f"🏢 {card['company']}｜⏱ {card['experience']}｜💰 {card['scale']}",
        f"📈 风格：{card['style_tags']}",
        f"🎯 能力圈：{card['area']}",
        "─" * 40,
        f"【业绩表现】",
        f"  年化收益：{card['annual_return']}",
        f"  累计收益：{card['cumulative_return']}",
        f"  最大回撤：{card['max_drawdown']}",
        f"  夏普比率：{card['sharpe']}",
        "─" * 40,
        f"【风险评估】{card['risk_level']}",
        f"  波动率：{card['risk_volatility']}",
        f"  回撤控制：{card['risk_drawdown']}",
        "─" * 40,
        f"【持仓】{card['top_holdings']}...",
        f"  持仓周期：{card['holding_period']}",
        f"【代表基金】{card['rep_fund']}",
        "─" * 40,
        f"【荣誉】{card['top_awards']}",
        "─" * 40,
        f"💬 「{card['famous_saying']}」",
        f"📋 {card['personality']}",
    ]
    return "\n".join(lines)


def build_wecom_interactive_card(name: str) -> dict:
    """
    生成企微 interactive 消息卡片 JSON
    适用于企业微信 webhook 推送
    """
    card = format_wecom_card(name)
    if not card["success"]:
        return {}

    return {
        "msgtype": "interactive",
        "interactive": {
            "tag": "div",
            "text": card["error_msg"],
        }
    }


# 企微 Markdown 格式（支持部分 Markdown）
def build_wecom_markdown(name: str) -> str:
    """生成企微 Markdown 格式的卡片内容"""
    card = format_wecom_card(name)
    if not card["success"]:
        return card["error_msg"]

    lines = [
        f"### 📊 {card['manager_name']} — 基金经理画像",
        "",
        f"**🏢 公司**：{card['company']}",
        f"**⏱ 从业**：{card['experience']}　**💰 管理规模**：{card['scale']}",
        "",
        f"**📈 投资风格**：{card['style_tags']}",
        f"**🎯 能力圈**：{card['area']}",
        "",
        "---",
        "",
        "**【业绩表现】**",
        f"- 年化收益：{card['annual_return']}",
        f"- 累计收益（5年）：{card['cumulative_return']}",
        f"- 最大回撤：{card['max_drawdown']}",
        f"- 夏普比率：{card['sharpe']}",
        "",
        "**【风险特征】**",
        f"- 风险等级：{card['risk_level']}",
        f"- 波动率：{card['risk_volatility']}",
        f"- 回撤控制：{card['risk_drawdown']}",
        "",
        "---",
        "",
        f"**【代表基金】**：{card['rep_fund']}",
        f"**【前三重仓】**：{card['top_holdings']}...",
        f"**【持仓周期】**：{card['holding_period']}",
        "",
        f"**【主要荣誉】**：{card['top_awards']}",
        "",
        f"> 💬 「{card['famous_saying']}」",
        "",
        f"📋 {card['personality']}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    print(build_wecom_markdown("张坤"))
