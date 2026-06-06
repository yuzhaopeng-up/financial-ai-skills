#!/usr/bin/env python3
"""
每日指标自动汇总
用法: python daily_metrics_cron.py
建议配置为每天 00:00 运行
"""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feishu_base_writer import FeishuBaseWriter


def collect_daily_metrics() -> dict:
    """收集每日指标"""
    metrics = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "skill_pushes": 0,
        "articles": 0,
        "active_nodes": 0,
        "github_stars": 0,
        "wecom_users": 0,
        "zhihu_views": 0,
        "note": ""
    }
    
    # TODO: 从各数据源收集实际数据
    # - GitHub API: 今日 push 数、新增 Stars
    # - 知乎 API: 今日阅读量
    # - 企微 API: 今日活跃用户数
    # - ClawLink: 在线节点数
    
    return metrics


def main():
    print("=" * 50)
    print("每日指标汇总")
    print(f"日期: {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 50)
    print()
    
    # 收集指标
    print("📊 收集指标...")
    metrics = collect_daily_metrics()
    print(f"   Skill提交: {metrics['skill_pushes']}")
    print(f"   文章发布: {metrics['articles']}")
    print(f"   活跃节点: {metrics['active_nodes']}")
    print(f"   GitHub Stars: {metrics['github_stars']}")
    print()
    
    # 写入飞书
    print("📝 写入飞书多维表格...")
    try:
        writer = FeishuBaseWriter()
        result = writer.add_daily_metrics(
            date=metrics["date"],
            skill_pushes=metrics["skill_pushes"],
            articles=metrics["articles"],
            active_nodes=metrics["active_nodes"],
            github_stars=metrics["github_stars"],
            wecom_users=metrics["wecom_users"],
            zhihu_views=metrics["zhihu_views"],
            note=metrics["note"]
        )
        
        if result.get("code") == 0:
            print("✅ 汇总成功!")
            record_id = result.get("data", {}).get("record", {}).get("record_id", "N/A")
            print(f"   Record ID: {record_id}")
        else:
            print(f"❌ 汇总失败: {result.get('msg', '未知错误')}")
    except Exception as e:
        print(f"❌ 异常: {e}")


if __name__ == "__main__":
    main()
