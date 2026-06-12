#!/usr/bin/env python3
"""
企业对公开户 CLI 入口
用法: python3 scripts/account_cli.py generate "对公开户 科技公司 注册资本500万"
"""

import sys
import os
import json
import argparse

# 添加父目录到路径，以便导入 corp_account_opening
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from account_engine import CorpAccountEngine, generate_account_opening_report


def cmd_generate(args):
    """生成开户报告"""
    engine = CorpAccountEngine()

    if args.format == "json":
        result = engine.generate(args.query, args.account_type, format="json")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        result = engine.generate(args.query, args.account_type, format="text")
        print(result)

    return 0


def cmd_list_types(args):
    """列出支持的企业类型"""
    engine = CorpAccountEngine()
    types = engine.ENTERPRISE_TYPES
    print("支持的企业类型：")
    for name, code in types.items():
        print(f"  - {name} ({code})")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="企业对公开户智能指引工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python3 scripts/account_cli.py generate "对公开户 科技公司 注册资本500万"
  python3 scripts/account_cli.py generate "对公开户 外资企业 注册资本1000万" --format json
  python3 scripts/account_cli.py generate "对公开户 股份有限公司" --account-type 一般户
  python3 scripts/account_cli.py list-types
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成开户报告")
    gen_parser.add_argument("query", help="查询内容，如'对公开户 科技公司 注册资本500万'")
    gen_parser.add_argument("--account-type", "-t", default="基本户",
                           choices=["基本户", "一般户"],
                           help="开户类型（默认：基本户）")
    gen_parser.add_argument("--format", "-f", default="text",
                           choices=["text", "json"],
                           help="输出格式（默认：text）")

    # list-types 命令
    subparsers.add_parser("list-types", help="列出支持的企业类型")

    args = parser.parse_args()

    if args.command == "generate":
        return cmd_generate(args)
    elif args.command == "list-types":
        return cmd_list_types(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
