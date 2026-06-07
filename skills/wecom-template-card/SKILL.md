---
name: wecom-template-card
description: "Enterprise WeChat template_card builder and sender. Provides reusable card templates for due diligence reports, stock alerts, risk warnings, and more. Supports text_notice, news_notice, and button_interaction card types with fallback to markdown."
description_zh: "企业微信 template_card 卡片构建与发送套件，提供尽调报告、行情快讯、风险预警等可复用模板"
description_en: "WeCom template_card builder with reusable templates for financial reports and alerts"
version: "1.0.0"
allowed-tools: Bash, Read, Write
---

# WeCom Template Card

企业微信 `template_card` 卡片构建与发送工具包，专为金融场景设计。

## 能力概览

| 模板类型 | 适用场景 | card_type |
|---------|---------|-----------|
| 尽调摘要卡 | 贷前尽调报告推送 | `text_notice` |
| 行情快讯卡 | 实时股价异动提醒 | `text_notice` |
| 风险预警卡 | 风险等级变更通知 | `text_notice` |
| 图文报告卡 | 带封面的深度报告 | `news_notice` |
| 交互确认卡 | 审批/确认操作 | `button_interaction` |

## 核心模块

### `WeComCardBuilder` — 卡片构建器

```python
from wecom_card_builder import WeComCardBuilder

builder = WeComCardBuilder()

# 尽调摘要卡
card = builder.due_diligence_card(
    company="美的集团",
    code="000333",
    risk_level="AA",
    score=88,
    change_percent=1.23,
    sentiment="正面",
    h5_url="http://your-domain.com/report"
)

# 行情快讯卡
card = builder.stock_alert_card(
    company="比亚迪",
    code="002594",
    price=268.50,
    change_percent=5.67,
    alert_type="涨幅异动"
)

# 风险预警卡
card = builder.risk_warning_card(
    company="XX股份",
    code="600XXX",
    risk_level="CCC",
    warning="限售股解禁 | 大股东减持",
    score=32
)
```

### `send_template_card` — 发送函数

```python
from wecom_card_builder import send_template_card

result = await send_template_card(
    access_token="YOUR_TOKEN",
    to_user="USER_ID",
    agent_id=AGENT_ID,
    card=card
)
```

## 卡片设计规范

### 颜色映射

| 风险等级 | emphasis_content 颜色 | 语义 |
|---------|---------------------|------|
| AAA, AA, A | 绿色 (#07C160) | 安全 |
| BBB, BB | 橙色 (#FAAD14) | 关注 |
| CCC 及以下 | 红色 (#F5222D) | 危险 |

> 注: `text_notice` 的 `emphasis_content` 颜色由企微根据内容自动渲染，开发者只需确保数据准确。

### 跳转链接规范

```json
{
  "type": 1,
  "url": "http://your-domain.com/dd-report?company=XXX&code=XXX",
  "title": "📄 查看完整报告"
}
```

- `type=1`: 跳转 URL
- `type=2`: 跳转小程序 (需配置 appid)

## 完整示例

```python
import asyncio
from wecom_card_builder import WeComCardBuilder, send_template_card

async def main():
    builder = WeComCardBuilder()
    
    card = builder.due_diligence_card(
        company="贵州茅台",
        code="600519",
        risk_level="AAA",
        score=95,
        change_percent=-0.45,
        sentiment="正面",
        h5_url="http://your-domain.com/dd-report?company=贵州茅台&code=600519"
    )
    
    result = await send_template_card(
        access_token=await get_token(),
        to_user="USER_ID",
        agent_id=AGENT_ID,
        card=card
    )
    print(result)

asyncio.run(main())
```

## 与 H5 详情页配合

卡片仅展示**摘要**，详细数据通过跳转链接引导至 H5:

```
用户触发尽调
    ↓
Bot 发送 template_card (核心指标 + 跳转按钮)
    ↓
用户点击"查看完整报告"
    ↓
打开 H5 页面 (完整行情表格、舆情详情、评估细则)
```

## 依赖

```bash
pip install httpx
```

## 文件说明

- `SKILL.md`: 本说明文档
- `wecom_card_builder.py`: 核心构建器 + 发送函数
