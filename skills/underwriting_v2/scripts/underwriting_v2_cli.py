#!/usr/bin/env python3
"""
券商两融智能核保v2 CLI入口

用法：
    python3 underwriting_v2_cli.py generate "两融核保 客户资产500万 持仓市值300万 信用评分80 无负债"
    python3 underwriting_v2_cli.py evaluate --asset 500 --holding 300 --credit 80 --months 12 --risk C4
    python3 underwriting_v2_cli.py batch <input.json>
"""

import argparse
import json
import sys
import os
from pathlib import Path

# 添加父目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from underwriting_v2_engine import UnderwritingV2Engine


def cmd_generate(args):
    """从自然语言生成两融核保报告"""
    engine = UnderwritingV2Engine()
    text = args.text or args.T

    if not text:
        print("❌ 请提供核保描述文本")
        return 1

    print(f"\n🔍 解析输入：{text}\n")

    result = engine.underwrite(raw_input=text)

    # 格式化输出
    if args.format == "text":
        report = engine.format_text_report(result)
        print(report)
    elif args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.format == "wecom":
        from wecom_integration import generate_wecom_card_simple, generate_wecom_card
        if args.wecom_format == "card":
            card = generate_wecom_card(result)
            print(json.dumps(card, ensure_ascii=False, indent=2))
        else:
            text_card = generate_wecom_card_simple(result)
            print(text_card)
    else:
        # 默认详细文本
        report = engine.format_text_report(result)
        print(report)

    return 0


def cmd_evaluate(args):
    """结构化参数两融核保"""
    engine = UnderwritingV2Engine()

    result = engine.underwrite(
        total_asset=args.asset * 10000 if args.asset else None,
        holding_market_value=args.holding * 10000 if args.holding else None,
        credit_score=args.credit,
        debt_amount=args.debt * 10000 if args.debt else 0,
        holding_months=args.months or 12,
        risk_level=args.risk or "C4",
        credit_record=args.record or "良好",
        holding_type=args.holding_type or "主板股票",
    )

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        report = engine.format_text_report(result)
        print(report)

    return 0


def cmd_batch(args):
    """批量两融核保"""
    input_file = Path(args.input)

    if not input_file.exists():
        print(f"❌ 文件不存在：{input_file}")
        return 1

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cases = data.get("cases", [])
    if not cases:
        print("❌ 未找到cases字段")
        return 1

    engine = UnderwritingV2Engine()
    results = []

    for i, case in enumerate(cases):
        print(f"\n📋 处理案例 {i+1}/{len(cases)}...")
        # 转换万单位
        if "total_asset" in case:
            case["total_asset"] = case["total_asset"] * 10000
        if "holding_market_value" in case:
            case["holding_market_value"] = case["holding_market_value"] * 10000
        if "debt_amount" in case:
            case["debt_amount"] = case["debt_amount"] * 10000

        result = engine.underwrite(**case)
        results.append({
            "case_id": case.get("id", i+1),
            "result": result
        })

    # 输出结果
    output_file = input_file.with_suffix(".result.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 批量核保完成，共{len(results)}个案例")
    print(f"📄 结果已保存至：{output_file}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="券商两融智能核保引擎 v2 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 自然语言核保
  python3 scripts/underwriting_v2_cli.py generate "两融核保 客户资产500万 持仓市值300万 信用评分80 无负债"

  # 结构化参数核保（单位：万）
  python3 scripts/underwriting_v2_cli.py evaluate --asset 500 --holding 300 --credit 80 --months 12 --risk C4

  # 企微卡片格式
  python3 scripts/underwriting_v2_cli.py generate "两融核保 客户资产500万" --format wecom --wecom-format card

  # 批量核保（JSON格式）
  python3 scripts/underwriting_v2_cli.py batch cases.json
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="从自然语言文本生成两融核保报告")
    gen_parser.add_argument("text", nargs="?", help="核保描述文本")
    gen_parser.add_argument("-T", dest="T", help="核保描述文本（简写）")
    gen_parser.add_argument("--format", choices=["text", "json", "wecom"], default="text",
                          help="输出格式（text=文本报告，json=结构化JSON，wecom=企微卡片）")
    gen_parser.add_argument("--wecom-format", choices=["card", "text"], default="text",
                          help="企微格式（card=卡片JSON，text=纯文本）")
    gen_parser.set_defaults(func=cmd_generate)

    # evaluate 子命令
    eval_parser = subparsers.add_parser("evaluate", help="使用结构化参数两融核保")
    eval_parser.add_argument("--asset", type=float, help="客户总资产（万）")
    eval_parser.add_argument("--holding", type=float, help="持仓市值（万）")
    eval_parser.add_argument("--credit", type=int, default=75, help="信用评分（0-100）")
    eval_parser.add_argument("--debt", type=float, default=0, help="负债金额（万）")
    eval_parser.add_argument("--months", type=int, default=12, help="持股月数")
    eval_parser.add_argument("--risk", default="C4", help="风险等级（C1-C6）")
    eval_parser.add_argument("--record", default="良好", help="信用记录（良好/一般/较差）")
    eval_parser.add_argument("--holding-type", dest="holding_type", default="主板股票",
                           help="持仓类型")
    eval_parser.add_argument("--format", choices=["text", "json"], default="text",
                           help="输出格式")
    eval_parser.set_defaults(func=cmd_evaluate)

    # batch 子命令
    batch_parser = subparsers.add_parser("batch", help="批量核保")
    batch_parser.add_argument("input", help="输入JSON文件路径")
    batch_parser.add_argument("--format", choices=["text", "json"], default="json",
                            help="输出格式")
    batch_parser.set_defaults(func=cmd_batch)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
