#!/usr/bin/env python3
"""
反欺诈检测 CLI
用法:
  python fraud_cli.py generate "反欺诈 交易金额50万 时间凌晨2点 对方是新客户"
  python fraud_cli.py batch tests/test_cases.json
  python fraud_cli.py interactive
"""

import json
import sys
import os

# 确保导入路径正确
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fraud_engine import FraudDetectionEngine


def format_result(result):
    """格式化输出"""
    level_emoji = {"低": "🟢", "中": "🟡", "高": "🟠", "极高": "🔴"}
    emoji = level_emoji.get(result.level, "⚪")

    lines = []
    lines.append(f"{'='*50}")
    lines.append(f"  🚨 反欺诈检测报告")
    lines.append(f"{'='*50}")
    lines.append(f"  风险评分: {result.score}/100 {emoji} [{result.level}风险]")
    lines.append(f"")

    if result.rules:
        lines.append(f"  触发规则 ({len(result.rules)}条):")
        # 按置信度排序
        sorted_rules = sorted(result.rules, key=lambda r: -r.confidence)
        for r in sorted_rules:
            conf_bar = "█" * int(r.confidence * 10) + "░" * (10 - int(r.confidence * 10))
            lines.append(f"    [{r.id}] {r.name}")
            lines.append(f"        置信度: {r.confidence:.0%} | {conf_bar}")
            if r.detail:
                lines.append(f"        详情: {r.detail}")
            lines.append("")
    else:
        lines.append("  ✅ 未检测到异常规则")

    lines.append(f"  建议行动:")
    for i, action in enumerate(result.actions, 1):
        lines.append(f"    {i}. {action}")

    lines.append("")
    lines.append(f"  摘要: {result.summary}")
    lines.append(f"{'='*50}")
    return "\n".join(lines)


def cmd_generate(args):
    """生成模式"""
    text = " ".join(args) if args else ""
    if not text:
        print("错误: 请提供检测描述")
        print(__doc__)
        return 1

    engine = FraudDetectionEngine()
    result = engine.detect_from_nl(text)

    print(format_result(result))

    # JSON输出
    if "--json" in args:
        print("\n--- JSON Output ---")
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))

    return 0


def cmd_batch(args):
    """批量测试模式"""
    if not args:
        print("错误: 请提供测试用例文件路径")
        return 1

    filepath = args[0]
    if not os.path.exists(filepath):
        print(f"错误: 文件不存在 {filepath}")
        return 1

    with open(filepath, "r", encoding="utf-8") as f:
        cases = json.load(f)

    engine = FraudDetectionEngine()
    passed = 0
    failed = 0

    print(f"\n{'='*50}")
    print(f"  批量测试: {len(cases)}个用例")
    print(f"{'='*50}\n")

    for i, case in enumerate(cases, 1):
        result = engine.detect_from_nl(case.get("input", ""))
        expected_level = case.get("expected_level", "低")

        ok = result.level == expected_level
        status = "✅" if ok else "❌"
        if ok:
            passed += 1
        else:
            failed += 1

        print(f"  [{i}] {status} {case.get('name', case.get('input','')[:30])}")
        print(f"       预期: {expected_level} | 实际: {result.level} | 评分: {result.score}")

    print(f"\n{'='*50}")
    print(f"  结果: {passed}通过 / {failed}失败 / {len(cases)}总计")
    print(f"{'='*50}")

    return 0


def cmd_interactive(args):
    """交互模式"""
    engine = FraudDetectionEngine()
    print("=" * 50)
    print("  反欺诈检测 - 交互模式")
    print("  输入自然语言描述交易，输入 q 退出")
    print("=" * 50)
    print()

    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n退出")
            break

        if text.lower() in ("q", "quit", "exit"):
            break
        if not text:
            continue

        result = engine.detect_from_nl(text)
        print(format_result(result))
        print()

    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 0

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "generate":
        return cmd_generate(args)
    elif cmd == "batch":
        return cmd_batch(args)
    elif cmd == "interactive":
        return cmd_interactive(args)
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
        return 1


if __name__ == "__main__":
    sys.exit(main())
