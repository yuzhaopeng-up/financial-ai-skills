#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易指令优化 - 企微集成
"""

import json
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trade_optimize_engine import TradeOptimizeEngine


class TradeOptimizeWecom:
    def __init__(self):
        self.engine = TradeOptimizeEngine(api_mode=True)

    def handle_message(self, text: str, user_id: str = None) -> dict:
        text = text.strip()

        # 解析命令
        # 格式: "优化 600036.SH 100000 35.50" 或 "优化 600036.SH 100000 35.50 vwap"
        if text.startswith("优化") or text.startswith("下单优化"):
            parts = text.replace("优化", "").replace("下单优化", "").strip().split()
            if len(parts) >= 3:
                symbol = parts[0]
                try:
                    quantity = int(parts[1])
                    price = float(parts[2])
                    algorithm = parts[3] if len(parts) > 3 else "vwap"
                    return self._build_result(symbol, quantity, price, algorithm)
                except (ValueError, IndexError):
                    return {"type": "text", "content": "参数格式错误，示例：`优化 600036.SH 100000 35.50 vwap`"}
            return {"type": "text", "content": "请输入：`优化 [标的] [数量] [价格] [算法可选]`\n示例：`优化 600036.SH 100000 35.50 vwap`"}

        elif text.startswith("对比"):
            parts = text.replace("对比", "").strip().split()
            if len(parts) >= 3:
                symbol = parts[0]
                try:
                    quantity = int(parts[1])
                    price = float(parts[2])
                    return self._build_compare(symbol, quantity, price)
                except ValueError:
                    pass
            return {"type": "text", "content": "请输入：`对比 [标的] [数量] [价格]`"}

        elif text in ["优化帮助", "帮助", "优化命令"]:
            return self._build_help()

        return self._build_help()

    def _build_result(self, symbol: str, quantity: int, price: float, algorithm: str) -> dict:
        try:
            engine = TradeOptimizeEngine(
                symbol=symbol,
                quantity=quantity,
                price=price,
                algorithm=algorithm,
                api_mode=True,
            )
            result = engine.optimize()
            return self._format_card(result)
        except Exception as e:
            return {"type": "text", "content": f"优化失败：{str(e)}"}

    def _build_compare(self, symbol: str, quantity: int, price: float) -> dict:
        try:
            engine = TradeOptimizeEngine(
                symbol=symbol, quantity=quantity, price=price, api_mode=True
            )
            results = engine.compare_algorithms()
            lines = [f"🐟 算法对比 [{symbol}] 数量:{quantity:,}\n"]
            best_algo = max(results.items(), key=lambda x: x[1]["score"])
            lines.append(f"推荐: **{best_algo[0].upper()}** (评分 {best_algo[1]['score']:.1f})\n")
            lines.append(f"{'算法':<6} {'收益':>8} {'vs基准':>8} {'夏普':>6} {'冲击':>8} {'验收':>4}")
            lines.append("-" * 50)
            for algo, r in results.items():
                bt = r["backtest"]
                status = "✅" if r["passes_acceptance"] else "❌"
                lines.append(
                    f"{algo:<6} "
                    f"{bt['return_pct']:>7.3f}% "
                    f"{bt['improvement_over_baseline_pct']:>+7.3f}% "
                    f"{bt['sharpe_ratio']:>6.3f} "
                    f"{r['market_impact_bps']:>7.2f}bps "
                    f"{status}"
                )
            return {"type": "text", "content": "\n".join(lines)}
        except Exception as e:
            return {"type": "text", "content": f"对比失败：{str(e)}"}

    def _format_card(self, result: dict) -> dict:
        status = "✅ 通过" if result["passes_acceptance"] else "❌ 未通过"
        status_color = "green" if result["passes_acceptance"] else "red"
        bt = result["backtest"]

        slices_text = "\n".join(
            f"• {sl['slot']} | {sl['quantity']:,}股 @ {sl['price']:.2f} | 权重{sl['weight']:.1%}"
            for sl in result["slices"]
        )

        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"📈 交易优化 - {result['algorithm'].upper()} | {status}",
                    "template": status_color,
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": (
                                f"**标的**: {result['symbol']} | **方向**: {result['side']}\n"
                                f"**总量**: {result['quantity']:,}股 @ {result['reference_price']:.2f}\n"
                                f"**算法**: {result['algorithm'].upper()}"
                            ),
                        },
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": (
                                f"**预期VWAP**: {result['expected_vwap']:.4f}\n"
                                f"**市场冲击**: {result['market_impact_bps']:.2f} bps\n"
                                f"**vs基准提升**: {result['improvement_vs_baseline_pct']:+.4f}%"
                            ),
                        },
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": (
                                f"**回测收益**: {bt['return_pct']:+.4f}%  "
                                f"**夏普**: {bt['sharpe_ratio']:.4f}  "
                                f"**最大回撤**: {bt['max_drawdown_pct']:.4f}%\n"
                                f"**综合评分**: {result['score']:.1f}/100  "
                                f"**验收(≥5%)**: {status}"
                            ),
                        },
                    },
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"**订单拆分**:\n{slices_text}"}},
                ],
            },
        }

    def _build_help(self) -> dict:
        return {
            "type": "text",
            "content": """🐟 **交易指令优化引擎**

📋 功能：将大单拆分为最优下单策略

📝 命令：
- `优化 600036.SH 100000 35.50` — 默认VWAP
- `优化 600036.SH 100000 35.50 twap` — 指定算法
- `对比 600036.SH 100000 35.50` — 对比所有算法

🏷️ 算法：TWAP / VWAP / POV / IS

📊 验收标准：回测收益率提升 ≥5%""",
        }


def handle(text: str, user_id: str = None) -> dict:
    return TradeOptimizeWecom().handle_message(text, user_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="600036.SH")
    parser.add_argument("--quantity", type=int, default=100000)
    parser.add_argument("--price", type=float, default=35.50)
    parser.add_argument("--algorithm", default="vwap")
    parser.add_argument("--compare", action="store_true")
    args = parser.parse_args()

    if args.compare:
        result = handle(f"对比 {args.symbol} {args.quantity} {args.price}")
    else:
        result = handle(f"优化 {args.symbol} {args.quantity} {args.price} {args.algorithm}")

    print(json.dumps(result, ensure_ascii=False, indent=2)[:800])
