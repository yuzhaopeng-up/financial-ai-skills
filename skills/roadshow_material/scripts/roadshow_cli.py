#!/usr/bin/env python3
"""路演材料生成 CLI"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from roadshow_material import RoadshowEngine
import json

def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] == "--help":
        print("用法: python3 roadshow_cli.py generate <产品信息>")
        return
    if args[0] == "generate":
        text = " ".join(args[1:])
        eng = RoadshowEngine()
        r = eng.generate(text)
        print(json.dumps({
            "title": r.title, "product_name": r.product_name,
            "target_audience": r.target_audience, "duration": r.duration,
            "ppt_outline": r.ppt_outline,
            "speech_script": r.speech_script,
            "comparison_table": r.comparison_table,
            "risk_disclosure": r.risk_disclosure,
            "qa_prep": r.qa_prep,
            "generated_at": r.generated_at,
        }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
