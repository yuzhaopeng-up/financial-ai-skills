#!/usr/bin/env python3
"""
企微卡片集成 - wecom_integration.py

将回测报告以企微消息卡片形式发送给指定用户/群组。

用法:
    python3 wecom_integration.py --report_id test_001
    python3 wecom_integration.py --report_id test_002 --wecom_userid "your_userid"
    python3 wecom_integration.py --agent "wecom" --report '...' 
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backtest_engine import BacktestEngine, parse_strategy_from_text, parse_date_range, parse_symbol


def build_wecom_card(report: dict) -> dict:
    """将回测报告转换为企微消息卡片格式"""
    m = report.get("metrics", {})

    # 胜率颜色：绿色(盈利) / 红色(亏损)
    total_return = m.get("total_return", 0)
    return_color = "#00B42A" if total_return >= 0 else "#F53F3F"

    # 月度收益最好/最差月份
    monthly = report.get("monthly_returns", {})
    best_month = max(monthly.items(), key=lambda x: x[1], default=("", 0))
    worst_month = min(monthly.items(), key=lambda x: x[1], default=("", 0))

    card = {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "config": {
                "wide_screen_mode": True,
            },
            "header": {
                "title": {"tag": "plain_text", "content": f"📊 量化回测报告 — {report.get('strategy', 'N/A').upper()}"},
                "template": "#165DFF",
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": (
                            f"**标的：** {report.get('symbol', 'N/A')}  "
                            f"**区间：** {report.get('start_date', 'N/A')} → {report.get('end_date', 'N/A')}\n"
                            f"**初始资金：** ¥{report.get('initial_capital', 0):,.0f}  "
                            f"**信号数：** {report.get('signal_count', 0)}次"
                        ),
                    },
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": (
                            f"### 📈 关键指标\n\n"
                            f"**年化收益率：** {m.get('annual_return', 0):+.2f}%\n"
                            f"**总收益率：** {m.get('total_return', 0):+.2f}%\n"
                            f"**夏普比率：** {m.get('sharpe_ratio', 0):.3f}\n"
                            f"**卡尔玛比率：** {m.get('calmar_ratio', 0):.3f}\n"
                            f"**最大回撤：** {m.get('max_drawdown_pct', 0):.2f}%\n"
                            f"**胜率：** {m.get('win_rate', 0):.2f}%\n"
                            f"**盈亏比：** {m.get('profit_loss_ratio', 0):.3f}"
                        ),
                    },
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": (
                            f"### 🗓️ 月度收益\n\n"
                            f"最佳月份：{best_month[0]}（{best_month[1]:+.2f}%）\n"
                            f"最差月份：{worst_month[0]}（{worst_month[1]:+.2f}%）"
                        ),
                    },
                },
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": "**月份明细：**"},
                },
            ],
        },
    }

    # 添加月度收益表格
    if monthly:
        month_fields = []
        for month, ret in sorted(monthly.items())[-6:]:  # 最多6个月
            sign = "+" if ret >= 0 else ""
            month_fields.append({
                "tag": "column",
                "span": 1,
                "text": {
                    "tag": "lark_md",
                    "content": f"**{month}**\n{sign}{ret:.1f}%",
                },
            })

        card["interactive"]["elements"].append({
            "tag": "columns_set",
            "columns": month_fields,
        })

    # 添加最近买卖信号
    signals = report.get("trade_signals", [])
    if signals:
        signal_lines = []
        for s in signals[:5]:
            emoji = "🟢" if s["signal"] == "BUY" else "🔴"
            signal_lines.append(f"{emoji} {s['date']} {s['signal']} @ {s['close']}")

        card["interactive"]["elements"].extend([
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "### 📋 买卖信号示例\n\n" + "\n".join(signal_lines),
                },
            },
        ])

    card["interactive"]["elements"].append({
        "tag": "note",
        "elements": [
            {"tag": "plain_text", "content": f"由 ArkClaw quant_backtest 生成 | {report.get('end_date', 'N/A')}"},
        ],
    })

    return card


def send_wecom_card(card: dict, user_id: str = None, agent_id: str = None) -> dict:
    """通过企微API发送卡片消息"""
    #企微集成占位（实际使用时导入真实SDK）
    pass  # import wecom_sdk

    # 这里需要实际的企微应用凭证
    # 读取环境变量或配置文件
    import os

    corp_id = os.getenv("WECOM_CORP_ID", "")
    corp_secret = os.getenv("WECOM_CORP_SECRET", "")
    agent_id = agent_id or os.getenv("WECOM_AGENT_ID", "")

    if not corp_id or not corp_secret:
        return {
            "errcode": 0,
            "errmsg": "skip",
            "note": "企微凭证未配置，仅返回卡片内容",
            "card": card,
        }

    # 获取access_token
    token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}"
    try:
        import urllib.request
        with urllib.request.urlopen(token_url, timeout=10) as resp:
            token_data = json.loads(resp.read())
        access_token = token_data.get("access_token", "")
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}

    # 发送消息
    msg_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"

    msg_body = {
        "touser": user_id or "@all",
        "msgtype": "markdown",
        "agentid": agent_id,
        "markdown": {
            "content": format_markdown(report=None),
        },
    }

    try:
        import urllib.request
        req = urllib.request.Request(
            msg_url,
            data=json.dumps(msg_body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}


def format_markdown(report: dict) -> str:
    """将报告格式化为Markdown供企微发送"""
    if not report:
        return "无报告数据"
    m = report.get("metrics", {})
    monthly = report.get("monthly_returns", {})
    best = max(monthly.items(), key=lambda x: x[1], default=("", 0))
    worst = min(monthly.items(), key=lambda x: x[1], default=("", 0))

    lines = [
        f"**📊 量化回测 — {report.get('strategy', 'N/A').upper()}**",
        f"",
        f"**标的：** {report.get('symbol')}  **区间：** {report.get('start_date')} → {report.get('end_date')}",
        f"**初始资金：** ¥{report.get('initial_capital', 0):,.0f}",
        f"",
        f"### 关键指标",
        f"> 年化收益率：{m.get('annual_return', 0):+.2f}%",
        f"> 夏普比率：{m.get('sharpe_ratio', 0):.3f}",
        f"> 最大回撤：{m.get('max_drawdown_pct', 0):.2f}%",
        f"> 卡尔玛比率：{m.get('calmar_ratio', 0):.3f}",
        f"> 胜率：{m.get('win_rate', 0):.2f}%",
        f"> 盈亏比：{m.get('profit_loss_ratio', 0):.3f}",
        f"",
        f"### 月度收益",
        f"> 最佳：{best[0]}（{best[1]:+.2f}%）| 最差：{worst[0]}（{worst[1]:+.2f}%）",
    ]

    signals = report.get("trade_signals", [])
    if signals:
        lines.append("")
        lines.append("### 买卖信号")
        for s in signals[:5]:
            emoji = "🟢" if s["signal"] == "BUY" else "🔴"
            lines.append(f"{emoji} {s['date']} {s['signal']} @ {s['close']} | {s['reason']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="企微回测报告卡片")
    parser.add_argument("--report_id", type=str, help="报告ID（用于生成示例报告）")
    parser.add_argument("--wecom_userid", type=str, help="企微用户ID")
    parser.add_argument("--format", choices=["card", "markdown", "json"], default="card")
    parser.add_argument("--strategy", type=str, default="ma_cross")
    parser.add_argument("--symbol", type=str, default="XXXXXX.SH")
    parser.add_argument("--start", type=str, default="2024-01-01")
    parser.add_argument("--end", type=str, default="2024-12-31")

    args = parser.parse_args()

    # 生成示例报告
    engine = BacktestEngine(
        strategy=args.strategy,
        symbol=args.symbol,
        start_date=args.start,
        end_date=args.end,
        fast_period=20,
        slow_period=60,
    )
    report = engine.run()

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if args.format == "markdown":
        print(format_markdown(report))
        return 0

    # card 格式
    card = build_wecom_card(report)
    print(json.dumps(card, ensure_ascii=False, indent=2))

    # 尝试发送（如果配置了企微凭证）
    if args.wecom_userid:
        result = send_wecom_card(card, user_id=args.wecom_userid)
        print(f"\n[企微发送结果] {result}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
