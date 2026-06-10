#!/usr/bin/env python3
"""
期权策略 CLI 入口

用法:
    python3 options_cli.py generate "期权策略 买入认购 标的50元 行权价52元 权利金2元 剩余30天"
    python3 options_cli.py greeks 买入认沽 --spot 50 --strike 52 --premium 2 --days 30 --vol 25
"""

import argparse
import json
import sys
import os

# 将父目录加入路径以便导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from options_engine import OptionsStrategyEngine

def cmd_generate(args_raw: str) -> None:
    """从自然语言生成分析"""
    engine = OptionsStrategyEngine()
    params = engine.parse_cli_input(args_raw)

    missing = []
    if not params["strategy"]:
        missing.append("strategy (策略类型)")
    if not params["spot"]:
        missing.append("spot (标的价格)")
    if not params["strike"]:
        missing.append("strike (行权价)")
    if not params["premium"]:
        missing.append("premium (权利金)")

    if missing:
        print(f"⚠️  参数缺失: {', '.join(missing)}")
        print(f"   解析结果: {json.dumps(params, ensure_ascii=False, indent=2)}")
        sys.exit(1)

    result = engine.analyze(
        strategy_type=params["strategy"],
        spot_price=params["spot"],
        strike_price=params["strike"],
        premium=params["premium"],
        days_to_expiry=params["days"],
        volatility=params["vol"],
    )
    print(engine.format_report(result))

def cmd_greeks(args) -> None:
    """直接指定参数计算"""
    engine = OptionsStrategyEngine()

    # 处理波动率
    vol = args.vol
    if vol > 1:
        vol = vol / 100  # 转为小数

    result = engine.analyze(
        strategy_type=args.strategy,
        spot_price=args.spot,
        strike_price=args.strike,
        premium=args.premium,
        days_to_expiry=args.days,
        volatility=vol,
        risk_free_rate=args.rate or 0.025,
    )
    print(engine.format_report(result))

def main():
    parser = argparse.ArgumentParser(
        description="期权策略分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 自然语言生成
  python3 options_cli.py generate "期权策略 买入认购 标的50元 行权价52元 权利金2元 剩余30天"

  # 直接指定参数
  python3 options_cli.py greeks 买入认购 --spot 50 --strike 52 --premium 2 --days 30 --vol 25
        """
    )
    subparsers = parser.add_subparsers(dest="cmd", help="子命令")

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="从自然语言生成分析")
    gen_parser.add_argument("text", nargs="*", help="自然语言描述")
    gen_parser.set_defaults(func=lambda args: cmd_generate(" ".join(args.text)))

    # greeks 子命令
    grk_parser = subparsers.add_parser("greeks", help="直接计算希腊值和情景")
    grk_parser.add_argument("strategy", help="策略类型")
    grk_parser.add_argument("--spot", type=float, required=True, help="标的价格")
    grk_parser.add_argument("--strike", type=float, required=True, help="行权价")
    grk_parser.add_argument("--premium", type=float, required=True, help="权利金")
    grk_parser.add_argument("--days", type=int, default=30, help="剩余天数（默认30）")
    grk_parser.add_argument("--vol", type=float, default=25, help="波动率%%（默认25）")
    grk_parser.add_argument("--rate", type=float, default=0.025, help="无风险利率（默认2.5%%）")
    grk_parser.set_defaults(func=cmd_greeks)

    args = parser.parse_args()

    if args.cmd is None:
        # 兼容无子命令模式：把所有 args 当作 generate 的 text
        if args.text:
            cmd_generate(" ".join(args.text))
        else:
            parser.print_help()
        return

    args.func(args)

if __name__ == "__main__":
    main()
