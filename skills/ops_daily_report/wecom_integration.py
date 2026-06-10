"""
企微卡片集成 - 运营日报
用法：python3 wecom_integration.py <运营数据>
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ops_daily_report import OpsDailyReportEngine

def build_card(result) -> dict:
    """构建企微消息卡片。"""
    overview_text = "\n".join(
        f"• {o['指标']}：{o['今日']}（环比{o['环比']}）"
        for o in result.business_overview[:4]
    )
    alert_text = "\n".join(
        f"• {a['类型']} {a['指标']}：{a['建议'][:40]}"
        for a in result.alerts[:3]
    ) if result.alerts else "✅ 今日无异常预警"
    plan_text = "\n".join(f"• {p}" for p in result.tomorrow_plan[:3])

    return {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"📋 {result.title}"},
                "color": "orange",
            },
            "elements": [
                {"tag": "markdown", "content": f"**一句话总结：**{result.summary}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【业务概况】**\n{overview_text}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【异常预警】**\n{alert_text}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【明日计划】**\n{plan_text}"},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": f"生成时间：{result.generated_at}"}]},
            ],
        },
    }

if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "运营日报 存款1000亿 贷款800亿 理财200亿"
    eng = OpsDailyReportEngine()
    result = eng.generate(text)
    card = build_card(result)
    print(card)
