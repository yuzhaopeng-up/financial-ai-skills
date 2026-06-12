"""
企微机器人卡片消息输出

将期权策略分析结果格式化为企业微信交互卡片
"""

import json
from typing import List, Dict, Any, Optional

# 企业微信卡片最大元素数限制
MAX_CARD_ITEMS = 20

def _format_pnl(val: float) -> str:
    """格式化损益值，带正负号颜色"""
    if val > 0:
        return f"<span style='color: #F56C6C'>+{val:.4f}</span>"
    elif val < 0:
        return f"<span style='color: #67C23A'>{val:.4f}</span>"
    return f"{val:.4f}"

def _scenario_table(scenarios) -> List[Dict[str, Any]]:
    """构建情景表格元素"""
    rows = []
    for s in scenarios:
        pnl_color = "#F56C6C" if s.net_pnl >= 0 else "#67C23A"
        rows.append({
            "type": "div",
            "text": {
                "tag": "lark_md",
                "content": (
                    f"**{s.scenario}** | "
                    f"到期价: `{s.final_spot:.4f}` | "
                    f"Payoff: `{s.payoff:.4f}` | "
                    f"净损益: <span style='color: {pnl_color}'>"
                    f"{'+' if s.net_pnl >= 0 else ''}{s.net_pnl:.4f}</span> | "
                    f"ROI: {s.roi:+.2f}%"
                )
            }
        })
    return rows

def _greeks_summary(greeks) -> List[Dict[str, Any]]:
    """构建希腊值摘要"""
    return [
        {
            "type": "column_set",
            "flex_mode": "bisect",
            "horizontal_spacing": "larged",
            "elements": [
                {
                    "type": "markdown",
                    "content": f"**Δ Delta**\n{greeks.delta:+.4f}\n\n"
                               f"**Γ Gamma**\n{greeks.gamma:+.6f}"
                },
                {
                    "type": "markdown",
                    "content": f"**ν Vega**\n{greeks.vega:+.4f}\n\n"
                               f"**Θ Theta**\n{greeks.theta:+.4f}\n\n"
                               f"**ρ Rho**\n{greeks.rho:+.4f}"
                },
            ]
        }
    ]

