#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
估值核算辅助引擎 CLI
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from valuation_helper_engine import ValuationHelperEngine


def main():
    parser = argparse.ArgumentParser(description="估值核算辅助引擎 CLI")
    parser.add_argument("--positions", "-p", type=str, help="持仓文本，如: 股票A 1000股@10.5元")
    parser.add_argument("--date", "-d", type=str, help="净值日期，如: 2024-01-15")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="输出格式")
    parser.add_argument("--input", "-i", type=str, help="从文件读取持仓数据(JSON格式)")
    
    args = parser.parse_args()
    
    engine = ValuationHelperEngine()
    
    # 读取输入
    positions_data = None
    
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            positions_data = json.load(f)
    elif args.positions:
        positions_data = args.positions
    else:
        # 默认示例
        positions_data = "招商银行 1000股@35.5元, 贵州茅台 200股@1680元, 沪深300ETF 5000份@3.85元, 现金 50000元"
        print("📋 使用默认示例持仓:", positions_data)
    
    # 解析持仓
    positions = engine.parse_positions(positions_data)
    
    # 模拟价格更新(实际场景从行情API获取)
    price_map = {
        "招商银行": 36.8,
        "贵州茅台": 1650.0,
        "沪深300ETF": 3.92,
    }
    positions = engine.update_prices(positions, price_map)
    
    # 计算估值
    result = engine.calculate_valuation(positions, nav_date=args.date)
    
    # 输出
    if args.format == "json":
        print(engine.format_json(result))
    else:
        print(engine.format_text(result))


if __name__ == "__main__":
    import json
    sys.exit(main())
