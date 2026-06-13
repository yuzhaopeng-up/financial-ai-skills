#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户健康度热力图引擎 CLI
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from customer_health_engine import CustomerHealthEngine


def main():
    parser = argparse.ArgumentParser(description="客户健康度热力图引擎")
    parser.add_argument("--group-id", "-g", type=str, help="客户群ID")
    parser.add_argument("--group-name", "-n", type=str, default="测试客户群", help="客户群名称")
    parser.add_argument("--format", "-f", choices=["text", "json", "card"], default="text", help="输出格式")
    parser.add_argument("--input", "-i", type=str, help="客户数据JSON文件路径")
    args = parser.parse_args()

    engine = CustomerHealthEngine()

    print("🦞 客户健康度热力图引擎 v1.0")
    print()

    # 加载客户数据
    customers = []
    if args.input:
        # 从文件加载
        with open(args.input, "r", encoding="utf-8") as f:
            customers = json.load(f)
        print(f"从文件加载 {len(customers)} 条客户数据")
    else:
        # 使用模拟数据
        import random
        segments = ["VIP客户", "普通客户", "潜力客户"]
        names = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
                 "郑十一", "王十二", "冯十三", "陈十四", "楚十五", "卫十六", "蒋十七"]

        for i, name in enumerate(names):
            seg = segments[i % len(segments)]
            customer = {
                "customer_id": f"C{i+1:04d}",
                "customer_name": f"{name}({seg})",
                "login_frequency": random.randint(0, 10),
                "transaction_frequency": random.randint(0, 15),
                "last_active_days": random.randint(0, 90),
                "service_interaction_count": random.randint(0, 10),
                "satisfaction_score": round(random.uniform(2.5, 5.0), 1),
                "response_rate": random.randint(50, 100),
                "overdue_days": random.randint(0, 30) if random.random() > 0.7 else 0,
                "overdue_count": random.randint(0, 5) if random.random() > 0.8 else 0,
                "credit_utilization": random.randint(10, 95),
                "complaint_count": random.randint(0, 5) if random.random() > 0.7 else 0,
                "unresolved_days": random.randint(0, 20) if random.random() > 0.8 else 0,
                "service_satisfaction": round(random.uniform(3.0, 5.0), 1),
                "tenure_months": random.randint(1, 48),
                "retention_rate": random.randint(50, 100),
                "product_count": random.randint(1, 6),
                "aum_change_pct": random.randint(-30, 30),
                "new_product_count": random.randint(0, 4),
                "asset_growth_pct": random.randint(-20, 25)
            }
            customers.append(customer)

    # 分析客户群
    group_id = args.group_id or "GROUP001"
    group_name = f"{args.group_name}({group_id})"
    result = engine.analyze_group(customers, group_name=group_name)

    # 输出结果
    if args.format == "json":
        print(engine.format_json(result))
    elif args.format == "card":
        card = engine.format_wecom_card(result)
        print(json.dumps(card, ensure_ascii=False, indent=2))
    else:
        print(engine.format_text(result))

    return 0


if __name__ == "__main__":
    sys.exit(main())
