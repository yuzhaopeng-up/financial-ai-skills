"""
企微卡片集成 - 市场观点
用法：python3 wecom_integration.py <市场描述>
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_view import MarketViewEngine

def build_card(result) -> dict:
    """构建企微消息卡片。"""
    index_text = "\n".join(
        f"• {idx['index']}：{idx['change_pct']:+.2f}%（{idx['comment']}）"
        for idx in result.index_performance
    )
    hot_text = "\n".join(
        f"• 🔥 **{t['theme']}**：{', '.join(t['leaders'][:2])}"
        for t in result.hot_themes[:3]
    )
    outlook_short = result.outlook.get("short_term", "")[:80]

    return {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"📊 {result.title}"},
                "color": "purple",
            },
            "elements": [
                {"tag": "markdown", "content": f"**【指数表现】**\n{index_text}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【热点主题】**\n{hot_text}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【资金流向】**\n北向：{result.money_flow['north_bound']['direction']}{result.money_flow['north_bound']['amount']}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【宏观视角】**\n{result.macro_view[:100]}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【短期展望】**\n{outlook_short}"},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": f"生成时间：{result.generated_at}"}]},
            ],
        },
    }

if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "市场日报 今天A股收盘情况"
    eng = MarketViewEngine()
    result = eng.generate(text)
    card = build_card(result)
    print(card)
