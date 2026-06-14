# 从工单到闭环：银行运营自动化完整方案

> 开源代码：https://github.com/yuzhaopeng-up/financial-ai-skills
> 
> 可运行的Python代码，实现工单自动分派+流程编排。

---

## 一、银行运营的日常

某银行运营中心的一天：

- 09:00 收到50个工单，人工分类分派，2小时过去
- 11:00 处理开户流程，跨5个系统操作，出错率5%
- 14:00 系统CPU飙升到90%，30分钟后才发现
- 17:00 日报还没写，加班整理数据

**问题**：靠人堆，效率低，容易出错，响应慢。

---

## 二、AI运营自动化：3大场景

### 场景1：智能工单处理

```python
# 保存为 ticket_demo.py，直接运行

from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum
from datetime import datetime

class TicketCategory(Enum):
    ACCOUNT = "账户问题"
    TRANSACTION = "交易问题"
    LOAN = "贷款问题"
    SECURITY = "安全问题"

class TicketPriority(Enum):
    CRITICAL = ("紧急", "🔴")
    HIGH = ("高", "🟠")
    MEDIUM = ("中", "🟡")
    LOW = ("低", "🟢")

@dataclass
class Ticket:
    ticket_id: str
    title: str
    category: TicketCategory
    priority: TicketPriority
    status: str = "新建"
    assigned_to: str = None

class TicketProcessor:
    """工单处理器"""
    
    def __init__(self):
        self.tickets = {}
        self.team_capacity = {
            "账户组": 5, "交易组": 4, "贷款组": 3,
            "安全组": 2, "咨询组": 6
        }
        self.team_load = {team: 0 for team in self.team_capacity}
    
    def create_ticket(self, ticket_id, title, category, priority):
        ticket = Ticket(ticket_id, title, category, priority)
        self.tickets[ticket_id] = ticket
        return ticket
    
    def auto_classify(self, title):
        """基于关键词自动分类"""
        text = title.lower()
        keywords = {
            TicketCategory.ACCOUNT: ["账户", "冻结", "开户", "密码"],
            TicketCategory.TRANSACTION: ["转账", "交易", "支付"],
            TicketCategory.LOAN: ["贷款", "还款", "额度"],
            TicketCategory.SECURITY: ["安全", "盗刷", "诈骗"]
        }
        scores = {cat: sum(1 for word in words if word in text) 
                  for cat, words in keywords.items()}
        return max(scores, key=scores.get)
    
    def auto_assign(self, ticket_id):
        """基于团队负载自动分派"""
        ticket = self.tickets[ticket_id]
        team_map = {
            TicketCategory.ACCOUNT: "账户组",
            TicketCategory.TRANSACTION: "交易组",
            TicketCategory.LOAN: "贷款组",
            TicketCategory.SECURITY: "安全组"
        }
        team = team_map.get(ticket.category, "咨询组")
        
        # 负载均衡
        if self.team_load[team] >= self.team_capacity[team]:
            available = [t for t, load in self.team_load.items() 
                        if load < self.team_capacity[t]]
            if available:
                team = min(available, key=lambda t: self.team_load[t])
        
        self.team_load[team] += 1
        ticket.assigned_to = team
        ticket.status = "已分派"
        
        return team

# ====== 实战演示 ======
if __name__ == "__main__":
    processor = TicketProcessor()
    
    # 模拟工单
    tickets = [
        ("TKT001", "账户异常冻结", TicketCategory.ACCOUNT, TicketPriority.HIGH),
        ("TKT002", "转账未到账", TicketCategory.TRANSACTION, TicketPriority.MEDIUM),
        ("TKT003", "疑似盗刷", TicketCategory.SECURITY, TicketPriority.CRITICAL),
        ("TKT004", "贷款额度查询", TicketCategory.LOAN, TicketPriority.LOW),
    ]
    
    print("=" * 60)
    print("🎫 智能工单处理演示")
    print("=" * 60)
    
    for ticket_id, title, category, priority in tickets:
        ticket = processor.create_ticket(ticket_id, title, category, priority)
        assigned_team = processor.auto_assign(ticket_id)
        
        print(f"\n工单: {ticket_id}")
        print(f"  标题: {title}")
        print(f"  分类: {category.value}")
        print(f"  优先级: {priority.value[1]} {priority.value[0]}")
        print(f"  分派给: {assigned_team}")
        print(f"  团队负载: {processor.team_load[assigned_team]}/{processor.team_capacity[assigned_team]}")
    
    print("\n" + "=" * 60)
```

