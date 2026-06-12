#!/usr/bin/env python3
"""
Trade Finance CLI - 贸易融资CLI入口

用法：
    python3 scripts/trade_cli.py generate "贸易融资 出口企业 金额100万美元 账期90天"
    python3 scripts/trade_cli.py compare LC FACTORING FORFAITING
    python3 scripts/trade_cli.py wecom "出口企业 金额50万美元 账期60天"
    python3 scripts/trade_cli.py all
"""

import json
import os
import sys
import re
from pathlib import Path

# 将skill根目录加入路径
SKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from trade_engine import TradeFinanceEngine, parse_cli_input


def format_recommendation(result: dict) -> str:
    """格式化推荐结果为易读文本"""
    input_info = result["input"]
    lines = []
    lines.append("=" * 60)
    lines.append("🗂  贸易融资方案推荐报告")
    lines.append("=" * 60)
    lines.append("")
    lines.append("📋 输入参数")
    lines.append(f"  企业类型：{input_info['company_type']}")
    lines.append(f"  贸易类型：{input_info['trade_type']}")
    lines.append(f"  融资金额：{input_info['amount_usd']:,.0f} USD")
    lines.append(f"  账期：{input_info['payment_terms_days']} 天")
    lines.append("")

    lines.append("🏆 推荐方案（按匹配度排序）")
    lines.append("-" * 60)
    for rec in result["recommendations"]:
        lines.append(f"  #{rec['rank']} {rec['name_cn']}（{rec['name_en']}）")
        lines.append(f"     匹配度：{rec['match_score']:.1f}/100")
        lines.append(f"     原因：{rec['match_reason']}")
        lines.append("")

    lines.append("📊 方案对比表")
    lines.append("-" * 60)
    # 打印表头
    header = result["comparison_table"][0] if result["comparison_table"] else {}
    if header:
        col_widths = {
            "产品": 8,
            "融资比例": 16,
            "利率参考": 16,
            "办理周期": 16,
            "主要特点": 12,
            "适用账期": 12,
        }
        header_line = "  " + " | ".join(k.ljust(col_widths.get(k, 10)) for k in header.keys())
        lines.append(header_line)
        lines.append("  " + "-" * len(header_line))
        for row in result["comparison_table"]:
            row_line = "  " + " | ".join(str(row.get(k, "")).ljust(col_widths.get(k, 10)) for k in header.keys())
            lines.append(row_line)

    lines.append("")
    lines.append("💡 决策建议")
    lines.append("-" * 60)
    lines.append(f"  {result['decision_advice']}")
    lines.append("")
    lines.append("📦 全产品一览")
    lines.append("-" * 60)
    for p in result["all_products_summary"]:
        lines.append(
            f"  • {p['产品']} | 适用: {p['适用企业']} | "
            f"融资: {p['融资比例']} | 利率: {p['利率参考']}"
        )
    lines.append("=" * 60)
    return "\n".join(lines)


def format_compare(result: dict) -> str:
    """格式化产品对比结果"""
    lines = []
    lines.append("=" * 60)
    lines.append("🔍 产品详细对比")
    lines.append("=" * 60)

    for i, p in enumerate(result.get("products", []), 1):
        lines.append("")
        lines.append(f"【{i}】{p['name_cn']} / {p['name_en']}")
        lines.append("-" * 50)
        lines.append(f"  💰 融资比例：{p['financing_ratio']}")
        lines.append(f"  📈 利率参考：{p['interest_rate_ref']}")
        lines.append(f"  ⏱  办理周期：{p['processing_cycle']}")
        lines.append(f"  💵 金额范围：{p['amount_range']}")
        lines.append(f"  📅 账期范围：{p['terms_range']}")
        lines.append(f"  🏷  主要特点：{', '.join(p['tags'])}")
        lines.append(f"  👥 适用企业：{', '.join(p['suitable_company_types'])}")
        lines.append("")
        lines.append("  📝 适用场景：")
        for s in p["applicable_scenarios"]:
            lines.append(f"     - {s}")
        lines.append("")
        lines.append("  📄 所需材料：")
        for m in p["required_materials"]:
            lines.append(f"     - {m}")
        lines.append("")
        lines.append("  ⚠️  风控要点：")
        for r in p["risk_points"]:
            lines.append(f"     - {r}")

    lines.append("")
    lines.append("📊 快速对比表")
    lines.append("-" * 50)
    for row in result.get("quick_compare", []):
        lines.append(
            f"  {row['产品']} | 比例:{row['融资比例']} | "
            f"利率:{row['利率参考']} | 周期:{row['办理周期']}"
        )
    lines.append("=" * 60)
    return "\n".join(lines)


