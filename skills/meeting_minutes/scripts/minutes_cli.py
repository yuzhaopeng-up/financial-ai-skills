#!/usr/bin/env python3
"""调研纪要生成 CLI"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from meeting_minutes import MeetingMinutesEngine
import json

def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] == "--help":
        print("用法: python3 minutes_cli.py generate <调研记录文字>")
        return
    if args[0] == "generate":
        text = " ".join(args[1:])
        eng = MeetingMinutesEngine()
        r = eng.generate(text)
        print(json.dumps({
            "title": r.title, "meeting_type": r.meeting_type,
            "company": r.company, "date": r.date,
            "core_topics": r.core_topics,
            "key_points": r.key_points[:5],
            "action_items": r.action_items,
            "risks": r.risks,
            "summary": r.summary,
            "generated_at": r.generated_at,
        }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
