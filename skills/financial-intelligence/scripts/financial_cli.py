#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务智能体 CLI 工具

用于 Hermes Agent 调用财务智能体引擎。
支持6大财务场景：发票查验、预算管控、财报速读、税务筹划、费用报销、资金预测

用法:
    python3 financial_cli.py <scenario> [args...]

示例:
    python3 financial_cli.py invoice 011001900111 12345678
    python3 financial_cli.py budget 市场部
    python3 financial_cli.py report 美的集团 2025
    python3 financial_cli.py tax 银联商务
    python3 financial_cli.py expense "北京出差机票" 1580
    python3 financial_cli.py cashflow 30
"""

import sys
import os
import json

# 添加引擎路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SKILL_DIR)

# 添加 wecom formatters 路径以导入 BaseFormatter
sys.path.insert(0, os.path.join(SKILL_DIR, "..", "..", "..", "tmp", "openclaw-workspace", "wecom", "formatters"))

# 添加 openclaw-workspace 路径
sys.path.insert(0, "/tmp/openclaw-workspace")
sys.path.insert(0, "/tmp/openclaw-workspace/wecom/formatters")

from engines import (
    InvoiceEngine, BudgetEngine, ReportEngine,
    TaxEngine, ExpenseEngine, CashflowEngine
)
from formatters import FinancialFormatter


def main():
    if len(sys.argv) < 2:
        print("用法: python3 financial_cli.py <scenario> [args...]")
        print("场景: invoice, budget, report, tax, expense, cashflow")
        sys.exit(1)

    scenario = sys.argv[1].lower()
    args = sys.argv[2:]
    formatter = FinancialFormatter()

    try:
        if scenario == "invoice":
            engine = InvoiceEngine()
            code = args[0] if len(args) > 0 else "011001900111"
            no = args[1] if len(args) > 1 else "12345678"
            result = engine.verify(code, no)
            output = formatter.format_invoice(result)

        elif scenario == "budget":
            engine = BudgetEngine()
            dept = args[0] if len(args) > 0 else None
            result = engine.analyze(dept=dept)
            output = formatter.format_budget(result)

        elif scenario == "report":
            engine = ReportEngine()
            company = args[0] if len(args) > 0 else "美的集团"
            year = int(args[1]) if len(args) > 1 else None
            result = engine.analyze(company_name=company, year=year)
            output = formatter.format_report(result)

        elif scenario == "tax":
            engine = TaxEngine()
            company = args[0] if len(args) > 0 else None
            result = engine.analyze(company_name=company)
            output = formatter.format_tax(result)

        elif scenario == "expense":
            engine = ExpenseEngine()
            desc = args[0] if len(args) > 0 else "差旅费"
            amount = float(args[1]) if len(args) > 1 else 100
            result = engine.process(description=desc, amount=amount)
            output = formatter.format_expense(result)

        elif scenario == "cashflow":
            engine = CashflowEngine()
            days = int(args[0]) if len(args) > 0 else 30
            result = engine.forecast(days=days)
            output = formatter.format_cashflow(result)

        else:
            print(f"未知场景: {scenario}")
            print("支持的场景: invoice, budget, report, tax, expense, cashflow")
            sys.exit(1)

        print(output)

    except Exception as e:
        print(f"❌ 处理失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
