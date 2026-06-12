"""
wecom_integration.py - 融资融券监控企微/飞书卡片集成

提供企业微信和飞书消息卡片的生成与发送能力。
"""

import json
from typing import Dict, Any, List, Optional

# 企微卡片模板颜色
COLOR_GREEN = "green"
COLOR_YELLOW = "yellow"
COLOR_RED = "red"
COLOR_GRAY = "gray"


def get_ratio_color(level_code: int) -> str:
    """根据风险等级获取颜色"""
    return {0: COLOR_GREEN, 1: COLOR_YELLOW, 2: COLOR_RED}.get(level_code, COLOR_GRAY)


def build_margin_monitor_card(
    total_assets: float,
    total_debt: float,
    maintenance_ratio: float,
    warning_line: float,
    liquidation_line: float,
    risk_level: int,
    risk_status: str,
    positions: List[Dict[str, Any]],
    concentrations: List[Dict[str, Any]],
    recommendations: List[Dict[str, Any]],
    warning_message: str = None,
) -> Dict[str, Any]:
    """
    构建融资融券监控消息卡片（企微/飞书通用）

    Args:
        total_assets: 总资产
        total_debt: 总负债
        maintenance_ratio: 维保比率（%）
        warning_line: 预警线（%）
        liquidation_line: 平仓线（%）
        risk_level: 风险等级 0=safe,1=warning,2=danger
        risk_status: 风险状态文本
        positions: 持仓列表
        concentrations: 集中度风险列表
        recommendations: 追保建议列表
        warning_message: 预警消息

    Returns:
        企微/飞书卡片 JSON
    """
    color = get_ratio_color(risk_level)

    # ── 持仓表格内容 ──
    position_lines = []
    for p in positions:
        pnl_emoji = "📈" if float(p.get("unrealized_pnl", "0").replace(",", "").replace("+", "")) > 0 else "📉"
        position_lines.append(
            f"{p['stock']} | {p['shares']}股 | 成本{p['cost']}→现价{p['current']} | "
            f"市值{p['market_value']} | {pnl_emoji}{p['unrealized_pnl']}"
        )
    position_md = "\n".join(position_lines) if position_lines else "暂无持仓数据"

    # ── 集中度 ──
    conc_md = ""
    for c in concentrations:
        conc_md += f"{c['stock']}：{c['ratio']} {c['level']}\n"

    # ── 追保建议 ──
    rec_md = ""
    for r in recommendations:
        if int(r.get("priority", 0)) > 0:
            rec_md += f"方案{r['plan']}（优先级{r['priority']}）：{r['description']}\n  → {r['action']}\n"

    # ── 预警消息 ──
    warn_md = warning_message or ""

    # ── 卡片元素 ──
    elements = []

    # 维保比率核心指标
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": (
                f"**📊 维保比率**：`{maintenance_ratio:.2f}%` **{risk_status}**\n"
                f"预警线 {warning_line}%（偏离 `{maintenance_ratio - warning_line:+.2f}%`）| "
                f"平仓线 {liquidation_line}%（偏离 `{maintenance_ratio - liquidation_line:+.2f}%`）"
            )
        }
    })

    if warn_md:
        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": warn_md}
        })

    elements.append({"tag": "hr"})

    # 账户概览
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": (
                f"**账户概览**\n"
                f"总资产：{total_assets:,.0f} 元\n"
                f"总负债：{total_debt:,.0f} 元\n"
                f"净资产：{total_assets - total_debt:,.0f} 元"
            )
        }
    })

    elements.append({"tag": "hr"})

    # 持仓明细
    elements.append({
        "tag": "div",
        "text": {"tag": "lark_md", "content": f"**💼 持仓明细**\n{position_md}"}
    })

    if conc_md:
        elements.append({"tag": "hr"})
        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": f"**🎯 集中度风险**\n{conc_md}"}
        })

    if rec_md:
        elements.append({"tag": "hr"})
        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": f"**💡 追保建议**\n{rec_md}"}
        })

    # 操作按钮（飞书支持，企微部分支持）
    actions = []
    if risk_level >= 1:  # WARNING or DANGER
        actions.append({
            "tag": "button",
            "text": {"tag": "lark_md", "content": "📌 追加保证金"},
            "type": "primary",
            "value": {"action": "add_margin"}
        })
        actions.append({
            "tag": "button",
            "text": {"tag": "lark_md", "content": "📉 减仓"},
            "type": "danger",
            "value": {"action": "reduce_position"}
        })

    card = {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "header": {
                "title": {"tag": "plain_text", "content": "📊 融资融券监控预警"},
                "template": color
            },
            "elements": elements
        }
    }

    if actions:
        card["interactive"]["elements"].append({"tag": "hr"})
        card["interactive"]["elements"].append({"tag": "action", "actions": actions})

    return card


def send_wecom_card(card: Dict[str, Any], webhook_url: str = None) -> Dict[str, Any]:
    """
    发送企微卡片消息

    Args:
        card: 卡片 JSON
        webhook_url: 企微 webhook 地址（可选）

    Returns:
        发送结果
    """
    if not webhook_url:
        return {"success": False, "error": "未配置 webhook_url"}

    try:
        import requests
        resp = requests.post(webhook_url, json=card, timeout=10)
        result = resp.json()
        if result.get("errcode") == 0:
            return {"success": True, "errmsg": result.get("errmsg", "ok")}
        else:
            return {"success": False, "error": result.get("errmsg", "unknown error")}
    except Exception as e:
        return {"success": False, "error": str(e)}


def build_from_engine(engine) -> Dict[str, Any]:
    """
    从 MarginTradingEngine 实例直接构建卡片

    Args:
        engine: MarginTradingEngine 实例

    Returns:
        卡片 JSON
    """
    report = engine.generate_report()
    mr = report["maintenance_ratio"]

    return build_margin_monitor_card(
        total_assets=float(report["account"]["total_assets"].replace(",", "")),
        total_debt=float(report["account"]["total_debt"].replace(",", "")),
        maintenance_ratio=float(mr["value"].replace("%", "")),
        warning_line=float(mr["warning_line"].replace("%", "")),
        liquidation_line=float(mr["liquidation_line"].replace("%", "")),
        risk_level=mr["level_code"],
        risk_status=mr["level"],
        positions=report["positions"],
        concentrations=report["concentration_risks"],
        recommendations=report["recommendations"],
        warning_message=report["warning"].get("message") if isinstance(report["warning"], dict) else None,
    )


# ─── 快捷 CLI ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, default="融资监控 持仓某股票100万 融资50万 成本10元 现价8元")
    parser.add_argument("--webhook", type=str, default=None)
    args = parser.parse_args()

    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from margin_engine import MarginTradingEngine

    engine = MarginTradingEngine.from_natural_language(args.text)
    card = build_from_engine(engine)
    print(json.dumps(card, ensure_ascii=False, indent=2))

    if args.webhook:
        result = send_wecom_card(card, args.webhook)
        print(f"\n发送结果: {result}")
