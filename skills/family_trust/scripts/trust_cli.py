#!/usr/bin/env python3
"""家族信托方案生成 CLI"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from family_trust import FamilyTrustEngine
import json

def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] == "--help":
        print("用法: python3 trust_cli.py generate <客户画像>")
        return
    if args[0] == "generate":
        text = " ".join(args[1:])
        eng = FamilyTrustEngine()
        r = eng.generate(text)
        print(json.dumps({
            "title": r.title,
            "client_profile": r.client_profile,
            "trust_structure": r.trust_structure,
            "asset_allocation": r.asset_allocation,
            "tax_planning": r.tax_planning,
            "beneficiary_arrangement": r.beneficiary_arrangement,
            "risk_isolation": r.risk_isolation,
            "timeline": r.timeline,
            "fee_estimate": r.fee_estimate,
            "risks_and_notes": r.risks_and_notes,
            "generated_at": r.generated_at,
        }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
