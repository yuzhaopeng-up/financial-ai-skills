"""
企微卡片集成 - 路演材料
用法：python3 wecom_integration.py <产品信息>
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from roadshow_material import RoadshowEngine

def build_card(result) -> dict:
    """构建企微消息卡片。"""
    ppt_text = "\n".join(
        f"{p['page']}. {p['title']}（{p.get('time_pages','')}页）"
        for p in result.ppt_outline[:6]
    )
    script_text = "\n".join(
        f"• **{s['section']}**：{s['duration']}"
        for s in result.speech_script
    )

    return {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"🎤 {result.title}"},
                "color": "green",
            },
            "elements": [
                {"tag": "markdown", "content": f"**产品：**{result.product_name}  |  **受众：**{result.target_audience}  |  **时长：**{result.duration}分钟"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【PPT大纲】**\n{ppt_text}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【讲稿结构】**\n{script_text}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【风险揭示】**\n{result.risk_disclosure[:100]}..."},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": f"生成时间：{result.generated_at}"}]},
            ],
        },
    }

if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "路演材料 固收理财 50岁以上保守型 30分钟"
    eng = RoadshowEngine()
    result = eng.generate(text)
    card = build_card(result)
    print(card)
