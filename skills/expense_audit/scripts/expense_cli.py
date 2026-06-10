#!/usr/bin/env python3
"""
费用报销审计 CLI 入口

用法：
    python3 scripts/expense_cli.py generate "费用报销 张三 市场部 招待费 5000元 事前未审批"
    python3 scripts/expense_cli.py audit --employee 张三 --department 市场部 --type 招待费 --amount 5000 --invoice 有 --pre-approval 无
    python3 scripts/expense_cli.py interactive
"""

import sys
import json
import argparse

# 添加父目录到路径以便导入
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from expense_engine import ExpenseAuditEngine


def cmd_generate(engine: ExpenseAuditEngine, args):
    """从自然语言文本生成审计报告"""
    result = engine.audit_from_text(args.text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_audit(engine: ExpenseAuditEngine, args):
    """直接指定参数审计"""
    result = engine.audit(
        employee=args.employee,
        department=args.department,
        expense_type=args.type,
        amount=float(args.amount),
        invoice=args.invoice,
        pre_approval=args.pre_approval,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_interactive(engine: ExpenseAuditEngine):
    """交互式输入"""
    print("=" * 50)
    print("费用报销审计 - 交互模式")
    print("=" * 50)

    employee = input("员工姓名：").strip()
    department = input("部门：").strip()
    expense_type = input("费用类型（招待费/差旅费/办公费/交通费/培训费/其他）：").strip()
    amount = float(input("报销金额（元）：").strip())
    invoice = input("发票（有/无/待补）：").strip() or "有"
    pre_approval = input("事前审批（有/无）：").strip() or "有"

    print()
    result = engine.audit(
        employee=employee,
        department=department,
        expense_type=expense_type,
        amount=amount,
        invoice=invoice,
        pre_approval=pre_approval,
    )
    print("\n审计结果：", result["status"])
    print("风险等级：", result["risk_level"])
    if result["violations"]:
        print("违规类型：", ", ".join(result["violations"]))
    if result["suggestions"]:
        print("合规建议：")
        for s in result["suggestions"]:
            print(f"  - {s}")
    print("说明：", result["details"])


def main():
    parser = argparse.ArgumentParser(description="费用报销审计工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="从自然语言文本生成审计报告")
    gen_parser.add_argument("text", help="报销描述文本，如：费用报销 张三 市场部 招待费 5000元 事前未审批")

    # audit 子命令
    audit_parser = subparsers.add_parser("audit", help="直接指定参数审计")
    audit_parser.add_argument("--employee", required=True, help="员工姓名")
    audit_parser.add_argument("--department", required=True, help="部门")
    audit_parser.add_argument("--type", required=True, help="费用类型")
    audit_parser.add_argument("--amount", required=True, help="报销金额")
    audit_parser.add_argument("--invoice", default="有", help="发票（有/无/待补）")
    audit_parser.add_argument("--pre-approval", dest="pre_approval", default="有", help="事前审批（有/无）")

    # interactive 子命令
    subparsers.add_parser("interactive", help="交互式输入")

    args = parser.parse_args()

    # API模式静默
    api_mode = args.command in ["generate", "audit"] and not sys.stdout.isatty()
    engine = ExpenseAuditEngine(api_mode=api_mode)

    if args.command == "generate":
        cmd_generate(engine, args)
    elif args.command == "audit":
        cmd_audit(engine, args)
    elif args.command == "interactive":
        cmd_interactive(engine)
    else:
        # 默认使用generate模式处理标准输入
        if not sys.stdin.isatty():
            text = sys.stdin.read().strip()
            if text:
                cmd_generate(engine, argparse.Namespace(text=text))
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
