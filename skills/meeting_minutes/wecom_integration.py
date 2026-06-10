"""
企微卡片集成 - 调研纪要
用法：python3 wecom_integration.py <调研记录文字>
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from meeting_minutes import MeetingMinutesEngine

def build_card(result) -> dict:
    """构建企微消息卡片。"""
    points_text = "\n".join(
        f"• {p['content'][:60]}{'...' if len(p['content']) > 60 else ''}"
        for p in result.key_points[:4]
    )
    risks_text = "\n".join(f"⚠️ {r}" for r in result.risks[:3]) if result.risks else "暂无重大风险提示"
    actions = "\n".join(f"📋 {a['item'][:40]}" for a in result.action_items[:3]) if result.action_items else "暂无待办事项"

    return {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"📝 {result.title}"},
                "color": "blue",
            },
            "elements": [
                {"tag": "markdown", "content": f"**会议类型：**{result.meeting_type}  |  **公司：**{result.company}  |  **日期：**{result.date}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【核心议题】**\n{', '.join(result.core_topics) if result.core_topics else '综合交流'}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【关键要点】**\n{points_text}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【待办事项】**\n{actions}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【风险提示】**\n{risks_text}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【纪要摘要】**\n{result.summary}"},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": f"生成时间：{result.generated_at}"}]},
            ],
        },
    }

if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "今天上午调研宁德时代储能业务"
    eng = MeetingMinutesEngine()
    result = eng.generate(text)
    card = build_card(result)
    print(card)
