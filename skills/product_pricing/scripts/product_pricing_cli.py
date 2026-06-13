#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品定价引擎 CLI
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from product_pricing_engine import ProductPricingEngine


def main():
    engine = ProductPricingEngine(api_mode=True)

    print("💰 产品定价引擎 v1.0")
    print()

    # 解析命令行参数
    parser = argparse.ArgumentParser(description="产品定价引擎")
    parser.add_argument("product", nargs="?", default="贷款", help="产品类型")
    parser.add_argument("risk", nargs="?", default="稳健型", help="客户风险等级")
    parser.add_argument("rate", nargs="?", type=float, default=3.6, help="市场利率(%%)")
    parser.add_argument("--sub", "--sub-product", dest="sub_product", default=None, help="子产品")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    args = parser.parse_args()

    result = engine.price(
        product_type=args.product,
        risk_level=args.risk,
        market_rate=args.rate,
        sub_product=args.sub_product,
    )

    if args.json:
        print(engine.format_json(result))
    else:
        print(engine.format_text(result))


if __name__ == "__main__":
    sys.exit(main())
