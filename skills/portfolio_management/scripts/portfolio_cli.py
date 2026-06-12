#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portfolio Management CLI
Usage: python3 scripts/portfolio_cli.py generate "组合管理 平衡型 资产500万 期限3年 目标收益8%"
"""

import sys
import re
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from portfolio_engine import PortfolioEngine


def parse_input(text: str):
    """自然语言解析输入参数"""
    text = text.strip()

    # 风险偏好
    risk_map = {
        "保守": "保守型", "稳健": "稳健型", "平衡": "平衡型",
        "进取": "进取型", "激进": "激进型",
    }
    risk_pref = None
    for k, v in risk_map.items():
        if k in text:
            risk_pref = v
            break
    if risk_pref is None:
        risk_pref = "平衡型"

    # 资产规模
    size_match = re.search(r"([\d.]+)\s*(万|百万|元|万万元)", text)
    if size_match:
        val = float(size_match.group(1))
        unit = size_match.group(2)
        if unit in ("百万", "万万元"):
            val *= 100
        if "元" in unit and val < 1000:
            val *= 10000
    else:
        val = 500.0
    asset_size = val

    # 投资期限
    horizon_match = re.search(r"(\d+)\s*年", text)
    horizon = int(horizon_match.group(1)) if horizon_match else 3

    # 目标收益
    target_match = re.search(r"([\d.]+)\s*%", text)
    target_return = float(target_match.group(1)) if target_match else None

    return risk_pref, asset_size, horizon, target_return


def format_text_output(result: dict) -> str:
    """格式化文本输出"""
    meta = result["metadata"]
    lines = []
    lines.append("=" * 60)
    lines.append(f"📊 投资组合分析报告")
    lines.append(f"风险偏好: {meta['risk_preference']} | 资产规模: {meta['asset_size']:.0f}万元 | 投资期限: {meta['investment_horizon_years']}年")
    if meta.get("target_return_pct"):
        lines.append(f"目标收益: {meta['target_return_pct']}%")
    lines.append("=" * 60)

    strategies = [
        ("markowitz_efficient", "马科维茨有效前沿（最优夏普）", "⭐"),
        ("markowitz_min_variance", "马科维茨最小方差", "🔒"),
        ("risk_parity", "风险平价", "⚖️"),
        ("max_diversification", "最大多样化", "🌐"),
    ]

    for key, name, icon in strategies:
        s = result[key]
        lines.append(f"\n{icon} {name}")
        lines.append(f"   预期年化收益: {s['expected_return_annual']:.2f}%")
        lines.append(f"   年化波动率:   {s['volatility_annual']:.2f}%")
        lines.append(f"   夏普比率:     {s['sharpe_ratio']:.3f}")
        lines.append(f"   估算最大回撤: {s['max_drawdown_estimate']:.2f}%")
        lines.append("   持仓明细:")
        for h in s["holdings"]:
            lines.append(f"     {h['asset']:12s} {h['weight']:5.1f}%  {h['asset_type']:4s}  {h['region']}")

    lines.append("\n" + "=" * 60)
    lines.append("💡 建议:")
    summary = result["summary"]
    lines.append(f"  最高夏普 → {result[summary['highest_sharpe']]['strategy']} ({result[summary['highest_sharpe']]['sharpe_ratio']:.3f})")
    lines.append(f"  最低波动 → {result[summary['lowest_volatility']]['strategy']} ({result[summary['lowest_volatility']]['volatility_annual']:.2f}%)")
    lines.append(f"  最高收益 → {result[summary['highest_return']]['strategy']} ({result[summary['highest_return']]['expected_return_annual']:.2f}%)")
    lines.append("⚠️  以上为模型测算结果，仅供参考，不构成投资建议。")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Portfolio Management CLI")
    parser.add_argument("command", nargs="+", help="Command with arguments")
    parser.add_argument("--format", default="text", choices=["text", "json"], help="Output format")
    args = parser.parse_args()

    # 拼接所有命令参数
    raw = " ".join(args.command)

    # 提取generate子命令（如果有）
    parts = raw.replace("generate", " ").strip().split()
    input_text = " ".join(parts) if parts else raw

    try:
        risk_pref, asset_size, horizon, target_return = parse_input(input_text)
    except Exception as e:
        print(f"❌ 参数解析失败: {e}")
        sys.exit(1)

    engine = PortfolioEngine(api_mode=(args.format == "json"))
    result = engine.generate(
        risk_preference=risk_pref,
        asset_size=asset_size,
        investment_horizon_years=horizon,
        target_return=target_return,
    )

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_text_output(result))


if __name__ == "__main__":
    main()