def cmd_generate(args: list[str]):
    """generate 命令"""
    text = " ".join(args)
    if not text:
        print("⚠️  请提供参数，如：贸易融资 出口企业 金额100万美元 账期90天")
        return

    engine = TradeFinanceEngine()
    params = parse_cli_input(text)

    if not params["company_type"]:
        params["company_type"] = "出口企业"
    if not params["amount_usd"]:
        params["amount_usd"] = 100_000
    if not params["payment_terms_days"]:
        params["payment_terms_days"] = 90

    result = engine.recommend(
        company_type=params["company_type"],
        amount_usd=params["amount_usd"],
        payment_terms_days=params["payment_terms_days"],
        scenarios=params["scenarios"],
    )
    print(format_recommendation(result))


def cmd_compare(args: list[str]):
    """compare 命令"""
    keys = args if args else ["LC", "FACTORING", "FORFAITING"]
    engine = TradeFinanceEngine()
    result = engine.compare_products(keys)
    if "error" in result:
        print(f"⚠️  {result['error']}")
        return
    print(format_compare(result))


def cmd_all(args: list[str]):
    """all 命令：展示所有产品"""
    engine = TradeFinanceEngine()
    result = engine.recommend(
        company_type="出口企业",
        amount_usd=100_000,
        payment_terms_days=90,
        top_k=8,
    )
    print(format_recommendation(result))


def cmd_wecom(args: list[str]):
    """wecom 命令：生成企微卡片"""
    from wecom_integration import generate_trade_finance_card

    text = " ".join(args)
    params = parse_cli_input(text)

    engine = TradeFinanceEngine()
    result = engine.recommend(
        company_type=params["company_type"] or "出口企业",
        amount_usd=params["amount_usd"] or 100_000,
        payment_terms_days=params["payment_terms_days"] or 90,
        top_k=3,
    )

    card = generate_trade_finance_card(result)
    print("📤 企微卡片 JSON（可复制到企微消息卡片模板）：")
    print(json.dumps(card, ensure_ascii=False, indent=2))


USAGE = """
╔══════════════════════════════════════════════════════════╗
║           Trade Finance CLI - 贸易融资工具              ║
╠══════════════════════════════════════════════════════════╣
║  generate <描述>  -  推荐融资方案                        ║
║  compare <产品1> <产品2> ...  -  对比指定产品           ║
║  all              -  查看所有产品                       ║
║  wecom <描述>     -  生成企微卡片                       ║
╚══════════════════════════════════════════════════════════╝

示例：
  python3 scripts/trade_cli.py generate "贸易融资 出口企业 金额100万美元 账期90天"
  python3 scripts/trade_cli.py compare LC FACTORING FORFAITING
  python3 scripts/trade_cli.py all
  python3 scripts/trade_cli.py wecom "出口企业 金额50万美元 账期60天"
"""


def main():
    if len(sys.argv) < 2:
        print(USAGE)
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd == "generate":
        cmd_generate(args)
    elif cmd == "compare":
        cmd_compare(args)
    elif cmd == "all":
        cmd_all(args)
    elif cmd == "wecom":
        cmd_wecom(args)
    else:
        print(f"⚠️  未知命令：{cmd}")
        print(USAGE)


if __name__ == "__main__":
    main()
