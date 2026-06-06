#!/usr/bin/env python3
"""
知乎文章自动发布脚本
用法: python publish_to_zhihu.py --article articles/series1/01_financial_intelligence.md --topics "人工智能" "金融科技"
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("请先安装requests: pip install requests")
    sys.exit(1)

# 知乎API基础URL
ZHIHU_API = "https://www.zhihu.com/api/v4"

class ZhihuPublisher:
    def __init__(self, cookies_str: str):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://zhuanlan.zhihu.com/",
            "Origin": "https://zhuanlan.zhihu.com",
            "x-requested-with": "fetch",
        })
        # 解析Cookie字符串
        self._parse_cookies(cookies_str)

    def _parse_cookies(self, cookies_str: str):
        """解析多种格式的Cookie输入"""
        # 尝试直接作为z_c0值
        if not cookies_str.startswith("_") and len(cookies_str) > 50:
            self.session.cookies.set("z_c0", cookies_str, domain=".zhihu.com")
            return
        # 解析标准Cookie格式
        for line in cookies_str.split(";"):
            line = line.strip()
            if "=" in line:
                parts = line.split("=", 1)
                if len(parts) == 2:
                    name, value = parts
                    name = name.strip()
                    value = value.strip()
                    if name in ["z_c0", "_xsrf", "d_c0", "SESSIONID"]:
                        self.session.cookies.set(name, value, domain=".zhihu.com")

    def _get_xsrf(self) -> str:
        """获取XSRF Token"""
        xsrf = self.session.cookies.get("_xsrf", "")
        if not xsrf:
            # 先访问首页获取xsrf
            self.session.get("https://www.zhihu.com/", timeout=10)
            xsrf = self.session.cookies.get("_xsrf", "")
        return xsrf or ""

    def create_draft(self, title: str, content: str, topics: list = None) -> dict:
        """创建文章草稿"""
        xsrf = self._get_xsrf()
        headers = {
            "x-xsrftoken": xsrf,
            "Content-Type": "application/json",
        }

        # 构建话题标签
        topic_ids = []
        if topics:
            for topic in topics:
                tid = self._search_topic(topic)
                if tid:
                    topic_ids.append(tid)

        payload = {
            "title": title,
            "content": content,
            "table_of_contents": False,
            "delta_time": 5,
        }
        if topic_ids:
            payload["topics"] = topic_ids

        url = f"{ZHIHU_API}/articles/draft"
        resp = self.session.post(url, headers=headers, json=payload, timeout=30)
        return resp.json()

    def _search_topic(self, keyword: str) -> dict | None:
        """搜索话题"""
        url = f"{ZHIHU_API}/topics"
        params = {"offset": 0, "limit": 5, "name": keyword}
        resp = self.session.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("data"):
            t = data["data"][0]
            return {"id": t["id"], "name": t["name"]}
        return None

    def publish_article(self, draft_id: str) -> dict:
        """发布文章"""
        xsrf = self._get_xsrf()
        headers = {
            "x-xsrftoken": xsrf,
            "Content-Type": "application/json",
        }
        url = f"{ZHIHU_API}/articles/{draft_id}/publish"
        resp = self.session.put(url, headers=headers, json={}, timeout=30)
        return resp.json()

    def publish_from_file(self, filepath: str, topics: list = None, dry_run: bool = False) -> dict:
        """从Markdown文件发布文章"""
        path = Path(filepath)
        if not path.exists():
            return {"error": f"文件不存在: {filepath}"}

        content = path.read_text(encoding="utf-8")

        # 提取标题 (第一个#开头的行)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # 移除标题行，剩余作为正文
            content = re.sub(r'^#\s+.+\n+', '', content, count=1)
        else:
            title = path.stem

        # 转换Markdown为知乎HTML格式
        html_content = self._markdown_to_zhihu_html(content)

        print(f"\n{'='*60}")
        print(f"标题: {title}")
        print(f"文件: {filepath}")
        print(f"字数: {len(content)}")
        print(f"话题: {topics or '无'}")
        print(f"模式: {'试运行' if dry_run else '正式发布'}")
        print(f"{'='*60}\n")

        if dry_run:
            print("[试运行] 内容预览:")
            print(html_content[:500] + "..." if len(html_content) > 500 else html_content)
            return {"dry_run": True, "title": title}

        # 创建草稿
        draft = self.create_draft(title, html_content, topics or [])
        if "id" in draft:
            draft_id = draft["id"]
            print(f"草稿创建成功: {draft_id}")
            # 发布
            result = self.publish_article(draft_id)
            if "id" in result:
                article_url = f"https://zhuanlan.zhihu.com/p/{result['id']}"
                print(f"✅ 发布成功: {article_url}")
                return {"success": True, "url": article_url, "id": result["id"]}
            else:
                print(f"❌ 发布失败: {result}")
                return {"error": "publish_failed", "detail": result}
        else:
            print(f"❌ 草稿创建失败: {draft}")
            return {"error": "draft_failed", "detail": draft}

    def _markdown_to_zhihu_html(self, md: str) -> str:
        """将Markdown转换为知乎支持的HTML"""
        import html as html_module

        html = md
        # 代码块
        html = re.sub(
            r'```(\w+)?\n(.*?)```',
            lambda m: f'<pre><code class="language-{m.group(1) or "text"}">{html_module.escape(m.group(2))}</code></pre>',
            html, flags=re.DOTALL
        )
        # 行内代码
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        # 粗体
        html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html)
        # 斜体
        html = re.sub(r'\*(.+?)\*', r'<i>\1</i>', html)
        # 标题
        html = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        # 列表
        html = re.sub(r'^\*\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        # 段落
        paragraphs = html.split('\n\n')
        new_paragraphs = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<') and not p.startswith('```'):
                p = f'<p>{p}</p>'
            new_paragraphs.append(p)
        html = '\n\n'.join(new_paragraphs)
        return html


def main():
    parser = argparse.ArgumentParser(description="知乎文章自动发布工具")
    parser.add_argument("--article", "-a", required=True, help="Markdown文章路径")
    parser.add_argument("--topics", "-t", nargs="+", help="话题标签，如: 人工智能 金融科技")
    parser.add_argument("--dry-run", "-d", action="store_true", help="试运行，不实际发布")
    parser.add_argument("--cookie", "-c", help="Cookie字符串，或从环境变量ZHIHU_COOKIE读取")
    args = parser.parse_args()

    cookie = args.cookie or os.environ.get("ZHIHU_COOKIE", "")
    if not cookie:
        print("错误: 请提供知乎Cookie，通过--cookie参数或ZHIHU_COOKIE环境变量")
        sys.exit(1)

    publisher = ZhihuPublisher(cookie)
    result = publisher.publish_from_file(args.article, args.topics, args.dry_run)

    if result.get("success"):
        print(f"\n🎉 文章发布成功！")
        print(f"链接: {result['url']}")
    elif result.get("dry_run"):
        print(f"\n✅ 试运行完成，可以正式发布")
    else:
        print(f"\n❌ 发布失败: {result}")
        sys.exit(1)


if __name__ == "__main__":
    main()
