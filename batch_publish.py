#!/usr/bin/env python3
"""
批量发布文章到知乎
"""
import requests
import re
import html as html_module
import time
from pathlib import Path

# Cookie配置
ZHIHU_COOKIE = "2|1:0|10:1780704513|4:z_c0|92:Mi4xdE1ITkdnQUFBQUNza2hSenhVTE1HeVlBQUFCZ0FsVk5KNXdQYXdBdG0xV0lWMXBVZlZXNEpCMDl1Zml2cHpXSlJ3|d700d2be7148a6db86cb23eb035e4979b610813705798c0dfd2e9c39d333939e"

class ZhihuPublisher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://zhuanlan.zhihu.com/",
            "Origin": "https://zhuanlan.zhihu.com",
            "x-requested-with": "fetch",
        })
        self.session.cookies.set("z_c0", ZHIHU_COOKIE, domain=".zhihu.com")
        self.xsrf = ""
        self._refresh_xsrf()
    
    def _refresh_xsrf(self):
        """刷新XSRF Token"""
        self.session.get("https://www.zhihu.com/", timeout=10)
        self.xsrf = self.session.cookies.get("_xsrf", "")
    
    def markdown_to_html(self, md: str) -> str:
        """Markdown转HTML"""
        html = md
        # 代码块
        html = re.sub(
            r'```(\w+)?\n(.*?)```',
            lambda m: f'<pre><code>{html_module.escape(m.group(2))}</code></pre>',
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
        # 段落
        paragraphs = html.split('\n\n')
        new_paragraphs = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<') and not p.startswith('```'):
                p = f'<p>{p}</p>'
            new_paragraphs.append(p)
        return '\n\n'.join(new_paragraphs)
    
    def publish(self, filepath: str) -> dict:
        """发布单篇文章"""
        path = Path(filepath)
        if not path.exists():
            return {"error": f"文件不存在: {filepath}"}
        
        # 读取内容
        content = path.read_text(encoding="utf-8")
        
        # 提取标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else path.stem
        content = re.sub(r'^#\s+.+\n+', '', content, count=1)
        
        # 转换HTML
        html_content = self.markdown_to_html(content)
        
        print(f"\n{'='*60}")
        print(f"发布: {title[:40]}...")
        print(f"文件: {filepath}")
        
        # 创建草稿
        headers = {
            "x-xsrftoken": self.xsrf,
            "Content-Type": "application/json",
        }
        payload = {
            "title": title,
            "content": html_content,
            "table_of_contents": False,
            "delta_time": 5,
        }
        
        resp = self.session.post(
            "https://zhuanlan.zhihu.com/api/articles/drafts",
            headers=headers, json=payload, timeout=30
        )
        
        if resp.status_code != 200:
            return {"error": f"创建草稿失败: {resp.status_code}", "detail": resp.text[:200]}
        
        draft = resp.json()
        draft_id = draft.get("id")
        
        if not draft_id:
            return {"error": "草稿ID为空", "detail": draft}
        
        print(f"草稿创建: {draft_id}")
        
        # 发布
        resp = self.session.put(
            f"https://zhuanlan.zhihu.com/api/articles/{draft_id}/publish",
            headers=headers, json={}, timeout=30
        )
        
        if resp.status_code != 200:
            return {"error": f"发布失败: {resp.status_code}", "detail": resp.text[:200]}
        
        result = resp.json()
        article_id = result.get("id")
        
        print(f"✅ 发布成功!")
        print(f"链接: https://zhuanlan.zhihu.com/p/{article_id}")
        
        return {
            "success": True,
            "article_id": article_id,
            "url": f"https://zhuanlan.zhihu.com/p/{article_id}",
            "title": title
        }

def main():
    publisher = ZhihuPublisher()
    
    # 文章列表
    articles = [
        # 系列1
        "articles/series1/01_financial_intelligence.md",
        "articles/series1/02_risk_compliance.md",
        "articles/series1/03_due_diligence.md",
        "articles/series1/04_retail_marketing.md",
        "articles/series1/05_credit_approval.md",
        "articles/series1/06_operations_automation.md",
        "articles/series1/07_wealth_management.md",
        # 系列2
        "articles/series2/01_anti_money_laundering.md",
        "articles/series2/02_due_diligence_report.md",
        "articles/series2/03_rfm_customer_segment.md",
        "articles/series2/04_loan_calculator.md",
        "articles/series2/05_workflow_automation.md",
        "articles/series2/06_skill_architecture.md",
        "articles/series2/07_open_source_ecosystem.md",
        # 系列3
        "articles/series3/01_digital_transformation.md",
        "articles/series3/02_data_privacy.md",
        "articles/series3/03_llm_plus_rules.md",
        "articles/series3/04_book_writing.md",
        "articles/series3/05_ai_assessment.md",
        "articles/series3/06_ecosystem_building.md",
    ]
    
    results = []
    for i, article in enumerate(articles, 1):
        print(f"\n[{i}/{len(articles)}] ", end="")
        result = publisher.publish(article)
        results.append(result)
        
        if result.get("success"):
            # 每篇间隔30秒，避免触发反spam
            if i < len(articles):
                print(f"等待30秒...")
                time.sleep(30)
        else:
            print(f"❌ 失败: {result.get('error')}")
    
    # 汇总
    print(f"\n{'='*60}")
    print("发布汇总")
    print(f"{'='*60}")
    success = sum(1 for r in results if r.get("success"))
    print(f"成功: {success}/{len(articles)}")
    
    for r in results:
        if r.get("success"):
            print(f"✅ {r['title'][:30]}... -> {r['url']}")
        else:
            print(f"❌ {r.get('error', '未知错误')}")

if __name__ == "__main__":
    main()
