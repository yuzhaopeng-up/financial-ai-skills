#!/usr/bin/env python3
"""
知乎文章发布 + 飞书多维表格自动记录
用法: python publish_article_with_tracking.py --article articles/series1/01.md --platform 知乎
"""
import argparse
import os
import sys

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_base_writer import record_article_publish


def main():
    parser = argparse.ArgumentParser(description="发布文章并记录到飞书多维表格")
    parser.add_argument("--article", "-a", required=True, help="文章文件路径")
    parser.add_argument("--platform", "-p", required=True, 
                       choices=["知乎", "掘金", "公众号", "CSDN"],
                       help="发布平台")
    parser.add_argument("--url", "-u", required=True, help="文章URL")
    parser.add_argument("--author", default="Hermes", help="作者节点")
    args = parser.parse_args()
    
    # 从文件提取标题
    import re
    with open(args.article, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "未命名文章"
    
    print(f"📄 文章: {title[:50]}...")
    print(f"📰 平台: {args.platform}")
    print(f"🔗 URL: {args.url}")
    print()
    
    # 记录到飞书多维表格
    print("📝 记录到飞书多维表格...")
    try:
        result = record_article_publish(title, args.platform, args.url, args.author)
        if result.get("code") == 0:
            print("✅ 记录成功!")
            record_id = result.get("data", {}).get("record", {}).get("record_id", "N/A")
            print(f"   Record ID: {record_id}")
        else:
            print(f"❌ 记录失败: {result.get('msg', '未知错误')}")
    except Exception as e:
        print(f"❌ 异常: {e}")


if __name__ == "__main__":
    main()
