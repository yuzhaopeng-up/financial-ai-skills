#!/usr/bin/env python3
"""
精算模型 CLI 入口
用法:
    python3 scripts/actuarial_cli.py generate "精算模型 终身寿险 30岁男性 保额100万 20年缴"
    python3 scripts/actuarial_cli.py --table CL2 --rate 0.03 generate "定期寿险 40岁女性 保额50万 10年缴"
"""

import sys
import os
import re
import json
import argparse

# 确保模块路径可导入（actuarial_model/ 是包，其父目录是 skills/）
_ACTUARIAL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../skills/actuarial_model
sys.path.insert(0, os.path.dirname(_ACTUARIAL_ROOT))  # .../skills/

from actuarial_model import ActuarialModelEngine


def parse_product_type(text: str) -> str:
    """从文本中提取险种类型"""
    if "终身" in text or "寿险" in text:
        if "终身" in text:
            return "终身寿险"
        return "终身寿险"
    if "定期" in text:
        return "定期寿险"
    if "重疾" in text or "疾病" in text:
        return "重疾险"
    return "终身寿险"  # 默认


def parse_gender(text: str) -> str:
    """从文本中提取性别"""
    if "女性" in text or "女" in text:
        return "女性"
    if "男性" in text or "男" in text:
        return "男性"
    return "男性"  # 默认


def parse_age(text: str) -> int:
    """从文本中提取年龄"""
    patterns = [
        r"(\d+)岁",
        r"年龄\s*(\d+)",
        r"(\d+)\s*周岁",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return int(m.group(1))
    return 30  # 默认


def parse_sum_insured(text: str) -> float:
    """从文本中提取保额"""
    patterns = [
        r"保额\s*(\d+(?:\.\d+)?)\s*[万亿]",
        r"(\d+(?:\.\d+)?)\s*万",
        r"(\d+(?:\.\d+)?)\s*亿",
        r"保额\s*(\d+(?:\.\d+)?)",
    ]
    multipliers = {"亿": 100000000, "万": 10000, "千": 1000}

    for p in patterns:
        m = re.search(p, text)
        if m:
            value = float(m.group(1))
            # 检查是否有单位
            for unit, mult in multipliers.items():
                if unit in text[m.start() : m.end() + 1]:
                    value *= mult
                    break
            # 如果没有明确单位，但数字很大，可能是元为单位
            if value < 1000 and "万" not in text and "亿" not in text:
                value *= 10000  # 默认万
            return value
    return 1000000  # 默认100万


def parse_payment_term(text: str) -> int:
    """从文本中提取缴费期限"""
    patterns = [
        r"(\d+)\s*年缴",
        r"缴\s*(\d+)\s*年",
        r"(\d+)年",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return int(m.group(1))
    return 20  # 默认


def generate_report(text: str, mortality_table: str = "CL1", interest_rate: float = 0.025, output_format: str = "text") -> str:
    """生成精算报告"""
    product_type = parse_product_type(text)
    gender = parse_gender(text)
    age = parse_age(text)
    sum_insured = parse_sum_insured(text)
    payment_term = parse_payment_term(text)

    engine = ActuarialModelEngine(
        mortality_table=mortality_table,
        interest_rate=interest_rate,
    )

    result = engine.calculate(
        product_type=product_type,
        age=age,
        gender=gender,
        sum_insured=sum_insured,
        payment_term=payment_term,
    )

    if output_format == "json":
        return json.dumps(result, ensure_ascii=False, indent=2)
    else:
        return engine.format_report(result)


def main():
    parser = argparse.ArgumentParser(description="精算模型 CLI")
    parser.add_argument("--table", default="CL1", choices=["CL1", "CL2"], help="死亡率表 (CL1/CL2)")
    parser.add_argument("--rate", type=float, default=0.025, help="预定利率")
    parser.add_argument("--format", "-f", default="text", choices=["text", "json"], help="输出格式")
    parser.add_argument("command", nargs="?", default="generate", help="命令")
    parser.add_argument("text", nargs="?", default="", help="产品描述文本")

    args = parser.parse_args()

    # 合并剩余参数作为文本
    if not args.text and len(sys.argv) > 1:
        # 尝试从 "generate" 之后提取
        try:
            idx = sys.argv.index("generate")
            args.text = " ".join(sys.argv[idx + 1 :])
        except ValueError:
            args.text = " ".join(sys.argv[1:])

    if not args.text.strip():
        print("错误: 请提供产品描述，例如: 精算模型 终身寿险 30岁男性 保额100万 20年缴", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    try:
        report = generate_report(
            text=args.text,
            mortality_table=args.table,
            interest_rate=args.rate,
            output_format=args.format,
        )
        print(report)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
