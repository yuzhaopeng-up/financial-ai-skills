#!/usr/bin/env python3
"""
大宗交易分析 CLI

用法:
    python3 scripts/block_cli.py generate "大宗交易 某股票 500万股 价格10元 大股东转让"
    python3 scripts/block_cli.py generate "大宗交易 贵州茅台 100万股 价格1600元 机构转让"
    python3 scripts/block_cli.py --json generate "大宗交易 宁德时代 200万股 价格380元 私募接盘"
    python3 scripts/block_cli.py cases --buyer=大股东
    python3 scripts/block_cli.py cases --discount=10-20
    python3 scripts/block_cli.py cases --sector=金融
"""

import argparse
import json
import sys
import os
import re
import math

# Add parent dir to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from block_engine import BlockTradeEngine, HISTORICAL_CASES


def cmd_generate(args: list, as_json: bool = False):
    """生成大宗交易分析报告"""
    text = " ".join(args) if args else ""
    if not text:
        print("❌ 请提供大宗交易描述，例如：大宗交易 某股票 500万股 价格10元 大股东转让")
        sys.exit(1)

    engine = BlockTradeEngine()
    params = engine.parse_command(text)

    # 检查关键参数
    if params["price"] is None:
        print("❌ 未能从描述中解析出价格，请使用'价格XX元'格式，例如：大宗交易 某股票 500万股 价格10元")
        sys.exit(1)

    result = engine.analyze(
        stock_name=params["stock_name"],
        quantity=params["quantity"],
        price=params["price"],
        buyer_type=params["buyer_type"],
        closing_price=params["closing_price"],
    )

    if as_json:
        output = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        print(output)
    else:
        print(result.summary())
        print("")
        # 打印合规要点
        alerts = result.compliance_alerts
        print(f"【合规要点摘要】")
        severe = [a for a in alerts if a["level"] == "🔴 严重"]
        if severe:
            print("  🔴 严重风险：")
            for a in severe:
                print(f"    - {a['rule']}：{a['description']}")
        warnings = [a for a in alerts if a["level"] == "⚠️ 警告"]
        if warnings:
            print("  ⚠️ 需关注：")
            for a in warnings:
                print(f"    - {a['rule']}：{a['description']}")
        normal = [a for a in alerts if a["level"] == "✅ 正常"]
        if normal:
            print("  ✅ 合规项：")
            for a in normal:
                print(f"    - {a['rule']}：{a['description']}")

        print("")
        print(f"【锁定期提示】{result.lockup_warning[:60]}...")


def cmd_cases(args: argparse.Namespace):
    """查询历史案例"""
    buyer = getattr(args, "buyer", None)
    discount_range = getattr(args, "discount", None)
    sector = getattr(args, "sector", None)

    filtered = HISTORICAL_CASES

    # 按买方类型过滤
    if buyer:
        buyer_keywords = BUYER_TYPE_KEYWORDS.get(buyer, [buyer])
        filtered = [c for c in filtered if c["buyer_type"] in buyer_keywords or buyer in c["buyer_type"]]

    # 按折扣率范围过滤
    if discount_range:
        try:
            if "-" in discount_range:
                low, high = discount_range.split("-")
                low_rate = float(low) / 100
                high_rate = float(high) / 100
            elif discount_range.endswith("%"):
                rate = float(discount_range[:-1]) / 100
                low_rate = high_rate = rate
            else:
                rate = float(discount_range) / 100
                low_rate = high_rate = rate
            filtered = [c for c in filtered if low_rate <= c["discount_rate"] <= high_rate]
        except ValueError:
            print(f"❌ 折扣率格式有误，请使用如 10-20 或 15% 或 10")
            return

    # 按行业过滤
    if sector:
        filtered = [c for c in filtered if sector in c.get("sector", "")]

    print(f"📋 历史大宗交易案例（共{len(filtered)}条）")
    print(f"{'股票':<12} {'买方类型':<8} {'数量':>10} {'价格':>8} {'折扣率':>8} {'年份':>6} {'行业':<8} 备注")
    print("-" * 90)
    for c in filtered:
        print(
            f"{c['stock']:<12} {c['buyer_type']:<8} "
            f"{c['quantity']:>10,} {c['price']:>8.2f} "
            f"{c['discount_rate']*100:>7.1f}% {c['year']:>6} "
            f"{c['sector']:<8} {c['note'][:20]}"
        )


# 买方类型关键词映射（复用于cases命令）
BUYER_TYPE_KEYWORDS = {
    "大股东": ["大股东"],
    "机构": ["机构"],
    "私募": ["私募"],
}


def main():
    parser = argparse.ArgumentParser(description="大宗交易分析 CLI")
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出JSON格式",
    )

    sub = parser.add_subparsers(dest="cmd")

    # generate 子命令
    gen = sub.add_parser("generate", help="生成大宗交易分析报告")
    gen.add_argument("text", nargs="*", help="大宗交易描述")

    # cases 子命令
    cases = sub.add_parser("cases", help="查询历史大宗交易案例")
    cases.add_argument("--buyer", dest="buyer", help="买方类型：大股东/机构/私募")
    cases.add_argument("--discount", dest="discount", help="折扣率范围，如 10-20 或 15%")
    cases.add_argument("--sector", dest="sector", help="行业，如 金融/科技/新能源")

    args = parser.parse_args()

    if args.cmd == "generate":
        cmd_generate(args.text, as_json=args.json)
    elif args.cmd == "cases":
        cmd_cases(args)
    else:
        # 默认行为：直接读取命令行剩余文本
        remaining = sys.argv[1:] if len(sys.argv) > 1 else []
        json_mode = False
        if "--json" in remaining:
            json_mode = True
            remaining = [r for r in remaining if r != "--json"]
        if remaining:
            cmd_generate(remaining, as_json=json_mode)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
