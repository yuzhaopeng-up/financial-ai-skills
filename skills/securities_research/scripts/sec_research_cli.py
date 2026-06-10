#!/usr/bin/env python3
"""
securities_research CLI — 投研报告命令行工具

用法:
    python3 scripts/sec_research_cli.py generate "投研报告 某新能源公司 深度报告"
    python3 scripts/sec_research_cli.py generate "投研报告 某银行 行业跟踪"
    python3 scripts/sec_research_cli.py generate "投研报告 宏观 宏观策略"
    python3 scripts/sec_research_cli.py generate "投研报告 某证券公司 晨会点评" --format=json
    python3 scripts/sec_research_cli.py info
"""

import argparse
import json
import sys
import os

# Add parent dir to path for development mode
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sec_research_engine import SecuritiesResearchEngine


def cmd_info():
    print("SecuritiesResearch CLI v1.0.0")
    print()
    print("内置行业框架:", ", ".join([
        "银行", "证券", "保险", "房地产", "医药",
        "科技/半导体", "消费", "新能源", "能源/煤炭",
        "钢铁/建材", "交通运输",
    ]))
    print()
    print("报告类型: 深度报告, 行业跟踪, 宏观策略, 晨会点评")
    print()
    print("用法示例:")
    print('  python3 scripts/sec_research_cli.py generate "投研报告 某新能源公司 深度报告"')
    print('  python3 scripts/sec_research_cli.py generate "投研报告 某银行 行业跟踪"')
    print('  python3 scripts/sec_research_cli.py generate "投研报告 宏观 宏观策略" --format=json')


def cmd_generate(args):
    engine = SecuritiesResearchEngine()

    # 解析命令
    parsed = engine.parse_command(args.command)

    print(
        f"[解析结果] 公司: {parsed['company']} | "
        f"行业: {parsed['industry']} | "
        f"报告类型: {parsed['report_type']}",
        file=sys.stderr,
    )

    # 生成报告
    report = engine.generate(
        company=parsed["company"],
        industry=parsed["industry"],
        report_type=parsed["report_type"],
    )

    # 输出
    if args.format == "json":
        result = engine.format_json(report)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        md = engine.format_markdown(report)
        print(md)


def main():
    parser = argparse.ArgumentParser(
        description="securities_research CLI — 投研报告生成工具",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # info
    sub.add_parser("info", help="显示技能信息")

    # generate
    gen = sub.add_parser("generate", help="生成投研报告")
    gen.add_argument("command", help="命令字符串，如 '投研报告 某新能源公司 深度报告'")
    gen.add_argument(
        "--format", "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="输出格式（默认 markdown）",
    )

    args = parser.parse_args()

    if args.cmd == "info":
        cmd_info()
    elif args.cmd == "generate":
        cmd_generate(args)


if __name__ == "__main__":
    main()
