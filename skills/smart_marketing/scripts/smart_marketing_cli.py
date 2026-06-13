#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能营销话术引擎 - CLI工具

Usage:
    python smart_marketing_cli.py "营销话术 客户年龄=35 职业=企业主 资产=500万 风险偏好=稳健"
    python smart_marketing_cli.py "保险话术 30岁白领50万进取型" --format=json
    python smart_marketing_cli.py "短信 存款话术 50岁退休人员100万保守型" --format=text
"""

import sys
import json
import argparse
from smart_marketing_engine import SmartMarketingEngine


def main():
    parser = argparse.ArgumentParser(description="智能营销话术引擎 CLI")
    parser.add_argument("input", nargs="?", help="客户画像描述文本")
    parser.add_argument("--product", "-p", default=None, help="指定产品类型")
    parser.add_argument("--goal", "-g", default=None, help="指定营销目标")
    parser.add_argument("--channel", "-c", default=None, help="指定营销渠道（短信/微信/电话/面对面）")
    parser.add_argument("--format", "-f", default="text", choices=["text", "json"], help="输出格式")
    args = parser.parse_args()

    engine = SmartMarketingEngine()

    if not args.input:
        print("🎯 智能营销话术引擎 CLI")
        print("-" * 40)
        print("用法:")
        print("  python smart_marketing_cli.py <客户画像描述>")
        print()
        print("示例:")
        print('  python smart_marketing_cli.py "营销话术 客户年龄=35 职业=企业主 资产=500万 风险偏好=稳健"')
        print('  python smart_marketing_cli.py "保险话术 30岁白领50万进取型" --format=json')
        print('  python smart_marketing_cli.py "短信 存款话术 50岁退休人员100万保守型"')
        print()
        print("支持的产品类型:")
        for i, p in enumerate(engine.PRODUCT_TEMPLATES.keys(), 1):
            print(f"  {i}. {p}")
        return

    # 解析产品/目标/渠道（从文本中抽取或使用参数）
    text = args.input
    if args.product:
        text = f"{text} 产品={args.product}"
    if args.goal:
        text = f"{text} 目标={args.goal}"

    result = engine.generate_script(text, product=args.product, goal=args.goal, channel=args.channel)

    # 验收检查
    product_count = len(engine.PRODUCT_TEMPLATES)
    time_ms = result["generation_time_ms"]

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(engine.format_text(result))

    print()
    print(f"📊 验收报告: 产品支持={product_count}种 ✅ | 生成耗时={time_ms}ms {'✅' if time_ms < 5000 else '❌'}")

    # 返回码
    sys.exit(0 if time_ms < 5000 else 1)


if __name__ == "__main__":
    main()
