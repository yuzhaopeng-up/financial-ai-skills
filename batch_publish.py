#!/usr/bin/env python3
"""
知乎文章批量发布脚本（带频率限制保护和状态记录）

策略：
- 每次运行只发布下一篇未发布的文章
- 发布成功后记录到 publish_state.json
- 遇到 403 频率限制时退出，等待下次运行
- 通过 cron 每 2-3 小时运行一次
"""
import requests
import re
import html as html_module
import time
import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Cookie配置
ZHIHU_COOKIE = "2|1:0|10:1780704513|4:z_c0|92:Mi4xdE1ITkdnQUFBQUNza2hSenhVTE1HeVlBQUFCZ0FsVk5KNXdQYXdBdG0xV0lWMXBVZlZXNEpCMDl1Zml2cHpXSlJ3|d700d2be7148a6db86cb23eb035e4979b610813705798c0dfd2e9c39d333939e"

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / "publish_state.json"

# 文章发布顺序
ARTICLES = [
    "articles/series1/01_financial_intelligence.md",
    "articles/series1/02_risk_compliance.md",
    "articles/series1/03_due_diligence.md",
    "articles/series1/04_retail_marketing.md",
    "articles/series1/05_credit_approval.md",
    "articles/series1/06_operations_automation.md",
    "articles/series1/07_wealth_management.md",
    "articles/series2/01_anti_money_laundering.md",
    "articles/series2/02_due_diligence_report.md",
    "articles/series2/03_rfm_customer_segment.md",
    "articles/series2/04_loan_calculator.md",
    "articles/series2/05_workflow_automation.md",
    "articles/series2/06_skill_architecture.md",
    "articles/series2/07_open_source_ecosystem.md",
    "articles/series3/01_digital_transformation.md",
    "articles/series3/02_data_privacy.md",
    "articles/series3/03_llm_plus_rules.md",
    "articles/series3/04_book_writing.md",
    "articles/series3/05_ai_assessment.md",
    "articles/series8/01_esg_quant_crossborder.md",
    "articles/series9/01_63_scenes_full_coverage.md",
]

# 昨天已发布的文章（标题 -> URL）
PUBLISHED_URLS = {
    "零API费用！我用Python写了一套银行财务AI智能体：6大场景全覆盖": "https://zhuanlan.zhihu.com/p/2046683959950586928",
    "银行风控合规的AI实践：关联图谱自动识别洗钱网络": "https://zhuanlan.zhihu.com/p/2046684091861546661",
    "如何写一个 Hermes Skill：从零到一完整指南": "https://zhuanlan.zhihu.com/p/2046524748184675279",
    "我用 Python 写了一套财务 AI 智能体：6大场景全覆盖，零API费用": "https://zhuanlan.zhihu.com/p/2046509606504080699",
}


def load_state() -> dict:
    """加载发布状态"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {
        "published": {},  # title -> {"url": ..., "published_at": ..., "article_id": ...}
        "last_attempt": None,
        "last_error": None,
    }


def save_state(state: dict):
    """保存发布状态"""
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_title(filepath: str) -> str:
    """从文章文件提取标题"""
    path = BASE_DIR / filepath
    content = path.read_text(encoding="utf-8")
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return title_match.group(1).strip() if title_match else path.stem


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
        html = re.sub(
            r'```(\w+)?\n(.*?)```',
            lambda m: f'<pre><code>{html_module.escape(m.group(2))}</code></pre>',
            html, flags=re.DOTALL
        )
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html)
        html = re.sub(r'\*(.+?)\*', r'<i>\1</i>', html)
        html = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
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
        path = BASE_DIR / filepath
        if not path.exists():
            return {"error": f"文件不存在: {filepath}"}

        content = path.read_text(encoding="utf-8")
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else path.stem
        content = re.sub(r'^#\s+.+\n+', '', content, count=1)
        html_content = self.markdown_to_html(content)

        print(f"\n发布: {title[:50]}...")

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
            return {"error": f"创建草稿失败: {resp.status_code}", "detail": resp.text[:300], "title": title}

        draft = resp.json()
        draft_id = draft.get("id")

        if not draft_id:
            return {"error": "草稿ID为空", "detail": draft, "title": title}

        print(f"草稿创建: {draft_id}")

        resp = self.session.put(
            f"https://zhuanlan.zhihu.com/api/articles/{draft_id}/publish",
            headers=headers, json={}, timeout=30
        )

        if resp.status_code != 200:
            return {"error": f"发布失败: {resp.status_code}", "detail": resp.text[:300], "title": title}

        result = resp.json()
        article_id = result.get("id")

        print(f"✅ 发布成功! https://zhuanlan.zhihu.com/p/{article_id}")

        return {
            "success": True,
            "article_id": article_id,
            "url": f"https://zhuanlan.zhihu.com/p/{article_id}",
            "title": title
        }


def sync_to_feishu(title: str, url: str, author: str = "Hermes_Brain"):
    """同步发布记录到飞书多维表格"""
    try:
        import sys
        sys.path.insert(0, str(BASE_DIR / "scripts"))
        from feishu_base_writer import record_article_publish
        result = record_article_publish(title, "知乎", url, author)
        if result.get("code") == 0:
            print(f"  飞书记录成功: {result.get('data', {}).get('record', {}).get('record_id', 'N/A')}")
            return True
        else:
            print(f"  飞书记录失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"  飞书同步异常: {e}")
        return False


def main():
    state = load_state()

    # 初始化：把昨天已知的发布记录加入状态
    for title, url in PUBLISHED_URLS.items():
        if title not in state["published"]:
            state["published"][title] = {
                "url": url,
                "published_at": "2026-06-06T00:00:00+08:00",
                "article_id": url.split("/p/")[-1],
            }

    # 找出下一篇待发布的文章
    pending = []
    for filepath in ARTICLES:
        title = extract_title(filepath)
        if title not in state["published"]:
            pending.append((filepath, title))

    print(f"=" * 60)
    print(f"知乎批量发布 | 已发布 {len(state['published'])}/{len(ARTICLES)} | 待发布 {len(pending)}")
    print(f"=" * 60)

    if not pending:
        print("所有文章已发布完毕！")
        save_state(state)
        return

    publisher = ZhihuPublisher()

    # 每次只发布一篇，避免触发频率限制
    filepath, title = pending[0]
    result = publisher.publish(filepath)

    now = datetime.now(tz=timezone(timedelta(hours=8))).isoformat()
    state["last_attempt"] = now

    if result.get("success"):
        state["published"][result["title"]] = {
            "url": result["url"],
            "published_at": now,
            "article_id": result["article_id"],
        }
        state["last_error"] = None
        save_state(state)

        # 同步到飞书
        print("同步到飞书多维表格...")
        sync_to_feishu(result["title"], result["url"])

        print(f"\n✅ 本次发布完成: {result['title']}")
        print(f"🔗 {result['url']}")
        remaining = len(pending) - 1
        print(f"⏳ 剩余 {remaining} 篇，建议 {2 if remaining > 0 else 0} 小时后再次运行")
    else:
        state["last_error"] = {
            "time": now,
            "error": result.get("error"),
            "detail": result.get("detail"),
        }
        save_state(state)
        print(f"\n❌ 发布失败: {result.get('error')}")
        detail_text = result.get("detail", "")
        if isinstance(detail_text, str):
            is_rate_limit = "频率" in detail_text or "PublishArticleLimitException" in detail_text
        else:
            is_rate_limit = False
        if is_rate_limit:
            print("⚠️ 触发知乎频率限制，请 2-3 小时后重试")


if __name__ == "__main__":
    main()
