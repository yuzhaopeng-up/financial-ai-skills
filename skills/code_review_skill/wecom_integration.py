"""
企业微信集成 - Code Review 报告推送
将代码审查结果以卡片形式推送至企业微信群
"""

import json
import requests
from typing import Optional


WECOM_CARD_TEMPLATE = {
    "msgtype": "interactive",
    "interactive": {
        "tag": "div",
        "text": "代码安全审查报告"
    }
}


def build_review_card(report: dict) -> dict:
    """
    将 CodeReviewReport 转换为企业微信卡片格式

    :param report: code_review_engine.CodeReviewReport.to_dict() 输出
    :return: 企业微信消息卡片 JSON
    """
    summary = report.get("summary", {})
    issues = report.get("issues", [])

    # 评分颜色
    score = summary.get("quality_score", 10)
    if score >= 8:
        score_color = "#36BA6B"  # 绿色
    elif score >= 6:
        score_color = "#FFA500"  # 橙色
    else:
        score_color = "#FF0000"  # 红色

    # 构建问题摘要
    high = summary.get("high", 0)
    medium = summary.get("medium", 0)
    low = summary.get("low", 0)

    issue_brief = []
    if high > 0:
        issue_brief.append(f"🔴 HIGH: {high}")
    if medium > 0:
        issue_brief.append(f"🟡 MEDIUM: {medium}")
    if low > 0:
        issue_brief.append(f"🔵 LOW: {low}")

    # 高危问题详情
    high_issues_text = ""
    for issue in issues:
        if issue.get("severity") == "HIGH":
            high_issues_text += (
                f"<div class=\"highlight\">"
                f"<section>🔴 [{issue['severity']}] {issue['title']}</section>"
                f"<section>📍 {issue['location']} | 📂 {issue['category']}</section>"
                f"<section>📝 {issue['description']}</section>"
                f"<section>✅ 修复: {issue['fix_suggestion'][:80]}...</section>"
                f"</div>"
            )

    card = {
        "msgtype": "interactive",
        "interactive": {
            "card": {
                "header": {
                    "title": "🔍 代码安全审查报告",
                    "subtitle": f"语言: {summary.get('language', 'Unknown')}  |  问题: {summary.get('total_issues', 0)}个",
                    "template": "info" if high == 0 else "warning"
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": (
                            f"**质量评分:** <font color=\"{score_color}\">{score}/10</font>\n\n"
                            f"**问题统计:** {' | '.join(issue_brief)}\n"
                        )
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "markdown",
                        "content": (
                            f"**🔴 高危问题 ({high}个):**\n\n"
                            f"{high_issues_text if high_issues_text else '_暂无高危问题_'}"
                        )
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "markdown",
                        "content": (
                            f"**🟡 中危问题 ({medium}个):**\n\n"
                            + "\n\n".join([
                                f"<section>🟡 [{i['severity']}] {i['title']} - {i['location']}</section>"
                                for i in issues if i.get("severity") == "MEDIUM"
                            ]) if medium > 0 else "_暂无中危问题_"
                        )
                    },
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": "📋 查看完整报告",
                                "type": "view",
                                "url": "https://github.com/yuzhaopeng-up/financial-ai-skills/tree/main/skills/code_review_skill"
                            }
                        ]
                    }
                ]
            }
        }
    }

    return card


def send_review_card(
    report: dict,
    webhook_url: str,
    webhook_key: Optional[str] = None
) -> dict:
    """
    推送审查报告到企业微信

    :param report: code_review_engine.CodeReviewReport.to_dict() 输出
    :param webhook_url: 企业微信机器人 Webhook URL
    :param webhook_key: 可选，直接传入 webhook key 自动拼接 URL
    :return: 企业微信 API 响应
    """
    if webhook_key:
        webhook_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"

    card = build_review_card(report)

    try:
        response = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(card, ensure_ascii=False),
            timeout=10
        )
        result = response.json()
        if result.get("errcode") == 0:
            print("✅ 企业微信卡片发送成功")
        else:
            print(f"❌ 发送失败: {result}")
        return result
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return {"errcode": -1, "errmsg": str(e)}


def print_card_preview(report: dict):
    """打印卡片预览（不发送，仅预览格式）"""
    card = build_review_card(report)
    print(json.dumps(card, ensure_ascii=False, indent=2))


# 快捷函数
if __name__ == "__main__":
    # 演示用法
    sample_report = {
        "summary": {
            "language": "Python",
            "total_issues": 2,
            "high": 1,
            "medium": 1,
            "low": 0,
            "quality_score": 6.5
        },
        "issues": [
            {
                "id": 1,
                "severity": "HIGH",
                "category": "SQL_INJECTION",
                "title": "SQL 拼接查询 - 未使用参数化",
                "location": "line 12",
                "description": "用户输入直接拼接到 SQL 语句中",
                "code_snippet": "SELECT * FROM users WHERE name = '" + username + "'",
                "fix_suggestion": "cursor.execute('SELECT * FROM users WHERE name = %s', (username,))"
            },
            {
                "id": 2,
                "severity": "MEDIUM",
                "category": "SENSITIVE_INFO_LEAK",
                "title": "敏感信息泄露 - 硬编码密码",
                "location": "line 5",
                "description": "数据库连接密码硬编码在源码中",
                "code_snippet": "password = 'admin123'",
                "fix_suggestion": "import os; password = os.environ.get('DB_PASSWORD')"
            }
        ]
    }

    print("=== 卡片预览 ===")
    print_card_preview(sample_report)

    print("\n=== 推送测试（需提供真实 webhook_url） ===")
    # send_review_card(sample_report, "YOUR_WEBHOOK_URL_HERE")
