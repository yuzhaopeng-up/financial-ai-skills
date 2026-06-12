"""
企微卡片集成 - 调研纪要 v2.0
支持增强数据结构：情感分析、关键数据点、风险信号、竞品信息、行业数据、管理层指引
用法：python3 wecom_integration.py <调研记录文字>
      python3 wecom_integration.py "音频文件路径.wav"
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from meeting_minutes import MeetingMinutesEngine, SentimentAnalyzer


def build_card(result) -> dict:
    """构建企微消息卡片（增强版）。"""

    # 情感分析摘要
    sentiment = result.sentiment_analysis
    sentiment_icon = "🟢" if sentiment.get("overall_sentiment") == "正面" else \
                     "🔴" if sentiment.get("overall_sentiment") == "负面" else "🟡"
    sentiment_text = f"{sentiment_icon} 整体情感：{sentiment.get('overall_sentiment', '中性')} " \
                     f"(正{sentiment.get('positive_count', 0)}/负{sentiment.get('negative_count', 0)})"

    # 关键要点
    points_text = "\n".join(
        f"• {p['content'][:60]}{'...' if len(p['content']) > 60 else ''}"
        for p in result.key_points[:4]
    ) if result.key_points else "暂无记录"

    # 风险信号摘要
    if result.risk_signals:
        risk_types = {}
        for r in result.risk_signals:
            t = r.get("type", "其他")
            risk_types[t] = risk_types.get(t, 0) + 1
        risk_summary = " / ".join(f"{k}({v})" for k, v in risk_types.items())
        risks_text = f"⚠️ {len(result.risk_signals)}个风险信号：{risk_summary}"
    else:
        risks_text = "✅ 暂无明显风险信号"

    # 待办事项
    actions = "\n".join(f"📋 {a['item'][:40]}" for a in result.action_items[:3]) if result.action_items else "暂无待办事项"

    # 关键数据点
    if result.key_data_points:
        data_preview = " / ".join(d["value"] for d in result.key_data_points[:3])
        data_text = f"📊 数据点：{data_preview}"
    else:
        data_text = ""

    # 竞品信息
    if result.competitor_info:
        comp_names = [c["company"] for c in result.competitor_info[:3]]
        comp_text = f"🏢 竞品动态：{', '.join(comp_names)}"
    else:
        comp_text = ""

    # 承诺事项
    if result.commitments:
        commit_count = len(result.commitments)
        high_priority = sum(1 for c in result.commitments if c.get("priority") == "高")
        commit_text = f"📝 承诺事项：{commit_count}项 (高优{high_priority}项)"
    else:
        commit_text = ""

    # 会议类型颜色映射
    color_map = {
        "策略会": "purple",
        "业绩会": "orange",
        "实地调研": "blue",
        "电话会议": "green",
        "投资者日": "red",
        "交流会": "default",
    }
    card_color = color_map.get(result.meeting_category, "blue")

    # 构建 elements
    elements = [
        # 头部信息
        {"tag": "markdown", "content": f"**会议类型：**{result.meeting_type}  |  **分类：**{result.meeting_category}  |  **公司：**{result.company}  |  **日期：**{result.date}"},
        {"tag": "hr"},
        # 情感分析
        {"tag": "markdown", "content": sentiment_text},
        {"tag": "hr"},
        # 核心议题
        {"tag": "markdown", "content": f"**【核心议题】**\n{', '.join(result.core_topics) if result.core_topics else '综合交流'}"},
        {"tag": "hr"},
    ]

    # 数据点和承诺（如果存在）
    if data_text:
        elements.append({"tag": "markdown", "content": data_text})
        elements.append({"tag": "hr"})

    if commit_text:
        elements.append({"tag": "markdown", "content": commit_text})
        elements.append({"tag": "hr"})

    # 关键要点
    elements.append({"tag": "markdown", "content": f"**【关键要点】**\n{points_text}"})
    elements.append({"tag": "hr"})

    # 待办事项
    elements.append({"tag": "markdown", "content": f"**【待办事项】**\n{actions}"})
    elements.append({"tag": "hr"})

    # 风险信号
    elements.append({"tag": "markdown", "content": f"**【风险信号】**\n{risks_text}"})
    elements.append({"tag": "hr"})

    # 竞品信息
    if comp_text:
        elements.append({"tag": "markdown", "content": comp_text})
        elements.append({"tag": "hr"})

    # 管理层指引
    if result.guidance and any(v for v in result.guidance.values() if v):
        guidance_parts = []
        for k, v in result.guidance.items():
            if v and k != "other_guidance":
                guidance_parts.append(str(v))
        if guidance_parts:
            elements.append({"tag": "markdown", "content": f"**【管理层指引】**\n{' / '.join(guidance_parts)}"})
            elements.append({"tag": "hr"})

    # 纪要摘要
    elements.append({"tag": "markdown", "content": f"**【纪要摘要】**\n{result.summary}"})
    elements.append({"tag": "note", "elements": [{"tag": "plain_text", "content": f"生成时间：{result.generated_at} | 增强版v2.0"}]})

    return {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"📝 {result.title}"},
                "color": card_color,
            },
            "elements": elements,
        },
    }


def build_simple_card(result) -> dict:
    """构建简洁版企微卡片（仅核心字段）。"""
    points_text = "\n".join(
        f"• {p['content'][:60]}{'...' if len(p['content']) > 60 else ''}"
        for p in result.key_points[:3]
    ) if result.key_points else "暂无"
    risks_text = "\n".join(f"⚠️ {r}" for r in result.risks[:2]) if result.risks else "暂无重大风险"
    actions = "\n".join(f"📋 {a['item'][:30]}" for a in result.action_items[:2]) if result.action_items else "暂无"

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
                {"tag": "markdown", "content": f"**{result.meeting_category}** | {result.company} | {result.date}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【要点】**\n{points_text}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【待办】**\n{actions}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【风险】**\n{risks_text}"},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": f"生成：{result.generated_at}"}]},
            ],
        },
    }


if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "今天上午调研宁德时代储能业务"
    eng = MeetingMinutesEngine()
    result = eng.generate(text)
    card = build_card(result)
    print(f"Card built: {card['interactive']['header']['title']['content']}")
    print(f"Meeting category: {result.meeting_category}")
    print(f"Sentiment: {result.sentiment_analysis.get('overall_sentiment', 'N/A')}")
    print(f"Key data points: {len(result.key_data_points)}")
    print(f"Commitments: {len(result.commitments)}")
    print(f"Risk signals: {len(result.risk_signals)}")
