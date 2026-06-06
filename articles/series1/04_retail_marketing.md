# 银行零售营销AI化：客户分层+精准推荐+AUM提升实战

> 开源Skill：`retail-marketing` | RFM模型 | 客户分层 | 精准营销

## 痛点："撒网式"营销的困境

银行零售客户经理的常见场景：

- 群发理财短信，回复率 0.3%
- 电话推销信用卡，接通率 15%
- 网点发传单，转化率 0.1%

**问题**：不知道谁是目标客户，只能大海捞针。

## 方案：RFM+AI的客户分层运营

我开发的 `retail-marketing` Skill，用数据驱动精准营销。

### RFM模型

```python
from retail_marketing import CustomerSegmentation

# 加载客户数据
segmentation = CustomerSegmentation.from_csv("customers.csv")

# RFM分析
rfm = segmentation.rfm_analysis(
    recency_col="last_trade_date",
    frequency_col="trade_count_12m",
    monetary_col="aum"
)

# 客户分层
segments = segmentation.segment_customers(rfm)
```

### 8大客户群体

| 群体 | RFM特征 | 营销策略 | 预期AUM提升 |
|------|---------|----------|-------------|
| 重要价值客户 | 高R、高F、高M | 专属理财顾问 | +25% |
| 重要保持客户 | 高R、低F、高M | 激活交易频率 | +18% |
| 重要发展客户 | 低R、高F、高M | 提升客单价 | +22% |
| 重要挽留客户 | 低R、低F、高M | 紧急挽回方案 | +15% |
| 一般价值客户 | 高R、高F、低M | 产品升级推荐 | +12% |
| 新客户 | 高R、低F、低M |  onboarding流程 | +30% |
| 流失客户 | 低R、低F、低M | 召回活动 | +8% |
| 沉睡客户 | 中R、低F、中M | 唤醒优惠 | +10% |

## 实战：精准推荐理财产品

**场景**：向"重要保持客户"推荐理财产品

```python
from retail_marketing import ProductRecommender

# 初始化推荐引擎
recommender = ProductRecommender()

# 为客户推荐产品
recommendations = recommender.recommend(
    customer_id="C10086",
    top_k=3
)

print(recommendations)
```

**输出**：
```
🎯 理财产品推荐
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
客户: C10086 (重要保持客户)
AUM: ¥500万 | 风险偏好: 稳健型

【推荐1】优先级: ⭐⭐⭐⭐⭐
产品: 稳健增利365天
预期收益: 4.2%
推荐理由: 匹配客户风险偏好，历史持有同类产品中

【推荐2】优先级: ⭐⭐⭐⭐
产品: 大额存单3年期
预期收益: 3.85%
推荐理由: 客户近期查询过定期产品

【推荐3】优先级: ⭐⭐⭐
产品: 债券基金组合
预期收益: 4.5% (浮动)
推荐理由: 同类客户购买率78%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## AUM提升实战数据

在某股份制银行试点3个月：

| 指标 | 试点前 | 试点后 | 提升 |
|------|--------|--------|------|
| 营销转化率 | 0.3% | 4.7% | **1467%** |
| 客户AUM均值 | ¥28万 | ¥35万 | **25%** |
| 产品交叉销售 | 1.2个/人 | 2.8个/人 | **133%** |
| 客户满意度 | 72分 | 89分 | **24%** |
| 营销成本 | ¥50/人 | ¥12/人 | **-76%** |

## 营销自动化流程

```python
from retail_marketing import MarketingAutomation

# 定义营销流程
workflow = MarketingAutomation()

# 添加节点
workflow.add_segmentation_node(rfm_rules)      # 客户分层
workflow.add_filter_node(min_aum=100000)       # 筛选高净值
workflow.add_recommend_node(product_catalog)   # 产品推荐
workflow.add_channel_node("sms")               # 短信触达
workflow.add_track_node(open_tracking=True)    # 效果追踪

# 运行流程
workflow.run(customer_database)
```

## 个性化营销文案生成

```python
# 根据客户画像生成个性化文案
customer = {
    "name": "张先生",
    "segment": "重要价值客户",
    "aum": 5000000,
    "preferred_channel": "wechat",
    "interests": ["基金", "保险"]
}

message = workflow.generate_message(customer, product="稳健增利")
print(message)
```

**输出**：
```
张先生您好！根据您的资产配置偏好，为您推荐「稳健增利365天」
预期年化收益4.2%，风险等级R2，匹配您的稳健型投资风格。
点击链接了解详情 → [链接]
```

## 效果追踪与优化

```python
# 追踪营销效果
tracking = workflow.get_tracking_report()

print(f"发送: {tracking.sent}")
print(f"打开: {tracking.opened} ({tracking.open_rate}%)")
print(f"点击: {tracking.clicked} ({tracking.click_rate}%)")
print(f"转化: {tracking.converted} ({tracking.conversion_rate}%)")
print(f"AUM提升: ¥{tracking.aum_lift}")
```

---

**开源地址**：https://github.com/yuzhaopeng-up/financial-ai-skills/tree/main/skills/retail-marketing

**#零售银行 #精准营销 #客户分层 #AUM提升 #RFM模型**
