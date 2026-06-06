#!/usr/bin/env python3
import requests
import re
import html as html_module

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

# 读取文章内容
with open('articles/series1/01_financial_intelligence.md') as f:
    content = f.read()

# 提取标题
title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
title = title_match.group(1).strip() if title_match else 'Test'
content = re.sub(r'^#\s+.+\n+', '', content, count=1)

# 转换HTML
html = content
html = re.sub(r'```(\w+)?\n(.*?)```', lambda m: f'<pre><code>{html_module.escape(m.group(2))}</code></pre>', html, flags=re.DOTALL)
html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html)
html = re.sub(r'\*(.+?)\*', r'<i>\1</i>', html)
html = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
html = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

# 分段
paragraphs = html.split('\n\n')
new_paragraphs = []
for p in paragraphs:
    p = p.strip()
    if p and not p.startswith('<') and not p.startswith('```'):
        p = f'<p>{p}</p>'
    new_paragraphs.append(p)
html = '\n\n'.join(new_paragraphs)

print('Title:', title[:50])
print('HTML length:', len(html))
print('HTML preview:', html[:300])

# 发送请求
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
print('Status:', resp.status_code)
print('Response:', resp.text[:500])
