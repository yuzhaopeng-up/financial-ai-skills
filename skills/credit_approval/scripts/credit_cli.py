#!/usr/bin/env python3
"""
credit_cli.py - 信用审批 CLI 入口
用法：
    python3 credit_cli.py generate "信用审批 某制造企业 年营收5000万 负债率60% 利润率8%"
    python3 credit_cli.py evaluate --revenue 5000 --debt 60 --profit 8 --years 5 --industry 制造业
    python3 credit_cli.py markdown "信用审批 某制造企业 年营收5000万 负债率60% 利润率8%"
    python3 credit_cli.py json "信用审批 某制造企业 年营收5000万 负债率60% 利润率8%"
"""

import sys
import json
import argparse

# 确保可以导入 credit_approval
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from credit_engine import CreditApprovalEngine


def cmd_generate(engine: CreditApprovalEngine, args: argparse.Namespace):
    """从自然语言文本生成信用报告"""
    text = args.text
    result = engine.evaluate_from_text(text)
    output = args.output

    if output == "markdown":
        print(engine.to_markdown(result))
    elif output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认：markdown
        print(engine.to_markdown(result))


def cmd_evaluate(engine: CreditApprovalEngine, args: argparse.Namespace):
    """通过参数直接评估"""
    result = engine.evaluate(
        company_name=args.name or "待评估企业",
        annual_revenue=args.revenue,
        debt_ratio=args.debt,
        profit_margin=args.profit,
        operating_years=args.years,
        industry=args.industry,
        current_ratio=args.current_ratio,
        total_assets=args.assets,
    )
    output = args.output

    if output == "markdown":
        print(engine.to_markdown(result))
    elif output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(engine.to_markdown(result))


def cmd_json(engine: CreditApprovalEngine, args: argparse.Namespace):
    """输出 JSON 格式"""
    result = engine.evaluate_from_text(args.text)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        prog="credit_cli",
        description="信用审批 CLI - 企业/个人信用评估工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python3 credit_cli.py generate "信用审批 某制造企业 年营收5000万 负债率60% 利润率8%"
  python3 credit_cli.py evaluate --revenue 5000 --debt 60 --profit 8 --years 5 --industry 制造业
  python3 credit_cli.py markdown "信用审批 某制造企业 年营收5000万 负债率60% 利润率8%"
  python3 credit_cli.py json "信用审批 某制造企业 年营收5000万 负债率60% 利润率8%"

支持的参数：
  generate   从自然语言文本解析并评估（默认命令）
  evaluate   通过显式参数评估
  markdown   输出 Markdown 格式报告
  json       输出 JSON 格式结果
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="从自然语言文本生成报告")
    gen_parser.add_argument("text", type=str, help="自然语言描述")
    gen_parser.add_argument(
        "--output", "-o", choices=["markdown", "json"], default="markdown",
        help="输出格式（默认markdown）"
    )

    # evaluate 子命令
    eval_parser = subparsers.add_parser("evaluate", help="通过参数直接评估")
    eval_parser.add_argument("--name", "-n", type=str, default="待评估企业", help="企业名称")
    eval_parser.add_argument("--revenue", "-r", type=float, required=True, help="年营收（万元）")
    eval_parser.add_argument("--debt", "-d", type=float, required=True, help="负债率（%）")
    eval_parser.add_argument("--profit", "-p", type=float, required=True, help="利润率（%）")
    eval_parser.add_argument("--years", "-y", type=float, default=5, help="经营年限（年）")
    eval_parser.add_argument("--industry", "-i", type=str, default="制造业", help="行业类型")
    eval_parser.add_argument("--current-ratio", "-c", type=float, default=None, help="流动比率")
    eval_parser.add_argument("--assets", "-a", type=float, default=None, help="资产总额（万元）")
    eval_parser.add_argument(
        "--output", "-o", choices=["markdown", "json"], default="markdown",
        help="输出格式（默认markdown）"
    )

    # markdown 子命令
    md_parser = subparsers.add_parser("markdown", help="输出 Markdown 格式")
    md_parser.add_argument("text", type=str, help="自然语言描述")

    # json 子命令
    json_parser = subparsers.add_parser("json", help="输出 JSON 格式")
    json_parser.add_argument("text", type=str, help="自然语言描述")

    args = parser.parse_args()
    engine = CreditApprovalEngine()

    # 默认命令
    if args.command is None:
        # 尝试作为 generate 处理（兼容无子命令的调用方式）
        if len(sys.argv) > 1:
            text = " ".join(sys.argv[1:])
            result = engine.evaluate_from_text(text)
            print(engine.to_markdown(result))
        else:
            parser.print_help()
        return

    if args.command == "generate":
        cmd_generate(engine, args)
    elif args.command == "evaluate":
        cmd_evaluate(engine, args)
    elif args.command == "markdown":
        result = engine.evaluate_from_text(args.text)
        print(engine.to_markdown(result))
    elif args.command == "json":
        cmd_json(engine, args)


if __name__ == "__main__":
    main()
