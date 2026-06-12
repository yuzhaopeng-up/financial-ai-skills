#!/usr/bin/env python3
"""
insurance_recommend CLI - 保险产品智能推荐命令行工具

用法:
    python3 ins_rec_cli.py generate "保险推荐 30岁男性 已婚 孩子1岁 年收入30万 已有医保"
    python3 ins_rec_cli.py parse "30岁男性 年收入50万"
    python3 ins_rec_cli.py interactive

示例:
    python3 scripts/ins_rec_cli.py generate "保险推荐 35岁女性 已婚 两个孩子(5岁/8岁) 年收入40万 房贷200万 已有重疾险30万"
"""

import sys
import os
import json
import argparse

# 添加父目录到路径以便导入（向上3级：scripts -> insurance_recommend -> skills -> 根目录）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from insurance_recommend import InsuranceRecommendEngine

def format_output(result: dict, output_format: str = "text") -> str:
    """格式化输出"""
    if output_format == "json":
        return json.dumps(result, ensure_ascii=False, indent=2)

    lines = []
    lines.append("=" * 70)
    lines.append("🛡️  保险产品智能推荐方案")
    lines.append("=" * 70)

    # 客户画像
    lines.append("\n【👤 客户画像】")
    profile = result.get("customer_profile", {})
    for k, v in profile.items():
        lines.append(f"  • {k}: {v}")

    # 保障缺口
    lines.append("\n【📊 保障缺口分析】")
    gap = result.get("protection_gap", {})
    for k, v in gap.items():
        lines.append(f"  • {k}: {v}")

    # 推荐方案
    lines.append("\n【💡 推荐方案】(按投保优先级排序)")
    recs = result.get("recommendations", [])
    if not recs:
        lines.append("  ✓ 您的基础保障已较完善，建议查漏补缺")
    else:
        for rec in recs:
            lines.append(f"\n  {rec['priority']}. {rec['insurance_type']} - {rec['product_matching']}")
            lines.append(f"     保额: {rec['coverage']} | 年保费: {rec['annual_premium']} | 期间: {rec['policy_term']}")
            lines.append(f"     📝 {rec['reason']}")
            if rec.get('key_benefits'):
                lines.append(f"     ✨ 亮点: {' / '.join(rec['key_benefits'])}")

    # 家庭保障全景
    lines.append("\n【🏠 家庭保障全景】")
    overview = result.get("family_protection_overview", {})
    for k, v in overview.items():
        if k == "priority_order":
            lines.append(f"  • 投保优先级: {' → '.join(v)}")
        else:
            lines.append(f"  • {k}: {v}")

    # 保费预算
    lines.append("\n【💰 保费预算】")
    budget = result.get("premium_budget", {})
    lines.append(f"  • 年度总保费: {budget.get('total_annual', 'N/A')}")
    for k, v in budget.get("by_type", {}).items():
        lines.append(f"    - {k}: {v}")
    if budget.get("note"):
        lines.append(f"  • {budget['note']}")

    lines.append("\n" + "=" * 70)
    lines.append("⚠️  仅供参考，具体方案请咨询专业保险顾问")
    lines.append("=" * 70)

    return "\n".join(lines)


def interactive_mode():
    """交互式输入模式"""
    print("\n🎯 保险产品智能推荐 - 交互式模式")
    print("-" * 50)
    print("请回答以下问题（直接回车使用默认值）:\n")

    engine = InsuranceRecommendEngine()

    # 年龄
    age_input = input("年龄 [30]: ").strip()
    age = int(age_input) if age_input else 30

    # 性别
    gender_input = input("性别 (男/女) [男]: ").strip()
    gender = "male" if gender_input != "女" else "female"

    # 年收入
    income_input = input("年收入(万元) [30]: ").strip()
    annual_income = float(income_input) * 10000 if income_input else 300000

    # 婚姻状态
    married_input = input("是否已婚 (是/否) [否]: ").strip()
    married = married_input == "是"

    # 孩子
    children = []
    if married:
        child_count = input("孩子数量 [0]: ").strip()
        if child_count and int(child_count) > 0:
            for i in range(int(child_count)):
                child_age = input(f"  第{i+1}个孩子年龄: ").strip()
                children.append({"age": int(child_age) if child_age else 0})

    # 负债
    liab = {}
    mortgage = input("\n房贷(万元) [0]: ").strip()
    if mortgage:
        liab["mortgage"] = float(mortgage) * 10000

    # 已有保单
    policies = []
    has_medical = input("\n已有医保/社保? (是/否) [否]: ").strip()
    if has_medical == "是":
        policies.append({"type": "医保", "coverage": 100000})

    has_critical = input("已有重疾险? (是/否) [否]: ").strip()
    if has_critical == "是":
        cov = input("  重疾险保额(万元): ").strip()
        policies.append({"type": "重疾险", "coverage": float(cov) * 10000 if cov else 300000})

    # 保费预算
    budget_input = input("\n保费预算占年收入比例? (%) [10]: ").strip()
    budget_percent = float(budget_input) / 100 if budget_input else 0.1

    print("\n" + "-" * 50)
    print("正在生成推荐方案...\n")

    result = engine.generate_recommendation(
        age=age,
        gender=gender,
        annual_income=annual_income,
        family={
            "married": married,
            "children": children,
            "dependents": 0
        },
        existing_policies=policies,
        liabilities=liab,
        budget_percent=budget_percent
    )

    print(format_output(result))


def main():
    parser = argparse.ArgumentParser(
        description="保险产品智能推荐CLI工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 ins_rec_cli.py generate "保险推荐 30岁男性 已婚 孩子1岁 年收入30万 已有医保"
  python3 ins_rec_cli.py parse "30岁男性 年收入50万"
  python3 ins_rec_cli.py interactive
  python3 ins_rec_cli.py generate "35岁女性 已婚 两个孩子5岁8岁 年收入40万 房贷200万" -o json
        """
    )

    parser.add_argument(
        "command",
        choices=["generate", "parse", "interactive"],
        help="命令: generate(生成推荐) / parse(解析输入) / interactive(交互式)"
    )

    parser.add_argument(
        "text",
        nargs="*",
        help="描述文本（generate和parse命令使用）"
    )

    parser.add_argument(
        "-o", "--output",
        choices=["text", "json"],
        default="text",
        help="输出格式 (默认: text)"
    )

    parser.add_argument(
        "-f", "--file",
        type=str,
        help="从文件读取输入（每行一个描述）"
    )

    args = parser.parse_args()

    engine = InsuranceRecommendEngine()

    if args.command == "interactive":
        interactive_mode()
        return

    text = " ".join(args.text) if args.text else ""

    if args.file:
        # 批量处理
        with open(args.file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                print(f"\n{'='*60}")
                print(f"📋 案例 {line_num}: {line}")
                print("=" * 60)

                try:
                    params = engine.parse_natural_language(line)
                    if args.command == "parse":
                        print(json.dumps(params, ensure_ascii=False, indent=2))
                    else:
                        result = engine.generate_recommendation(**params)
                        print(format_output(result, args.output))
                except Exception as e:
                    print(f"❌ 错误: {e}")
    else:
        if not text:
            print("❌ 请提供描述文本或使用 interactive 模式")
            parser.print_help()
            sys.exit(1)

        if args.command == "parse":
            result = engine.parse_natural_language(text)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\n📋 输入: {text}\n")
            params = engine.parse_natural_language(text)
            print(f"📊 解析结果: {json.dumps(params, ensure_ascii=False, indent=2)}\n")

            result = engine.generate_recommendation(**params)
            print(format_output(result, args.output))


if __name__ == "__main__":
    main()
