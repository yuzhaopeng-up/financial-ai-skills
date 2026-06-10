#!/usr/bin/env python3
"""基金研究报告生成 CLI"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fund_research import FundResearchEngine
import json

def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] == "--help":
        print("用法: python3 fund_cli.py generate <基金名称或代码>")
        return
    if args[0] == "generate":
        text = " ".join(args[1:])
        eng = FundResearchEngine()
        r = eng.generate(text)
        print(json.dumps({
            "fund_name": r.fund_name, "fund_code": r.fund_code,
            "fund_type": r.fund_type, "risk_level": r.risk_level,
            "performance": r.performance,
            "vs_benchmark": r.vs_benchmark,
            "risk_metrics": r.risk_metrics,
            "attribution": r.attribution,
            "manager": r.manager,
            "asset_allocation": r.asset_allocation,
            "top_holdings": r.top_holdings,
            "recommendation": r.recommendation,
            "generated_at": r.generated_at,
        }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
