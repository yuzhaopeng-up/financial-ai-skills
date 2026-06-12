#!/usr/bin/env python3
"""市场观点输出 CLI"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from market_view import MarketViewEngine
import json

def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] == "--help":
        print("用法: python3 market_view_cli.py generate <市场描述>")
        return
    if args[0] == "generate":
        text = " ".join(args[1:])
        eng = MarketViewEngine()
        r = eng.generate(text)
        print(json.dumps({
            "report_type": r.report_type, "title": r.title,
            "date_range": r.date_range,
            "index_performance": r.index_performance,
            "sector_performance": r.sector_performance[:5],
            "hot_themes": r.hot_themes,
            "money_flow": r.money_flow,
            "macro_view": r.macro_view,
            "outlook": r.outlook,
            "risks": r.risks,
            "generated_at": r.generated_at,
        }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
