# 企业微信消息卡片化实战：从 Markdown 到 Template Card 的进化之路

> 本文记录了「龙马金融AI」将企微尽调报告从 Markdown 文本升级为 Template Card 的完整过程，包含类型选型、分层设计、代码实现与踩坑记录。文末附可复用的 Python 卡片构建器。

---

## 一、背景：Markdown 的「天花板」

我们的企微金融助手每天向风控/业务同事推送数十份贷前尽调报告。早期采用 Markdown 格式：

```
## 📊 示例制造集团 尽调报告
**股票代码**: 000000.DEMO

### 💹 实时行情
| 指标 | 数值 |
|------|------|
| 最新价 | ¥72.5 |
| 涨跌幅 | 📈 +1.23% |
...
```

**问题很快暴露：**

1. **移动端阅读体验差**：Markdown 表格在企微手机端被挤压，需左右滑动查看
2. **视觉层级混乱**：`###` 标题 + `|` 表格 + 空行，在 6 寸屏幕上占满 2-3 屏
3. **信息密度低**：风险等级、综合得分等核心指标淹没在表格中，无法「一眼抓取」
4. **无行动引导**：报告看完就结束，没有引导用户查看更详细的 H5 分析页

我们决定：将推送形式从 **Markdown 文本** 升级为 **Template Card 卡片 + H5 详情页**。

---

## 二、企微 Template Card 类型选型

企微目前提供 5 种原生卡片类型，我们逐一评估：

| 类型 | 特点 | 适用场景 | 我们的评估 |
|------|------|---------|-----------|
| `text_notice` | 大数字高亮 + 副标题 + 跳转按钮 | 通知类、指标摘要 | ✅ **主力选择** |
| `news_notice` | 封面图 + 图文摘要 + 引用块 | 深度文章、Newsletter | ✅ 备选（带封面报告） |
| `button_interaction` | 单选/多选按钮 + 回调 | 审批、投票、确认 | ⚪ 暂不适用 |
| `vote_interaction` | 投票计数 + 选项统计 | 问卷、表决 | ❌ 不适用 |
| `multiple_interaction` | 多行列表 + 选择器 | 任务清单、待办 | ❌ 不适用 |

**最终策略：**
- **常规尽调报告** → `text_notice`（风险等级大字号高亮，底部引导 H5）
- **深度研报/周报** → `news_notice`（配封面图 + 引用摘要）
- **行情异动提醒** → `text_notice`（最新价大字号 + 涨跌幅）

---

## 三、分层设计：卡片是「封面」，H5 是「正文」

卡片化的核心原则：**卡片只做摘要，详情交给 H5。**

### 3.1 信息分层

```
┌─────────────────────────────┐
│  龙马金融AI                   │  ← 来源
├─────────────────────────────┤
│  示例制造集团 尽调报告            │  ← 主标题
│  000000.DEMO | 06-06 20:54        │  ← 副标题
├─────────────────────────────┤
│           AA                │  ← 核心高亮 (风险等级)
│        风险等级              │
├─────────────────────────────┤
│ 得分 88 | 💹 +1.23% | 🟢舆情正面 │  ← 次级指标
├─────────────────────────────┤
│  [📄 查看完整报告]           │  ← 行动按钮 → H5
└─────────────────────────────┘
```

### 3.2 为什么这样设计？

- **3 秒法则**：用户收到消息后 3 秒内应抓住核心结论（风险等级 AA）
- **单一焦点**：`emphasis_content` 只允许一个核心数字，强迫我们选出最重要的指标
- **渐进披露**：感兴趣的同事点击按钮查看完整数据，不感兴趣的也不被长文本打扰

---

## 四、代码实现：Python + FastAPI

### 4.1 卡片构建函数

```python
def build_dd_template_card(result: dict) -> dict:
    """构建尽调报告 template_card (text_notice)"""
    company = result.get('company_name', '-')
    code = result.get('stock_code', '-')
    market = result.get('market_data', {})
    assessment = result.get('assessment', {})
    sentiment = result.get('sentiment', {})

    risk_level = assessment.get('risk_level', '未知')
    overall_score = assessment.get('overall_score', 70)

    # 行情摘要
    change_str = '-'
    if market and market.get('success'):
        change = market.get('change_percent', 0)
        change_str = f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"

    # 舆情摘要
    sentiment_level = sentiment.get('level', '未知')
    sentiment_score = sentiment.get('score', 50)
    sentiment_emoji = "🟢" if sentiment_score >= 70 else "🟡" if sentiment_score >= 40 else "🔴"

    # H5 详情页 URL
    h5_url = f"http://your-domain.com/dd-report?company={company}&code={code}"

    return {
        "card_type": "text_notice",
        "source": {"desc": "龙马金融AI", "desc_color": 0},
        "main_title": {
            "title": f"{company} 尽调报告",
            "desc": f"{code} | {datetime.now().strftime('%m-%d %H:%M')}"
        },
        "emphasis_content": {
            "title": risk_level,
            "desc": "风险等级"
        },
        "sub_title_text": f"得分 {overall_score} | 💹 {change_str} | {sentiment_emoji}舆情{sentiment_level}",
        "jump_list": [
            {"type": 1, "url": h5_url, "title": "📄 查看完整报告"}
        ]
    }
```

