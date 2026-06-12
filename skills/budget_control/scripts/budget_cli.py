#!/usr/bin/env python3
"""
Budget Control CLI - 预算管控命令行工具

用法:
    python3 budget_cli.py generate "预算管控 市场部 差旅费 预算20万 已用18万 剩余2个月"
    python3 budget_cli.py parse "预算管控 市场部 差旅费 预算20万 已用18万 剩余2个月"
    python3 budget_cli.py report "预算管控 市场部 差旅费 预算20万 已用18万 剩余2个月"
"""

import sys
import json
import argparse

# 添加父目录到路径以支持模块导入
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from budget_engine import BudgetControlEngine, parse_input


def cmd_generate(text: str) -> dict:
    """生成预算分析结果（JSON格式）"""
    engine = BudgetControlEngine()
    parsed = parse_input(text)
    result = engine.analyze(**parsed)
    return result.to_dict()


def cmd_report(text: str) -> str:
    """生成格式化的文本报告"""
    engine = BudgetControlEngine()
    parsed = parse_input(text)
    result = engine.analyze(**parsed)
    return engine.format_report(result)


def cmd_parse(text: str) -> dict:
    """仅解析输入参数"""
    return parse_input(text)


def main():
    parser = argparse.ArgumentParser(
        description="预算管控CLI工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 budget_cli.py generate "预算管控 市场部 差旅费 预算20万 已用18万 剩余2个月"
    python3 budget_cli.py parse "预算管控 市场部 差旅费 预算20万 已用18万 剩余2个月"
    python3 budget_cli.py report "预算管控 市场部 差旅费 预算20万 已用18万 剩余2个月"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成预算分析结果JSON")
    gen_parser.add_argument("text", help="预算信息文本")
    
    # parse 命令
    parse_parser = subparsers.add_parser("parse", help="解析输入参数")
    parse_parser.add_argument("text", help="预算信息文本")
    
    # report 命令
    report_parser = subparsers.add_parser("report", help="生成格式化报告")
    report_parser.add_argument("text", help="预算信息文本")
    
    args = parser.parse_args()
    
    if not args.command:
        # 默认行为：generate
        if len(sys.argv) > 1:
            text = " ".join(sys.argv[1:])
        else:
            parser.print_help()
            return 0
    
    try:
        if args.command == "generate":
            result = cmd_generate(args.text)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "parse":
            result = cmd_parse(args.text)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "report":
            result = cmd_report(args.text)
            print(result)
        else:
            # 兼容旧用法：直接作为generate命令
            text = " ".join(sys.argv[1:])
            result = cmd_generate(text)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        return 0
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
