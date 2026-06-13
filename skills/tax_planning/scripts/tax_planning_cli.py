#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
税务筹划方案引擎 CLI
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tax_planning_engine import TaxPlanningEngine


def main():
    parser = argparse.ArgumentParser(description="税务筹划方案引擎")
    parser.add_argument("--income-type", "-t", default="工资", help="收入类型")
    parser.add_argument("--amount", "-a", type=float, default=None, help="年收入（万元）")
    parser.add_argument("--region", "-r", default="全国", help="地区")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="输出格式")
    parser.add_argument("text", nargs="*", help="输入文本（可替代参数）")

    args = parser.parse_args()

    engine = TaxPlanningEngine()

    # 优先使用位置文本参数，否则用选项参数
    if args.text:
        text = " ".join(args.text)
    else:
        amount_str = f"{args.amount}万" if args.amount else "未知"
        text = f"收入类型={args.income_type} 收入={amount_str} 地区={args.region}"

    print(f"💰 税务筹划方案引擎 v1.0")
    print(f"输入: {text}")
    print()

    result = engine.generate_tax_plan(text)

    if args.format == "json":
        print(engine.format_json(result))
    else:
        print(engine.format_text(result))


if __name__ == "__main__":
    sys.exit(main())
