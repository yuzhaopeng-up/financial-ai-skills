#!/bin/bash
# 知乎文章同步到飞书多维表格

token="t-g10469mXGEL5ASKUZTRTOJAJXPCCPH6FXZPAP2BH"
base_token="G1kgbpDYlaFO8DsoTE2c3vBonBh"
table_id="tblRU0knKUahGzm5"

python3 << PYEOF
import requests
import json
import os

token = "$token"
base_token = "$base_token"
table_id = "$table_id"

# 读取知乎发布状态
with open('/tmp/financial-ai-skills/publish_state.json') as f:
    state = json.load(f)
articles = state.get('published', {})

# 获取已有记录
resp = requests.get(
    f'https://open.feishu.cn/open-apis/bitable/v1/apps/{base_token}/tables/{table_id}/records',
    headers={'Authorization': f'Bearer {token}'},
    params={'page_size': 500}
)
data = resp.json()
existing_titles = set()
if data.get('code') == 0:
    for r in data.get('data', {}).get('items', []):
        title = r.get('fields', {}).get('标题', '')
        if title:
            existing_titles.add(title)

# 同步新文章
success = 0
for title, info in articles.items():
    if title in existing_titles:
        continue
    
    url = info.get('url', '')
    payload = {
        'fields': {
            '标题': title,
            '链接': {'text': '查看文章', 'link': url},
            '作者节点': 'Hermes_Brain',
            '平台': '知乎',
            '状态': '已发布',
        }
    }
    
    resp = requests.post(
        f'https://open.feishu.cn/open-apis/bitable/v1/apps/{base_token}/tables/{table_id}/records',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json=payload
    )
    result = resp.json()
    if result.get('code') == 0:
        success += 1

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 同步完成: 新增{success}篇")
PYEOF
