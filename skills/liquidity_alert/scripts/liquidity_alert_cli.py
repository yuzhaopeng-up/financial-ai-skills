#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资金流动性风险预警引擎 CLI

Usage:
    python liquidity_alert_cli.py --balance 1000000 --inflow 600000 --outflow 400000
    python liquidity_alert_cli.py --lcr "某银行" 1000000 500000 1200000
    python liquidity_alert_cli.py --stress 中度 30 1000000
"""

import argparse
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from liquidity_alert_engine import LiquidityAlertEngine


def main():
    parser = argparse.ArgumentParser(description="资金流动性风险预警引擎 CLI")
    parser.add_argument("--balance", type=float, default=1000000, help="当前账户余额")
    parser.add_argument("--inflow", type=float, default=600000, help="30天总流入")
    parser.add_argument("--outflow", type=float, default=400000, help="30天总流出")
    parser.add_argument("--lcr", nargs=4, metavar=("NAME", "HQLA", "NQLA", "NET_OUT"),
                        help="LCR检查: 机构名 HQLA NQLA 净流出")
    parser.add_argument("--stress", nargs=3, metavar=("SCENARIO", "DAYS", "BALANCE"),
                        help="压力测试: 情景 天数 余额")
    parser.add_argument("--json", action="store_true", help="输出JSON格式")
    args = parser.parse_args()

    engine = LiquidityAlertEngine()

    # LCR检查
    if args.lcr:
        name, hqla, nqla, net_out = args.lcr
        result = engine.check_lcr(name, float(hqla), float(nqla), float(net_out))
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\n🏦 LCR检查结果: {name}")
            print(f"  LCR: {result['lcr']:.1f}% ({'✅ 达标' if result['达标'] else '❌ 不达标'})")
        return

    # 压力测试
    if args.stress:
        scenario, days, balance = args.stress[0], int(args.stress[1]), float(args.stress[2])
        result = engine.stress_test(scenario, days, [], [], balance)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\n🧪 压力测试结果: {scenario}情景")
            print(f"  可支撑天数: {result['survive_days']}天 / {result['days']}天")
            print(f"  预测期末余额: ¥{result['projected_balance']:,.2f}")
            print(f"  日均净流量: ¥{result['daily_net_flow']:,.2f}")
        return

    # 标准流动性预警
    print("🦞 资金流动性风险预警引擎 v1.0.0")
    print(f"  当前余额: ¥{args.balance:,.2f}")
    print(f"  30天流入: ¥{args.inflow:,.2f}")
    print(f"  30天流出: ¥{args.outflow:,.2f}")

    # 构造模拟数据（实际应用中从数据库读取）
    today = datetime.now()
    inflows = [
        {
            "date": (today - timedelta(days=i)).strftime("%Y-%m-%d"),
            "amount": args.inflow / 30,
            "category": "稳定流入",
        }
        for i in range(30)
    ]
    outflows = [
        {
            "date": (today - timedelta(days=i)).strftime("%Y-%m-%d"),
            "amount": args.outflow / 30,
            "category": "常规流出",
        }
        for i in range(30)
    ]

    result = engine.analyze({
        "balance": args.balance,
        "inflows": inflows,
        "outflows": outflows,
    })

    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print()
        print(engine.format_text(result))


if __name__ == "__main__":
    import json
    sys.exit(main())
