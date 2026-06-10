#!/usr/bin/env python3
"""
厅堂精准营销 CLI 入口

用法：
    python3 scripts/lobby_mkt_cli.py generate "厅堂营销 40岁企业主 等候15分钟 资产200万 持有定期"
    python3 scripts/lobby_mkt_cli.py generate --age 40 --occupation 企业主 --waiting-minutes 15 --asset-level 100-500万 --history 定期,理财
    python3 scripts/lobby_mkt_cli.py card "厅堂营销 40岁企业主 等候15分钟 资产200万 持有定期"
    python3 scripts/lobby_mkt_cli.py timing "厅堂营销 40岁企业主 等候15分钟 资产200万"
"""

import argparse
import json
import sys
import os

# 确保从 skills/lobby_marketing/ 上一级可以 import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lobby_mkt_engine import LobbyMarketingEngine


def cmd_generate(args):
    """生成完整营销方案"""
    engine = LobbyMarketingEngine()

    if args.raw:
        result = engine.generate(raw_input=args.raw)
    else:
        history = [h.strip() for h in (args.history or "").split(",") if h.strip()]
        result = engine.generate(
            age=args.age,
            occupation=args.occupation,
            waiting_minutes=args.waiting_minutes,
            asset_level=args.asset_level,
            history_products=history,
            risk_preference=args.risk_preference or "",
        )

    # 格式化输出
    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.format == "json":
        print(output)
        return

    # 友好文本格式
    cp = result["customer_profile"]
    print("=" * 60)
    print("🎯 厅堂精准营销 - 营销辅助方案")
    print("=" * 60)
    print(f"\n📋 客户画像")
    print(f"  年龄：{cp['age']}岁  |  职业：{cp['occupation']}  |  风险偏好：{cp['risk_preference']}")
    print(f"  资产级别：{cp['asset_level']}  |  等候时间：{cp['waiting_minutes']}分钟")
    print(f"  已持产品：{', '.join(cp['history_products']) or '无'}")

    print(f"\n💰 推荐产品（匹配度排序）")
    for p in result["recommended_products"]:
        bar = "█" * int(p["match_score"] * 10) + "░" * (10 - int(p["match_score"] * 10))
        print(f"  [{bar}] {int(p['match_score']*100):3d}%  {p['product']}（{p['type']}）")
        print(f"         原因：{p['reason']}")

    print(f"\n🗣️ 话术方案")
    s = result["script"]
    print(f"\n  ── 开场白 ──")
    print(f"  {s['opening']}")

    print(f"\n  ── 需求挖掘 ──")
    print(f"  {s['need_discovery'][:300]}{'...' if len(s['need_discovery']) > 300 else ''}")

    print(f"\n  ── 产品呈现 ──")
    print(f"  {s['product_presentation'][:300]}{'...' if len(s['product_presentation']) > 300 else ''}")

    if s["objection_handling"]:
        print(f"\n  ── 异议处理（Top 3）──")
        for i, obj in enumerate(s["objection_handling"], 1):
            print(f"  {i}. 【{obj['objection']}】")
            print(f"     → {obj['response'][:120]}...")

    print(f"\n  ── 促成话术 ──")
    print(f"  {s['closing']}")

    timing = result["timing_signal"]
    status = "✅ 建议立即切入" if timing["ready"] else "⏳ 继续培养"
    print(f"\n⏱️ 促成时机：{status}（置信度 {int(timing['confidence']*100)}%）")
    for r in timing["reasons"]:
        print(f"    • {r}")

    print("\n" + "=" * 60)
    print("完整JSON已输出（添加 --format json 获取纯JSON）")
    print("=" * 60)


def cmd_card(args):
    """仅输出企微卡片内容"""
    engine = LobbyMarketingEngine()
    result = engine.generate(raw_input=args.raw)

    card = result["wecom_card"]
    if args.format == "json":
        print(json.dumps(card, ensure_ascii=False, indent=2))
    else:
        print(card["text"]["content"])


def cmd_timing(args):
    """仅输出促成时机判断"""
    engine = LobbyMarketingEngine()
    result = engine.generate(raw_input=args.raw)

    t = result["timing_signal"]
    status = "✅ 建议立即切入" if t["ready"] else "⏳ 继续培养"
    print(f"促成时机：{status}")
    print(f"置信度：{int(t['confidence']*100)}%")
    print("依据：")
    for r in t["reasons"]:
        print(f"  • {r}")


def main():
    parser = argparse.ArgumentParser(description="厅堂精准营销 CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # generate
    g = sub.add_parser("generate", help="生成完整营销方案")
    g.add_argument("--raw", help="自然语言输入，如：厅堂营销 40岁企业主 等候15分钟 资产200万 持有定期")
    g.add_argument("--age", type=int, help="客户年龄")
    g.add_argument("--occupation", help="职业（企业主/上班族/退休/高管）")
    g.add_argument("--waiting-minutes", type=int, dest="waiting_minutes", help="等候时间（分钟）")
    g.add_argument("--asset-level", dest="asset_level", help="资产级别")
    g.add_argument("--history", help="历史产品（逗号分隔，如：定期,理财）")
    g.add_argument("--risk-preference", dest="risk_preference", help="风险偏好")
    g.add_argument("--format", dest="format", choices=["text", "json"], default="text", help="输出格式")
    g.set_defaults(func=cmd_generate)

    # card
    c = sub.add_parser("card", help="输出企微卡片内容")
    c.add_argument("--raw", required=True, help="自然语言输入")
    c.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")
    c.set_defaults(func=cmd_card)

    # timing
    t = sub.add_parser("timing", help="输出促成时机判断")
    t.add_argument("--raw", required=True, help="自然语言输入")
    t.set_defaults(func=cmd_timing)

    args = parser.parse_args()

    # 如果没有传 raw 但有 --raw 参数位置错误，从 sys.argv 拼
    if not hasattr(args, "raw") or args.raw is None:
        pass  # handled by subparser

    args.func(args)


if __name__ == "__main__":
    main()
