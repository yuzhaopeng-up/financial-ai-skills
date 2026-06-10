#!/usr/bin/env python3
"""
网点分析 CLI 入口

用法:
    python3 scripts/branch_cli.py generate "网点分析 商业区 员工10人 周边3个竞争网点"
    python3 scripts/branch_cli.py generate "网点分析 工业区 面积300平米 员工15人"
    python3 scripts/branch_cli.py json "商业区 员工8人 周边2个竞争网点 50家企业"
"""

import sys
import os
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from branch_analysis import (
    BranchAnalysisEngine,
    parse_cli_input,
)


def cmd_generate(args: argparse.Namespace):
    """生成网点分析报告"""
    engine = BranchAnalysisEngine()
    params = parse_cli_input(args.text)
    
    result = engine.analyze(**params)
    
    if args.format == "json":
        output = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        print(output)
    else:
        report = engine.generate_report(result)
        print(report)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            if args.format == "json":
                f.write(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            else:
                f.write(engine.generate_report(result))
        print(f"\n[已保存至: {args.output}]")


def cmd_json(args: argparse.Namespace):
    """JSON格式输出（快捷命令）"""
    args.format = "json"
    args.output = None
    cmd_generate(args)


def main():
    parser = argparse.ArgumentParser(
        description="网点分析技能 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)
    
    gen = sub.add_parser("generate", help="生成网点分析报告")
    gen.add_argument("text", help="网点描述文本，如：网点分析 商业区 员工10人 周边3个竞争网点")
    gen.add_argument("-f", "--format", choices=["text", "json"], default="text", help="输出格式")
    gen.add_argument("-o", "--output", help="保存到文件")
    
    j = sub.add_parser("json", help="JSON格式快捷输出")
    j.add_argument("text", help="网点描述文本")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "json":
        cmd_json(args)


if __name__ == "__main__":
    main()
