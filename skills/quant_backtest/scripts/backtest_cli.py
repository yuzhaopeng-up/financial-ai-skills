#!/usr/bin/env python3
"""
量化回测CLI - scripts/backtest_cli.py

用法:
    python3 scripts/backtest_cli.py generate "均线交叉 20日60日 上证指数 2024年"
    python3 scripts/backtest_cli.py report --format=json
    python3 scripts/backtest_cli.py report --format=text
"""

import sys
import os
import json
import argparse
from pathlib import Path

# 将父目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtest_engine import (
    BacktestEngine,
    parse_strategy_from_text,
    parse_date_range,
    parse_symbol,
)


def cmd_generate(args):
    """从自然语言描述生成回测报告"""
    text = args.text or "均线交叉 20日60日 上证指数 2024年"

    strategy, fast, slow = parse_strategy_from_text(text)
    start_date, end_date = parse_date_range(text)
    symbol = parse_symbol(text)

    print(f"[quant_backtest] 解析参数:")
    print(f"  策略: {strategy} | 标的: {symbol}")
    print(f"  周期: {fast}/{slow}")
    print(f"  区间: {start_date} → {end_date}")
    print()

    engine = BacktestEngine(
        strategy=strategy,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        fast_period=fast,
        slow_period=slow,
        initial_capital=args.capital or 1_000_000,
    )

    if args.format == "json":
        report = engine.run()
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(engine.summary())

    return 0


def cmd_report(args):
    """格式化输出已有报告"""
    if args.format == "json":
        print(json.dumps({"status": "ok", "message": "Use 'generate' subcommand for full report"}, ensure_ascii=False, indent=2))
    else:
        print("Use: python3 scripts/backtest_cli.py generate <策略描述>")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="quant_backtest CLI - 量化回测命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="从策略描述生成回测报告")
    gen_parser.add_argument("text", nargs="?", default="均线交叉 20日60日 上证指数 2024年", help="策略描述")
    gen_parser.add_argument("--capital", type=float, default=1_000_000, help="初始资金")
    gen_parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")
    gen_parser.set_defaults(func=cmd_generate)

    # report 子命令
    rep_parser = subparsers.add_parser("report", help="格式化报告输出")
    rep_parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")
    rep_parser.set_defaults(func=cmd_report)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
