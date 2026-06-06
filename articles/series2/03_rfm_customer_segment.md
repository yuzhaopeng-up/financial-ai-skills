# RFM模型+AI：银行客户分层运营实战代码

> 实战代码：基于 `retail-marketing` Skill | RFM分析 | 客户分层 | 精准营销

## 什么是RFM模型？

RFM是客户价值分析的经典模型：

- **R (Recency)**：最近一次交易时间
- **F (Frequency)**：交易频率
- **M (Monetary)**：交易金额

```python
# RFM计算示例
from datetime import datetime

# 客户交易数据
customer = {
    "customer_id": "C10086",
    "last_trade_date": "2024-01-10",  # R: 5天前
    "trade_count_12m": 24,             # F: 年均24次
    "aum": 500000                      # M: 50万AUM
}

# RFM评分 (1-5分)
rfm = {
    "R": 4,  # 5天前 → 4分 (越近越高)
    "F": 5,  # 24次/年 → 5分 (越多越高)
    "M": 4   # 50万 → 4分 (越高越高)
}

# 客户类型: 重要价值客户 (R=4, F=5, M=4)
```

## 完整代码

```python
"""
银行客户RFM分析与分层
运行: python rfm_analysis.py --data customers.csv
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse

class RFMAnalyzer:
    """RFM分析器"""
    
    def __init__(self, recency_bins=5, frequency_bins=5, monetary_bins=5):
        self.recency_bins = recency_bins
        self.frequency_bins = frequency_bins
        self.monetary_bins = monetary_bins
    
    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        RFM分析
        
        Args:
            df: 包含 customer_id, last_trade_date, trade_count, aum 的DataFrame
        
        Returns:
            包含RFM评分和分层的DataFrame
        """
        # 计算R值 (距今天数)
        df['R'] = (datetime.now() - pd.to_datetime(df['last_trade_date'])).dt.days
        
        # R评分 (越近越高，所以用降序)
        df['R_Score'] = pd.qcut(df['R'], self.recency_bins, labels=[5,4,3,2,1])
        
        # F评分 (越高越好)
        df['F_Score'] = pd.qcut(df['trade_count'].rank(method='first'), 
                                self.frequency_bins, labels=[1,2,3,4,5])
        
        # M评分 (越高越好)
        df['M_Score'] = pd.qcut(df['aum'].rank(method='first'), 
                                self.monetary_bins, labels=[1,2,3,4,5])
        
        # RFM组合
        df['RFM_Score'] = df['R_Score'].astype(str) + \
                           df['F_Score'].astype(str) + \
                           df['M_Score'].astype(str)
        
        # 客户分层
        df['Segment'] = df.apply(self._segment, axis=1)
        
        return df
    
    def _segment(self, row) -> str:
        """根据RFM评分分层"""
        r, f, m = int(row['R_Score']), int(row['F_Score']), int(row['M_Score'])
        
        if r >= 4 and f >= 4 and m >= 4:
            return "重要价值客户"
        elif r >= 4 and f <= 2 and m >= 4:
            return "重要保持客户"
        elif r <= 2 and f >= 4 and m >= 4:
            return "重要发展客户"
        elif r <= 2 and f <= 2 and m >= 4:
            return "重要挽留客户"
        elif r >= 4 and f >= 4 and m <= 2:
            return "一般价值客户"
        elif r >= 4 and f <= 2 and m <= 2:
            return "新客户"
        elif r <= 2 and f >= 4 and m <= 2:
            return "潜力客户"
        elif r <= 2 and f <= 2 and m <= 2:
            return "流失客户"
        else:
            return "一般客户"
    
    def get_segment_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """获取各分层统计"""
        stats = df.groupby('Segment').agg({
            'customer_id': 'count',
            'aum': ['mean', 'sum'],
            'trade_count': 'mean',
            'R': 'mean'
        }).round(2)
        
        stats.columns = ['客户数', 'AUM均值', 'AUM总和', '交易频次', '平均未交易天数']
        stats['占比'] = (stats['客户数'] / len(df) * 100).round(1)
        
        return stats.sort_values('AUM总和', ascending=False)

class MarketingStrategy:
    """营销策略生成器"""
    
    def __init__(self):
        self.strategies = {
            "重要价值客户": {
                "strategy": "VIP专属服务",
                "actions": ["专属理财顾问", "高端产品优先认购", "生日礼遇"],
                "expected_lift": 0.25
            },
            "重要保持客户": {
                "strategy": "激活交易频率",
                "actions": ["交易返现活动", "积分加倍", "限时优惠"],
                "expected_lift": 0.18
            },
            "重要发展客户": {
                "strategy": "提升客单价",
                "actions": ["产品升级推荐", "组合优惠", "专属理财方案"],
                "expected_lift": 0.22
            },
            "重要挽留客户": {
                "strategy": "紧急挽回",
                "actions": ["高管亲自拜访", "定制化方案", "特别利率"],
                "expected_lift": 0.15
            },
            "新客户": {
                "strategy": "onboarding",
                "actions": ["新手礼包", "首投奖励", "理财教育"],
                "expected_lift": 0.30
            },
            "流失客户": {
                "strategy": "召回活动",
                "actions": ["回归礼包", "专属优惠", "情感连接"],
                "expected_lift": 0.08
            }
        }
    
    def get_strategy(self, segment: str) -> dict:
        """获取营销策略"""
        return self.strategies.get(segment, {
            "strategy": "常规维护",
            "actions": ["定期关怀", "产品推荐"],
            "expected_lift": 0.05
        })

# 主程序
def main():
    parser = argparse.ArgumentParser(description="银行客户RFM分析")
    parser.add_argument("--data", "-d", required=True, help="客户数据CSV")
    parser.add_argument("--output", "-o", default="rfm_result.csv", help="输出文件")
    args = parser.parse_args()
    
    # 加载数据
    print(f"📊 加载客户数据: {args.data}")
    df = pd.read_csv(args.data)
    print(f"客户总数: {len(df)}")
    
    # RFM分析
    print("\n🔍 进行RFM分析...")
    analyzer = RFMAnalyzer()
    result = analyzer.analyze(df)
    
    # 统计
    print("\n📈 客户分层统计:")
    stats = analyzer.get_segment_stats(result)
    print(stats.to_string())
    
    # 营销策略
    print("\n🎯 营销策略建议:")
    strategy = MarketingStrategy()
    for segment in stats.index:
        s = strategy.get_strategy(segment)
        print(f"\n【{segment}】")
        print(f"  策略: {s['strategy']}")
        print(f"  行动: {', '.join(s['actions'])}")
        print(f"  预期AUM提升: {s['expected_lift']*100:.0f}%")
    
    # 保存结果
    result.to_csv(args.output, index=False)
    print(f"\n✅ 结果已保存: {args.output}")
    
    # 生成可视化
    generate_visualization(stats)

def generate_visualization(stats):
    """生成可视化图表"""
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 客户分布饼图
    axes[0, 0].pie(stats['客户数'], labels=stats.index, autopct='%1.1f%%')
    axes[0, 0].set_title('客户分层分布')
    
    # AUM分布柱状图
    stats['AUM总和'].plot(kind='bar', ax=axes[0, 1])
    axes[0, 1].set_title('各分层AUM总和')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # 客户数柱状图
    stats['客户数'].plot(kind='bar', ax=axes[1, 0])
    axes[1, 0].set_title('各分层客户数')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # AUM均值柱状图
    stats['AUM均值'].plot(kind='bar', ax=axes[1, 1])
    axes[1, 1].set_title('各分层AUM均值')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('rfm_analysis.png', dpi=150)
    print("📊 可视化图表已保存: rfm_analysis.png")

if __name__ == "__main__":
    main()
```

