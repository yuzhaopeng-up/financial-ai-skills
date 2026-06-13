#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
催收策略优化 - CLI命令行工具

用法:
    python collection_optimize_cli.py --days 45 --amount 58000 --name 张三
    python collection_optimize_cli.py --interactive
    python collection_optimize_cli.py --json --days 10 --amount 5000

Author: ArkClaw
Version: 1.0.0
"""

import argparse
import json
import sys
import os

# 添加父目录到路径以便导入引擎
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collection_optimize_engine import CollectionOptimizeEngine


def parse_args():
    parser = argparse.ArgumentParser(
        description="催收策略优化引擎 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python collection_optimize_cli.py --days 45 --amount 58000 --name 张三
  python collection_optimize_cli.py -d 10 -a 5000 -n 李四 --format json
  python collection_optimize_cli.py --interactive
        """
    )

    parser.add_argument("-d", "--days", type=int, default=None,
                        help="逾期天数")
    parser.add_argument("-a", "--amount", type=float, default=None,
                        help="逾期金额（元）")
    parser.add_argument("-n", "--name", type=str, default="客户",
                        help="客户姓名")
    parser.add_argument("-p", "--phone", type=str, default="",
                        help="联系电话")
    parser.add_argument("-t", "--product", type=str, default="贷款",
                        help="产品类型（贷款/信用卡/消费贷）")
    parser.add_argument("-c", "--company", type=str, default="",
                        help="所属公司")
    parser.add_argument("-f", "--format", type=str, choices=["text", "json"], default="text",
                        help="输出格式（text/json）")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="交互式输入模式")
    parser.add_argument("--history", type=str, default="",
                        help="历史记录JSON文件路径")

    return parser.parse_args()


def interactive_input():
    """交互式输入模式"""
    print("=" * 50)
    print("🦞 催收策略优化 - 交互式输入")
    print("=" * 50)
    print()

    customer = {}
    customer["customer_name"] = input("客户姓名: ").strip() or "客户"
    customer["phone"] = input("联系电话: ").strip()
    customer["product_type"] = input("产品类型（贷款/信用卡/消费贷）: ").strip() or "贷款"
    customer["company"] = input("所属公司: ").strip()

    try:
        customer["overdue_days"] = int(input("逾期天数: ").strip())
        customer["overdue_amount"] = float(input("逾期金额（元）: ").strip())
    except ValueError:
        print("❌ 输入格式错误！")
        sys.exit(1)

    history = []
    add_history = input("\n是否添加历史催收记录？(y/n): ").strip().lower()
    if add_history == "y":
        print("\n添加历史记录（输入空行结束）:")
        while True:
            content = input("催收内容: ").strip()
            if not content:
                break
            responded = input("是否联系上？(y/n): ").strip().lower() == "y"
            repaid = input("是否还款？(y/n): ").strip().lower() == "y"
            history.append({
                "date": "",
                "channel": "",
                "content": content,
                "responded": responded,
                "repaid": repaid,
            })

    return customer, history


def main():
    args = parse_args()
    engine = CollectionOptimizeEngine(api_mode=False)

    if args.interactive:
        customer_info, history_records = interactive_input()
    else:
        if args.days is None or args.amount is None:
            print("❌ 错误：缺少必要参数。请使用 --days 和 --amount")
            print("   或使用 --interactive 进入交互模式")
            sys.exit(1)

        customer_info = {
            "customer_name": args.name,
            "phone": args.phone,
            "product_type": args.product,
            "company": args.company,
            "overdue_days": args.days,
            "overdue_amount": args.amount,
        }

        history_records = []
        if args.history and os.path.exists(args.history):
            try:
                with open(args.history, "r", encoding="utf-8") as f:
                    history_records = json.load(f)
            except Exception as e:
                print(f"⚠️ 读取历史记录失败: {e}")

    print()
    print("📋 正在生成催收策略...")
    print()

    result = engine.generate_strategy(customer_info, history_records)

    if args.format == "json":
        print(engine.format_json(result))
    else:
        print(engine.format_text(result))

    # 返回退出码
    if not result["recovery_rate_estimate"]["meets_acceptance"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
