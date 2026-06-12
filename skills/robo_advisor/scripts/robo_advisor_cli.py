#!/usr/bin/env python3
"""
Robo Advisor CLI - 智能投顾命令行入口
Usage:
    python3 robo_advisor_cli.py generate "智能投顾 稳健型 资产100万 养老规划"
    python3 robo_advisor_cli.py questionnaire "年龄30 收入50万 投资经验5年 亏损承受20%"
    python3 robo_advisor_cli.py rebalance '{"stocks_china_a":0.30,"bonds_gov":0.50,"cash":0.20}'
"""

import json
import sys
import os

# 确保模块路径正确
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robo_advisor_engine import RoboAdvisorEngine


def cmd_generate(args: list) -> None:
    """生成投顾方案"""
    if not args:
        print("Usage: generate <自然语言描述>", file=sys.stderr)
        print('Example: "智能投顾 稳健型 资产100万 养老规划"', file=sys.stderr)
        return
    user_input = " ".join(args)
    engine = RoboAdvisorEngine()
    result = engine.generate_advisory(user_input)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_questionnaire(args: list) -> None:
    """问卷模式"""
    if not args:
        print("Usage: questionnaire <问卷描述>", file=sys.stderr)
        print('Example: "年龄30 收入50万 投资经验5年 亏损承受20%"', file=sys.stderr)
        return
    import re
    text = " ".join(args)
    engine = RoboAdvisorEngine()
    age_m = re.search(r"年龄(\d+)", text)
    income_m = re.search(r"收入([0-9.]+)万", text)
    exp_m = re.search(r"投资经验(\d+)年", text)
    loss_m = re.search(r"亏损承受([0-9.]+)%", text)
    goal_m = re.search(r"目标([\u4e00-\u9fa5]+)", text)
    result = engine.generate_advisory_from_questionnaire(
        age=int(age_m.group(1)) if age_m else None,
        annual_income=float(income_m.group(1)) if income_m else None,
        invest_experience_years=int(exp_m.group(1)) if exp_m else None,
        loss_tolerance_pct=float(loss_m.group(1)) if loss_m else None,
        investment_goal=goal_m.group(1) if goal_m else "增值",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_rebalance(args: list) -> None:
    """再平衡分析"""
    if not args:
        print("Usage: rebalance <当前配置JSON或描述>", file=sys.stderr)
        print('Example: \'{"stocks_china_a":0.30,"bonds_gov":0.50,"cash":0.20}\'', file=sys.stderr)
        return
    import re, json
    text = " ".join(args)
    # 尝试解析JSON
    try:
        current = json.loads(text)
    except json.JSONDecodeError:
        # 简单解析百分比描述
        current = {}
        patterns = [
            (r"股票\s*([0-9.]+)%", "stocks_china_a"),
            (r"A股\s*([0-9.]+)%", "stocks_china_a"),
            (r"债券\s*([0-9.]+)%", "bonds_gov"),
            (r"现金\s*([0-9.]+)%", "cash"),
            (r"黄金\s*([0-9.]+)%", "alternatives_gold"),
        ]
        for pat, key in patterns:
            m = re.search(pat, text)
            if m:
                current[key] = float(m.group(1)) / 100

    if "total_value" in current:
        total_value = current.pop("total_value")
    else:
        total_value = 1000000.0  # 默认100万

    # 目标配置（默认稳健型）
    engine = RoboAdvisorEngine()
    result_default = engine.generate_advisory("稳健型 资产100万")
    target = {}
    for k, v in result_default["asset_allocation"]["detail"].items():
        target[k] = float(v.rstrip("%")) / 100

    result = engine.calculate_rebalance(current, target, total_value)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Robo Advisor CLI - 智能投顾引擎", file=sys.stderr)
        print(f"Usage: {sys.argv[0]} <command> [args...]", file=sys.stderr)
        print("Commands:", file=sys.stderr)
        print("  generate     - 自然语言生成投顾方案", file=sys.stderr)
        print("  questionnaire - 问卷模式生成投顾方案", file=sys.stderr)
        print("  rebalance    - 再平衡分析", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "generate":
        cmd_generate(sys.argv[2:])
    elif cmd in ("questionnaire", "questionnaire"):
        cmd_questionnaire(sys.argv[2:])
    elif cmd == "rebalance":
        cmd_rebalance(sys.argv[2:])
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
