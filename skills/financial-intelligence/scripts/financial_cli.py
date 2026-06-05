#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial AI CLI Tool

Usage:
    python financial_cli.py invoice <code> <number>
    python financial_cli.py budget <department>
    python financial_cli.py report <company> [year]
    python financial_cli.py tax <company>
    python financial_cli.py expense "<description>" <amount>
    python financial_cli.py cashflow [days]
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines import (
    InvoiceEngine, BudgetEngine, ReportEngine,
    TaxEngine, ExpenseEngine, CashflowEngine
)
from formatters import FinancialFormatter


def main():
    if len(sys.argv) < 2:
        print(FinancialFormatter.format_welcome())
        return
    
    command = sys.argv[1].lower()
    
    if command == "invoice":
        if len(sys.argv) < 4:
            print("Usage: financial_cli.py invoice <code> <number>")
            return
        engine = InvoiceEngine()
        result = engine.verify(sys.argv[2], sys.argv[3])
        print(FinancialFormatter.format_invoice(result))
    
    elif command == "budget":
        dept = sys.argv[2] if len(sys.argv) > 2 else None
        engine = BudgetEngine()
        result = engine.analyze(dept=dept)
        print(FinancialFormatter.format_budget(result))
    
    elif command == "report":
        if len(sys.argv) < 3:
            print("Usage: financial_cli.py report <company> [year]")
            return
        engine = ReportEngine()
        year = int(sys.argv[3]) if len(sys.argv) > 3 else 2025
        result = engine.analyze(sys.argv[2], year=year)
        print(FinancialFormatter.format_report(result))
    
    elif command == "tax":
        company = sys.argv[2] if len(sys.argv) > 2 else None
        engine = TaxEngine()
        result = engine.analyze(company_name=company)
        print(FinancialFormatter.format_tax(result))
    
    elif command == "expense":
        if len(sys.argv) < 4:
            print('Usage: financial_cli.py expense "<description>" <amount>')
            return
        engine = ExpenseEngine()
        result = engine.process(description=sys.argv[2], amount=float(sys.argv[3]))
        print(FinancialFormatter.format_expense(result))
    
    elif command == "cashflow":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        engine = CashflowEngine()
        result = engine.forecast(days=days)
        print(FinancialFormatter.format_cashflow(result))
    
    else:
        print(f"Unknown command: {command}")
        print(FinancialFormatter.format_help())


if __name__ == "__main__":
    main()
