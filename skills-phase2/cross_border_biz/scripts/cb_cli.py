#!/usr/bin/env python3
"""
跨境业务CLI
用法:
    python3 cb_cli.py generate "跨境业务 出口企业 100万美元 欧盟"
    python3 cb_cli.py generate "跨境业务 进口企业 50万欧元 德国"
    python3 cb_cli.py generate "跨境业务 跨境投融资 500万美元 越南"
"""

import sys
import json
import re
import argparse
from pathlib import Path

# 添加skill目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from crossborder_engine import CrossBorderEngine


def parse_command(command: str) -> dict:
    """解析命令行输入"""
    # 格式: "跨境业务 出口企业 100万美元 欧盟"
    # 或: "跨境业务 进口企业 50万欧元 德国"
    # 或: "跨境业务 跨境投融资 500万美元 越南"

    pattern = r"跨境业务\s*(出口企业|进口企业|跨境投融资)\s*(\d+(?:\.\d+)?)\s*(万欧元|万英镑|万美元|亿|万|欧元|EUR|英镑|GBP|美元|USD|JPY|日元|人民币|CNY)?\s*(.*)"

    match = re.search(pattern, command)
    if not match:
        # 尝试简化解析
        parts = command.replace("跨境业务", "").strip().split()
        if len(parts) >= 4:
            business_type = parts[0]
            amount_str = parts[1]
            currency = parts[2]
            destination = " ".join(parts[3:])
        elif len(parts) == 3:
            business_type = parts[0]
            amount_str = parts[1]
            currency = parts[2]
            destination = "未知"
        else:
            raise ValueError(f"无法解析命令: {command}")
    else:
        business_type = match.group(1)
        amount_str = match.group(2)
        currency_suffix = match.group(3) or "万美元"
        destination = match.group(4).strip()

    # 解析金额
    amount = float(amount_str)
    if "亿" in currency_suffix:
        amount = amount * 100000000
    elif "万" in currency_suffix and "美元" in currency_suffix:
        amount = amount * 10000 * 7.2  # 假设USD/CNY=7.2
    elif "万" in currency_suffix and "欧元" in currency_suffix:
        amount = amount * 10000 * 7.8  # 假设EUR/CNY=7.8
    elif "万" in currency_suffix and "英镑" in currency_suffix:
        amount = amount * 10000 * 9.0  # 假设GBP/CNY=9.0
    elif "万" in currency_suffix:
        amount = amount * 10000
    elif "USD" in currency_suffix.upper() or "美元" in currency_suffix:
        amount = amount
    elif "EUR" in currency_suffix.upper() or "欧元" in currency_suffix:
        amount = amount * 1.1  # EUR/USD
    elif "GBP" in currency_suffix.upper() or "英镑" in currency_suffix:
        amount = amount * 1.27  # GBP/USD
    elif "JPY" in currency_suffix.upper() or "日元" in currency_suffix:
        amount = amount / 150  # USD/JPY
    elif "CNY" in currency_suffix.upper() or "人民币" in currency_suffix:
        amount = amount / 7.2  # CNY/USD
    else:
        amount = amount  # 默认美元

    # 解析币种
    currency = "USD"
    if "EUR" in currency_suffix.upper() or "欧元" in currency_suffix:
        currency = "EUR"
    elif "GBP" in currency_suffix.upper() or "英镑" in currency_suffix:
        currency = "GBP"
    elif "JPY" in currency_suffix.upper() or "日元" in currency_suffix:
        currency = "JPY"
    elif "CNY" in currency_suffix.upper() or "人民币" in currency_suffix:
        currency = "CNY"
    elif "USD" in currency_suffix.upper() or "美元" in currency_suffix or "万" in currency_suffix:
        currency = "USD"

    return {
        "business_type": business_type,
        "amount": amount,
        "currency": currency,
        "destination_country": destination or "未知",
    }


def generate(command: str, output_format: str = "text") -> str:
    """生成跨境业务方案"""
    params = parse_command(command)

    engine = CrossBorderEngine()
    result = engine.generate(
        business_type=params["business_type"],
        amount=params["amount"],
        currency=params["currency"],
        destination_country=params["destination_country"],
    )

    if output_format == "json":
        return json.dumps(result, ensure_ascii=False, indent=2)
    else:
        return engine.format_output(result)


def main():
    parser = argparse.ArgumentParser(description="跨境业务综合解决方案CLI")
    parser.add_argument("action", choices=["generate"], help="执行动作")
    parser.add_argument(
        "command",
        nargs="*",
        help='命令，如: "跨境业务 出口企业 100万美元 欧盟"',
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="输出格式",
    )

    args = parser.parse_args()

    if args.action == "generate":
        command = " ".join(args.command)
        if not command:
            print("错误: 请提供命令")
            print(__doc__)
            sys.exit(1)

        output = generate(command, args.format)
        print(output)


if __name__ == "__main__":
    main()
