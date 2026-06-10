#!/usr/bin/env python3
"""
投资组合优化 CLI 入口
用法：
    python3 scripts/port_opt_cli.py generate "组合优化 当前持仓股票70%债券20%现金10% 目标风险降低"
    python3 scripts/port_opt_cli.py parse "股票60%债券30%现金10%"
"""

import sys
import json
import argparse
from pathlib import Path

# 将父目录加入路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from port_opt_engine import PortfolioOptimizeEngine, parse_cli_args


def cmd_generate(text: str, format: str = "text"):
    """生成组合优化方案"""
    engine = PortfolioOptimizeEngine()

    # 解析输入
    args = parse_cli_args(text)
    portfolio = args["portfolio"]
    goal = args["goal"]
    risk_pref = args["risk_preference"]

    if not portfolio:
        print("❌ 未能从文本中解析出有效持仓信息")
        print("请提供类似格式：股票70%债券20%现金10%")
        return 1

    print(f"\n📊 组合优化分析")
    print(f"   当前持仓：{portfolio}")
    print(f"   优化目标：{goal}")
    print(f"   风险偏好：{risk_pref}")
    print("-" * 50)

    # 执行优化
    result = engine.optimize(
        current_portfolio=portfolio,
        risk_preference=risk_pref,
        optimization_goal=goal,
    )

    if format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    # 格式化输出
    opt_weights = result["optimized_portfolio"]["weights"]
    opt_metrics = result["optimized_portfolio"]["metrics"]
    cur_metrics = result["current_portfolio"]["metrics"]

    print(f"\n📈 优化后资产配置")
    print(f"   {'资产':<12} {'当前':>8} {'优化后':>8} {'变动':>8}")
    print(f"   {'-'*40}")

    all_assets = set(list(result["current_portfolio"]["weights"].keys()) +
                     list(opt_weights.keys()))

    for asset in sorted(all_assets, key=lambda x: opt_weights.get(x, 0), reverse=True):
        cur = result["current_portfolio"]["weights"].get(asset, 0)
        opt = opt_weights.get(asset, 0)
        chg = opt - cur
        chg_str = f"{chg:+.2%}"
        print(f"   {asset:<12} {cur:>8.2%} {opt:>8.2%} {chg_str:>8}")

    print(f"\n📉 风险收益指标对比")
    print(f"   {'指标':<16} {'当前':>10} {'优化后':>10} {'变化':>10}")
    print(f"   {'-'*50}")
    print(f"   {'年化收益率':<14} {cur_metrics['expected_return']:>10.2%} "
          f"{opt_metrics['expected_return']:>10.2%} "
          f"{result['comparison']['return_change']:>+10.2%}")
    print(f"   {'年化波动率':<14} {cur_metrics['volatility']:>10.2%} "
          f"{opt_metrics['volatility']:>10.2%} "
          f"{result['comparison']['volatility_change']:>+10.2%}")
    print(f"   {'夏普比率':<16} {cur_metrics['sharpe_ratio']:>10.3f} "
          f"{opt_metrics['sharpe_ratio']:>10.3f} "
          f"{result['comparison']['sharpe_change']:>+10.3f}")
    print(f"   {'最大回撤(估)':<14} {cur_metrics['max_drawdown']:>10.2%} "
          f"{opt_metrics['max_drawdown']:>10.2%}")
    print(f"   {'95% VaR(估)':<14} {cur_metrics['var_95']:>10.2%} "
          f"{opt_metrics['var_95']:>10.2%}")

    print(f"\n💡 优化摘要")
    print(f"   {result['comparison']['summary']}")

    print(f"\n🔄 调仓建议（按优先级）")
    priority_list = result["execution_priority"]
    for item in priority_list:
        if item["action"] == "hold":
            continue
        emoji = "📈" if item["action"] == "buy" else "📉"
        priority_label = f"P{item['priority']}" if item['priority'] < 99 else "P99"
        print(f"   {emoji} [{priority_label}] {item['action'].upper()} "
              f"{item['asset']}: {item['current_weight']:.2%} → {item['target_weight']:.2%} "
              f"({item['ratio']:+.2%})")
        print(f"       → {item['reason']}")

    print()
    return 0


def cmd_parse(text: str):
    """解析持仓文本"""
    engine = PortfolioOptimizeEngine()
    result = engine.parse_portfolio_from_text(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description="投资组合优化工具")
    sub = parser.add_subparsers(dest="cmd")

    gen = sub.add_parser("generate", help="生成组合优化方案")
    gen.add_argument("text", help="自然语言描述，如：组合优化 当前持仓股票70%债券20%现金10% 目标风险降低")
    gen.add_argument("--format", "-f", choices=["text", "json"], default="text")

    par = sub.add_parser("parse", help="解析持仓文本")
    par.add_argument("text", help="持仓描述，如：股票60%债券30%现金10%")

    args = parser.parse_args()

    if args.cmd == "generate":
        return cmd_generate(args.text, args.format)
    elif args.cmd == "parse":
        return cmd_parse(args.text)
    else:
        # 兼容：直接传入generate子命令的文本
        if len(sys.argv) > 1:
            # 去掉 "generate" 子命令前缀
            remaining = " ".join(sys.argv[1:]).strip()
            if remaining.startswith("generate"):
                remaining = remaining[len("generate"):].strip()
            if remaining:
                return cmd_generate(remaining)
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
