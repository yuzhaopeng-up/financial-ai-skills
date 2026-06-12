#!/usr/bin/env python3
"""
Performance Attribution - 企微卡片集成
用法：
    python3 wecom_integration.py send --fund F000001 --return 0.12 --benchmark 0.08
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from perf_attr_engine import PerformanceAttributionEngine

# 企微 Webhook URL（需要替换为实际机器人 Webhook 地址）
DEFAULT_WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY_HERE"


def build_wecom_card(
    fund_code: str,
    fund_return: float,
    benchmark_return: float,
    excess_return: float,
    attribution: dict,
    risk_metrics: dict,
) -> dict:
    """
    构建企微消息卡片（Markdown 格式）
    """
    pct = lambda x: f"{x*100:.2f}%"

    # 效应排序（找出最大贡献）
    effects = [
        ("行业配置", attribution["allocation_effect"]),
        ("选股效应", attribution["selection_effect"]),
        ("交互效应", attribution["interaction_effect"]),
    ]
    effects_sorted = sorted(effects, key=lambda x: abs(x[1]), reverse=True)
    top_name, top_val = effects_sorted[0]

    # 行业归因表格（Top 5）
    by_ind = attribution.get("by_industry", [])
    top_industries = sorted(by_ind, key=lambda x: abs(x["total_effect"]), reverse=True)[:5]

    rows = []
    for row in top_industries:
        rows.append(
            f"| {row['industry']} | {pct(row['portfolio_weight'])} | "
            f"{pct(row['benchmark_weight'])} | {pct(row['industry_return'])} | "
            f"{pct(row['total_effect'])} |"
        )
    table_rows = "\n".join(rows) if rows else "| - | - | - | - | - |"

    card = {
        "msgtype": "markdown",
        "markdown": {
            "content": (
                f"## 📊 基金业绩归因报告 · **{fund_code}**\n\n"
                f"**期间收益** {pct(fund_return)} | "
                f"**基准收益** {pct(benchmark_return)} | "
                f"**超额收益** {pct(excess_return)}\n\n"
                f"---\n\n"
                f"### 🔍 Brinson 双归因分解\n\n"
                f"| 效应 | 贡献 |\n"
                f"|------|------|\n"
                f"| 行业配置效应 | {pct(attribution['allocation_effect'])} |\n"
                f"| 选股效应 | {pct(attribution['selection_effect'])} |\n"
                f"| 交互效应 | {pct(attribution['interaction_effect'])} |\n\n"
                f"> 🏆 最大贡献来源：**{top_name}**（{pct(top_val)}）\n\n"
                f"---\n\n"
                f"### 📈 行业归因详情（Top 5）\n\n"
                f"| 行业 | 组合权重 | 基准权重 | 行业收益 | 归因贡献 |\n"
                f"|------|----------|----------|----------|----------|\n"
                f"{table_rows}\n\n"
                f"---\n\n"
                f"### ⚖️ 风险调整指标\n\n"
                f"| 指标 | 数值 |\n"
                f"|------|------|\n"
                f"| 跟踪误差 | {pct(risk_metrics['tracking_error'])} |\n"
                f"| 信息比率 | {risk_metrics['information_ratio']:.2f} |\n"
                f"| 夏普比率 | {risk_metrics['sharpe_ratio']:.2f} |\n"
                f"| 最大回撤 | {pct(risk_metrics['max_drawdown'])} |\n\n"
                f"---\n\n"
                f"📅 归因报告 | 基金代码 {fund_code} | 数据脱敏版"
            )
        },
    }
    return card


def send_wecom_message(webhook_url: str, payload: dict) -> dict:
    """
    发送企微机器人消息
    """
    try:
        import urllib.request
        import urllib.error

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {"errcode": -1, "errmsg": str(e)}


def main() -> int:
    parser = argparse.ArgumentParser(description="基金业绩归因 - 企微卡片发送")
    parser.add_argument("--fund", dest="fund_code", default="F000001", help="基金代码")
    parser.add_argument("--return", dest="fund_return", type=float, default=0.12, help="基金收益率（如 0.12）")
    parser.add_argument("--benchmark", dest="benchmark_return", type=float, default=0.08, help="基准收益率（如 0.08）")
    parser.add_argument("--webhook", dest="webhook_url", default=None, help="企微 Webhook URL")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="仅打印卡片内容，不发送")
    args = parser.parse_args()

    engine = PerformanceAttributionEngine()
    result = engine.analyze(
        fund_code=args.fund_code,
        fund_return=args.fund_return,
        benchmark_return=args.benchmark_return,
    )

    card = build_wecom_card(
        fund_code=result["fund_code"],
        fund_return=result["period_return"],
        benchmark_return=result["benchmark_return"],
        excess_return=result["excess_return"],
        attribution=result["attribution"],
        risk_metrics=result["risk_metrics"],
    )

    print("=" * 60)
    print("【企微卡片内容预览】")
    print("=" * 60)
    print(card["markdown"]["content"])
    print("=" * 60)

    if args.dry_run:
        print("\n[DRY-RUN] 未发送，实际发送需去掉 --dry-run 并配置 --webhook")
        return 0

    webhook_url = args.webhook_url or DEFAULT_WEBHOOK_URL
    if "YOUR_KEY_HERE" in webhook_url:
        print("\n[WARNING] 请配置企微机器人 Webhook URL：")
        print(f"  python3 wecom_integration.py send --fund {args.fund_code} "
              f"--return {args.fund_return} --benchmark {args.benchmark_return} "
              f"--webhook https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY")
        print("\n或修改 DEFAULT_WEBHOOK_URL")
        return 0

    resp = send_wecom_message(webhook_url, card)
    if resp.get("errcode") == 0:
        print(f"\n✅ 企微卡片发送成功（errcode=0）")
    else:
        print(f"\n❌ 发送失败：{resp}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
