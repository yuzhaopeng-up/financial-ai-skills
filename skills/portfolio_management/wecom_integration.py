# -*- coding: utf-8 -*-
"""
企微/飞书消息卡片集成
生成适合通过 feishu_im_user_message 或企微API发送的卡片格式
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from portfolio_engine import PortfolioEngine


def build_feshu_card(result: dict) -> dict:
    """构建飞书消息卡片（Feishu Card / 消息卡片格式）"""
    meta = result["metadata"]
    summary = result["summary"]

    def build_holdings_md(portfolio_key: str, max_items: int = 5) -> list:
        s = result[portfolio_key]
        elements = []
        for h in s["holdings"][:max_items]:
            bar_len = int(h["weight"] / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            elements.append({
                "tag": "markdown",
                "content": f"`{h['asset']:<10s}` {bar} {h['weight']:5.1f}%"
            })
        if len(s["holdings"]) > max_items:
            elements.append({"tag": "markdown", "content": f"_...还有{len(s['holdings'])-max_items}只持仓_"})
        return elements

    strat_lines = []
    for key, label in [
        ("markowitz_efficient", "⭐马科维茨最优"),
        ("risk_parity", "⚖️风险平价"),
        ("max_diversification", "🌐最大多样化"),
    ]:
        s = result[key]
        strat_lines.append({
            "tag": "markdown",
            "content": f"**{label}**\n"
                       f"收益 {s['expected_return_annual']:.1f}% | 波动 {s['volatility_annual']:.1f}% | "
                       f"夏普 {s['sharpe_ratio']:.2f}"
        })

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"📊 投资组合分析 | {meta['risk_preference']}"},
                "subtitle": {"tag": "plain_text", "content": f"规模{meta['asset_size']:.0f}万 · {meta['investment_horizon_years']}年 · 目标{meta.get('target_return_pct', '未设')}%" if meta.get('target_return_pct') else f"规模{meta['asset_size']:.0f}万 · {meta['investment_horizon_years']}年"},
                "template": "blue"
            },
            "elements": [
                {"tag": "markdown", "content": "**三大策略对比**"},
                *strat_lines,
                {"tag": "hr"},
                {"tag": "markdown", "content": "**📌 马科维茨最优夏普组合持仓**"},
                *build_holdings_md("markowitz_efficient"),
                {"tag": "hr"},
                {"tag": "markdown", "content": "**⚖️ 风险平价组合持仓**"},
                *build_holdings_md("risk_parity"),
                {"tag": "hr"},
                {
                    "tag": "note",
                    "elements": [
                        {"tag": "plain_text", "content": "⚠️ 以上为模型测算结果，仅供参考，不构成投资建议。"}
                    ]
                }
            ]
        }
    }
    return card


def build_wecom_markdown(result: dict) -> str:
    """构建企微Markdown文本（用于企微群消息）"""
    meta = result["metadata"]
    summary = result["summary"]

    lines = [
        f"📊 **投资组合分析报告**",
        f"风险偏好: {meta['risk_preference']} | 规模: {meta['asset_size']:.0f}万元 | 期限: {meta['investment_horizon_years']}年",
        f"目标收益: {meta.get('target_return_pct', '未设')}%",
        "",
        "---",
    ]

    for key, icon, name in [
        ("markowitz_efficient", "⭐", "马科维茨有效前沿"),
        ("risk_parity", "⚖️", "风险平价"),
        ("max_diversification", "🌐", "最大多样化"),
    ]:
        s = result[key]
        lines.append(f"{icon} **{name}**")
        lines.append(f"收益 {s['expected_return_annual']:.2f}% | 波动 {s['volatility_annual']:.2f}% | 夏普 {s['sharpe_ratio']:.3f}")
        holdings_str = " | ".join([f"{h['asset']}{h['weight']:.1f}%" for h in s['holdings'][:4]])
        lines.append(f"持仓: {holdings_str}")
        if len(s['holdings']) > 4:
            lines.append(f"...共{len(s['holdings'])}只资产")
        lines.append("")

    lines.extend([
        "---",
        "**💡 策略建议**",
        f"• 最高夏普 → {result[summary['highest_sharpe']]['strategy']} (夏普 {result[summary['highest_sharpe']]['sharpe_ratio']:.3f})",
        f"• 最低波动 → {result[summary['lowest_volatility']]['strategy']} (波动 {result[summary['lowest_volatility']]['volatility_annual']:.2f}%)",
        f"• 最高收益 → {result[summary['highest_return']]['strategy']} (收益 {result[summary['highest_return']]['expected_return_annual']:.2f}%)",
        "",
        "⚠️ *以上为模型测算结果，仅供参考，不构成投资建议。*",
    ])
    return "\n".join(lines)


if __name__ == "__main__":
    engine = PortfolioEngine(api_mode=True)
    result = engine.generate("平衡型", 500, 3, 8.0)
    print(build_wecom_markdown(result))