def build_options_card(result) -> Dict[str, Any]:
    """
    将 StrategyAnalysis 结果转换为企微消息卡片

    Args:
        result: OptionsStrategyEngine.analyze() 返回的 StrategyAnalysis 对象

    Returns:
        企微消息卡片 JSON（适合作为 feishu_im_user_message 的 content 参数）
    """
    # 解析器兼容：result 可能是 dict 或 StrategyAnalysis
    if isinstance(result, dict):
        g = result.get("greeks", {})
        scenarios = result.get("scenarios", [])
        strategy_type = result.get("strategy_type", "")
        spot_price = result.get("spot_price", 0)
        strike_prices = result.get("strike_prices", [])
        premium = result.get("premium", 0)
        days_to_expiry = result.get("days_to_expiry", 0)
        volatility = result.get("volatility", 0)
        risk_free_rate = result.get("risk_free_rate", 0)
        max_profit = result.get("max_profit")
        max_loss = result.get("max_loss")
        breakeven_points = result.get("breakeven_points", [])
       适用场景 = result.get("适用场景", "")
        策略特点 = result.get("策略特点", "")
        注意事项 = result.get("注意事项", "")
    else:
        g = result.greeks
        scenarios = result.scenarios
        strategy_type = result.strategy_type
        spot_price = result.spot_price
        strike_prices = result.strike_prices
        premium = result.premium
        days_to_expiry = result.days_to_expiry
        volatility = result.volatility
        risk_free_rate = result.risk_free_rate
        max_profit = result.max_profit
        max_loss = result.max_loss
        breakeven_points = result.breakeven_points
        适用场景 = result.适用场景
        策略特点 = result.策略特点
        注意事项 = result.注意事项

    max_profit_str = "无限" if max_profit is None or max_profit == float('inf') \
        else f"{max_profit:.4f}"
    strikes_str = "/".join(str(k) for k in strike_prices)
    be_str = " / ".join(f"{b:.4f}" for b in breakeven_points)

    # === 企微卡片结构 ===
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"📊 期权策略分析 — {strategy_type}"
                },
                "template": "blue"
            },
            "elements": [
                # 基本信息区
                {
                    "type": "markdown",
                    "content": (
                        f"**标的价格**: {spot_price}  |  **行权价**: {strikes_str}  |  "
                        f"**权利金**: {premium:.4f}\n"
                        f"**剩余天数**: {days_to_expiry}天  |  **波动率**: "
                        f"{volatility:.2%}  |  **无风险利率**: {risk_free_rate:.2%}"
                    )
                },
                {"type": "hr"},
                # 希腊值
                {
                    "type": "markdown",
                    "content": "**📐 希腊值分析**"
                },
                {
                    "type": "column_set",
                    "flex_mode": "bisect",
                    "horizontal_spacing": "larged",
                    "elements": [
                        {
                            "type": "markdown",
                            "content": (
                                f"**Delta**: {g.delta:+.4f}\n"
                                f"**Gamma**: {g.gamma:+.6f}"
                            )
                        },
                        {
                            "type": "markdown",
                            "content": (
                                f"**Vega**: {g.vega:+.4f}\n"
                                f"**Theta**: {g.theta:+.4f}\n"
                                f"**Rho**: {g.rho:+.4f}"
                            )
                        },
                    ]
                },
                {"type": "hr"},
                # 策略摘要
                {
                    "type": "markdown",
                    "content": "**📋 策略摘要**"
                },
                {
                    "type": "column_set",
                    "flex_mode": "bisect",
                    "horizontal_spacing": "larged",
                    "elements": [
                        {
                            "type": "markdown",
                            "content": (
                                f"**最大收益**: {max_profit_str}\n"
                                f"**最大损失**: {max_loss:.4f}\n"
                                f"**盈亏平衡点**: {be_str}"
                            )
                        },
                        {
                            "type": "markdown",
                            "content": (
                                f"**适用场景**: {适用场景}\n"
                                f"**注意事项**: {注意事项}"
                            )
                        },
                    ]
                },
                {"type": "hr"},
                # 情景分析
                {
                    "type": "markdown",
                    "content": "**📈 情景损益分析（6情景）**"
                },
            ]
        }
    }

    # 添加情景行
    for s in scenarios:
        pnl_color = "#F56C6C" if s.net_pnl >= 0 else "#67C23A"
        sign = "+" if s.net_pnl >= 0 else ""
        roi_sign = "+" if s.roi >= 0 else ""
        card["card"]["elements"].append({
            "type": "markdown",
            "content": (
                f"`{s.scenario}` | 到期 `{s.final_spot:.4f}` | "
                f"Payoff `{s.payoff:.4f}` | "
                f"净损益 <span style='color:{pnl_color}'>{sign}{s.net_pnl:.4f}</span> | "
                f"ROI {roi_sign}{s.roi:.2f}%"
            )
        })

    # 底部
    card["card"]["elements"].append({
        "type": "note",
        "elements": [
            {
                "tag": "plain_text",
                "text": f"⚠️ {策略特点}  本分析仅供参考，不构成投资建议。"
            }
        ]
    })

    return card

def format_wecom_card_json(result) -> str:
    """返回可直接使用的 JSON 字符串（用于企微卡片 content）"""
    return json.dumps(build_options_card(result), ensure_ascii=False)

def send_wecom_card_async(
    result,
    chat_id: Optional[str] = None,
    webhook_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    发送企微卡片消息

    Args:
        result: StrategyAnalysis 结果
        chat_id: 企微群 ID
        webhook_url: 企微机器人 webhook 地址

    Returns:
        API 响应结果
    """
    card_json = format_wecom_card_json(result)

    if webhook_url:
        # 使用 webhook 发送
        import urllib.request
        payload = json.dumps({
            "msgtype": "interactive",
            "interactive": json.loads(card_json)["card"]
        }).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    else:
        # 仅返回卡片 JSON（供外部工具调用）
        return {"card": json.loads(card_json), "status": "ready"}
