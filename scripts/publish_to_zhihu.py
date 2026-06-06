#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知乎文章自动发布脚本
使用 z_c0 Cookie 认证

使用方法:
1. 从浏览器获取 z_c0 Cookie
2. 设置环境变量: export ZHihu_COOKIE="z_c0=你的cookie值"
3. 运行: python publish_to_zhihu.py --article articles/series1/01_financial_intelligence.md

注意：
- z_c0 Cookie 有效期约1个月，需定期更新
- 发布频率建议：每天不超过3篇，避免被封号
- 文章需符合知乎社区规范
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

# 尝试导入requests，如果没有则提示安装
try:
    import requests
except ImportError:
    print("请先安装requests库: pip install requests")
    sys.exit(1)


class ZhihuPublisher:
    """知乎文章发布器"""
    
    BASE_URL = "https://www.zhihu.com"
    API_URL = "https://www.zhihu.com/api/v4"
    
    def __init__(self, cookie=None):
        """
        初始化发布器
        
        Args:
            cookie: z_c0 cookie字符串，如 "z_c0=MTY4NTk0MjE5Mnx..."
                   如果为None，则从环境变量 ZHihu_COOKIE 读取
        """
        if cookie is None:
            cookie = os.environ.get('ZHihu_COOKIE', '')
        
        if not cookie:
            raise ValueError(
                "请提供 z_c0 Cookie\n"
                "方法1: 设置环境变量 export ZHihu_COOKIE='z_c0=你的cookie值'\n"
                "方法2: 传入参数 cookie='z_c0=你的cookie值'"
            )
        
        self.cookie = cookie
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Cookie': cookie,
            'x-requested-with': 'fetch',
            'referer': 'https://zhuanlan.zhihu.com/write',
            'origin': 'https://zhuanlan.zhihu.com'
        })
        
        # 验证登录状态
        self._verify_login()
    
    def _verify_login(self):
        """验证登录状态"""
        try:
            resp = self.session.get(f"{self.API_URL}/me")
            data = resp.json()
            
            if 'error' in data:
                print(f"❌ Cookie无效: {data['error'].get('message', '未知错误')}")
                print("请更新 z_c0 Cookie")
                sys.exit(1)
            
            self.user_id = data.get('id')
            self.user_name = data.get('name', '未知')
            print(f"✅ 登录成功: {self.user_name} (ID: {self.user_id})")
            
        except Exception as e:
            print(f"❌ 验证登录失败: {e}")
            sys.exit(1)
    
    def publish_article(self, title, content, topics=None):
        """
        发布文章到知乎专栏
        
        Args:
            title: 文章标题
            content: 文章内容（Markdown格式）
            topics: 话题标签列表，如 ["人工智能", "金融科技"]
        
        Returns:
            dict: 发布结果，包含文章URL等信息
        """
        # 1. 创建草稿
        print("📝 创建草稿...")
        draft_resp = self.session.post(
            f"{self.API_URL}/articles/drafts",
            json={}
        )
        draft_data = draft_resp.json()
        draft_id = draft_data.get('id')
        
        if not draft_id:
            print(f"❌ 创建草稿失败: {draft_data}")
            return None
        
        print(f"✅ 草稿创建成功: {draft_id}")
        
        # 2. 更新草稿内容
        print("📝 更新草稿内容...")
        update_resp = self.session.patch(
            f"{self.API_URL}/articles/drafts/{draft_id}",
            json={
                'title': title,
                'content': content,
                'topics': topics or []
            }
        )
        
        if update_resp.status_code not in [200, 201]:
            print(f"❌ 更新草稿失败: {update_resp.text}")
            return None
        
        print("✅ 草稿更新成功")
        
        # 3. 发布文章
        print("🚀 发布文章...")
        publish_resp = self.session.post(
            f"{self.API_URL}/articles/drafts/{draft_id}/publish",
            json={}
        )
        
        publish_data = publish_resp.json()
        
        if 'error' in publish_data:
            print(f"❌ 发布失败: {publish_data['error']}")
            return None
        
        article_url = publish_data.get('url', '')
        article_id = publish_data.get('id', '')
        
        print(f"✅ 文章发布成功!")
        print(f"   文章ID: {article_id}")
        print(f"   文章链接: {article_url}")
        
        return {
            'success': True,
            'id': article_id,
            'url': article_url,
            'title': title
        }
    
    def publish_from_file(self, file_path, topics=None):
        """
        从Markdown文件发布文章
        
        Args:
            file_path: Markdown文件路径
            topics: 话题标签列表
        
        Returns:
            dict: 发布结果
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            return None
        
        # 读取文件内容
        content = file_path.read_text(encoding='utf-8')
        
        # 提取标题（第一行#开头的）
        lines = content.split('\n')
        title = ''
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        if not title:
            print("❌ 无法提取标题，请确保文件第一行是 # 标题")
            return None
        
        print(f"📄 读取文件: {file_path}")
        print(f"📌 文章标题: {title}")
        print(f"📝 文章长度: {len(content)} 字符")
        
        # 发布
        return self.publish_article(title, content, topics)


def main():
    parser = argparse.ArgumentParser(description='知乎文章自动发布工具')
    parser.add_argument('--article', '-a', required=True, help='Markdown文件路径')
    parser.add_argument('--cookie', '-c', help='z_c0 Cookie（如不设置则从环境变量读取）')
    parser.add_argument('--topics', '-t', nargs='+', help='话题标签，如 "人工智能" "金融科技"')
    parser.add_argument('--dry-run', '-d', action='store_true', help='试运行，不实际发布')
    
    args = parser.parse_args()
    
    # 初始化发布器
    try:
        publisher = ZhihuPublisher(cookie=args.cookie)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # 试运行模式
    if args.dry_run:
        print("\n🏃 试运行模式（不会实际发布）")
        print(f"📄 文件: {args.article}")
        print(f"🏷️ 话题: {args.topics or '无'}")
        
        # 读取并显示文章信息
        file_path = Path(args.article)
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    print(f"📌 标题: {line[2:].strip()}")
                    break
            print(f"📝 长度: {len(content)} 字符")
        return
    
    # 发布文章
    print("\n" + "="*60)
    print("🚀 开始发布文章到知乎")
    print("="*60 + "\n")
    
    result = publisher.publish_from_file(
        file_path=args.article,
        topics=args.topics
    )
    
    if result and result.get('success'):
        print("\n" + "="*60)
        print("✅ 发布完成!")
        print(f"📎 文章链接: {result['url']}")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ 发布失败")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
