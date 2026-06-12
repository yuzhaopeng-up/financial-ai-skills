"""
企微（WeChat Work）卡片集成
生成适合发送至企业微信机器人的交互卡片
"""

import json
from typing import Dict, List, Optional
from .port_opt_engine import PortfolioOptimizeEngine


def build_wecom_card(
    result: Dict,
    title: str = "📊 投资组合优化分析报告",
    open_link_url: Optional[str] = None,
) -> Dict:
    """
    将优化结果转换为企微消息卡片格式

    :param result: PortfolioOptimizeEngine.optimize() 返回的结果
    :param title: 卡片标题
    :param open_link_url: 点击卡片跳转链接
    :return: 企微 interactive 卡片 JSON
    """
    opt_metrics = result["optimized_portfolio"]["metrics"]
    cur_metrics = result["current_portfolio"]["metrics"]
    comparison = result["comparison"]
    adjustments = result["execution_priority"]
    opt_weights = result["optimized_portfolio"]["weights"]

    # 风险收益指标对比
    ret_chg = comparison.get("return_change", 0)
    vol_chg = comparison.get("volatility_change", 0)
    sharpe_chg = comparison.get("sharpe_change", 0)

    ret_emoji = "🔼" if ret_chg >= 0 else "🔽"
    vol_emoji = "🔽" if vol_chg < 0 else "🔼"

    # 调仓建议摘要（最多5条）
    trade_actions = [a for a in adjustments if a["action"] != "hold"][:5]

    elements = []

    # ---- Header 摘要区 ----
    summary_lines = comparison.get("summary", "").split("\n")
    summary_md = "\n".join([f"• {line}" for line in summary_lines if line.strip()])

    elements.append({
        "tag": "markdown",
        "content": f"**{title}**\n"
                   f"—— 风险收益对比 ——\n"
                   f"年化收益率 {opt_metrics['expected_return']:.2%} "
                   f"{ret_emoji} {ret_chg:+.2%}\n"
                   f"年化波动率 {opt_metrics['volatility']:.2%} "
                   f"{vol_emoji} {vol_chg:+.2%}\n"
                   f"夏普比率   {opt_metrics['sharpe_ratio']:.3f} "
                   f"{'🔼' if sharpe_chg >= 0 else '🔽'} {sharpe_chg:+.3f}\n"
                   f"\n📋 优化摘要\n{summary_md}"
    })

    # ---- 优化后配置 ----
    top_assets = sorted(
        [(k, v) for k, v in opt_weights.items() if v > 0.01],
        key=lambda x: x[1],
        reverse=True
    )[:6]

    config_lines = "\n".join([
        f"• {name}: {wt:.1%}" for name, wt in top_assets
    ])
    elements.append({
        "tag": "markdown",
        "content": f"**📦 优化后资产配置（前{len(top_assets)}类）**\n{config_lines}"
    })

    # ---- 调仓建议 ----
    if trade_actions:
        action_lines = []
        for a in trade_actions:
            emoji = "🟢买入" if a["action"] == "buy" else "🔴卖出"
            prio = f"P{a['priority']}" if a['priority'] < 99 else ""
            action_lines.append(
                f"[{emoji}{prio}] {a['asset']}: {a['current_weight']:.1%}→{a['target_weight']:.1%}"
            )
        elements.append({
            "tag": "markdown",
            "content": f"**🔄 调仓建议（按优先级）**\n" + "\n".join(action_lines)
        })

    # ---- 风险指标 ----
    elements.append({
        "tag": "markdown",
        "content": f"**📉 风险评估**\n"
                   f"• 最大回撤（估算）: {opt_metrics['max_drawdown']:.2%}\n"
                   f"• 95% VaR（估算）: {opt_metrics['var_95']:.2%}\n"
                   f"• 组合波动率: {opt_metrics['volatility']:.2%}"
    })

    # ---- 按钮区 ----
    buttons = []
    if open_link_url:
        buttons.append({
            "tag": "a",
            "text": {"tag": "plain_text", "text": "📎 查看完整报告"},
            "action_type": "link",
            "url": open_link_url,
        })

    buttons.extend([
        {
            "tag": "a",
            "text": {"tag": "plain_text", "text": "🔄 生成新方案"},
            "action_type": "link",
            "url": "https://example.com/rebalance",
        },
        {
            "tag": "a",
            "text": {"tag": "plain_text", "text": "✅ 确认执行"},
            "action_type": "link",
            "url": "https://example.com/confirm",
        },
    ])

    card = {
        "msgtype": "interactive",
        "interactive": {
            "header": {
                "title": {"tag": "plain_text", "text": title},
                "template_id": "3XgDfxxx",  # 可替换为实际的卡片模板ID
            },
            "elements": elements,
            "btn_interface_list": buttons[:3],
        }
    }

    return card


def build_simple_wecom_text(result: Dict) -> str:
    """构建纯文本企微消息（不支持卡片的场景）"""
    opt_metrics = result["optimized_portfolio"]["metrics"]
    comparison = result["comparison"]

    lines = [
        "📊 投资组合优化报告",
        "=" * 40,
        f"预期年化收益: {opt_metrics['expected_return']:.2%}",
        f"年化波动率: {opt_metrics['volatility']:.2%}",
        f"夏普比率: {opt_metrics['sharpe_ratio']:.3f}",
        f"最大回撤(估): {opt_metrics['max_drawdown']:.2%}",
        "",
        "🔄 调仓建议:",
    ]

    for a in result["execution_priority"]:
        if a["action"] == "hold":
            continue
        emoji = "🟢" if a["action"] == "buy" else "🔴"
        lines.append(
            f"  {emoji} {a['action'].upper()} {a['asset']}: "
            f"{a['current_weight']:.1%} → {a['target_weight']:.1%}"
        )

    lines.extend(["", comparison.get("summary", "")])

    return "\n".join(lines)


# ============================================================
# CLI 入口（直接调用）
# ============================================================

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))

    engine = PortfolioOptimizeEngine()

    # 默认测试用例
    result = engine.optimize(
        current_portfolio={"stock": 0.7, "bond": 0.2, "cash": 0.1},
        risk_preference="medium",
        optimization_goal="reduce_risk",
    )

    card = build_wecom_card(result)
    print(json.dumps(card, ensure_ascii=False, indent=2))
