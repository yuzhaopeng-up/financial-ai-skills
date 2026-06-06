# 我用 Python 写了一套银行风控合规智能体：关联图谱自动识别洗钱网络

> 开源地址：https://github.com/yuzhaopeng-up/financial-ai-skills
> 
> 基于《AI赋能银行数字化转型》第10章实战代码，零API费用，纯Python实现。

---

## 一、为什么银行需要关联图谱分析？

2024年某城商行的一笔可疑交易引起了我的注意：

- 6个个人账户在同一天向同一个对公账户转账
- 单笔金额从5万到50万不等，总计143万
- 转账时间集中在下午2:00-2:30之间
- 6个账户开户时间都在最近3个月内

传统的规则引擎只能识别"大额交易"，却无法发现这6个账户之间的隐秘联系。直到我们引入了**关联图谱分析**——

```
📊 风险检测结果：
├── 星型转账：1个 🔴 极高风险
│   └── 6账户 → 中心节点，¥143万
├── 循环转账：2个 🔴 极高风险  
│   └── A→B→C→A 闭环
└── 链式转账：12条 🟡 高风险
    └── 4层以上资金嵌套
```

这就是本文要分享的 `risk-compliance` Skill，一个用纯Python实现的金融风控关联图谱分析工具。

---

## 二、核心能力一览

| 检测模式 | 风险场景 | 书中对应 |
|---------|---------|---------|
| **星型转账** | 非法集资、洗钱 | 第10章 10.2.3 |
| **循环转账** | 虚构交易、洗钱 | 第10章 10.2.3 |
| **链式转账** | 多层嵌套、规避监管 | 第10章 10.2.3 |
| **隐性关联** | 空壳公司集群 | 第10章 10.2.3 |
| **担保链** | 风险传导、连环违约 | 第10章 10.2.3 |

---

## 三、快速上手

### 3.1 安装

```bash
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
cd financial-ai-skills/skills/risk-compliance
```

无需安装任何依赖，纯Python标准库实现。

### 3.2 构建关联图谱

```python
from knowledge_graph import KnowledgeGraphBuilder, FraudPatternDetector

# 1. 构建图谱
graph = KnowledgeGraphBuilder()

# 添加节点（账户）
graph.add_node("A001", "账户", "企业A")
graph.add_node("P001", "个人账户", "张三")
graph.add_node("P002", "个人账户", "李四")

# 添加边（转账关系）
graph.add_edge("P001", "A001", "转账", 500000)
graph.add_edge("P002", "A001", "转账", 300000)

# 2. 风险检测
detector = FraudPatternDetector(graph)

# 检测星型转账
stars = detector.detect_star_pattern(min_branches=3, min_amount=1000000)
print(f"发现 {len(stars)} 个星型转账网络")

# 检测循环转账
cycles = detector.detect_cycle_pattern(max_length=5)
print(f"发现 {len(cycles)} 个循环转账")
```

### 3.3 输出报告

```
📊 关联图谱风险分析报告
├── 星型转账：1个 🔴 极高风险
│   └── 中心：企业A (A001)
│       ├── 张三 (P001) → ¥50万
│       ├── 李四 (P002) → ¥30万
│       ├── 王五 (P003) → ¥25万
│       ├── 赵六 (P004) → ¥20万
│       ├── 孙七 (P005) → ¥10万
│       └── 周八 (P006) → ¥8万
│       总计：¥143万 | 时间窗口：30分钟
│
├── 循环转账：2个 🔴 极高风险
│   └── 循环1：A→B→C→A
│       金额：¥200万 | 周期：7天
│
└── 链式转账：12条 🟡 高风险
    └── 最长链：4层嵌套
        A → B → C → D → E
        总金额：¥500万
```

---

## 四、核心算法解析

### 4.1 星型检测算法

```python
def detect_star_pattern(self, min_branches=3, min_amount=1000000):
    """检测星型转账模式"""
    stars = []
    
    for node_id in self.graph.nodes:
        # 查找所有指向该节点的边
        incoming = self.graph.get_incoming_edges(node_id)
        
        # 筛选大额转账
        large_transfers = [
            edge for edge in incoming 
            if edge['amount'] >= min_amount
        ]
        
        # 判断是否为星型
        if len(large_transfers) >= min_branches:
            total_amount = sum(e['amount'] for e in large_transfers)
            time_window = self._calculate_time_window(large_transfers)
            
            if time_window <= 3600:  # 1小时内
                stars.append({
                    'center': node_id,
                    'branches': large_transfers,
                    'total_amount': total_amount,
                    'time_window': time_window,
                    'risk_level': '极高风险'
                })
    
    return stars
```

