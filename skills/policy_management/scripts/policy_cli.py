#!/usr/bin/env python3
"""
保单管理 CLI 入口

用法：
    python3 scripts/policy_cli.py generate "保单检视 寿险50万 重疾30万 年缴保费2万 已缴5年"
    python3 scripts/policy_cli.py generate "保单检视 寿险50万 重疾30万 年缴保费2万 已缴5年 年收入30万 负债80万"
    python3 scripts/policy_cli.py report --policies '{"type":"寿险","sum_insured":500000}' --premium 20000 --years 5
    python3 scripts/policy_cli.py suggest --years-paid 5 --total-premium 20000
"""

import argparse
import json
import sys
import os

# 添加父目录到路径以支持模块导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from policy_engine import PolicyManagementEngine


def cmd_generate(args):
    """从自然语言文本生成保单检视报告"""
    engine = PolicyManagementEngine()

    # 解析输入文本
    params = engine.parse_cli_input(args.text)

    if not params.get("policies"):
        print("⚠️ 未能识别保单信息，请确保包含险种和保额，如：寿险50万 重疾30万")
        sys.exit(1)

    if params.get("total_annual_premium", 0) == 0:
        print("⚠️ 未能识别年缴保费，请包含年缴保费信息，如：年缴保费2万")
        sys.exit(1)

    if params.get("years_paid", 0) == 0:
        print("⚠️ 未能识别已缴年限，请包含已缴年限，如：已缴5年")
        sys.exit(1)

    # 生成报告
    result = engine.generate_review(**params)

    # 格式化输出
    if args.format == "text":
        print(engine.format_report(result))
    elif args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.format == "wecom":
        # 企业微信卡片格式（简化版）
        print(format_wecom_card(result))


def cmd_report(args):
    """从结构化参数生成报告"""
    engine = PolicyManagementEngine()

    # 解析保单JSON
    try:
        policies = json.loads(args.policies) if args.policies else []
    except json.JSONDecodeError:
        print("⚠️ 保单JSON格式错误")
        sys.exit(1)

    result = engine.generate_review(
        policies=policies,
        total_annual_premium=args.premium,
        years_paid=args.years,
        client_info=args.client_info
    )

    if args.format == "text":
        print(engine.format_report(result))
    elif args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_suggest(args):
    """快速保全建议"""
    engine = PolicyManagementEngine()

    # 构建简化参数
    params = {
        "policies": [
            {"type": "寿险", "sum_insured": 0},
            {"type": "重疾", "sum_insured": 0},
        ],
        "total_annual_premium": args.total_premium,
        "years_paid": args.years_paid,
    }

    result = engine.generate_review(**params)

    print("【保全建议】")
    for i, s in enumerate(result["policy_suggestions"], 1):
        print(f"  {i}. [{s['priority']}级] {s['action']} {s['target']}")
        print(f"     {s['detail']}")
        print()


def format_wecom_card(result: dict) -> str:
    """格式化为企业微信消息卡片"""
    cg = result["coverage_gap"]
    rn = result["renewal_reminder"]

    # 构建卡片内容
    card = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"""**🏦 保单检视报告**

**保障缺口分析**
• 寿险：{cg['current_life_cover']/10000:.1f}万 / 应有{cg['needed_life_cover']/10000:.1f}万，缺口**{cg['life_gap']/10000:.1f}万**
• 重疾：{cg['current_critical_illness']/10000:.1f}万 / 应有{cg['needed_critical_illness']/10000:.1f}万，缺口**{cg['critical_gap']/10000:.1f}万**

**现金价值**
• 当前现金价值：**{result['cash_value']['current_cv']/10000:.2f}万**
• 已缴保费：{result['cash_value']['total_premium_paid']/10000:.2f}万
• 回本年度：第{result['cash_value']['break_even_year']}年

**续期提醒**
• 下次缴费：{rn['next_due_amount']/10000:.2f}万 | {rn['lapse_risk']}

**保全建议**
{' | '.join([f"{s['action']}({s['priority']}级)" for s in result['policy_suggestions'][:3]])}"""
        }
    }

    return json.dumps(card, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="保单管理 CLI")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="从文本生成检视报告")
    gen_parser.add_argument("text", help="保单信息文本")
    gen_parser.add_argument("--format", "-f", choices=["text", "json", "wecom"],
                           default="text", help="输出格式")

    # report 子命令
    rep_parser = subparsers.add_parser("report", help="从参数生成检视报告")
    rep_parser.add_argument("--policies", help="保单JSON数组")
    rep_parser.add_argument("--premium", type=float, required=True, help="年缴保费")
    rep_parser.add_argument("--years", type=int, required=True, help="已缴年限")
    rep_parser.add_argument("--format", "-f", choices=["text", "json"],
                           default="text", help="输出格式")
    rep_parser.add_argument("--client-info", help="客户信息JSON")

    # suggest 子命令
    sug_parser = subparsers.add_parser("suggest", help="快速保全建议")
    sug_parser.add_argument("--total-premium", type=float, required=True, help="年缴保费")
    sug_parser.add_argument("--years-paid", type=int, required=True, help="已缴年限")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "suggest":
        cmd_suggest(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
