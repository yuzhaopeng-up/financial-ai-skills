#!/usr/bin/env python3
"""
定投计算器 CLI

用法:
    python3 scripts/dca_cli.py generate "定投计算 沪深300 每月1000元 3年"
    python3 scripts/dca_cli.py generate "定投 创业板指 每周500 5年"
    python3 scripts/dca_cli.py list
"""

import argparse
import json
import sys
import os

# Add parent dir to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dca_engine import DCACalculatorEngine, BUILTIN_FUNDS


def cmd_generate(args: list):
    """生成定投计算报告"""
    text = " ".join(args) if args else ""
    if not text:
        print("❌ 请提供定投计算描述，例如：定投计算 沪深300 每月1000元 3年")
        sys.exit(1)

    engine = DCACalculatorEngine()
    params = engine.parse_command(text)

    result = engine.calculate(
        fund_name=params["fund_name"],
        amount=params["amount"],
        frequency=params["frequency"],
        years=params["years"],
    )

    if args and "--json" in args:
        output = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        print(output)
    else:
        print(result.summary())
        print(result.scenario_summary())
        print("")
        # 显示前几期和后几期记录
        records = result.monthly_records
        if records:
            print(f"【定投明细（前{min(6, len(records))}期）】")
            print(f"{'月份':>4} {'月投入':>10} {'净值':>8} {'购入份额':>10} {'累计份额':>12} {'累计投入':>12} {'账户价值':>12}")
            for r in records[:6]:
                print(
                    f"{r['month']:>4} {r['invested']:>10.2f} {r['nav']:>8.4f} "
                    f"{r['shares']:>10.4f} {r['total_shares']:>12.4f} "
                    f"{r['cumulative_invested']:>12.2f} {r['account_value']:>12.2f}"
                )
            if len(records) > 12:
                print(f"... 共 {len(records)} 期 ...")
                print(f"{'月份':>4} {'月投入':>10} {'净值':>8} {'购入份额':>10} {'累计份额':>12} {'累计投入':>12} {'账户价值':>12}")
                for r in records[-6:]:
                    print(
                        f"{r['month']:>4} {r['invested']:>10.2f} {r['nav']:>8.4f} "
                        f"{r['shares']:>10.4f} {r['total_shares']:>12.4f} "
                        f"{r['cumulative_invested']:>12.2f} {r['account_value']:>12.2f}"
                    )


def cmd_list(_args=None):
    """列出支持的指数基金"""
    print("📈 支持的指数基金：")
    print(f"{'基金名称':<15} {'基金代码':<15} {'类型':<15}")
    print("-" * 50)
    for name, fund in sorted(BUILTIN_FUNDS.items()):
        print(f"{name:<15} {fund['code']:<15} {fund['type']:<15}")


def main():
    parser = argparse.ArgumentParser(description="定投计算器 CLI")
    sub = parser.add_subparsers(dest="cmd")

    gen = sub.add_parser("generate", help="生成定投计算报告")
    gen.add_argument("text", nargs="*", help="定投描述，如：定投计算 沪深300 每月1000元 3年")

    sub.add_parser("list", help="列出支持的指数基金")

    args = parser.parse_args()

    if args.cmd == "generate":
        cmd_generate(args.text)
    elif args.cmd == "list":
        cmd_list([])
    else:
        # 默认行为：直接读取命令行剩余文本
        remaining = sys.argv[2:] if len(sys.argv) > 2 else []
        if remaining:
            cmd_generate(remaining)
        else:
            cmd_list([])


if __name__ == "__main__":
    main()
