#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易指令优化引擎 CLI
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trade_optimize_engine import TradeOptimizeEngine


def cmd_optimize(args):
    engine = TradeOptimizeEngine(
        symbol=args.symbol,
        quantity=args.quantity,
        side=args.side,
        price=args.price,
        start_time=args.start,
        end_time=args.end,
        algorithm=args.algorithm,
        seed=args.seed or 42,
    )
    result = engine.optimize()
    if args.format == "json":
        print(engine.format_json(result))
    else:
        print(engine.format_text(result))


def cmd_backtest(args):
    engine = TradeOptimizeEngine(
        symbol=args.symbol,
        quantity=args.quantity,
        side=args.side,
        price=args.price,
        algorithm=args.algorithm,
        seed=args.seed or 42,
    )
    result = engine.optimize()
    bt = result["backtest"]
    print(f"🐟 回测结果 [{args.symbol}] 算法:{args.algorithm} 数量:{args.quantity}")
    print(f"  回测收益率:    {bt['return_pct']:.4f}%")
    print(f"  基准收益率:    {bt['baseline_return_pct']:.4f}%")
    print(f"  提升幅度:      {bt['improvement_over_baseline_pct']:.4f}%")
    print(f"  夏普比率:      {bt['sharpe_ratio']:.4f}")
    print(f"  最大回撤:      {bt['max_drawdown_pct']:.4f}%")
    print(f"  验收(≥5%):     {'✅ 通过' if result['passes_acceptance'] else '❌ 未通过'}")


def cmd_compare(args):
    engine = TradeOptimizeEngine(
        symbol=args.symbol,
        quantity=args.quantity,
        side=args.side,
        price=args.price,
        seed=args.seed or 42,
    )
    results = engine.compare_algorithms()
    print(f"🐟 算法对比 [{args.symbol}] 数量:{args.quantity:,}")
    print(f"{'='*60}")
    print(f"{'算法':<8} {'回测收益':>10} {'vs基准':>10} {'夏普':>8} {'冲击(bps)':>12} {'评分':>6} {'验收':>6}")
    print(f"{'-'*60}")
    for algo, r in results.items():
        bt = r["backtest"]
        status = "✅" if r["passes_acceptance"] else "❌"
        print(
            f"{algo:<8} "
            f"{bt['return_pct']:>10.4f}% "
            f"{bt['improvement_over_baseline_pct']:>+10.4f}% "
            f"{bt['sharpe_ratio']:>8.4f} "
            f"{r['market_impact_bps']:>12.2f} "
            f"{r['score']:>6.1f} "
            f"{status:>6}"
        )


def main():
    parser = argparse.ArgumentParser(description="交易指令优化引擎 CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # optimize
    p_opt = sub.add_parser("optimize", help="优化下单策略")
    p_opt.add_argument("--symbol", required=True, help="标的代码，如 600036.SH")
    p_opt.add_argument("--quantity", type=int, required=True, help="总股数")
    p_opt.add_argument("--price", type=float, required=True, help="参考价格")
    p_opt.add_argument("--side", default="buy", choices=["buy", "sell"], help="买卖方向")
    p_opt.add_argument("--algorithm", default="vwap", choices=["twap", "vwap", "pov", "is"], help="算法")
    p_opt.add_argument("--start", default="09:30", help="开始时间 HH:MM")
    p_opt.add_argument("--end", default="14:57", help="结束时间 HH:MM")
    p_opt.add_argument("--format", default="text", choices=["text", "json"], help="输出格式")
    p_opt.add_argument("--seed", type=int, default=None, help="随机种子")
    p_opt.set_defaults(func=cmd_optimize)

    # backtest
    p_bt = sub.add_parser("backtest", help="回测单算法")
    p_bt.add_argument("--symbol", required=True)
    p_bt.add_argument("--quantity", type=int, required=True)
    p_bt.add_argument("--price", type=float, required=True)
    p_bt.add_argument("--side", default="buy", choices=["buy", "sell"])
    p_bt.add_argument("--algorithm", default="vwap", choices=["twap", "vwap", "pov", "is"])
    p_bt.add_argument("--seed", type=int, default=None)
    p_bt.set_defaults(func=cmd_backtest)

    # compare
    p_cmp = sub.add_parser("compare", help="对比所有算法")
    p_cmp.add_argument("--symbol", required=True)
    p_cmp.add_argument("--quantity", type=int, required=True)
    p_cmp.add_argument("--price", type=float, required=True)
    p_cmp.add_argument("--side", default="buy", choices=["buy", "sell"])
    p_cmp.add_argument("--seed", type=int, default=None)
    p_cmp.set_defaults(func=cmd_compare)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