### 4.2 发送与 Fallback 策略

生产环境必须考虑 **降级方案**。企微的 `template_card` 有严格的字段校验，一旦格式错误整条消息作废。

```python
async def handle_due_diligence(user_id: str, company_name: str):
    result = await run_due_diligence(company_name)

    # 1. 优先发送卡片
    card = build_dd_template_card(result)
    card_resp = await send_wecom_card(user_id, card)

    if card_resp.get('errcode') != 0:
        # 2. 卡片失败 → fallback 到 Markdown
        logger.warning(f"卡片失败: {card_resp}, fallback到Markdown")
        report = format_dd_report(result)
        await send_wecom_message(user_id, report, "markdown")
```

**Fallback 触发场景实测：**
- `emphasis_content.title` 超过 10 个字符会被截断显示异常
- `sub_title_text` 超过 64 字部分机型不显示
- `jump_list` 超过 3 个按钮会直接报错
- H5 URL 未备案域名在部分企微版本中被拦截

### 4.3 与现有 Markdown 的对比

| 指标 | Markdown 版 | Template Card 版 |
|------|------------|-----------------|
| 首屏信息 | 标题+表格，需滑动 | 风险等级大字号，一眼可见 |
| 垂直高度 | 约 25 行 | 约 8 行 |
| 行动引导 | 无 | 「查看完整报告」按钮 |
| 视觉层级 | 弱（纯文本） | 强（字号/颜色对比） |
| 失败兜底 | 无 | 自动降级 Markdown |

---

## 五、踩坑记录

### 5.1 `emphasis_content` 只能有一组

企微 `text_notice` 只支持一组 `emphasis_content`（一个大数字 + 描述）。我们最初想同时展示「风险等级 AA」和「综合得分 88」，发现第二个会被忽略。

**解决**：将得分、涨跌幅、舆情压缩到 `sub_title_text` 中，用 `|` 分隔。

### 5.2 卡片与 Markdown 不能混发

企微单条消息只能有一个 `msgtype`。以下写法无效：

```python
# ❌ 错误：一条消息不能同时有 template_card 和 markdown
payload = {
    "msgtype": "template_card",
    "template_card": {...},
    "markdown": {...}  # 会被忽略
}
```

**解决**：拆成两条消息发送，或采用 Fallback 策略（二选一）。

### 5.3 H5 页面需处理企微内置浏览器兼容性

点击卡片跳转的 H5，在企微内置 WebView 中测试时发现：
- `localStorage` 偶发读写失败 → 改用服务端 Session
- `fixed` 定位在键盘弹起时错位 → 改用 `transform` 布局
- 缓存极激进 → URL 加 `?v=1.0.1` 时间戳

### 5.4 `task_id` 用于去重

如果尽调查询耗时较长，用户可能重复触发。企微卡片支持 `task_id` 字段，相同 `task_id` 的消息会自动覆盖旧卡片（而非刷屏）。

```python
card["task_id"] = f"dd_{user_id}_{company_name}_{datetime.now().strftime('%Y%m%d')}"
```

---

## 六、可复用的卡片构建器

我们将卡片逻辑封装为独立模块，已开源在项目中：

```python
from wecom_card_builder import WeComCardBuilder, send_card_with_fallback

builder = WeComCardBuilder()

# 尽调摘要
card = builder.due_diligence_card(
    company="示例制造集团", code="000000.DEMO",
    risk_level="AA", score=88,
    change_percent=1.23, sentiment="正面",
    h5_url="http://your-domain.com/report"
)

# 行情预警
card = builder.stock_alert_card(
    company="示例新能源汽车企业", code="000000.DEMO",
    price=268.5, change_percent=5.67
)

# 风险预警
card = builder.risk_warning_card(
    company="XX股份", code="600XXX",
    risk_level="CCC", warning="限售股解禁", score=32
)
```

支持 5 种模板 + 自动 Fallback，即插即用。

---

## 七、总结

| 阶段 | 动作 | 收益 |
|------|------|------|
| 1. 紧凑 Markdown | 减少空行、内联指标 | 行数 -40% |
| 2. Template Card | 大字号高亮 + 跳转按钮 | 3 秒抓核心 |
| 3. H5 详情页 | 完整数据 + 图表 | 深度用户留存 |

企微 Template Card 不是「花架子」，而是**信息降噪 + 行动引导**的有效工具。对于金融、风控、B 端工具类应用，卡片化能显著降低用户的认知负荷。

---

**相关链接：**
- 企微 Template Card 官方文档：[work.weixin.qq.com](https://developer.work.weixin.qq.com/document/path/90236#template_card)
- 本文代码已集成于「龙马金融AI」开源项目

---

*如果这篇文章对你有帮助，欢迎点赞收藏。有问题欢迎在评论区交流。*
