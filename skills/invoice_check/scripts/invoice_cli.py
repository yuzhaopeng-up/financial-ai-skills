#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发票查验CLI入口

用法:
    python3 scripts/invoice_cli.py generate "发票查验 发票代码144031900360 号码44450123 开票日期2024-03-01 金额10万"
    python3 scripts/invoice_cli.py "发票查验 发票代码144031900360 号码44450123 开票日期2024-03-01 金额10万"
"""

import sys
import os
import json

# 将技能目录加入路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SKILL_DIR)

from invoice_engine import InvoiceCheckEngine


def format_result(result: dict) -> str:
    """格式化查验结果为易读文本"""
    lines = []
    lines.append("=" * 60)
    lines.append(f"  📄 发票查验报告")
    lines.append("=" * 60)

    # 基本信息
    lines.append(f"\n【基本信息】")
    lines.append(f"  发票代码: {result['invoice_code']}")
    lines.append(f"  发票号码: {result['invoice_number']}")
    lines.append(f"  查验状态: {result['status']}")
    lines.append(f"  置信度:   {result['confidence']*100:.1f}%")

    # 异常提示
    if result["anomalies"]:
        lines.append(f"\n【异常提示】({len(result['anomalies'])}项)")
        for i, a in enumerate(result["anomalies"], 1):
            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(a["severity"], "⚪")
            lines.append(f"  {severity_emoji} [{a['severity'].upper()}] {a['type']}")
            lines.append(f"      {a['description']}")
            lines.append(f"      💡 建议: {a['suggestion']}")
    else:
        lines.append(f"\n【异常提示】✅ 未发现明显异常")

    # 增值税抵扣建议
    vat = result["vat_deduction"]
    lines.append(f"\n【增值税抵扣建议】")
    can_deduct = "✅ 可以抵扣" if vat["can_deduct"] else "❌ 不可抵扣"
    lines.append(f"  抵扣状态: {can_deduct}")
    lines.append(f"  抵扣类型: {vat['deduction_type']}")
    lines.append(f"  原因:     {vat['reason']}")

    # 税务风险点
    if result["tax_risk_points"]:
        lines.append(f"\n【税务风险点】")
        for rp in result["tax_risk_points"]:
            risk_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rp["risk_level"], "⚪")
            lines.append(f"  {risk_emoji} [{rp['risk_level'].upper()}] {rp['point']}")

    # 备查记录
    if result["reference_records"]:
        lines.append(f"\n【备查记录】")
        for rec in result["reference_records"]:
            lines.append(f"  📌 {rec['record_type']}: {rec['content']}")

    lines.append("\n" + "=" * 60)
    lines.append("⚠️  本结果仅供参考，最终以主管税务机关认定为准")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    """CLI主入口"""
    args = sys.argv[1:]

    if not args:
        print("用法: python3 scripts/invoice_cli.py [generate] \"发票查验 发票代码xxx 号码xxx 开票日期2024-01-01 金额10万\"")
        sys.exit(1)

    # 处理 generate 参数
    if "generate" in args:
        args = [a for a in args if a != "generate"]

    text = " ".join(args)
    if not text.strip():
        print("错误: 未提供查验参数")
        sys.exit(1)

    # 执行查验
    engine = InvoiceCheckEngine(api_mode=True)
    result = engine.check_from_text(text)

    # 输出格式优先JSON（用于程序调用），纯文本用于交互
    if "--json" in args:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_result(result))


if __name__ == "__main__":
    main()