### 4.2 循环检测算法（DFS）

```python
def detect_cycle_pattern(self, max_length=5):
    """检测循环转账（DFS）"""
    cycles = []
    visited = set()
    
    def dfs(node, path, amount):
        if len(path) > max_length:
            return
        
        for neighbor in self.graph.get_neighbors(node):
            if neighbor == path[0] and len(path) >= 3:
                # 发现循环
                cycles.append({
                    'cycle': path + [neighbor],
                    'amount': amount,
                    'length': len(path)
                })
            elif neighbor not in visited:
                visited.add(neighbor)
                edge_amount = self.graph.get_edge_amount(node, neighbor)
                dfs(neighbor, path + [neighbor], amount + edge_amount)
                visited.remove(neighbor)
    
    for node in self.graph.nodes:
        dfs(node, [node], 0)
    
    return cycles
```

---

## 五、实战案例：识别空壳公司集群

### 场景
某银行发现一批新注册企业客户，需要判断是否存在空壳公司集群。

### 代码
```python
# 添加企业节点和关联关系
companies = ["C001", "C002", "C003", "C004"]
for c in companies:
    graph.add_node(c, "企业", f"公司{c}")

# 共同股东
graph.add_association("C001", "C002", "共同股东", "张三")
graph.add_association("C002", "C003", "共同股东", "张三")
graph.add_association("C003", "C004", "共同地址", "XX大厦1001")

# 检测隐性关联
hidden = detector.detect_hidden_association()
print(f"发现 {len(hidden)} 组隐性关联")
```

### 输出
```
🔍 隐性关联检测结果：
├── 关联组1：4家企业通过共同股东/地址关联
│   ├── 公司C001 ←→ 公司C002 (共同股东：张三)
│   ├── 公司C002 ←→ 公司C003 (共同股东：张三)
│   └── 公司C003 ←→ 公司C004 (共同地址：XX大厦1001)
│   
│   风险评级：🔴 极高风险
│   关联特征：空壳公司集群典型模式
│   建议措施：加强尽职调查，限制授信额度
```

---

## 六、与其他模块的联动

关联图谱分析不是孤立的，它与整个风控体系联动：

```
┌─────────────────────────────────────────┐
│           风控合规智能体                   │
├─────────────────────────────────────────┤
│  关联图谱分析  →  风险评分  →  预警报告   │
│     (knowledge_graph.py)   (scorer.py)   │
│         ↓              ↓         ↓       │
│    星型/循环/链式    综合评级    推送     │
│    隐性关联/担保链   高/中/低   告警      │
└─────────────────────────────────────────┘
```

---

## 七、性能表现

| 数据规模 | 检测时间 | 内存占用 |
|---------|---------|---------|
| 1,000节点/10,000边 | < 1秒 | ~50MB |
| 10,000节点/100,000边 | ~5秒 | ~200MB |
| 100,000节点/1,000,000边 | ~60秒 | ~1GB |

---

## 八、开源与贡献

本项目已开源在 GitHub：

```
https://github.com/yuzhaopeng-up/financial-ai-skills
```

- ⭐ 如果对你有帮助，欢迎 Star
- 🍴 欢迎 Fork 并提交 PR
- 💬 有问题请提 Issue

---

## 九、系列文章

| 文章 | Skill | 状态 |
|------|-------|------|
| 财务AI智能体：6大场景全覆盖 | financial-intelligence | ✅ 已发布 |
| **风控合规：关联图谱识别洗钱网络** | **risk-compliance** | **本文** |
| 对公尽调：从7天到7分钟 | due-diligence | 待发布 |
| 零售营销：客户分层+AUM提升 | retail-marketing | 待发布 |
| 信贷审批：信用评分88分自动通过 | credit-approval | 待发布 |
| 运营自动化：7×24无人值守 | operations-automation | 待发布 |

---

> **关于作者**：于兆鹏，银联工作，服务超500家金融机构。《AI赋能银行数字化转型》作者，专注金融AI落地实践。
