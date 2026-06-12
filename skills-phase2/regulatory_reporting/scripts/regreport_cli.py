#!/usr/bin/env python3
"""
监管报送CLI - regreport_cli.py

用法:
    python3 scripts/regreport_cli.py generate "监管报送 1104 2024年Q1"
    python3 scripts/regreport_cli.py generate "报送 GL18 2024年6月"
    python3 scripts/regreport_cli.py generate "报送 GRS 2024年Q1"
    python3 scripts/regreport_cli.py list-types
    python3 scripts/regreport_cli.py generate "监管报送 1104 2024Q1" --format=json
"""

import argparse
import json
import re
import sys
import os

# 将父目录加入 path 以便直接运行脚本时能 import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reg_report_engine import RegReportingEngine


def parse_command(text: str) -> tuple[str, str]:
    """
    将自然语言命令解析为 (report_type, period)。

    示例:
        "监管报送 1104 2024年Q1"  → ("1104", "2024Q1")
        "报送 GL18 2024年6月"     → ("GL18", "2024年6月")
        "报送 GR-S 2024年Q1"      → ("GRS",  "2024Q1")
        "报送 EAST 2024年Q1"      → ("EAST", "2024Q1")
    """
    text = text.strip()

    # 去掉常见前缀
    text = re.sub(r"^(监管报送|报送|上报|提交)\s+", "", text)

    # 识别报送类型代码
    type_patterns = [
        (r"^(1104|EAST|RPBC|GRS|GR-S|WM|SPECIAL|GL18)\b", None),
        (r"^人民银行|人行\s*金融统计", "RPBC"),
        (r"^银保监|1104", "1104"),
        (r"^金融稳定|GR-?S", "GRS"),
        (r"^理财|理财登记|WM", "WM"),
        (r"^EAST4?\.?0?", "EAST"),
        (r"^GL\s*18|跨境融资|GL18", "GL18"),
        (r"^特殊|专项", "SPECIAL"),
    ]

    report_type = None
    remaining = text

    for pattern, code in type_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            report_type = code if code else m.group(1)
            remaining = text[m.end():].strip()
            break

    if not report_type:
        # 尝试提取报告类型代码
        m = re.match(r"([A-Z][A-Z0-9\-]{1,10})\b", text)
        if m:
            report_type = m.group(1).upper()
            remaining = text[m.end():].strip()
        else:
            raise ValueError(f"无法识别报送类型: {text!r}，支持的类型: 1104, EAST, RPBC/GRS/WM/SPECIAL")

    # 识别期间
    period = remaining if remaining else "2024Q1"

    return report_type, period


def cmd_generate(args: argparse.Namespace) -> None:
    """执行 generate 命令。"""
    engine = RegReportingEngine()

    # 从 args.text 解析或直接用参数
    if args.text:
        report_type, period = parse_command(args.text)
    elif args.report_type and args.period:
        report_type = args.report_type.upper()
        period = args.period
    else:
        print("错误: 请提供 --text 或 --type + --period 参数", file=sys.stderr)
        sys.exit(1)

    result = engine.generate(report_type, period, api_mode=(args.format == "json"))

    if args.format == "json":
        # 去掉打印输出，仅返回 JSON
        result_no_ts = {k: v for k, v in result.items() if k != "generated_at"}
        print(json.dumps(result_no_ts, ensure_ascii=False, indent=2))


def cmd_list_types(_args: argparse.Namespace) -> None:
    """列出所有支持的报送类型。"""
    engine = RegReportingEngine()
    types = engine.list_types()

    print("\n" + "=" * 50)
    print("  支持的报送类型")
    print("=" * 50)
    for t in types:
        print(f"  [{t['code']:<10}] {t['name']:<30} ({t['authority']})")
    print("=" * 50 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="regreport_cli",
        description="监管报送技能 CLI - 生成报送要求清单",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="生成报送要求清单")
    gen_parser.add_argument(
        "text",
        nargs="?",
        help='完整命令文本，如 "监管报送 1104 2024年Q1" 或 "报送 GL18 2024年6月"',
    )
    gen_parser.add_argument("--type", "-t", dest="report_type", help="报送类型代码，如 1104, EAST, GRS")
    gen_parser.add_argument("--period", "-p", dest="period", help="报送期间，如 2024Q1, 2024年6月")
    gen_parser.add_argument(
        "--format", "-f",
        dest="format",
        choices=["text", "json"],
        default="text",
        help="输出格式 (默认: text)",
    )
    gen_parser.set_defaults(func=cmd_generate)

    # list-types 子命令
    list_parser = subparsers.add_parser("list-types", help="列出所有支持的报送类型")
    list_parser.set_defaults(func=cmd_list_types)

    args = parser.parse_args()

    # 如果是 generate 但没有任何参数，显示帮助
    if args.command == "generate" and not args.text and not args.report_type:
        gen_parser.print_help()
        print("\n示例:")
        print('  python3 scripts/regreport_cli.py generate "监管报送 1104 2024年Q1"')
        print('  python3 scripts/regreport_cli.py generate "报送 GL18 2024年6月"')
        print('  python3 scripts/regreport_cli.py generate --type 1104 --period 2024Q1')
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
