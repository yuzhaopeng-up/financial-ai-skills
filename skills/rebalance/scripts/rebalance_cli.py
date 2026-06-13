#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资产配置再平衡引擎 CLI
用法: python rebalance_cli.py --holdings '{"股票":400000,"债券":200000}' --target '{"股票":50,"债券":50}' [--tolerance 5] [--min-trade 1000]
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rebalance_engine import RebalanceEngine


def parse_args():
    parser = argparse.ArgumentParser(description="资产配置再平衡引擎")
    parser.add_argument(
        "--holdings", "-c",
        type=str,
        required=False,
        help="当前持仓 JSON，格式: '{\"股票\":400000,\"债券\":200000}'"
    )
    parser.add_argument(
        "--target", "-t",
        type=str,
        required=False,
        help="目标配置 JSON，格式: '{\"股票\":50,\"债券\":50}' (百分比)"
    )
    parser.add_argument(
        "--total", "-v",
        type=float,
        required=False,
        help="总市值（不传则自动求和）"
    )
    parser.add_argument(
        "--tolerance", "-d",
        type=float,
        default=5.0,
        help="容忍偏差%%（默认5%%）"
    )
    parser.add_argument(
        "--min-trade", "-m",
        type=float,
        default=1000.0,
        help="最小交易金额（默认1000元）"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "card"],
        default="text",
        help="输出格式"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    # 默认示例数据
    if args.holdings:
        try:
            current_holdings = json.loads(args.holdings)
        except json.JSONDecodeError as e:
            print(f"❌ 持仓 JSON 解析错误: {e}")
            sys.exit(1)
    else:
        current_holdings = {
            "A股股票": 400000,
            "债券基金": 200000,
            "货币基金": 150000,
            "黄金": 100000,
            "银行存款": 150000,
        }
        print("ℹ️  使用默认示例持仓")
    
    if args.target:
        try:
            target_allocation = json.loads(args.target)
        except json.JSONDecodeError as e:
            print(f"❌ 目标配置 JSON 解析错误: {e}")
            sys.exit(1)
    else:
        target_allocation = {
            "A股股票": 35.0,
            "债券基金": 25.0,
            "货币基金": 20.0,
            "黄金": 10.0,
            "银行存款": 10.0,
        }
        print("ℹ️  使用默认示例目标配置")
    
    total_value = args.total or sum(current_holdings.values())
    
    print()
    print("=" * 50)
    print("🦞 资产配置再平衡引擎 v1.0")
    print("=" * 50)
    print()
    
    engine = RebalanceEngine(api_mode=False)
    
    result = engine.rebalance(
        current_holdings=current_holdings,
        target_allocation=target_allocation,
        total_value=total_value,
        tolerance=args.tolerance,
        min_trade_amount=args.min_trade,
    )
    
    if args.format == "json":
        print(engine.format_json(result))
    elif args.format == "card":
        card = engine.format_wecom_card(result)
        print(json.dumps(card, ensure_ascii=False, indent=2))
    else:
        print(engine.format_text(result))


if __name__ == "__main__":
    sys.exit(main())
