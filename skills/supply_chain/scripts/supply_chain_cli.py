#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
供应链金融方案引擎 CLI
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supply_chain_engine import SupplyChainFinanceEngine


def main():
    parser = argparse.ArgumentParser(description="供应链金融方案引擎 CLI")
    parser.add_argument("--core", "-c", help="核心企业名称")
    parser.add_argument("--supplier", "-s", help="供应商名称")
    parser.add_argument("--amount", "-a", type=float, help="交易规模（万元）")
    parser.add_argument("--period", "-p", type=int, help="账期（天）")
    parser.add_argument("--months", "-m", type=int, help="合作月数")
    parser.add_argument("--core-rating", "-r", help="核心企业评级（AAA/AA/A/BBB/BB/B）")
    parser.add_argument("--supplier-rating", help="供应商评级")
    parser.add_argument("--mode", help="融资模式（accounts_receivable/order/inventory/prepayment/core_guarantee）")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="输出格式")
    parser.add_argument("--text", "-t", help="直接传入文本进行解析（替代参数模式）")

    args = parser.parse_args()

    engine = SupplyChainFinanceEngine()

    if args.text:
        params = engine.parse_input(args.text)
    else:
        params = {}
        if args.core:
            params["core_enterprise"] = args.core
        if args.supplier:
            params["supplier"] = args.supplier
        if args.amount:
            params["transaction_amount"] = args.amount
        if args.period:
            params["credit_period"] = args.period
        if args.months:
            params["history_months"] = args.months
        if args.core_rating:
            params["core_rating"] = args.core_rating.upper()
        if args.supplier_rating:
            params["supplier_rating"] = args.supplier_rating.upper()
        if args.mode:
            params["finance_mode"] = args.mode

    report = engine.generate_full_report(params)

    if args.format == "json":
        print(engine.format_json(report))
    else:
        print(engine.format_text(report))


if __name__ == "__main__":
    sys.exit(main())
