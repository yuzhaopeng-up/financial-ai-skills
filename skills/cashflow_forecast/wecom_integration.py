"""
企微（WeCom）卡片集成

将资金预测结果以企微消息卡片格式推送。
支持通过企业微信 Webhook 或企微机器人 API 发送。
"""

import json
import os
from typing import Dict, Any, Optional

try:
    from wecom_robot import send_interactive_card  # type: ignore
    WECOM_AVAILABLE = True
except ImportError:
    WECOM_AVAILABLE = False


def build_card(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    将预测结果构建为企微交互卡片结构。

    Args:
        result: CashflowForecastEngine.forecast() 返回的字典

    Returns:
        企微卡片 JSON 结构（dict）
    """
    inp = result["input"]
    forecast = result["forecast"]
    gap_warning = result["gap_warning"]
    solutions = result["solutions"]

    # 状态颜色映射
    status_color = {
        "normal": "2",   # 绿色
        "warning": "3",  # 橙色/黄色
        "danger": "1",   # 红色
    }

    # 预测行
    forecast_elements = []
    for label, data in forecast.items():
        months_map = {"month_1": "1个月", "month_3": "3个月", "month_6": "6个月", "month_12": "12个月"}
        months_str = months_map.get(label, label)
        color_tag = status_color.get(data["status"], "0")
        emoji = {"normal": "🟢", "warning": "🟡", "danger": "🔴"}.get(data["status"], "⚪")
        cash_str = f"{data['cash']:+.2f}万"
        forecast_elements.append({
            "tag": "markdown",
            "content": f"{emoji} **{months_str}**：<font color='{color_tag}'>{cash_str}</font>  [{data['status']}]"
        })

    # 预警行
    warning_elements = []
    if gap_warning:
        for label, w in gap_warning.items():
            months_map = {"month_1": "1个月", "month_3": "3个月", "month_6": "6个月", "month_12": "12个月"}
            months_str = months_map.get(label, label)
            warning_elements.append({
                "tag": "markdown",
                "content": (
                    f"🔴 <font color='red'>**缺口预警**</font> | "
                    f"{months_str} 缺口 **{w['gap']}万** | "
                    f"预计 {w['deadline']} | 提前{w.get('note', '3个月')}"
                )
            })
    else:
        warning_elements.append({
            "tag": "markdown",
            "content": "🟢 当前无资金缺口预警"
        })

    # 方案行
    solution_contents = []
    for i, sol in enumerate(solutions[:5], 1):  # 最多5条
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(sol.get("priority", "low"), "⚪")
        solution_contents.append(
            f"{i}. {priority_emoji} **{sol['action']}**\n   效果：{sol['expected_impact']} | 周期：{sol['timeline']}"
        )

    card = {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "color": "red" if gap_warning else "green",
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "🚨 资金缺口预警" if gap_warning else "📊 资金预测报告"
                },
                "vertical": "center",
                "color": "red" if gap_warning else "green",
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": (
                        f"**当前资金**：{inp['current_cash']}万 | "
                        f"**应收**：{inp['receivables']}万 | "
                        f"**应付**：{inp['payables']}万 | "
                        f"**月支出**：{inp['monthly_expense']}万\n"
                        f"**净可用资金**：{inp['net_cash']}万"
                    ),
                },
                {"tag": "hr"},
                {
                    "tag": "markdown",
                    "content": "**📅 未来资金预测**",
                },
                *forecast_elements,
                {"tag": "hr"},
                {
                    "tag": "markdown",
                    "content": "**🚨 缺口预警（提前3个月红色标注）**",
                },
                *warning_elements,
                {"tag": "hr"},
                {
                    "tag": "markdown",
                    "content": "**💡 应对方案**",
                },
                {
                    "tag": "markdown",
                    "content": "\n".join(solution_contents) if solution_contents else "当前资金充裕，无需特别操作。",
                },
            ],
        },
    }
    return card


def send_card(
    webhook_url: str,
    result: Dict[str, Any],
    mentioned_list: Optional[list] = None,
) -> Dict[str, Any]:
    """
    通过企微 Webhook 发送交互卡片。

    Args:
        webhook_url: 企业微信群机器人的 Webhook URL
        result: CashflowForecastEngine.forecast() 返回的字典
        mentioned_list: 需要 @ 的用户 open_id 列表

    Returns:
        接口返回的 JSON（dict）
    """
    import urllib.request

    card = build_card(result)

    payload = json.dumps(card, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}


def format_wecom_text(result: Dict[str, Any]) -> str:
    """
    格式化为纯文本（用于企微机器人文本消息 fallback）。

    Args:
        result: CashflowForecastEngine.forecast() 返回的字典

    Returns:
        纯文本字符串
    """
    from cashflow_engine import CashflowForecastEngine
    engine = CashflowForecastEngine()
    return engine.format_text(result)


if __name__ == "__main__":
    # 单元测试
    from cashflow_engine import CashflowForecastEngine
    engine = CashflowForecastEngine()
    test_input = "资金预测 当前资金200万 应收500万 应付300万 月支出100万"
    parsed = engine.parse_input(test_input)
    assert parsed is not None
    result = engine.forecast(**parsed)
    card = build_card(result)
    print(json.dumps(card, ensure_ascii=False, indent=2))
