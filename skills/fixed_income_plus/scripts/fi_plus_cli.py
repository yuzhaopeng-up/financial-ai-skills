#!/usr/bin/env python3
"""
固收+策略 CLI 入口

用法:
    python3 scripts/fi_plus_cli.py generate "固收加分析 债券组合1亿 久期3.5 信用AA 目标收益4.5%"
    python3 scripts/fi_plus_cli.py generate --format json "固收加分析 债券组合1亿 久期3.5 信用AA 目标收益4.5%"
    python3 scripts/fi_plus_cli.py wecom "债券组合1亿 久期3.5 信用AA 目标收益4.5%"
"""

import argparse
import json
import re
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fi_plus_engine import FixedIncomePlusEngine


def parse_input(text: str) -> dict:
    """
    解析输入文本，提取组合规模、久期、信用评级、目标收益

    支持格式:
    - "固收加分析 债券组合1亿 久期3.5 信用AA 目标收益4.5%"
    - "债券组合1亿 久期3.5 信用AA 目标收益4.5"
    - "1亿 3.5 AA 4.5"
    """
    text = text.strip()

    # 提取金额（亿元或万元）
    amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(亿|万)', text)
    if amount_match:
        amount_val = float(amount_match.group(1))
        amount_unit = amount_match.group(2)
        portfolio_amount = amount_val * 10000 if amount_unit == "亿" else amount_val
    else:
        # 默认 1 亿
        portfolio_amount = 10000

    # 提取久期
    duration_match = re.search(r'久期\s*(\d+(?:\.\d+)?)', text)
    duration = float(duration_match.group(1)) if duration_match else 3.5

    # 提取信用评级
    rating_match = re.search(r'信用\s*(AAA|AA\+|AA|AA-|A\+|A|A-|BBB\+|BBB)', text)
    rating = rating_match.group(1) if rating_match else "AA"

    # 提取目标收益
    target_match = re.search(r'目标收益\s*(\d+(?:\.\d+))%?', text)
    target_return = float(target_match.group(1)) if target_match else 4.5

    return {
        "portfolio_amount": portfolio_amount,
        "duration": duration,
        "rating": rating,
        "target_return": target_return,
    }


def generate_report(params: dict, output_format: str = "markdown") -> str:
    """生成分析报告"""
    engine = FixedIncomePlusEngine()
    report = engine.analyze(
        portfolio_amount=params["portfolio_amount"],
        duration=params["duration"],
        rating=params["rating"],
        target_return=params["target_return"],
    )

    if output_format == "json":
        return engine.to_json(report)
    else:
        return engine.to_markdown(report)


def cmd_generate(args):
    """generate 命令"""
    params = parse_input(args.text)
    print(f"[参数] 组合规模: {params['portfolio_amount']:.0f}万元, "
          f"久期: {params['duration']}年, "
          f"评级: {params['rating']}, "
          f"目标收益: {params['target_return']}%", file=sys.stderr)

    report = generate_report(params, args.format)
    print(report)
    return 0


def cmd_wecom(args):
    """wecom 命令：生成企微卡片"""
    try:
        from wecom_integration import generate_wecom_card
    except ImportError:
        print("Error: wecom_integration module not found", file=sys.stderr)
        return 1

    params = parse_input(args.text)
    engine = FixedIncomePlusEngine()
    report = engine.analyze(
        portfolio_amount=params["portfolio_amount"],
        duration=params["duration"],
        rating=params["rating"],
        target_return=params["target_return"],
    )

    card = generate_wecom_card(report)
    print(json.dumps(card, ensure_ascii=False, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="固收+策略分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 scripts/fi_plus_cli.py generate "固收加分析 债券组合1亿 久期3.5 信用AA 目标收益4.5%"
  python3 scripts/fi_plus_cli.py generate --format json "1亿 3.5 AA 4.5"
  python3 scripts/fi_plus_cli.py wecom "债券组合1亿 久期3.5 信用AA 目标收益4.5%"
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="生成固收+分析报告")
    gen_parser.add_argument("text", help="分析参数文本")
    gen_parser.add_argument("--format", "-f", choices=["markdown", "json"],
                           default="markdown", help="输出格式")

    # wecom 子命令
    wecom_parser = subparsers.add_parser("wecom", help="生成企微卡片")
    wecom_parser.add_argument("text", help="分析参数文本")

    args = parser.parse_args()

    if args.command == "generate":
        return cmd_generate(args)
    elif args.command == "wecom":
        return cmd_wecom(args)
    else:
        # 兼容直接传入文本作为参数
        if len(sys.argv) > 1:
            params = parse_input(sys.argv[1])
            print(f"[参数] 组合规模: {params['portfolio_amount']:.0f}万元, "
                  f"久期: {params['duration']}年, "
                  f"评级: {params['rating']}, "
                  f"目标收益: {params['target_return']}%", file=sys.stderr)
            report = generate_report(params, "markdown")
            print(report)
            return 0

        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
