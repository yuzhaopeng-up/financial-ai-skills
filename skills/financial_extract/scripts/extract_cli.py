#!/usr/bin/env python3
"""
财报智能提取 CLI
用法：
  python3 extract_cli.py generate "财报提取 某公司 营收1000万 净利润80万 资产2000万 负债1200万"
"""

import sys
import json
import os

# 确保模块路径可导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from extract_engine import FinancialExtractEngine


def cmd_generate(text: str, format: str = "text"):
    engine = FinancialExtractEngine(api_mode=(format == "json"))
    result = engine.extract_from_text(text)

    if format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["summary"])
        print()
        print("📈 财务指标：")
        for k, v in result["indicators"].items():
            print(f"  {k}: {v}")
        print()
        print("🔬 杜邦分析：")
        for k, v in result["dupont"].items():
            if k != "ROE分解":
                print(f"  {k}: {v}")
        print(f"  {result['dupont']['ROE分解']}")
        print()
        print("📊 同业对比：")
        print(f"  {'指标':<8} {'某公司':>8} {'行业均值':>8} {'参考值'}")
        for row in result["industry_comparison"]:
            print(f"  {row['指标']:<8} {row['某公司']:>8} {row['行业均值']:>8} {row['参考值']}")
        print()
        print("⚠️ 预警：")
        for alert in result["alerts"]:
            print(f"  {alert}")


def main():
    args = sys.argv[1:]

    if not args:
        print("用法: extract_cli.py generate \"财报提取 某公司 营收1000万 净利润80万 资产2000万 负债1200万\"")
        sys.exit(1)

    cmd = args[0]

    if cmd == "generate":
        text = " ".join(args[1:])
        fmt = "text"
        if "--format=json" in text:
            fmt = "json"
            text = text.replace("--format=json", "").strip()
        cmd_generate(text, fmt)
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
