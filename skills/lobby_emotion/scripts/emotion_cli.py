#!/usr/bin/env python3
"""
lobby_emotion CLI - 客户情绪识别命令行工具

用法:
    python3 emotion_cli.py analyze --tone 急促 --expression 皱眉 --wait 40 --complaint-history
    python3 emotion_cli.py generate "情绪识别 客户语速急促 皱眉 等待40分钟 有投诉历史"
"""

import argparse
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from emotion_engine import LobbyEmotionEngine


def cmd_analyze(args):
    """结构化参数分析"""
    engine = LobbyEmotionEngine()
    result = engine.analyze(
        tone=args.tone,
        expression=args.expression,
        body_language=args.body,
        wait_minutes=args.wait,
        has_complaint_history=args.complaint_history,
        keywords=args.keywords if args.keywords else None
    )
    output = engine.to_dict(result)
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_generate(args):
    """从自然语言生成分析结果"""
    engine = LobbyEmotionEngine()
    result = engine.analyze_from_text(args.text)
    output = engine.to_dict(result)
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        prog="emotion_cli",
        description="客户情绪识别引擎 CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # analyze 子命令
    analyze_parser = subparsers.add_parser("analyze", help="结构化参数分析")
    analyze_parser.add_argument("--tone", default="平和", help="语气特征")
    analyze_parser.add_argument("--expression", default="无表情", help="表情特征")
    analyze_parser.add_argument("--body", default="正常", help="肢体语言")
    analyze_parser.add_argument("--wait", type=int, default=0, help="等待时长(分钟)")
    analyze_parser.add_argument("--complaint-history", action="store_true", help="有投诉历史")
    analyze_parser.add_argument("--keywords", nargs="+", help="敏感关键词列表")
    analyze_parser.set_defaults(func=cmd_analyze)

    # generate 子命令
    generate_parser = subparsers.add_parser("generate", help="自然语言描述分析")
    generate_parser.add_argument("text", help="自然语言描述")
    generate_parser.set_defaults(func=cmd_generate)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
