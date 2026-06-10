#!/usr/bin/env python3
"""
基金对比 CLI
用法:
    python3 compare_cli.py generate "基金对比 XXXXXX 163402"
    python3 compare_cli.py generate "比较 某基金公司中小盘 兴全趋势"
    python3 compare_cli.py generate "基金对比 XXXXXX 163402 260101" --format markdown
    python3 compare_cli.py generate "基金对比 XXXXXX 163402" --format wecom
"""

import sys
import json
import argparse
from pathlib import Path

# 将 skills 目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fund_compare import FundCompareEngine


def cmd_generate(args):
    engine = FundCompareEngine()
    inputs = args.query.strip().split()

    # 解析：如果用户传入完整句子，engine.resolve 会处理
    # 直接传入整个 query 让 engine 解析
    result = engine.compare([args.query])

    if args.format == "markdown":
        output = engine.render_markdown(result)
        print(output)
    elif args.format == "json":
        # 简化 result 去除不可序列化对象
        simple = {
            "scores": result["scores"],
            "recommendation": result["recommendation"],
            "analysis": result["analysis"],
            "profiles": [
                {
                    "code": p.code,
                    "name": p.name,
                    "returns": {
                        "m1": p.returns.m1, "m3": p.returns.m3,
                        "m6": p.returns.m6, "y1": p.returns.y1, "y3": p.returns.y3,
                    },
                    "risk": {
                        "sharpe": p.risk.sharpe,
                        "max_drawdown": p.risk.max_drawdown,
                        "volatility": p.risk.volatility,
                        "calmar": p.risk.calmar,
                    },
                    "info": {
                        "fund_type": p.info.fund_type,
                        "scale": p.info.scale,
                        "manager": p.info.manager,
                        "management_fee": p.info.management_fee,
                    },
                    "score": p.score,
                }
                for p in result["profiles"]
            ],
        }
        print(json.dumps(simple, ensure_ascii=False, indent=2))
    elif args.format == "wecom":
        card = engine.render_wecom_card(result)
        print(json.dumps(card, ensure_ascii=False, indent=2))
    else:
        # 默认 markdown
        output = engine.render_markdown(result)
        print(output)

    return 0


def main():
    parser = argparse.ArgumentParser(description="基金对比工具")
    sub = parser.add_subparsers(dest="cmd", help="子命令")

    gen = sub.add_parser("generate", help="生成基金对比报告")
    gen.add_argument("query", help="查询语句，如 '基金对比 XXXXXX 163402' 或 '比较 某基金公司中小盘 兴全趋势'")
    gen.add_argument("--format", "-f", choices=["markdown", "json", "wecom"],
                     default="markdown", help="输出格式（默认 markdown）")

    args = parser.parse_args()

    if args.cmd == "generate":
        return cmd_generate(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
