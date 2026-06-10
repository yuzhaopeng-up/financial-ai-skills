#!/usr/bin/env python3
"""全球资产配置 CLI"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from global_asset_allocation import GlobalAssetAllocationEngine
import json

def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] == "--help":
        print("用法: python3 allocation_cli.py generate <配置需求>")
        return
    if args[0] == "generate":
        text = " ".join(args[1:])
        eng = GlobalAssetAllocationEngine()
        r = eng.generate(text)
        print(json.dumps({
            "title": r.title,
            "client_profile": r.client_profile,
            "regional_allocation": r.regional_allocation,
            "asset_class_allocation": r.asset_class_allocation,
            "currency_hedge": r.currency_hedge,
            "rebalancing": r.rebalancing,
            "compliance_notes": r.compliance_notes,
            "product_recommendations": r.product_recommendations,
            "generated_at": r.generated_at,
        }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
