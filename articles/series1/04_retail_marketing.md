# 银行零售营销AI化：客户分层+精准推荐+AUM提升实战

> 开源地址：https://github.com/yuzhaopeng-up/financial-ai-skills
>
> 基于《AI赋能银行数字化转型》第12-13章实战代码。

---

## 一、零售营销的困境

某银行零售部的数据：

- 客户50万，但月活不到5%
- 产品推荐靠人工，转化率0.3%
- AUM增长停滞，客户流失率15%
- 营销活动ROI无法追踪

**问题**：没有分层、没有精准推荐、没有闭环。

---

## 二、AI解决方案：8大能力

| 能力 | 效果 |
|------|------|
| **客户画像构建** | 360°标签体系，价值评分72分 |
| **客户分层运营** | RFM+AUM+生命周期三层分层 |
| **精准营销推荐** | 基于画像的产品匹配，转化率提升5倍 |
| **产品匹配引擎** | 风险适配+需求匹配+收益预期 |
| **AUM提升策略** | 交叉销售+向上销售，目标提升30% |
| **营销效果评估** | ROI+NPS+转化率全链路追踪 |
| **客户流失预警** | 提前30天识别流失风险 |
| **营销活动策划** | 自动设计活动+渠道+预算 |

---

## 三、快速上手

```python
from retail_marketing import RetailMarketingEngine

engine = RetailMarketingEngine()

# 完整营销分析
result = engine.full_marketing_analysis(
    customer_id="C001",
    name="李明",
    age=35,
    gender="男",
    occupation="IT工程师",
    income_level="高",
    aum=500000,
    risk_preference="稳健型",
    last_transaction_days=15,
    transaction_count_12m=12,
    total_amount_12m=200000,
    customer_age_months=24,
    aum_trend="上升",
    current_products=["活期存款", "稳健理财"]
)
```

**输出**：
```
📊 零售客户营销分析报告
├── 客户画像：李明，35岁IT工程师，AUM 50万
│   ├── 标签：潜力客户、育儿期
│   └── 价值评分：72.0 分
├── 客户分层：🥉 黄金客户 | 重要发展客户
│   ├── RFM评分：R4 F4 M3 = 11
│   ├── 生命周期：成长期
│   └── 价值潜力：高
├── 产品推荐 TOP3：
│   1. 债券基金 (85分) - 风险匹配
│   2. 结构性存款 (85分) - 保本浮动
│   3. 混合基金 (80分) - 适合成长期
└── AUM提升路径：潜力→白金
    ├── 缺口：50万元
    ├── 预计时间：6-12个月
    └── 成功概率：25%
```

---

## 四、核心算法

### 4.1 RFM评分

```python
def calculate_rfm(self, last_transaction_days, transaction_count_12m, total_amount_12m):
    # Recency (最近交易)
    if last_transaction_days <= 7: r = 5
    elif last_transaction_days <= 30: r = 4
    elif last_transaction_days <= 90: r = 3
    elif last_transaction_days <= 180: r = 2
    else: r = 1
    
    # Frequency (交易频率)
    if transaction_count_12m >= 24: f = 5
    elif transaction_count_12m >= 12: f = 4
    elif transaction_count_12m >= 6: f = 3
    elif transaction_count_12m >= 3: f = 2
    else: f = 1
    
    # Monetary (交易金额)
    if total_amount_12m >= 1000000: m = 5
    elif total_amount_12m >= 500000: m = 4
    elif total_amount_12m >= 100000: m = 3
    elif total_amount_12m >= 50000: m = 2
    else: m = 1
    
    return RFMSegment(r, f, m, r+f+m)
```

### 4.2 产品匹配

```python
def match_products(self, risk_preference, aum, age, ...):
    score = 0
    
    # 风险适配 (40分)
    risk_diff = abs(product_risk - customer_risk)
    if risk_diff == 0: score += 40
    elif risk_diff == 1: score += 25
    
    # 资金门槛 (20分)
    if aum >= product.min_investment * 2: score += 20
    elif aum >= product.min_investment: score += 15
    
    # 年龄适配 (15分)
    if age >= 55 and product.type in [INSURANCE, DEPOSIT]: score += 15
    
    # 期限匹配 (15分)
    # 流动性 (10分)
    
    return sorted(recommendations, key=lambda x: x.score, reverse=True)
```

---

## 五、AUM提升路径

```python
# 生成AUM提升策略
aum_path = engine.generate_aum_strategy(
    customer_id="C001",
    current_aum=500000,
    current_products=["活期存款", "稳健理财"],
    risk_preference="稳健型",
    age=35,
    last_transaction_days=15
)
```

**策略输出**：
```
📈 AUM提升路径
├── 当前等级：潜力客户 (50万)
├── 目标等级：白金客户 (100万)
├── 缺口：50万元
├── 预计时间：6-12个月
└── 执行策略：
    1. 交叉销售：补充基金/保险/信托
       目标提升：10万 | 转化率：30%
    2. 向上销售：结构性存款+混合基金
       目标提升：15万 | 转化率：25%
```

---

## 六、开源

```
https://github.com/yuzhaopeng-up/financial-ai-skills/tree/master/skills/retail-marketing
```

---

> **关于作者**：于兆鹏，银联工作，服务超500家金融机构。《AI赋能银行数字化转型》作者。