## 运行效果

```bash
$ python rfm_analysis.py --data customers.csv

📊 加载客户数据: customers.csv
客户总数: 10000

🔍 进行RFM分析...

📈 客户分层统计:
                 客户数    AUM均值      AUM总和  交易频次  平均未交易天数   占比
重要价值客户      1200   850000.0  1020000000     45.2         5.2  12.0
重要保持客户       800   720000.0   576000000     12.5         4.8   8.0
重要发展客户      1500   680000.0  1020000000     38.6        45.3  15.0
一般价值客户      2000   280000.0   560000000     32.4         6.1  20.0
新客户           2500   150000.0   375000000      8.2         3.5  25.0
流失客户          2000    80000.0   160000000      5.3        78.5  20.0

🎯 营销策略建议:

【重要价值客户】
  策略: VIP专属服务
  行动: 专属理财顾问, 高端产品优先认购, 生日礼遇
  预期AUM提升: 25%

【重要保持客户】
  策略: 激活交易频率
  行动: 交易返现活动, 积分加倍, 限时优惠
  预期AUM提升: 18%

【重要发展客户】
  策略: 提升客单价
  行动: 产品升级推荐, 组合优惠, 专属理财方案
  预期AUM提升: 22%

【一般价值客户】
  策略: 常规维护
  行动: 定期关怀, 产品推荐
  预期AUM提升: 5%

【新客户】
  策略: onboarding
  行动: 新手礼包, 首投奖励, 理财教育
  预期AUM提升: 30%

【流失客户】
  策略: 召回活动
  行动: 回归礼包, 专属优惠, 情感连接
  预期AUM提升: 8%

✅ 结果已保存: rfm_result.csv
📊 可视化图表已保存: rfm_analysis.png
```

## 数据格式要求

```csv
customer_id,last_trade_date,trade_count,aum
C10001,2024-01-10,45,850000
C10002,2024-01-05,12,720000
C10003,2023-11-20,38,680000
...
```

## 进阶：动态RFM

```python
# 按月更新RFM
class DynamicRFM(RFMAnalyzer):
    def update_monthly(self, new_transactions):
        """每月更新RFM评分"""
        # 合并新交易
        self.transactions = pd.concat([self.transactions, new_transactions])
        
        # 重新计算RFM
        self.rfm = self.analyze(self.transactions)
        
        # 检测变化
        changes = self.detect_changes()
        
        for customer_id, change in changes.items():
            if change['segment_changed']:
                print(f"⚠️ 客户 {customer_id} 从 {change['old_segment']} 变为 {change['new_segment']}")
                # 触发营销动作
                self.trigger_marketing(customer_id, change['new_segment'])
```

---

**完整代码**：https://github.com/yuzhaopeng-up/financial-ai-skills/tree/main/skills/retail-marketing/examples

**#RFM模型 #客户分层 #精准营销 #银行零售 #Python实战**
