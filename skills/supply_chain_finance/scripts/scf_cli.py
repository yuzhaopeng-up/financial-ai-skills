#!/usr/bin/env python3
"""
供应链金融 CLI 入口

用法：
    python3 scripts/scf_cli.py generate "供应链金融 汽车整车厂 应付账款10亿"
    python3 scripts/scf_cli.py generate "供应链金融 汽车整车厂 应付账款10亿" --format json
    python3 scripts/scf_cli.py --help
"""

import sys
import os
import argparse

# 确保包可导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scf_engine import SCFEngine, parse_input


def cmd_generate(args):
    """生成供应链金融方案"""
    text = " ".join(args.text)
    profile = parse_input(text)

    if args.verbose:
        print(f"[DEBUG] 解析结果：", file=sys.stderr)
        print(f"  核心企业：{profile.core_enterprise}", file=sys.stderr)
        print(f"  供应商类型：{profile.supplier_type}", file=sys.stderr)
        print(f"  应付账款：{profile.accounts_payable} 万元", file=sys.stderr)
        print(f"  账期：{profile.payment_term_days} 天", file=sys.stderr)

    engine = SCFEngine(api_mode=True)
    result = engine.generate(profile)

    if args.format == "json":
        import json
        print(json.dumps(engine.format_json(result), ensure_ascii=False, indent=2))
    elif args.format == "wecom":
        import json
        print(json.dumps(engine.format_wecom_card(result), ensure_ascii=False, indent=2))
    else:
        print(engine.format_markdown(result))


def main():
    parser = argparse.ArgumentParser(
        prog="scf_cli",
        description="供应链金融（SCF）方案生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python3 scripts/scf_cli.py generate "供应链金融 汽车整车厂 应付账款10亿"
  python3 scripts/scf_cli.py generate "汽车整车厂 应付账款5亿 账期90天" --format json
  python3 scripts/scf_cli.py generate "核心企业:某新能源汽车企业 供应商:汽车零部件 应付账款20亿" --verbose
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成 SCF 方案")
    gen_parser.add_argument(
        "text",
        nargs="*",
        help="自然语言描述，如：供应链金融 汽车整车厂 应付账款10亿",
    )
    gen_parser.add_argument(
        "--format", "-f",
        choices=["markdown", "json", "wecom"],
        default="markdown",
        help="输出格式（默认 markdown）",
    )
    gen_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示解析过程",
    )
    gen_parser.set_defaults(func=cmd_generate)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
