#!/usr/bin/env python3
"""
银行压力测试 CLI 入口
Usage: python3 scripts/stress_cli.py generate "压力测试 资产1000亿 资本金80亿 不良率1.5%"
"""

import sys
import os
import re
import json

# Add parent dir to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from stress_engine import StressTestEngine


def parse_input(text: str):
    """解析输入文本"""
    text = text.strip()
    
    # 提取资产
    asset_match = re.search(r'资产\s*(\d+(?:\.\d+)?)\s*([亿万])?', text)
    # 提取资本金
    capital_match = re.search(r'资本金?\s*(\d+(?:\.\d+)?)\s*([亿万])?', text)
    # 提取不良率
    npl_match = re.search(r'不良率\s*(\d+(?:\.\d+)?)\s*%?', text)
    
    total_assets = None
    capital = None
    npl_ratio = None
    
    if asset_match:
        val = float(asset_match.group(1))
        unit = asset_match.group(2)
        total_assets = val if unit == '亿' else val / 10000
    
    if capital_match:
        val = float(capital_match.group(1))
        unit = capital_match.group(2)
        capital = val if unit == '亿' else val / 10000
    
    if npl_match:
        npl_ratio = float(npl_match.group(1))
    
    return total_assets, capital, npl_ratio


def main():
    if len(sys.argv) < 2:
        print("Usage: stress_cli.py <command> [args]")
        print("Commands: generate, report, compare")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "generate":
        if len(sys.argv) < 3:
            text = "压力测试 资产1000亿 资本金80亿 不良率1.5%"
        else:
            text = sys.argv[2]

        total_assets, capital, npl_ratio = parse_input(text)

        if total_assets is None:
            total_assets = 1000.0
        if capital is None:
            capital = 80.0
        if npl_ratio is None:
            npl_ratio = 1.5

        engine = StressTestEngine()
        results = engine.run_stress_test(
            total_assets=total_assets,
            capital=capital,
            npl_ratio=npl_ratio
        )

        # Output format detection
        if len(sys.argv) > 3 and sys.argv[3] == "--format=json":
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(engine.format_report(results))

    elif cmd == "report":
        format_type = "text"
        if len(sys.argv) > 3 and "--format=json" in sys.argv[3]:
            format_type = "json"
        
        # Default test
        engine = StressTestEngine()
        results = engine.run_stress_test(1000, 80, 1.5)
        
        if format_type == "json":
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(engine.format_report(results))

    elif cmd == "compare":
        engine = StressTestEngine()
        results = engine.run_stress_test(1000, 80, 1.5)
        
        base = results["baseline"]
        print("\n=== Baseline vs Stress Scenarios ===")
        print(f"{'Scenario':<8} {'CAR':>8} {'NPL':>8} {'ROE':>8} {'LCR':>8}")
        print("-" * 44)
        print(f"{'Baseline':<8} {base['car']:>7.2f}% {base['npl_ratio']:>7.2f}% {base['roe']:>7.2f}% {base['lcr']:>7.2f}%")
        for name, r in results["stress_scenarios"].items():
            print(f"{name:<8} {r['car']:>7.2f}% {r['npl_ratio']:>7.2f}% {r['roe']:>7.2f}% {r['lcr']:>7.2f}%")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
