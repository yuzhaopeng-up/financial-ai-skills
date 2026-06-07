#!/usr/bin/env python3
"""
Application Material Checker CLI
================================
进件材料自动核对工具。

子命令:
  scenarios    - 列出支持的业务场景
  required     - 列出场景所需材料清单
  check        - 对样本 JSON 做核对
  batch        - 批量核对（目录下所有 JSON）
"""
import argparse
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, SKILL)

from material_checker import MaterialChecker, MaterialReportFormatter
from checker_engine import MaterialDoc


def _load_case(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    docs = [
        MaterialDoc(
            doc_type=d["doc_type"],
            file_name=d.get("file_name", ""),
            fields=d.get("fields", {}),
            confidence=d.get("confidence", 1.0),
        )
        for d in data["documents"]
    ]
    return data["scenario"], data.get("case_name", ""), docs


def cmd_scenarios(args):
    checker = MaterialChecker()
    print(json.dumps(checker.list_scenarios(), ensure_ascii=False, indent=2))


def cmd_required(args):
    checker = MaterialChecker()
    docs = checker.get_required_docs(args.scenario)
    if not docs:
        print(f"❌ 未知场景: {args.scenario}", file=sys.stderr)
        sys.exit(1)
    print(f"📋 {args.scenario} 所需材料 ({len(docs)} 类):")
    for d in docs:
        print(f"   - {d}")


def cmd_check(args):
    scenario, name, docs = _load_case(args.case)
    today = datetime.strptime(args.today, "%Y-%m-%d") if args.today else None
    checker = MaterialChecker()
    report = checker.check(scenario, docs, today=today)
    if args.format == "json":
        print(MaterialReportFormatter.to_json(report))
    elif args.format == "md":
        print(MaterialReportFormatter.to_markdown(report))
    elif args.format == "card":
        print(json.dumps(
            MaterialReportFormatter.to_wecom_card(report),
            ensure_ascii=False, indent=2,
        ))
    else:
        print(MaterialReportFormatter.to_text(report))


def cmd_batch(args):
    files = [
        os.path.join(args.dir, f) for f in sorted(os.listdir(args.dir))
        if f.endswith(".json")
    ]
    summary = []
    checker = MaterialChecker()
    for fp in files:
        scenario, name, docs = _load_case(fp)
        report = checker.check(scenario, docs)
        summary.append({
            "file": os.path.basename(fp),
            "case": name,
            "scenario": report.scenario,
            "score": report.score,
            "pass": report.pass_,
            "issues": len(report.issues),
            "missing": len(report.missing),
        })
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Application Material Checker CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("scenarios", help="列出支持的业务场景")
    p1.set_defaults(func=cmd_scenarios)

    p2 = sub.add_parser("required", help="列出场景所需材料")
    p2.add_argument("scenario")
    p2.set_defaults(func=cmd_required)

    p3 = sub.add_parser("check", help="核对单个样本")
    p3.add_argument("case", help="样本 JSON 路径")
    p3.add_argument("--format", choices=["text", "json", "md", "card"], default="text")
    p3.add_argument("--today", help="模拟当前日期 YYYY-MM-DD")
    p3.set_defaults(func=cmd_check)

    p4 = sub.add_parser("batch", help="批量核对")
    p4.add_argument("--dir", required=True)
    p4.set_defaults(func=cmd_batch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
