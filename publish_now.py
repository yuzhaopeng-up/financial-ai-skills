#!/usr/bin/env python3
import requests
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://zhuanlan.zhihu.com/',
    'Origin': 'https://zhuanlan.zhihu.com',
    'x-requested-with': 'fetch',
})
session.cookies.set('z_c0', '2|1:0|10:1780704513|4:z_c0|92:Mi4xdE1ITkdnQUFBQUNza2hSenhVTE1HeVlBQUFCZ0FsVk5KNXdQYXdBdG0xV0lWMXBVZlZXNEpCMDl1Zml2cHpXSlJ3|d700d2be7148a6db86cb23eb035e4979b610813705798c0dfd2e9c39d333939e', domain='.zhihu.com')
resp = session.get('https://www.zhihu.com/')
xsrf = session.cookies.get('_xsrf', '')

articles = [
    'articles/series1/01_financial_intelligence.md',
    'articles/series1/02_risk_compliance.md',
    'articles/series1/03_due_diligence.md',
    'articles/series1/04_retail_marketing.md',
    'articles/series1/05_credit_approval.md',
    'articles/series1/06_operations_automation.md',
    'articles/series1/07_wealth_management.md',
]

published = []
for filepath in articles:
    with open(filepath) as f:
        content = f.read()
    
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else 'Test'
    content = re.sub(r'^#\s+.+\n+', '', content, count=1)
    
    # 简化HTML转换
    html = content
    html = re.sub(r'```(\w+)?\n(.*?)```', lambda m: f'<pre><code>{m.group(2)}</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html)
    html = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    
    paragraphs = html.split('\n\n')
    new_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<'):
            p = f'<p>{p}</p>'
        new_paragraphs.append(p)
    html = '\n\n'.join(new_paragraphs)
    
    headers = {
        'x-xsrftoken': xsrf,
        'Content-Type': 'application/json',
    }
    payload = {
        'title': title,
        'content': html,
        'table_of_contents': False,
        'delta_time': 5,
    }
    
    resp = session.post('https://zhuanlan.zhihu.com/api/articles/drafts', headers=headers, json=payload, timeout=30)
    if resp.status_code == 200:
        draft = resp.json()
        draft_id = draft.get('id')
        if draft_id:
            resp = session.put(f'https://zhuanlan.zhihu.com/api/articles/{draft_id}/publish', headers=headers, json={}, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                article_id = result.get('id')
                published.append({'title': title, 'id': article_id, 'url': f'https://zhuanlan.zhihu.com/p/{article_id}'})
                print(f'✅ 发布成功: {title[:50]}')
            else:
                print(f'❌ 发布失败: {title[:50]} - {resp.status_code}')
        else:
            print(f'❌ 草稿ID为空: {title[:50]}')
    else:
        print(f'❌ 草稿失败: {title[:50]} - {resp.status_code}')

print(f'\n共发布 {len(published)} 篇文章')
for p in published:
    print(f'  - {p["title"][:50]}: {p["url"]}')
