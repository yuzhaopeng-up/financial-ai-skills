#!/usr/bin/env python3
"""
fraud_alert CLI 入口
用法:
    python alert_cli.py generate "fraud_alert 交易金额5万 时间22:00 地点异地 设备更换"
    python alert_cli.py alert --amount 50000 --time "22:00" --location "异地" --device-change
    python alert_cli.py rule-list
"""

import sys
import os
import argparse
import json
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from fraud_alert_engine import FraudAlertEngine


def cmd_generate(engine, args):
    """从自然语言生成预警"""
    text = args.text
    result = engine.alert_from_nl(text)
    print_result(result)


def cmd_alert(engine, args):
    """直接传入参数预警"""
    result = engine.alert(
        amount=args.amount,
        transaction_type=args.type or "转账",
        transaction_time=args.time,
        location=args.location,
        device_change=args.device_change,
        counterparty=args.counterparty,
    )
    print_result(result)


def cmd_rule_list(engine, args):
    """列出所有规则"""
    rules = engine.RULES
    print(f"\n{'='*70}")
    print(f"  fraud_alert 预警规则清单 (共{len(rules)}条)")
    print(f"{'='*70}")

    groups = {"A": [], "B": [], "C": []}
    for r in rules:
        groups[r["severity"]].append(r)

    severity_labels = {
        "A": "🔴 红色高危",
        "B": "🟠 橙色中危",
        "C": "🟡 黄色低危",
    }

    for sev, label in severity_labels.items():
        print(f"\n{label} ({len(groups[sev])}条)")
        print("-" * 70)
        for r in groups[sev]:
            print(f"  [{r['id']}] {r['name']:<20s} 置信度:{r['confidence']:.0%}  类别:{r['category']}")


def print_result(result):
    """格式化打印预警结果"""
    emoji_map = {"红色": "🔴", "橙色": "🟠", "黄色": "🟡", "正常": "✅"}
    emoji = emoji_map.get(result.level, "⚪")

    print(f"\n{'='*60}")
    print(f"  🚨 实时欺诈预警报告")
    print(f"{'='*60}")
    print(f"")
    print(f"  预警等级: {emoji} 【{result.level}】")
    print(f"  风险评分: {result.score}/100")
    print(f"  人工复核: {'是' if result.review_required else '否'} (紧迫度: {result.review_urgency})")
    print(f"")
    print(f"  {'─'*60}")
    print(f"  📋 检测摘要:")
    print(f"  {result.summary}")
    print(f"")
    print(f"  {'─'*60}")
    print(f"  ⚠️  触发规则 ({len(result.rules)}条):")

    if not result.rules:
        print(f"    (无)")
    else:
        severity_emoji = {"A": "🔴", "B": "🟠", "C": "🟡"}
        for r in sorted(result.rules, key=lambda x: ({"A": 0, "B": 1, "C": 2}[x.severity], -x.confidence)):
            sev_emoji = severity_emoji.get(r.severity, "⚪")
            print(f"    {sev_emoji} [{r.id}] {r.name}")
            print(f"        置信度: {r.confidence:.0%}  |  {r.detail}")

    print(f"")
    print(f"  {'─'*60}")
    print(f"  ✅ 紧急处置建议:")

    if not result.actions:
        print(f"    (无)")
    else:
        for action in result.actions:
            print(f"    {action}")

    print(f"")
    print(f"{'='*60}")

    # JSON输出
    if os.environ.get("ALERT_OUTPUT_JSON", "").lower() in ("1", "true", "yes"):
        print("\n--- JSON OUTPUT ---")
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="fraud_alert CLI - 实时欺诈预警",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python alert_cli.py generate "fraud_alert 交易金额5万 时间22:00 地点异地 设备更换"
  python alert_cli.py alert --amount 50000 --time "22:00" --location "异地"
  python alert_cli.py rule-list
        """
    )
    subparsers = parser.add_subparsers(dest="cmd", help="子命令")

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="从自然语言生成预警")
    gen_parser.add_argument("text", help="自然语言描述")

    # alert 子命令
    alert_parser = subparsers.add_parser("alert", help="直接传入参数预警")
    alert_parser.add_argument("--amount", type=float, required=True, help="交易金额(元)")
    alert_parser.add_argument("--time", type=str, default=None, help="交易时间(HH:MM)")
    alert_parser.add_argument("--type", type=str, default=None, help="交易类型")
    alert_parser.add_argument("--location", type=str, default=None, help="地点")
    alert_parser.add_argument("--device-change", action="store_true", help="设备是否更换")
    alert_parser.add_argument("--counterparty", type=str, default=None, help="对手方")

    # rule-list 子命令
    subparsers.add_parser("rule-list", help="列出所有预警规则")

    args = parser.parse_args()
    engine = FraudAlertEngine()

    if args.cmd == "generate":
        cmd_generate(engine, args)
    elif args.cmd == "alert":
        cmd_alert(engine, args)
    elif args.cmd == "rule-list":
        cmd_rule_list(engine, args)
    else:
        # 默认：尝试作为自然语言处理
        if len(sys.argv) > 1:
            text = " ".join(sys.argv[1:])
            result = engine.alert_from_nl(text)
            print_result(result)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
