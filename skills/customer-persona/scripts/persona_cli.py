#!/usr/bin/env python3
"""
Customer Persona Skill CLI
==========================
360 度客户画像生成器命令行入口。

子命令:
  parse     - 仅解析自然语言为结构化字段（调试）
  generate  - 生成完整客户画像
  batch     - 批量从 JSON 文件生成
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, SKILL)

from persona_engine import PersonaEngine, parse_natural_language
from persona_formatter import PersonaFormatter


def cmd_parse(args):
    ci = parse_natural_language(args.text)
    print(json.dumps(
        {k: v for k, v in ci.__dict__.items() if v not in (None, "", False, [])},
        ensure_ascii=False, indent=2,
    ))


def cmd_generate(args):
    eng = PersonaEngine()
    text = args.text
    if args.json:
        with open(args.json, "r", encoding="utf-8") as f:
            text = json.load(f)
    persona = eng.generate(text)
    if args.format == "json":
        print(PersonaFormatter.to_json(persona))
    elif args.format == "md":
        print(PersonaFormatter.to_markdown(persona))
    elif args.format == "card":
        print(json.dumps(PersonaFormatter.to_wecom_card(persona),
                         ensure_ascii=False, indent=2))
    else:
        print(PersonaFormatter.to_text(persona))


def cmd_batch(args):
    eng = PersonaEngine()
    with open(args.file, "r", encoding="utf-8") as f:
        items = json.load(f)
    results = []
    for item in items:
        p = eng.generate(item)
        results.append({
            "name": p.customer.name,
            "segment": p.rfm_segment,
            "stage": p.life_cycle_stage,
            "top_product": p.recommended_products[0]["name"] if p.recommended_products else None,
            "rfm": p.rfm_score,
            "tags": p.value_tags,
        })
    print(json.dumps(results, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Customer Persona Skill CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("parse", help="仅解析自然语言")
    p1.add_argument("text")
    p1.set_defaults(func=cmd_parse)

    p2 = sub.add_parser("generate", help="生成完整画像")
    p2.add_argument("text", nargs="?", default="")
    p2.add_argument("--json", help="从 JSON 文件读取结构化输入")
    p2.add_argument("--format", choices=["text", "json", "md", "card"], default="text")
    p2.set_defaults(func=cmd_generate)

    p3 = sub.add_parser("batch", help="批量画像")
    p3.add_argument("file", help="JSON array file")
    p3.set_defaults(func=cmd_batch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
