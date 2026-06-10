#!/usr/bin/env python3
"""
margin_cli.py - 融资融券监控 CLI 入口

用法：
    python scripts/margin_cli.py generate "融资监控 持仓某股票100万 融资50万 成本10元 现价8元"
    python scripts/margin_cli.py analyze --total-assets 1000000 --debt 500000 --positions 某股票,100000,10,8
    python scripts/margin_cli.py wecom --positions 某股票,100000,10,8 --debt 500000
"""

import sys
import json
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from margin_engine import MarginTradingEngine
from wecom_integration import build_margin_monitor_card, build_from_engine


def cmd_generate(text: str):
    """从自然语言生成报告"""
    engine = MarginTradingEngine.from_natural_language(text)
    print(engine.format_text_report())


def cmd_analyze(total_assets: float, debt: float, positions_str: str = None,
                financing: float = 0, cash: float = 0):
    """结构化参数分析"""
    from margin_engine import Position

    positions = []
    if positions_str:
        for pos_str in positions_str.split(";"):
            parts = pos_str.split(",")
            if len(parts) == 4:
                positions.append(Position(
                    stock_name=parts[0].strip(),
                    shares=float(parts[1].strip()),
                    cost_price=float(parts[2].strip()),
                    current_price=float(parts[3].strip())
                ))

    engine = MarginTradingEngine(
        positions=positions,
        financing_balance=financing,
        cash=cash,
        short_position_value=debt - financing
    )
    print(engine.format_text_report())


def cmd_wecom(positions_str: str, debt: float, financing: float = 0):
    """生成企微卡片JSON"""
    from margin_engine import Position

    positions = []
    for pos_str in positions_str.split(";"):
        parts = pos_str.split(",")
        if len(parts) == 4:
            positions.append(Position(
                stock_name=parts[0].strip(),
                shares=float(parts[1].strip()),
                cost_price=float(parts[2].strip()),
                current_price=float(parts[3].strip())
            ))

    engine = MarginTradingEngine(
        positions=positions,
        financing_balance=financing,
        cash=0,
        short_position_value=debt - financing
    )
    report = engine.generate_report()
    card = build_from_engine(engine)
    print(json.dumps(card, ensure_ascii=False, indent=2))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="融资融券监控引擎 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python scripts/margin_cli.py generate "融资监控 持仓某股票100万 融资50万 成本10元 现价8元"
  python scripts/margin_cli.py analyze --total-assets 1000000 --debt 500000 --positions 某股票,100000,10,8
  python scripts/margin_cli.py wecom --positions 某股票,100000,10,8 --debt 500000 --financing 500000
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate
    g = subparsers.add_parser("generate", help="从自然语言生成报告")
    g.add_argument("text", help="自然语言描述")

    # analyze
    a = subparsers.add_parser("analyze", help="结构化参数分析")
    a.add_argument("--total-assets", type=float, required=True, help="总资产（元）")
    a.add_argument("--debt", type=float, required=True, help="总负债（元）")
    a.add_argument("--positions", type=str, help="持仓：名称,数量,成本,现价（多只分号隔开）")
    a.add_argument("--financing", type=float, default=0, help="融资借款金额")
    a.add_argument("--cash", type=float, default=0, help="现金余额")
    a.add_argument("--json", action="store_true", help="输出JSON格式")

    # wecom
    w = subparsers.add_parser("wecom", help="生成企微卡片JSON")
    w.add_argument("--positions", type=str, required=True, help="持仓：名称,数量,成本,现价（多只分号隔开）")
    w.add_argument("--debt", type=float, required=True, help="总负债（元）")
    w.add_argument("--financing", type=float, default=0, help="融资借款金额")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args.text)

    elif args.command == "analyze":
        cmd_analyze(
            total_assets=args.total_assets,
            debt=args.debt,
            positions_str=args.positions,
            financing=args.financing,
            cash=args.cash
        )
        if args.json:
            # 重新构造 JSON 输出
            from margin_engine import Position
            positions = []
            if args.positions:
                for pos_str in args.positions.split(";"):
                    parts = pos_str.split(",")
                    if len(parts) == 4:
                        positions.append(Position(
                            stock_name=parts[0].strip(),
                            shares=float(parts[1].strip()),
                            cost_price=float(parts[2].strip()),
                            current_price=float(parts[3].strip())
                        ))
            engine = MarginTradingEngine(
                positions=positions,
                financing_balance=args.financing,
                cash=args.cash,
                short_position_value=args.debt - args.financing
            )
            print(json.dumps(engine.generate_report(), ensure_ascii=False, indent=2))

    elif args.command == "wecom":
        cmd_wecom(args.positions, args.debt, args.financing)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
