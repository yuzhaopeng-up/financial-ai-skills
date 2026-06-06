# 银行风控合规的AI实践：关联图谱自动识别洗钱网络

> 开源地址：https://github.com/yuzhaopeng-up/financial-ai-skills
>
> 基于《AI赋能银行数字化转型》第10章实战代码，纯Python实现。

---

## 一、为什么传统规则引擎防不住洗钱？

2024年某城商行的一笔可疑交易：

- 6个个人账户同一天向同一个对公账户转账
- 单笔5万到50万不等，总计143万
- 转账时间集中在下午2:00-2:30
- 6个账户开户时间都在最近3个月内

传统规则只能识别"大额交易"，却无法发现账户间的隐秘联系。直到引入**关联图谱分析**——

```
📊 风险检测结果：
├── 星型转账：1个 🔴 极高风险（6→1，¥143万）
├── 循环转账：2个 🔴 极高风险（A→B→C→A）
└── 链式转账：12条 🟡 高风险（4层嵌套）
```

---

## 二、5大检测能力

| 检测模式 | 风险场景 | 书中对应 |
|---------|---------|---------|
| **星型转账** | 非法集资、洗钱 | 第10章 10.2.3 |
| **循环转账** | 虚构交易、洗钱 | 第10章 10.2.3 |
| **链式转账** | 多层嵌套、规避监管 | 第10章 10.2.3 |
| **隐性关联** | 空壳公司集群 | 第10章 10.2.3 |
| **担保链** | 风险传导、连环违约 | 第10章 10.2.3 |

---

## 三、快速上手

```python
from knowledge_graph import KnowledgeGraphBuilder, FraudPatternDetector

# 构建图谱
graph = KnowledgeGraphBuilder()
graph.add_node("A001", "账户", "企业A")
graph.add_node("P001", "个人账户", "张三")
graph.add_edge("P001", "A001", "转账", 500000)

# 风险检测
detector = FraudPatternDetector(graph)
stars = detector.detect_star_pattern()
cycles = detector.detect_cycle_pattern()
```

---

## 四、核心算法

### 4.1 星型检测

```python
def detect_star_pattern(self, min_branches=3, min_amount=1000000):
    stars = []
    for node_id in self.graph.nodes:
        incoming = self.graph.get_incoming_edges(node_id)
        large_transfers = [e for e in incoming if e['amount'] >= min_amount]
        if len(large_transfers) >= min_branches:
            total = sum(e['amount'] for e in large_transfers)
            time_window = self._calculate_time_window(large_transfers)
            if time_window <= 3600:
                stars.append({
                    'center': node_id,
                    'branches': large_transfers,
                    'total_amount': total,
                    'risk_level': '极高风险'
                })
    return stars
```

### 4.2 循环检测（DFS）

```python
def detect_cycle_pattern(self, max_length=5):
    cycles = []
    def dfs(node, path, amount):
        if len(path) > max_length:
            return
        for neighbor in self.graph.get_neighbors(node):
            if neighbor == path[0] and len(path) >= 3:
                cycles.append({
                    'cycle': path + [neighbor],
                    'amount': amount
                })
            elif neighbor not in visited:
                dfs(neighbor, path + [neighbor], 
                    amount + self.graph.get_edge_amount(node, neighbor))
    for node in self.graph.nodes:
        dfs(node, [node], 0)
    return cycles
```

---

## 五、实战：识别空壳公司集群

```python
companies = ["C001", "C002", "C003", "C004"]
for c in companies:
    graph.add_node(c, "企业", f"公司{c}")

# 共同股东/地址
graph.add_association("C001", "C002", "共同股东", "张三")
graph.add_association("C002", "C003", "共同股东", "张三")
graph.add_association("C003", "C004", "共同地址", "XX大厦1001")

hidden = detector.detect_hidden_association()
```

输出：
```
🔍 隐性关联检测：
├── 关联组1：4家企业通过共同股东/地址关联
│   ├── 公司C001 ←→ 公司C002 (共同股东：张三)
│   ├── 公司C002 ←→ 公司C003 (共同股东：张三)
│   └── 公司C003 ←→ 公司C004 (共同地址：XX大厦1001)
│   风险评级：🔴 极高风险 | 建议：加强尽调
```

---

## 六、性能

| 数据规模 | 检测时间 | 内存 |
|---------|---------|------|
| 1,000节点/10,000边 | <1秒 | ~50MB |
| 10,000节点/100,000边 | ~5秒 | ~200MB |
| 100,000节点/1,000,000边 | ~60秒 | ~1GB |

---

## 七、开源

```
https://github.com/yuzhaopeng-up/financial-ai-skills
```

---

> **关于作者**：于兆鹏，银联工作，服务超500家金融机构。《AI赋能银行数字化转型》作者。
