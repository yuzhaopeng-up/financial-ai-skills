#!/usr/bin/env python3
"""
资金预测 CLI 入口

用法：
    python3 scripts/cashflow_cli.py generate "资金预测 当前资金200万 应收500万 应付300万 月支出100万"
    python3 scripts/cashflow_cli.py parse 200 500 300 100
    python3 scripts/cashflow_cli.py help
"""

import sys
import json
import os

# 将 skills 目录加入路径以便直接导入 engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cashflow_engine import CashflowForecastEngine


def cmd_generate(text: str) -> int:
    """根据自然语言生成资金预测报告"""
    engine = CashflowForecastEngine()
    parsed = engine.parse_input(text)
    if not parsed:
        print("❌ 无法解析输入，请检查格式。", file=sys.stderr)
        print("示例：资金预测 当前资金200万 应收500万 应付300万 月支出100万", file=sys.stderr)
        return 1

    result = engine.forecast(**parsed)
    print(engine.format_text(result))
    return 0


def cmd_parse(current: float, receivables: float, payables: float, monthly_expense: float) -> int:
    """直接传入数值进行预测"""
    engine = CashflowForecastEngine()
    result = engine.forecast(current, receivables, payables, monthly_expense)
    print(engine.format_text(result))
    return 0


def cmd_json(text: str) -> int:
    """输出 JSON 格式"""
    engine = CashflowForecastEngine()
    parsed = engine.parse_input(text)
    if not parsed:
        print("❌ 无法解析输入", file=sys.stderr)
        return 1
    result = engine.forecast(**parsed)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main():
    if len(sys.argv) < 2:
        print("用法：")
        print("  python3 scripts/cashflow_cli.py generate <文本>")
        print("  python3 scripts/cashflow_cli.py parse <当前资金> <应收> <应付> <月支出>")
        print("  python3 scripts/cashflow_cli.py json <文本>")
        print("  python3 scripts/cashflow_cli.py help")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "help":
        print(__doc__)
    elif cmd == "generate":
        if len(sys.argv) < 3:
            print("❌ 请提供预测文本", file=sys.stderr)
            sys.exit(1)
        text = " ".join(sys.argv[2:])
        sys.exit(cmd_generate(text))
    elif cmd == "parse":
        if len(sys.argv) < 6:
            print("❌ 请提供4个数值参数：当前资金 应收 应付 月支出", file=sys.stderr)
            sys.exit(1)
        try:
            args = [float(x) for x in sys.argv[2:6]]
        except ValueError:
            print("❌ 参数必须为数字", file=sys.stderr)
            sys.exit(1)
        sys.exit(cmd_parse(*args))
    elif cmd == "json":
        if len(sys.argv) < 3:
            print("❌ 请提供预测文本", file=sys.stderr)
            sys.exit(1)
        text = " ".join(sys.argv[2:])
        sys.exit(cmd_json(text))
    else:
        # 兜底：所有参数当作 generate 处理
        text = " ".join(sys.argv[1:])
        sys.exit(cmd_generate(text))


if __name__ == "__main__":
    main()
