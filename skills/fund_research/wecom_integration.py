"""
企微卡片集成 - 基金研究
用法：python3 wecom_integration.py <基金名称或代码>
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fund_research import FundResearchEngine

def build_card(result) -> dict:
    """构建企微消息卡片。"""
    perf = result.performance.get("区间收益", {})
    perf_text = "\n".join(
        f"• {k}：{v:+.2f}%"
        for k, v in list(perf.items())[:4]
    )
    risk_text = f"夏普比率：{result.risk_metrics['夏普比率']}  |  最大回撤：{result.risk_metrics['最大回撤']}"
    rec = result.recommendation

    return {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"📈 {result.title}"},
                "color": "purple",
            },
            "elements": [
                {"tag": "markdown", "content": f"**基金名称：**{result.fund_name}（{result.fund_code}）  |  **类型：**{result.fund_type}  |  **风险：**{result.risk_level}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【收益表现】**\n{perf_text}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【风险指标】**\n{risk_text}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【基金经理】**\n{result.manager['name']}，从业{result.manager['tenure']}，管理风格：{result.manager['management_style']}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【配置建议】**\n{'⭐' * (3 if rec['rating']=='高配' else 2 if rec['rating']=='标配' else 1)} **{rec['rating']}**：{rec['rationale'][:60]}"},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": f"生成时间：{result.generated_at}"}]},
            ],
        },
    }

if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "基金研究 易方达中小盘"
    eng = FundResearchEngine()
    result = eng.generate(text)
    card = build_card(result)
    print(card)
