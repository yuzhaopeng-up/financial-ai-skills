#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信用卡逾期催收CLI入口

用法:
    python3 scripts/collection_cli.py generate "催收 客户逾期30天 欠款5万 首次逾期 联系方式有效"
    python3 scripts/collection_cli.py parse "催收 客户逾期30天 欠款5万"
    python3 scripts/collection_cli.py interactive
"""

import sys
import json
import argparse
from pathlib import Path

# 添加父目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from collection_engine import CreditCollectionEngine


def cmd_generate(args):
    """生成催收方案"""
    engine = CreditCollectionEngine()

    # 解析输入文本
    params = engine.parse_input(args.text)

    # 生成催收方案
    result = engine.generate_collection_plan(**params)

    # 输出结果
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_pretty(result)


def cmd_parse(args):
    """解析输入文本"""
    engine = CreditCollectionEngine()
    params = engine.parse_input(args.text)

    if args.format == "json":
        print(json.dumps(params, ensure_ascii=False, indent=2))
    else:
        print("解析结果:")
        for key, value in params.items():
            print(f"  {key}: {value}")


def cmd_interactive(args):
    """交互式模式"""
    engine = CreditCollectionEngine()

    print("=" * 60)
    print("信用卡逾期催收 - 交互式模式")
    print("输入 'quit' 或 'exit' 退出")
    print("=" * 60)

    while True:
        try:
            text = input("\n请输入催收描述: ").strip()

            if text.lower() in ["quit", "exit", "q"]:
                print("退出")
                break

            if not text:
                continue

            params = engine.parse_input(text)
            result = engine.generate_collection_plan(**params)

            print("\n" + "-" * 60)
            print_pretty(result)

        except KeyboardInterrupt:
            print("\n退出")
            break
        except Exception as e:
            print(f"错误: {e}")


def print_pretty(result: dict):
    """格式化打印结果"""
    print(f"逾期阶段: {result['stage']}")
    print(f"催收优先级: {result['priority']}")
    print(f"逾期天数: {result['overdue_days']}天")
    print(f"欠款金额: {result['outstanding_amount']:.2f}元")
    print(f"客户类型: {result['customer_type']}")
    print(f"联系方式有效: {'是' if result['contact_valid'] else '否'}")

    print("-" * 40)
    print(f"催收策略: {', '.join(result['strategies'])}")

    installment = result['installment_advice']
    print("-" * 40)
    print(f"分期建议: {installment['recommendation']}")
    print(f"建议期数: {installment['suggested_plan']}期")
    print(f"预计月还款: {installment['min_monthly_payment']:.2f}元")
    print(f"手续费率: {installment['handling_fee_rate']}")

    print("-" * 40)
    print(f"法律后果提示:\n{result['legal_warning']}")

    print("-" * 40)
    print(f"催收话术:")
    for stage_key, script in result['scripts'].items():
        print(f"  [{stage_key}] {script['channel']}: {script['template']}")

    print("-" * 40)
    if result['red_line_violations']:
        print("⚠️ 违规警告:")
        for v in result['red_line_violations']:
            print(f"  - {v}")
    else:
        print("✅ 合规检测: 通过")

    print("-" * 40)
    print(f"生成时间: {result['generated_at']}")


def main():
    parser = argparse.ArgumentParser(
        description="信用卡逾期催收CLI工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 scripts/collection_cli.py generate "催收 客户逾期30天 欠款5万 首次逾期 联系方式有效"
  python3 scripts/collection_cli.py parse "客户逾期60天 欠款10万"
  python3 scripts/collection_cli.py interactive
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="生成催收方案")
    gen_parser.add_argument("text", help="催收描述文本")
    gen_parser.add_argument("--format", "-f", choices=["text", "json"], default="text",
                           help="输出格式 (默认: text)")

    # parse 子命令
    parse_parser = subparsers.add_parser("parse", help="解析输入文本")
    parse_parser.add_argument("text", help="催收描述文本")
    parse_parser.add_argument("--format", "-f", choices=["text", "json"], default="text",
                             help="输出格式 (默认: text)")

    # interactive 子命令
    subparsers.add_parser("interactive", help="交互式模式")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "parse":
        cmd_parse(args)
    elif args.command == "interactive":
        cmd_interactive(args)
    else:
        # 默认行为：直接生成
        if len(sys.argv) > 1:
            text = " ".join(sys.argv[1:])
            engine = CreditCollectionEngine()
            params = engine.parse_input(text)
            result = engine.generate_collection_plan(**params)
            print_pretty(result)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
