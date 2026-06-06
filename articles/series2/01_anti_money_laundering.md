# 银行人必看：AI如何自动识别"星型转账"洗钱模式

> 开源代码：https://github.com/yuzhaopeng-up/financial-ai-skills
>
> 可运行的Python代码，复制粘贴即可执行。

---

## 一、什么是"星型转账"？

星型转账是洗钱最典型的模式之一：

```
        中心账户（对公）
        ↑      ↑      ↑      ↑
    个人账户 个人账户 个人账户 个人账户
```

**特征**：
- 多个个人账户向同一个对公账户转账
- 转账时间集中（通常1小时内）
- 金额分散，单笔不超过50万（规避大额交易监控）
- 账户开户时间相近

---

## 二、传统规则的盲区

传统反洗钱系统只能监控：
- 单笔大额交易（>50万）
- 频繁交易（日>10笔）

**但星型转账**：
- 单笔5-50万，不触发大额预警
- 每个账户只转1-2笔，不触发频繁预警
- **只有关联起来看，才能发现风险**

---

## 三、AI识别方案

### 3.1 完整代码

```python
# 保存为 anti_ml.py，直接运行

from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class Transaction:
    from_account: str
    to_account: str
    amount: float
    timestamp: datetime

class StarPatternDetector:
    """星型转账检测器"""
    
    def __init__(self):
        self.transactions = []
    
    def add_transaction(self, tx: Transaction):
        self.transactions.append(tx)
    
    def detect_star_pattern(self, min_branches=3, 
                           min_amount=1000000, 
                           time_window_hours=1):
        """
        检测星型转账模式
        
        参数:
            min_branches: 最少分支数（多少个账户向中心转账）
            min_amount: 最小总金额（元）
            time_window_hours: 时间窗口（小时）
        """
        # 按目标账户分组
        to_groups = {}
        for tx in self.transactions:
            if tx.to_account not in to_groups:
                to_groups[tx.to_account] = []
            to_groups[tx.to_account].append(tx)
        
        stars = []
        for center_account, txs in to_groups.items():
            # 检查分支数
            unique_sources = set(tx.from_account for tx in txs)
            if len(unique_sources) < min_branches:
                continue
            
            # 检查总金额
            total_amount = sum(tx.amount for tx in txs)
            if total_amount < min_amount:
                continue
            
            # 检查时间窗口
            timestamps = [tx.timestamp for tx in txs]
            time_span = (max(timestamps) - min(timestamps)).total_seconds() / 3600
            if time_span > time_window_hours:
                continue
            
            stars.append({
                'center': center_account,
                'branches': list(unique_sources),
                'branch_count': len(unique_sources),
                'total_amount': total_amount,
                'time_span_hours': time_span,
                'risk_level': '极高风险' if len(unique_sources) >= 5 else '高风险'
            })
        
        return stars

# ====== 实战演示 ======
if __name__ == "__main__":
    detector = StarPatternDetector()
    
    # 模拟可疑交易数据
    base_time = datetime(2025, 6, 1, 14, 0, 0)
    
    transactions = [
        # 6个个人账户向同一个对公账户转账
        Transaction("P001", "C001", 500000, base_time),
        Transaction("P002", "C001", 300000, base_time.replace(minute=5)),
        Transaction("P003", "C001", 250000, base_time.replace(minute=8)),
        Transaction("P004", "C001", 200000, base_time.replace(minute=12)),
        Transaction("P005", "C001", 100000, base_time.replace(minute=15)),
        Transaction("P006", "C001", 80000, base_time.replace(minute=18)),
        
        # 正常交易（分散到不同账户）
        Transaction("P007", "C002", 100000, base_time),
        Transaction("P008", "C003", 200000, base_time),
    ]
    
    for tx in transactions:
        detector.add_transaction(tx)
    
    # 检测
    stars = detector.detect_star_pattern(
        min_branches=3,
        min_amount=1000000,
        time_window_hours=1
    )
    
    # 输出结果
    print("=" * 60)
    print("🔍 星型转账检测结果")
    print("=" * 60)
    
    if not stars:
        print("未发现星型转账模式")
    else:
        for i, star in enumerate(stars, 1):
            print(f"\n⚠️  可疑网络 {i}: {star['risk_level']}")
            print(f"  中心账户: {star['center']}")
            print(f"  分支账户: {', '.join(star['branches'])}")
            print(f"  分支数量: {star['branch_count']} 个")
            print(f"  总金额: ¥{star['total_amount']:,.0f}")
            print(f"  时间跨度: {star['time_span_hours']:.1f} 小时")
    
    print("\n" + "=" * 60)
```

### 3.2 运行结果

```bash
$ python anti_ml.py
============================================================
🔍 星型转账检测结果
============================================================

⚠️  可疑网络 1: 极高风险
  中心账户: C001
  分支账户: P001, P002, P003, P004, P005, P006
  分支数量: 6 个
  总金额: ¥1,430,000
  时间跨度: 0.3 小时

============================================================
```

---

## 四、如何集成到现有系统

```python
# 从数据库读取交易数据
from your_database import get_transactions

txs = get_transactions(start_date='2025-06-01', end_date='2025-06-30')

detector = StarPatternDetector()
for tx in txs:
    detector.add_transaction(Transaction(
        from_account=tx['from_account'],
        to_account=tx['to_account'],
        amount=tx['amount'],
        timestamp=tx['timestamp']
    ))

# 每日定时检测
stars = detector.detect_star_pattern()
if stars:
    send_alert(stars)  # 发送告警
```

---

## 五、扩展：循环转账检测

```python
def detect_cycle(self, max_length=5):
    """检测循环转账 A→B→C→A"""
    graph = {}
    for tx in self.transactions:
        if tx.from_account not in graph:
            graph[tx.from_account] = []
        graph[tx.from_account].append(tx.to_account)
    
    cycles = []
    def dfs(node, path):
        if len(path) > max_length:
            return
        for neighbor in graph.get(node, []):
            if neighbor == path[0] and len(path) >= 3:
                cycles.append(path + [neighbor])
            elif neighbor not in path:
                dfs(neighbor, path + [neighbor])
    
    for node in graph:
        dfs(node, [node])
    
    return cycles
```

---

## 六、开源

完整代码在：
```
https://github.com/yuzhaopeng-up/financial-ai-skills/tree/master/skills/risk-compliance
```

---

> **关于作者**：于兆鹏，银联工作，服务超500家金融机构。《AI赋能银行数字化转型》作者。
