"""
企微卡片集成 - WeChat Work Card Integration for Research Notes
用于将调研纪要通过企微消息卡片推送
"""

import json
import os
from typing import Dict, Any, Optional


def build_wecom_card(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    将调研纪要结果转换为企微消息卡片格式

    Args:
        result: ResearchNotesEngine.generate() 返回的结构化纪要

    Returns:
        企微卡片 payload（可直接用于企微 Webhook 或 Agent 发送）
    """
    sentiment = result['sentiment_analysis']
    metadata = result['metadata']

    # 情绪标签和颜色
    sentiment_color = {
        "乐观": "green",
        "中性": "grey",
        "谨慎": "red"
    }
    color = sentiment_color.get(sentiment['sentiment_label'], "grey")

    # 出席人员
    attendees_text = "、".join(result['attendees'][:4])
    if len(result['attendees']) > 4:
        attendees_text += f" 等{len(result['attendees'])}人"

    # 关键数据摘要
    key_data_items = []
    for d in result['key_data'][:3]:
        key_data_items.append(f"- **{d['指标']}**：{d['数值']}")
    key_data_md = "\n".join(key_data_items) if key_data_items else "- 暂无关键数据"

    # 核心讨论摘要
    discussion_items = []
    for i, d in enumerate(result['core_discussions'][:3], 1):
        discussion_items.append(f"{i}. {d[:60]}{'...' if len(d) > 60 else ''}")
    discussion_md = "\n".join(discussion_items) if discussion_items else "- 暂无核心讨论记录"

    # 风险点
    risk_md = ""
    if result['risk_points']:
        risk_items = [f"- {r[:50]}{'...' if len(r) > 50 else ''}" for r in result['risk_points'][:2]]
        risk_md = "\n".join(risk_items)
    else:
        risk_md = "- 未识别明显风险点"

    # 承诺事项
    commitment_md = ""
    if result['commitments']:
        commitment_items = [f"- {c['事项'][:40]}" for c in result['commitments'][:2]]
        commitment_md = "\n".join(commitment_items)
    else:
        commitment_md = "- 暂无承诺事项"

    # 待跟进
    followup_md = ""
    if result['follow_up_questions']:
        followup_items = [f"- {q[:50]}{'...' if len(q) > 50 else ''}" for q in result['follow_up_questions'][:2]]
        followup_md = "\n".join(followup_items)
    else:
        followup_md = "- 无待跟进问题"

    card = {
        "msgtype": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "text": f"📋 调研纪要 | {metadata['company_masked']}"
                },
                "subtitle": {
                    "tag": "plain_text",
                    "text": f"{metadata.get('调研方式', 'N/A')} | {metadata.get('调研日期', 'N/A')}"
                },
                "card_color": color
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": f"**👥 出席人员**\n{attendees_text}"
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "markdown",
                    "content": f"**💬 核心交流**\n{discussion_md}"
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "markdown",
                    "content": f"**📈 关键数据**\n{key_data_md}"
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "markdown",
                    "content": f"**🚨 风险点**\n{risk_md}"
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "markdown",
                    "content": f"**📌 承诺事项**\n{commitment_md}"
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "markdown",
                    "content": f"**📝 投资建议**\n{result['investment_suggestion'][:100]}"
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "markdown",
                    "content": f"**🔍 待跟进**\n{followup_md}"
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "markdown",
                    "content": (
                        f"**📊 情感分析**\n"
                        f"- 管理层信心指数：**{sentiment['confidence_index']}/10**（{sentiment['sentiment_label']}）\n"
                        f"- 信息可信度评分：**{result['credibility_score']}/10**"
                    )
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "text": f"生成时间：{metadata.get('生成时间', 'N/A')}"
                        }
                    ]
                }
            ]
        }
    }

    return card


def send_card_via_webhook(webhook_url: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """
    通过企微 Webhook 发送消息卡片

    Args:
        webhook_url: 企微群机器人的 Webhook URL
        result: ResearchNotesEngine.generate() 返回的结构化纪要

    Returns:
        发送结果
    """
    import urllib.request
    import urllib.error

    card = build_wecom_card(result)
    payload = json.dumps(card).encode('utf-8')

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"errcode": e.code, "errmsg": str(e)}
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}


def card_to_file(result: Dict[str, Any], output_path: str = "/tmp/research_notes_card.json"):
    """
    将卡片保存到文件（用于调试或后续发送）
    """
    card = build_wecom_card(result)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(card, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 企微卡片已保存到: {output_path}")
    return output_path


# CLI 入口
if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from notes_engine import ResearchNotesEngine
    import argparse

    parser = argparse.ArgumentParser(description="企微卡片生成工具")
    parser.add_argument('--input', type=str, required=True, help='调研纪要输入文本')
    parser.add_argument('--webhook', type=str, default='', help='企微 Webhook URL（可选）')
    parser.add_argument('--output', type=str, default='/tmp/research_notes_card.json', help='输出文件')
    args = parser.parse_args()

    # 解析输入
    from scripts.notes_cli import parse_input
    parsed = parse_input(args.input)

    engine = ResearchNotesEngine()
    result = engine.generate(
        company=parsed['company'],
        subject=parsed['subject'],
        method=parsed['method'],
        raw_notes=parsed['raw_notes'],
        date=parsed['date']
    )

    # 生成并保存卡片
    card_to_file(result, args.output)

    # 如果提供了 Webhook 则发送
    if args.webhook:
        print(f"[INFO] 正在发送企微卡片...")
        resp = send_card_via_webhook(args.webhook, result)
        print(f"[INFO] 发送结果: {resp}")
