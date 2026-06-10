#!/usr/bin/env python3
"""
智能核保CLI入口

用法：
    python3 underwriting_cli.py generate "智能核保 年龄45 职业企业主 健康良好 年收入100万 寿险500万 20年"
    python3 underwriting_cli.py evaluate --age 45 --occupation 企业主 --health 良好 --income 100 --coverage 500 --period 20 --product 寿险
    python3 underwriting_cli.py batch <input.json>
"""

import argparse
import json
import sys
import os
from pathlib import Path

# 添加父目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from underwriting_engine import SmartUnderwritingEngine


def cmd_generate(args):
    """从自然语言生成核保报告"""
    engine = SmartUnderwritingEngine()
    text = args.text or args.T

    print(f"\n🔍 解析输入：{text}\n")

    result = engine.underwrite(raw_input=text)

    # 格式化输出
    if args.format == "text":
        report = engine.format_text_report(result)
        print(report)
    elif args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 默认详细文本
        report = engine.format_text_report(result)
        print(report)

    return 0


def cmd_evaluate(args):
    """结构化参数核保"""
    engine = SmartUnderwritingEngine()

    result = engine.underwrite(
        age=args.age,
        occupation=args.occupation,
        health_status=args.health,
        family_medical_history=args.family,
        annual_income=args.income,
        coverage_amount=args.coverage,
        coverage_period=args.period,
        product_type=args.product,
    )

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        report = engine.format_text_report(result)
        print(report)

    return 0


def cmd_batch(args):
    """批量核保"""
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

    engine = SmartUnderwritingEngine()
    results = []

    for i, case in enumerate(cases):
        print(f"\n📋 处理案例 {i+1}/{len(cases)}...")
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
        description="智能核保引擎 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 自然语言核保
  python3 underwriting_cli.py generate "智能核保 年龄45 职业企业主 健康良好 年收入100万 寿险500万 20年"

  # 结构化参数核保
  python3 underwriting_cli.py evaluate --age 45 --occupation 企业主 --health 良好 --income 100 --coverage 500

  # 批量核保（JSON格式）
  python3 underwriting_cli.py batch cases.json --format json
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="从自然语言文本生成核保报告")
    gen_parser.add_argument("text", nargs="?", help="核保描述文本")
    gen_parser.add_argument("-T", dest="T", help="核保描述文本（简写）")
    gen_parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")
    gen_parser.set_defaults(func=cmd_generate)

    # evaluate 子命令
    eval_parser = subparsers.add_parser("evaluate", help="使用结构化参数核保")
    eval_parser.add_argument("--age", type=int, required=True, help="年龄")
    eval_parser.add_argument("--occupation", required=True, help="职业")
    eval_parser.add_argument("--health", dest="health", required=True, help="健康状况（优秀/良好/一般/较差）")
    eval_parser.add_argument("--family", dest="family", default="无", help="家族病史")
    eval_parser.add_argument("--income", type=float, required=True, help="年收入（万元）")
    eval_parser.add_argument("--coverage", type=float, required=True, help="保额（万元）")
    eval_parser.add_argument("--period", type=int, default=20, help="保障期限（年）")
    eval_parser.add_argument("--product", default="寿险", help="产品类型")
    eval_parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")
    eval_parser.set_defaults(func=cmd_evaluate)

    # batch 子命令
    batch_parser = subparsers.add_parser("batch", help="批量核保")
    batch_parser.add_argument("input", help="输入JSON文件路径")
    batch_parser.add_argument("--format", choices=["text", "json"], default="json", help="输出格式")
    batch_parser.set_defaults(func=cmd_batch)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
