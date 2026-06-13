#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流失客户召回引擎 CLI

Usage:
    python churn_recall_cli.py analyze <customer_id> [options]
    python churn_recall_cli.py recall <customer_id> [options]
    python churn_recall_cli.py batch [options]
    python churn_recall_cli.py generate [options]

Examples:
    # 分析单个客户流失风险
    python churn_recall_cli.py analyze C88888 --name 张伟 --recency 30 --frequency 2 --amount 500
    
    # 生成召回话术
    python churn_recall_cli.py recall C88888 --name 张伟 --recency 60 --frequency 1 --amount 300
    
    # 批量分析
    python churn_recall_cli.py batch --count 10 --high-risk-only
    
    # 生成测试数据
    python churn_recall_cli.py generate --count 5
"""

import argparse
import json
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from churn_recall_engine import ChurnRecallEngine, generate_mock_customer


def cmd_analyze(args):
    """分析客户流失风险"""
    engine = ChurnRecallEngine()
    
    customer = {
        "customer_id": args.customer_id,
        "name": args.name or args.customer_id,
        "last_purchase_days": args.recency,
        "purchase_frequency": args.frequency,
        "avg_order_amount": args.amount,
        "login_interval_days": args.login_interval,
        "product_active_days": args.active_days,
        "service_complaints": args.complaints,
        "total_orders": args.total_orders,
        "member_level": args.member_level
    }
    
    result = engine.analyze_churn_risk(customer)
    
    if args.format == "json":
        print(engine.format_json(result))
    else:
        print(engine.format_text(result, "analysis"))
    
    return 0


def cmd_recall(args):
    """生成召回话术"""
    engine = ChurnRecallEngine()
    
    customer = {
        "customer_id": args.customer_id,
        "name": args.name or args.customer_id,
        "last_purchase_days": args.recency,
        "purchase_frequency": args.frequency,
        "avg_order_amount": args.amount,
        "login_interval_days": args.login_interval,
        "product_active_days": args.active_days,
        "service_complaints": args.complaints,
        "total_orders": args.total_orders,
        "member_level": args.member_level
    }
    
    risk_result = engine.analyze_churn_risk(customer)
    recall_result = engine.generate_recall_script(customer, risk_result, args.channel)
    
    if args.format == "json":
        print(engine.format_json(recall_result))
    else:
        print(engine.format_text(recall_result, "recall"))
    
    return 0


def cmd_batch(args):
    """批量分析客户"""
    engine = ChurnRecallEngine()
    
    # 生成测试客户数据
    customers = [generate_mock_customer() for _ in range(args.count)]
    
    if args.high_risk_only:
        results = engine.generate_batch_recall(customers, high_priority_only=True)
        print(f"📊 生成了 {len(results)} 份高优先级召回方案")
        print()
        for result in results:
            if args.format == "json":
                print(engine.format_json(result))
            else:
                print(engine.format_text(result, "recall"))
            print()
    else:
        results = engine.batch_analyze(customers)
        
        # 统计
        high = len([r for r in results if r["risk_level"] == "high"])
        medium = len([r for r in results if r["risk_level"] == "medium"])
        low = len([r for r in results if r["risk_level"] == "low"])
        
        print(f"📊 批量分析完成，共 {len(results)} 位客户")
        print(f"   🔴 高风险：{high}人")
        print(f"   🟡 中风险：{medium}人")
        print(f"   🟢 低风险：{low}人")
        print()
        
        # 输出前5个高风险客户
        high_risk = [r for r in results if r["risk_level"] == "high"][:5]
        if high_risk:
            print("🔴 **高风险客户 TOP 5**")
            print()
            for r in high_risk:
                print(f"   {r['name']} ({r['customer_id']}): {r['risk_score']:.1f}分 - {r['risk_label']}")
                if r['churn_reasons']:
                    print(f"   原因：{r['churn_reasons'][0]['reason']}")
                print()
    
    return 0


def cmd_generate(args):
    """生成测试数据"""
    print(f"📊 生成 {args.count} 条测试客户数据")
    print()
    
    for i in range(args.count):
        customer = generate_mock_customer()
        print(json.dumps(customer, ensure_ascii=False, indent=2))
        print()
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="🦞 流失客户召回引擎 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python churn_recall_cli.py analyze C88888 --name 张伟 --recency 30
  python churn_recall_cli.py recall C88888 --name 张伟 --recency 60
  python churn_recall_cli.py batch --count 10 --high-risk-only
  python churn_recall_cli.py generate --count 5
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # analyze 子命令
    analyze_parser = subparsers.add_parser("analyze", help="分析客户流失风险")
    analyze_parser.add_argument("customer_id", help="客户ID")
    analyze_parser.add_argument("--name", help="客户名称")
    analyze_parser.add_argument("--recency", type=int, default=30, help="最近购买距今天数")
    analyze_parser.add_argument("--frequency", type=float, default=2, help="月均购买次数")
    analyze_parser.add_argument("--amount", type=float, default=500, help="平均订单金额")
    analyze_parser.add_argument("--login-interval", type=int, default=7, help="平均登录间隔天数")
    analyze_parser.add_argument("--active-days", type=int, default=30, help="产品活跃天数")
    analyze_parser.add_argument("--complaints", type=int, default=0, help="投诉次数")
    analyze_parser.add_argument("--total-orders", type=int, default=50, help="总订单数")
    analyze_parser.add_argument("--member-level", default="普通会员", help="会员等级")
    analyze_parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # recall 子命令
    recall_parser = subparsers.add_parser("recall", help="生成召回话术")
    recall_parser.add_argument("customer_id", help="客户ID")
    recall_parser.add_argument("--name", help="客户名称")
    recall_parser.add_argument("--recency", type=int, default=30, help="最近购买距今天数")
    recall_parser.add_argument("--frequency", type=float, default=2, help="月均购买次数")
    recall_parser.add_argument("--amount", type=float, default=500, help="平均订单金额")
    recall_parser.add_argument("--login-interval", type=int, default=7, help="平均登录间隔天数")
    recall_parser.add_argument("--active-days", type=int, default=30, help="产品活跃天数")
    recall_parser.add_argument("--complaints", type=int, default=0, help="投诉次数")
    recall_parser.add_argument("--total-orders", type=int, default=50, help="总订单数")
    recall_parser.add_argument("--member-level", default="普通会员", help="会员等级")
    recall_parser.add_argument("--channel", default="企微", help="偏好触达渠道")
    recall_parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")
    recall_parser.set_defaults(func=cmd_recall)
    
    # batch 子命令
    batch_parser = subparsers.add_parser("batch", help="批量分析客户")
    batch_parser.add_argument("--count", type=int, default=10, help="客户数量")
    batch_parser.add_argument("--high-risk-only", action="store_true", help="仅输出高风险客户召回方案")
    batch_parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")
    batch_parser.set_defaults(func=cmd_batch)
    
    # generate 子命令
    generate_parser = subparsers.add_parser("generate", help="生成测试数据")
    generate_parser.add_argument("--count", type=int, default=5, help="生成数量")
    generate_parser.set_defaults(func=cmd_generate)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
