#!/usr/bin/env python3
"""
AML Rating CLI — 反洗钱客户评级命令行工具

用法:
    python3 aml_cli.py generate "AML评级 某客户 贸易行业 受益人信息完整"
    python3 aml_cli.py generate --name "测试客户" --industry "贸易" --region "中国" --features "跨境,大额" --beneficial-owner
    python3 aml_cli.py parse "客户XXX 行业:金融 地区:香港"
    python3 aml_cli.py batch <file.csv>
"""

import argparse
import json
import sys
import os

# 添加父目录到路径以支持导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aml_engine import AMLRatingEngine


def cmd_generate(args):
    """执行评级生成"""
    engine = AMLRatingEngine()

    # 如果传入的是完整文本，用文本解析
    if args.text:
        text_input = " ".join(args.text)
        result = engine.rate_from_text(text_input)
    else:
        # 使用显式参数
        features = []
        if args.features:
            features = [f.strip() for f in args.features.split(",")]

        customer_features = []
        if args.beneficial_owner:
            customer_features.append("受益人信息完整")

        result = engine.rate(
            customer_name=args.name or "未知客户",
            industry=args.industry or "",
            region=args.region or "",
            transaction_features=features,
            id_validity_days=args.id_validity_days,
            has_beneficial_owner=args.beneficial_owner,
            customer_features=customer_features
        )

    # 输出
    if args.format == "json":
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(engine.pretty_print(result))

    return 0


def cmd_parse(args):
    """解析文本中的客户信息"""
    engine = AMLRatingEngine()
    result = engine.rate_from_text(args.text)

    if args.format == "json":
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(engine.pretty_print(result))

    return 0


def cmd_batch(args):
    """批量处理CSV文件"""
    import csv

    engine = AMLRatingEngine()
    input_file = args.file

    if not os.path.exists(input_file):
        print(f"错误: 文件不存在: {input_file}", file=sys.stderr)
        return 1

    results = []
    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            features = row.get("transaction_features", "").split("|") if row.get("transaction_features") else []
            features = [f.strip() for f in features if f.strip()]

            result = engine.rate(
                customer_name=row.get("customer_name", "未知"),
                industry=row.get("industry", ""),
                region=row.get("region", ""),
                transaction_features=features,
                id_validity_days=int(row["id_validity_days"]) if row.get("id_validity_days") else None,
                has_beneficial_owner=row.get("has_beneficial_owner", "").lower() in ("true", "1", "yes"),
            )
            results.append(result.to_dict())

    # 输出结果
    output_file = args.output
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"结果已保存至: {output_file}")
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="AML Rating CLI — 反洗钱客户评级工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成AML评级")
    gen_parser.add_argument("text", nargs="*", type=str, default=None,
                             help="完整文本，例: AML评级 某客户 贸易行业 受益人信息完整")
    gen_parser.add_argument("--name", "-n", type=str, default="未知客户", help="客户名称")
    gen_parser.add_argument("--industry", "-i", type=str, default="", help="行业类型")
    gen_parser.add_argument("--region", "-r", type=str, default="", help="地区/国家")
    gen_parser.add_argument("--features", "-f", type=str,
                             help="交易特征，逗号分隔，如: 跨境,大额,现金")
    gen_parser.add_argument("--id-validity-days", type=int, default=None,
                             help="证件有效期（天）")
    gen_parser.add_argument("--beneficial-owner", action="store_true",
                             help="是否有明确受益人")
    gen_parser.add_argument("--format", choices=["text", "json"], default="text",
                             help="输出格式")
    gen_parser.set_defaults(func=cmd_generate)

    # parse 命令
    parse_parser = subparsers.add_parser("parse", help="从文本解析客户信息并评级")
    parse_parser.add_argument("text", type=str, help="要解析的文本")
    parse_parser.add_argument("--format", choices=["text", "json"], default="text",
                              help="输出格式")
    parse_parser.set_defaults(func=cmd_parse)

    # batch 命令
    batch_parser = subparsers.add_parser("batch", help="批量处理CSV文件")
    batch_parser.add_argument("file", type=str, help="CSV文件路径")
    batch_parser.add_argument("--output", "-o", type=str, default="",
                              help="输出JSON文件路径")
    batch_parser.set_defaults(func=cmd_batch)

    args = parser.parse_args()

    if not args.command:
        # 无子命令时，尝试直接解析第一个参数作为文本
        if len(sys.argv) > 1:
            text = " ".join(sys.argv[1:])
            engine = AMLRatingEngine()
            result = engine.rate_from_text(text)
            print(engine.pretty_print(result))
            return 0
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