**运行结果**：
```bash
$ python ticket_demo.py
============================================================
🎫 智能工单处理演示
============================================================

工单: TKT001
  标题: 账户异常冻结
  分类: 账户问题
  优先级: 🟠 高
  分派给: 账户组
  团队负载: 1/5

工单: TKT002
  标题: 转账未到账
  分类: 交易问题
  优先级: 🟡 中
  分派给: 交易组
  团队负载: 1/4
...
```

---

### 场景2：流程自动化编排

```python
# 工作流引擎
class WorkflowEngine:
    def __init__(self):
        self.workflows = {}
    
    def create_workflow(self, workflow_id, name):
        self.workflows[workflow_id] = {
            'name': name,
            'nodes': {},
            'start_node': None
        }
    
    def add_node(self, workflow_id, node_id, name, action, next_nodes=None):
        self.workflows[workflow_id]['nodes'][node_id] = {
            'name': name,
            'action': action,
            'next_nodes': next_nodes or []
        }
        if not self.workflows[workflow_id]['start_node']:
            self.workflows[workflow_id]['start_node'] = node_id
    
    def execute(self, workflow_id):
        workflow = self.workflows[workflow_id]
        current = workflow['start_node']
        path = []
        
        while current:
            node = workflow['nodes'][current]
            path.append(current)
            print(f"  📍 执行: {node['name']} ({node['action']})")
            
            if node['next_nodes']:
                current = node['next_nodes'][0]
            else:
                current = None
        
        return path

# 开户流程示例
engine = WorkflowEngine()
engine.create_workflow("WF001", "自动开户")
engine.add_node("WF001", "start", "开始", "notify", ["validate"])
engine.add_node("WF001", "validate", "身份验证", "api_call", ["create"])
engine.add_node("WF001", "create", "创建账户", "api_call", ["notify"])
engine.add_node("WF001", "notify", "发送通知", "send_sms", [])

path = engine.execute("WF001")
print(f"执行路径: {' -> '.join(path)}")
```

---

### 场景3：监控告警

```python
class Monitor:
    def __init__(self):
        self.metrics = {}
        self.alerts = []
    
    def register(self, metric_id, name, warning, critical):
        self.metrics[metric_id] = {
            'name': name,
            'warning': warning,
            'critical': critical,
            'current': 0
        }
    
    def collect(self, metric_id, value):
        metric = self.metrics[metric_id]
        metric['current'] = value
        
        if value >= metric['critical']:
            alert = f"🔴 紧急: {metric['name']} = {value}% (阈值: {metric['critical']}%)"
            self.alerts.append(alert)
            return alert
        elif value >= metric['warning']:
            alert = f"🟠 警告: {metric['name']} = {value}% (阈值: {metric['warning']}%)"
            self.alerts.append(alert)
            return alert
        
        return f"✅ {metric['name']} = {value}% (正常)"

# 演示
monitor = Monitor()
monitor.register("CPU001", "CPU使用率", 70, 90)

for value in [45, 52, 68, 75, 85, 92]:
    result = monitor.collect("CPU001", value)
    print(result)
```

---

## 三、开源

完整代码：
```
https://github.com/yuzhaopeng-up/financial-ai-skills/tree/master/skills/operations-automation
```

---

> **关于作者**：作者，金融科技从业经历，服务超500家金融机构。《AI赋能银行数字化转型》作者。
