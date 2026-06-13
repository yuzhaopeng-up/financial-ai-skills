#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并购方案生成引擎 CLI
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ma_scheme_engine import MaSchemeEngine


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="并购方案生成引擎 CLI")
    parser.add_argument("--acquirer", "-a", help="收购方")
    parser.add_argument("--target", "-t", help="被收购方/标的")
    parser.add_argument("--purpose", "-p", help="交易目的")
    parser.add_argument("--revenue", "-r", type=float, help="标的营业收入（万元）")
    parser.add_argument("--profit", "-e", type=float, help="标的净利润（万元）")
    parser.add_argument("--assets", "-n", type=float, help="标的净资产（万元）")
    parser.add_argument("--industry", "-i", help="所属行业")
    parser.add_argument("--deal-size", "-d", type=float, help="交易规模（万元）")
    parser.add_argument("--synergy-rev", type=float, help="协同效应-收入（万元/年）")
    parser.add_argument("--synergy-cost", type=float, help="协同效应-成本（万元/年）")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="输出格式")
    
    args = parser.parse_args()
    
    engine = MaSchemeEngine()
    
    print("🦞 并购方案生成引擎 v1.0")
    print()
    
    # 生成方案
    result = engine.generate_scheme(
        acquirer=args.acquirer,
        target=args.target,
        purpose=args.purpose,
        target_revenue=args.revenue,
        target_net_income=args.profit,
        target_net_assets=args.assets,
        target_industry=args.industry,
        deal_size=args.deal_size,
        synergy_revenue=args.synergy_rev,
        synergy_cost=args.synergy_cost
    )
    
    if args.format == "json":
        print(engine.format_json(result))
    else:
        print(engine.format_text(result))


if __name__ == "__main__":
    sys.exit(main())
