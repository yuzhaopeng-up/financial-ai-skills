#!/usr/bin/env python3
"""运营日报生成 CLI"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ops_daily_report import OpsDailyReportEngine
import json

def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] == "--help":
        print("用法: python3 ops_cli.py generate <运营数据>")
        return
    if args[0] == "generate":
        text = " ".join(args[1:])
        eng = OpsDailyReportEngine()
        r = eng.generate(text)
        print(json.dumps({
            "title": r.title, "date": r.date,
            "department": r.department, "summary": r.summary,
            "business_overview": r.business_overview,
            "key_metrics": r.key_metrics,
            "alerts": r.alerts,
            "tomorrow_plan": r.tomorrow_plan,
            "notes": r.notes,
            "generated_at": r.generated_at,
        }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
