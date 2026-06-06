#!/usr/bin/env python3
"""
飞书群聊通知器
用于发送 Actions 运行结果到飞书群聊
"""
import os
import requests
from typing import Optional

# 飞书群聊配置（Hermes Bot）
FEISHU_WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL", "")


def send_feishu_notification(title: str, content: str, 
                             status: str = "info") -> dict:
    """
    发送飞书群聊通知
    
    Args:
        title: 消息标题
        content: 消息内容
        status: 状态颜色 (info/success/warning/error)
    """
    if not FEISHU_WEBHOOK_URL:
        print("⚠️ 未配置 FEISHU_WEBHOOK_URL，跳过通知")
        return {}
    
    # 根据状态选择颜色
    color_map = {
        "info": "blue",
        "success": "green",
        "warning": "orange",
        "error": "red"
    }
    
    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                },
                "template": color_map.get(status, "blue")
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                }
            ]
        }
    }
    
    resp = requests.post(FEISHU_WEBHOOK_URL, json=payload, timeout=10)
    return resp.json()


def notify_github_stars_sync(repo: str, stars: int, forks: int, 
                              success: bool = True) -> dict:
    """GitHub Stars 同步完成通知"""
    status = "success" if success else "error"
    title = "✅ GitHub Stars 同步成功" if success else "❌ GitHub Stars 同步失败"
    
    content = f"""**仓库**: {repo}
**Stars**: ⭐ {stars}
**Forks**: 🍴 {forks}
**时间**: 刚刚

数据已同步到飞书多维表格「Skill追踪」表。"""
    
    return send_feishu_notification(title, content, status)


def notify_daily_metrics(summary: dict) -> dict:
    """每日指标汇总通知"""
    title = "📊 每日指标汇总"
    
    content = f"""**日期**: {summary.get('date', 'N/A')}

| 指标 | 数值 |
|------|------|
| Skill提交 | {summary.get('skill_pushes', 0)} |
| 文章发布 | {summary.get('articles', 0)} |
| 活跃节点 | {summary.get('active_nodes', 0)} |
| GitHub Stars | +{summary.get('github_stars', 0)} |
| 企微用户 | {summary.get('wecom_users', 0)} |
| 知乎阅读 | {summary.get('zhihu_views', 0)} |

数据已同步到飞书多维表格「每日指标」表。"""
    
    return send_feishu_notification(title, content, "info")


def notify_article_published(title: str, platform: str, url: str) -> dict:
    """文章发布成功通知"""
    notification_title = "📝 文章发布成功"
    
    content = f"""**标题**: {title}
**平台**: {platform}
**链接**: [点击查看]({url})

数据已同步到飞书多维表格「文章发布」表。"""
    
    return send_feishu_notification(notification_title, content, "success")


if __name__ == "__main__":
    # 测试通知
    print("=== 飞书通知测试 ===")
    
    # 测试 Stars 同步通知
    result = notify_github_stars_sync(
        "yuzhaopeng-up/financial-ai-skills",
        stars=156,
        forks=34
    )
    print(f"Stars通知: {result}")
    
    # 测试文章发布通知
    result = notify_article_published(
        "测试文章标题",
        "知乎",
        "https://zhuanlan.zhihu.com/p/test"
    )
    print(f"文章通知: {result}")
