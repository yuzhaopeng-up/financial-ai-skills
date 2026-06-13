#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抵押物估值引擎 CLI
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collateral_valuation_engine import CollateralValuationEngine


def main():
    parser = argparse.ArgumentParser(description="抵押物智能估值引擎 CLI")
    parser.add_argument("--type", "-t", default="房产", help="抵押物类型")
    parser.add_argument("--location", "-l", default="", help="地址/规格")
    parser.add_argument("--area", "-a", default="", help="面积/数量")
    parser.add_argument("--description", "-d", default="", help="补充描述")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="输出格式")
    parser.add_argument("--api", action="store_true", help="API模式（静默）")
    
    args = parser.parse_args()
    
    engine = CollateralValuationEngine(api_mode=args.api)
    
    if not args.location:
        print("🦞 抵押物智能估值引擎 v1.0")
        print()
        print("用法:")
        print("  python collateral_valuation_cli.py -t 房产 -l 北京朝阳 -a 100平 -d 房龄5年")
        print()
        print("参数说明:")
        print("  -t/--type      抵押物类型（房产/设备/车辆/土地/应收账款/股权）")
        print("  -l/--location  地址或规格")
        print("  -a/--area      面积或数量")
        print("  -d/--description 补充描述")
        print("  -f/--format    输出格式（text/json）")
        print()
        
        # 示例
        sample = [
            ("房产", "北京朝阳CBD", "100平", "房龄5年"),
            ("设备", "医疗设备型号ABC", "2台", "使用约3年"),
            ("车辆", "宝马530Li", "1辆", "使用约1年"),
            ("土地", "上海浦东", "5000平方米", "工业用地"),
        ]
        
        print("示例:")
        for ctype, loc, area, desc in sample:
            result = engine.valuate(ctype, loc, area, desc)
            if args.format == "json":
                print(engine.format_json(result))
            else:
                print(engine.format_text(result))
            print()
        return
    
    result = engine.valuate(args.type, args.location, args.area, args.description)
    
    if args.format == "json":
        print(engine.format_json(result))
    else:
        print(engine.format_text(result))


if __name__ == "__main__":
    sys.exit(main())
