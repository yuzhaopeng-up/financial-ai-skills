#!/usr/bin/env python3
"""
research-report CLI
===================
投研报告自动生成器。

子命令:
  list       - 列出已支持的行业与公司
  generate   - 生成报告
  parse      - 仅解析请求字段（调试）
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, SKILL)

from report_engine import ReportEngine, parse_request, _load_templates
from report_formatter import ReportFormatter


def cmd_list(args):
    t = _load_templates()
    print("📚 已支持的行业（按需选择）:")
    for ind in t["industries"]:
        if ind == "通用":
            continue
        print(f"   • {ind}")
    print("")
    print("🏢 已收录的公司（可直接生成完整报告）:")
    for c, info in t["companies"].items():
        print(f"   • {c}  ({info['code']})  → {info['industry']}")
    print("")
    print("💡 未收录的公司/行业也可生成报告，将使用通用模板。")


def cmd_generate(args):
    eng = ReportEngine()
    r = eng.generate(args.text)
    if args.format == "json":
        print(ReportFormatter.to_json(r))
    elif args.format == "md":
        print(ReportFormatter.to_markdown(r))
    elif args.format == "card":
        print(json.dumps(ReportFormatter.to_wecom_card(r),
                         ensure_ascii=False, indent=2))
    else:
        print(ReportFormatter.to_text(r))


def cmd_parse(args):
    req = parse_request(args.text)
    print(json.dumps(req.__dict__, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="research-report CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("list", help="列出支持的行业与公司")
    p1.set_defaults(func=cmd_list)

    p2 = sub.add_parser("generate", help="生成研报")
    p2.add_argument("text", help="自然语言请求，例如 '研报生成 新能源 宁德时代 2025'")
    p2.add_argument("--format", choices=["text", "json", "md", "card"], default="text")
    p2.set_defaults(func=cmd_generate)

    p3 = sub.add_parser("parse", help="仅解析请求")
    p3.add_argument("text")
    p3.set_defaults(func=cmd_parse)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
