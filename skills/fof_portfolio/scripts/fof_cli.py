#!/usr/bin/env python3
"""
FOF Portfolio CLI - 基金组合命令行工具
用法: python3 scripts/fof_cli.py generate "FOF组合 平衡型 规模1亿 养老规划 持有5年"
"""

import sys
import os
import json
import argparse

# 添加父目录到路径以便导入fof_engine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fof_engine import FOFEngine


def parse_command(command: str) -> dict:
    """解析FOF组合命令"""
    risk_pref = "平衡型"
    size = "1亿"
    goal = "养老规划"
    period = "5年"

    # 解析风险偏好
    for kw in ["保守型", "稳健型", "平衡型", "积极型", "激进型"]:
        if kw in command:
            risk_pref = kw
            break

    # 解析规模
    for kw in ["亿", "万"]:
        if kw in command:
            idx = command.find(kw)
            size = command[max(0, idx-3):idx+1].strip()
            if "规模" not in size and "组合" not in size:
                break
            else:
                size = command[max(0, idx-2):idx+1].strip()
            break

    # 简化：直接提取亿/万前面的数字
    import re
    size_match = re.search(r'([\d\.]+)(亿|万)', command)
    if size_match:
        size = size_match.group(0)

    # 解析投资目标
    if "养老" in command:
        goal = "养老规划"
    elif "教育" in command:
        goal = "教育金"
    elif "增值" in command:
        goal = "财富增值"
    elif "保值" in command or "保守" in command:
        goal = "资产保值"

    # 解析持有期限
    period_mapping = {
        "5年": ["5年", "长期"],
        "3年": ["3年", "4年"],
        "1年": ["1年", "2年"],
    }
    for pd, keywords in period_mapping.items():
        for kw in keywords:
            if kw in command:
                period = pd if pd != "1年" else "1-2年"
                if "长期" in command:
                    period = "5年以上"
                break
        else:
            continue
        break

    # 更精确的期限解析
    if "5年" in command or "长期" in command:
        period = "5年" if "5年" in command else "长期"
    elif "3年" in command or "4年" in command:
        period = "3年"
    elif "2年" in command:
        period = "2年"
    elif "1年" in command:
        period = "1年"

    return {
        "risk_preference": risk_pref,
        "portfolio_size": size,
        "investment_goal": goal,
        "holding_period": period
    }


def cmd_generate(args):
    """生成FOF组合"""
    engine = FOFEngine()

    # 解析命令
    command = args.command if hasattr(args, 'command') else " ".join(args.args)

    params = parse_command(command)

    print(f"\n🔍 正在根据以下参数生成FOF组合方案...")
    print(f"   风险偏好: {params['risk_preference']}")
    print(f"   组合规模: {params['portfolio_size']}")
    print(f"   投资目标: {params['investment_goal']}")
    print(f"   持有期限: {params['holding_period']}")
    print()

    result = engine.generate_portfolio(
        risk_preference=params['risk_preference'],
        portfolio_size=params['portfolio_size'],
        investment_goal=params['investment_goal'],
        holding_period=params['holding_period']
    )

    # 输出报告
    report = engine.generate_report(result)
    print(report)

    # 如果指定了输出文件，保存JSON
    if hasattr(args, 'output') and args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📁 JSON结果已保存到: {args.output}")


def cmd_list(args):
    """列出内池基金"""
    engine = FOFEngine()
    print("\n📋 内池基金列表 (共{}只)\n".format(len(engine.fund_pool)))
    print(f"{'代码':<10}{'名称':<20}{'类型':<10}{'风险':<8}{'1年收益':<10}{'夏普':<8}{'最大回撤':<10}{'经理':<10}{'规模':<10}")
    print("-" * 96)
    for fund in engine.fund_pool:
        print(f"{fund.code:<10}{fund.name:<20}{fund.fund_type:<10}{fund.risk_level:<8}"
              f"{fund.annual_return_1y:<10.2f}{fund.sharpe_ratio:<8.2f}{fund.max_drawdown:<10.1f}"
              f"{fund.manager_name:<10}{fund.aum:<10.1f}")
    print()


def cmd_screening(args):
    """仅做基金筛选"""
    engine = FOFEngine()
    params = parse_command(" ".join(args.args))
    screened = engine.screen_funds(
        params['risk_preference'],
        params['investment_goal'],
        params['holding_period']
    )
    print(f"\n🎯 基金筛选结果 (匹配{len(screened)}只)\n")
    for i, s in enumerate(screened, 1):
        print(f"{i}. {s.fund.name}({s.fund.code}) - {s.fund.fund_type} - 评分:{s.score:.2f}")
        if s.match_reasons:
            print(f"   匹配原因: {'; '.join(s.match_reasons)}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="FOF Portfolio CLI - 基金组合命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 scripts/fof_cli.py generate "FOF组合 平衡型 规模1亿 养老规划 持有5年"
  python3 scripts/fof_cli.py list
  python3 scripts/fof_cli.py screening "平衡型 养老 5年"
  python3 scripts/fof_cli.py generate "FOF组合 积极型 规模5000万 财富增值 3年" -o result.json
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # generate命令
    gen_parser = subparsers.add_parser('generate', help='生成FOF组合方案')
    gen_parser.add_argument('args', nargs='*', help='命令参数')
    gen_parser.add_argument('-o', '--output', help='输出JSON文件路径')

    # list命令
    subparsers.add_parser('list', help='列出内池基金')

    # screening命令
    screen_parser = subparsers.add_parser('screening', help='基金筛选测试')
    screen_parser.add_argument('args', nargs='*', help='筛选参数')

    args = parser.parse_args()

    if args.command == 'generate':
        cmd_generate(args)
    elif args.command == 'list':
        cmd_list(args)
    elif args.command == 'screening':
        cmd_screening(args)
    else:
        # 默认行为: 接受完整命令字符串
        if len(sys.argv) > 1:
            # 处理直接传入完整命令的情况
            full_command = " ".join(sys.argv[1:])
            if '-o' in full_command or '--output' in full_command:
                parts = full_command.split('-o')[0].strip().split()
                output_file = full_command.split('-o')[1].strip().split()[0] if '-o' in full_command else None
                if '--output' in full_command:
                    parts = full_command.split('--output')[0].strip().split()
                    output_file = full_command.split('--output')[1].strip().split()[0]
                gen_args = argparse.Namespace(command=" ".join(parts), args=parts, output=output_file)
            else:
                gen_args = argparse.Namespace(command=full_command, args=full_command.split(), output=None)
            cmd_generate(gen_args)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
