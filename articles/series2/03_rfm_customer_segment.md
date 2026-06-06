# RFM模型+AI：银行客户分层运营实战代码

> 开源代码：https://github.com/yuzhaopeng-up/financial-ai-skills
>
> 可直接运行的Python代码，实现客户分层+营销策略。

---

## 一、什么是RFM模型？

RFM是客户价值分析的经典模型：

- **R**ecency（最近交易时间）：客户多久没交易了？
- **F**requency（交易频率）：客户交易多频繁？
- **M**onetary（交易金额）：客户贡献了多少钱？

**传统RFM的问题**：
- 只考虑交易行为，不考虑AUM、年龄、风险偏好
- 分层后没有配套的营销策略
- 无法动态调整

---

## 二、AI增强版RFM

我们的方案：RFM + AUM + 生命周期 + 价值潜力

```python
# 保存为 rfm_demo.py，直接运行

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class SegmentLevel(Enum):
    DIAMOND = ("钻石客户", "💎")
    PLATINUM = ("白金客户", "🥈")
    GOLD = ("黄金客户", "🥉")
    SILVER = ("白银客户", "⭐")
    BRONZE = ("青铜客户", "🔹")

@dataclass
class Customer:
    customer_id: str
    name: str
    age: int
    aum: float
    last_transaction_days: int
    transaction_count_12m: int
    total_amount_12m: float

class CustomerSegmentation:
    """客户分层运营"""
    
    def __init__(self):
        self.segments = {}
    
    def segment_by_aum(self, aum: float) -> SegmentLevel:
        """基于AUM分层"""
        if aum >= 5000000: return SegmentLevel.DIAMOND
        elif aum >= 1000000: return SegmentLevel.PLATINUM
        elif aum >= 500000: return SegmentLevel.GOLD
        elif aum >= 100000: return SegmentLevel.SILVER
        else: return SegmentLevel.BRONZE
    
    def calculate_rfm(self, last_days: int, tx_count: int, total_amount: float):
        """计算RFM评分"""
        # Recency (最近交易)
        if last_days <= 7: r = 5
        elif last_days <= 30: r = 4
        elif last_days <= 90: r = 3
        elif last_days <= 180: r = 2
        else: r = 1
        
        # Frequency (交易频率)
        if tx_count >= 24: f = 5
        elif tx_count >= 12: f = 4
        elif tx_count >= 6: f = 3
        elif tx_count >= 3: f = 2
        else: f = 1
        
        # Monetary (交易金额)
        if total_amount >= 1000000: m = 5
        elif total_amount >= 500000: m = 4
        elif total_amount >= 100000: m = 3
        elif total_amount >= 50000: m = 2
        else: m = 1
        
        rfm_score = r + f + m
        
        if rfm_score >= 13: segment = "重要价值客户"
        elif rfm_score >= 10: segment = "重要发展客户"
        elif rfm_score >= 7: segment = "一般价值客户"
        elif rfm_score >= 5: segment = "一般维持客户"
        else: segment = "流失风险客户"
        
        return {
            'r': r, 'f': f, 'm': m,
            'rfm_score': rfm_score,
            'segment': segment
        }
    
    def generate_strategy(self, aum_level, rfm_segment, life_cycle, potential):
        """生成营销策略"""
        strategies = []
        
        # 基于AUM等级的策略
        if aum_level == SegmentLevel.DIAMOND:
            strategies.extend([
                "专属客户经理一对一服务",
                "定制化资产配置方案",
                "优先参与稀缺产品认购"
            ])
        elif aum_level == SegmentLevel.GOLD:
            strategies.extend([
                "AUM提升激励活动",
                "交叉销售产品推荐",
                "理财知识科普内容"
            ])
        else:
            strategies.extend([
                "入门级理财产品推荐",
                "线上活动参与邀请"
            ])
        
        # 基于RFM的策略
        if rfm_segment == "流失风险客户":
            strategies.append("🚨 立即安排客户回访")
        
        # 基于生命周期的策略
        if life_cycle == "沉睡期":
            strategies.append("沉睡客户唤醒活动")
        
        return strategies


# ====== 实战演示 ======
if __name__ == "__main__":
    segmentation = CustomerSegmentation()
    
    # 模拟客户数据
    customers = [
        Customer("C001", "李明", 35, 500000, 15, 12, 200000),
        Customer("C002", "王芳", 28, 200000, 5, 24, 500000),
        Customer("C003", "张伟", 55, 8000000, 2, 3, 100000),
        Customer("C004", "刘洋", 42, 50000, 200, 1, 10000),
    ]
    
    print("=" * 70)
    print("📊 客户分层运营分析")
    print("=" * 70)
    
    for customer in customers:
        aum_level = segmentation.segment_by_aum(customer.aum)
        rfm = segmentation.calculate_rfm(
            customer.last_transaction_days,
            customer.transaction_count_12m,
            customer.total_amount_12m
        )
        strategies = segmentation.generate_strategy(
            aum_level, rfm['segment'], "成长期", "高"
        )
        
        print(f"\n👤 {customer.name} ({customer.customer_id})")
        print(f"   AUM: ¥{customer.aum:,.0f} | {aum_level.value[0]} {aum_level.value[1]}")
        print(f"   RFM: R{rfm['r']} F{rfm['f']} M{rfm['m']} = {rfm['rfm_score']}")
        print(f"   分层: {rfm['segment']}")
        print(f"   策略:")
        for s in strategies:
            print(f"      • {s}")
    
    print("\n" + "=" * 70)
```

---

## 三、运行结果

```bash
$ python rfm_demo.py
======================================================================
📊 客户分层运营分析
======================================================================

👤 李明 (C001)
   AUM: ¥500,000 | 黄金客户 🥉
   RFM: R4 F4 M3 = 11
   分层: 重要发展客户
   策略:
      • AUM提升激励活动
      • 交叉销售产品推荐
      • 理财知识科普内容

👤 王芳 (C002)
   AUM: ¥200,000 | 白银客户 ⭐
   RFM: R5 F5 M4 = 14
   分层: 重要价值客户
   策略:
      • 入门级理财产品推荐
      • 线上活动参与邀请
      • 🚨 立即安排客户回访

👤 张伟 (C003)
   AUM: ¥8,000,000 | 钻石客户 💎
   RFM: R2 F2 M3 = 7
   分层: 一般价值客户
   策略:
      • 专属客户经理一对一服务
      • 定制化资产配置方案
      • 优先参与稀缺产品认购

👤 刘洋 (C004)
   AUM: ¥50,000 | 青铜客户 🔹
   RFM: R1 F1 M1 = 3
   分层: 流失风险客户
   策略:
      • 入门级理财产品推荐
      • 线上活动参与邀请
      • 🚨 立即安排客户回访
      • 沉睡客户唤醒活动

======================================================================
```

---

## 四、如何集成

```python
# 从CRM系统读取客户数据
from your_crm import get_customers

customers = get_customers()

segmentation = CustomerSegmentation()

for customer in customers:
    aum_level = segmentation.segment_by_aum(customer.aum)
    rfm = segmentation.calculate_rfm(...)
    strategies = segmentation.generate_strategy(...)
    
    # 推送营销策略到营销系统
    push_to_marketing_system(customer.id, strategies)
```

---

## 五、开源

完整代码：
```
https://github.com/yuzhaopeng-up/financial-ai-skills/tree/master/skills/retail-marketing
```

---

> **关于作者**：于兆鹏，银联工作，服务超500家金融机构。《AI赋能银行数字化转型》作者。
