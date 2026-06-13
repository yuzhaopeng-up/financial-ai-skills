#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
审计抽样引擎 CLI
支持从文件或命令行参数加载交易数据，执行风险导向抽样
"""

import argparse
import json
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audit_sampling_engine import AuditSamplingEngine


def generate_demo_data(n: int = 500) -> list:
    """生成演示用模拟交易数据"""
    random.seed(42)
    types = [
        "转账", "贷款发放", "还款", "手续费", "理财购买", "理财赎回",
        "担保", "信用证", "贴现", "咨询费", "资产处置", "大额转账"
    ]
    data = []
    for i in range(n):
        amount = random.uniform(100, 5_000_000)
        if i < int(n * 0.10):  # 10% 大额
            amount = random.uniform(1_000_000, 5_000_000)
        elif i < int(n * 0.30):  # 20% 中等
            amount = random.uniform(100_000, 1_000_000)
        data.append({
            "id": f"TXN_{i+1:06d}",
            "amount": round(amount, 2),
            "type": random.choice(types),
            "date": f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
            "counterparty": f"对手方{random.randint(1, 50)}",
            "description": random.choice(["正常", "大额", "异常", "关联交易", "可疑交易"])
        })
    return data


def load_json_file(path: str) -> list:
    """从JSON文件加载交易数据"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        # 支持 {"transactions": [...]} 或 {"data": [...]} 格式
        for key in ["transactions", "data", "records", "items"]:
            if key in data:
                return data[key]
        return [data]
    return data


def main():
    parser = argparse.ArgumentParser(description="风险导向审计抽样引擎 CLI")
    parser.add_argument("-f", "--file", help="交易数据JSON文件路径")
    parser.add_argument("-n", "--count", type=int, default=500, help="演示数据笔数（默认500）")
    parser.add_argument("--coverage", type=float, default=0.95, help="覆盖率目标（默认0.95）")
    parser.add_argument("--high-threshold", type=float, default=1_000_000, help="高风险金额阈值（默认100万）")
    parser.add_argument("--medium-threshold", type=float, default=100_000, help="中风险金额阈值（默认10万）")
    parser.add_argument("--output", "-o", help="结果输出JSON文件路径")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")
    parser.add_argument("--demo", action="store_true", help="使用内置演示数据")

    args = parser.parse_args()

    # 加载数据
    if args.file:
        print(f"从文件加载交易数据: {args.file}")
        transactions = load_json_file(args.file)
    elif args.demo:
        print(f"使用演示数据: {args.count} 笔")
        transactions = generate_demo_data(args.count)
    else:
        print("使用默认演示数据 (500笔)")
        transactions = generate_demo_data(args.count)

    print(f"交易数据: {len(transactions)} 笔")
    print()

    # 配置
    config = {
        "high_risk_amount_threshold": args.high_threshold,
        "medium_risk_amount_threshold": args.medium_threshold,
        "coverage_target": args.coverage,
    }

    engine = AuditSamplingEngine(config=config)

    # 处理数据
    processed = engine.load_transactions(transactions)

    # 执行抽样
    result = engine.sample(processed, coverage_target=args.coverage)

    # 输出
    if args.format == "json":
        output = engine.format_json(result)
    else:
        output = engine.format_plan_text(result)

    print(output)

    # 保存结果
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(engine.format_json(result))
        print(f"\n结果已保存: {args.output}")

    # 返回码
    if result.get("coverage_met"):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
