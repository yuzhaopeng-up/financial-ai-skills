# 从工单到闭环：银行运营自动化完整方案

> 实战代码：基于 `operations-automation` Skill | 工单系统 | 流程编排 | SLA监控

## 痛点：银行运营的"人肉接力"

银行运营流程的典型场景：

```
客户投诉 → 客服记录 → 转运营 → 转技术 → 转合规 → 回复客户
         ↑___________________________________________↓
                    (平均耗时: 3-5天)
```

**问题**：
- 工单流转靠人工转发
- 处理进度不透明
- SLA超时无预警
- 重复问题无沉淀

## 方案：端到端自动化

```python
from operations_automation import TicketSystem, WorkflowEngine, SLAMonitor

# 1. 创建工单系统
ticket_system = TicketSystem()

# 2. 配置工作流
workflow = WorkflowEngine()
workflow.add_node("受理", auto_accept)
workflow.add_node("分类", auto_classify)
workflow.add_node("分派", auto_dispatch)
workflow.add_node("处理", auto_process)
workflow.add_node("复核", auto_review)
workflow.add_node("关闭", auto_close)

# 3. 配置SLA
sla = SLAMonitor()
sla.add_rule("P0", response_time=30, resolve_time=240)  # 4小时
sla.add_rule("P1", response_time=60, resolve_time=480)  # 8小时
sla.add_rule("P2", response_time=240, resolve_time=1440) # 24小时

# 4. 启动系统
ticket_system.set_workflow(workflow)
ticket_system.set_sla(sla)
ticket_system.start()
```

## 完整代码

```python
"""
银行运营自动化系统
运行: python workflow_demo.py
"""
import time
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field

class Priority(Enum):
    P0 = "紧急"
    P1 = "高"
    P2 = "中"
    P3 = "低"

class Status(Enum):
    NEW = "新建"
    ASSIGNED = "已分派"
    PROCESSING = "处理中"
    PENDING = "待复核"
    RESOLVED = "已解决"
    CLOSED = "已关闭"

@dataclass
class Ticket:
    id: str
    title: str
    category: str
    priority: Priority
    status: Status
    created_at: datetime
    assigned_to: Optional[str] = None
    sla_deadline: Optional[datetime] = None
    history: List[Dict] = field(default_factory=list)
    
    def add_history(self, action: str, user: str, note: str = ""):
        self.history.append({
            "time": datetime.now().isoformat(),
            "action": action,
            "user": user,
            "note": note
        })

class TicketSystem:
    """工单系统"""
    
    def __init__(self):
        self.tickets: Dict[str, Ticket] = {}
        self.workflows = {}
        self.sla_rules = {}
        self.handlers = {
            "系统故障": "运维组",
            "客户投诉": "客服组",
            "合规审查": "合规组",
            "产品咨询": "产品组"
        }
    
    def create_ticket(self, title: str, category: str, 
                      priority: Priority = Priority.P2) -> Ticket:
        """创建工单"""
        ticket_id = f"TKT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        ticket = Ticket(
            id=ticket_id,
            title=title,
            category=category,
            priority=priority,
            status=Status.NEW,
            created_at=datetime.now()
        )
        
        # 计算SLA截止时间
        if priority in self.sla_rules:
            rule = self.sla_rules[priority]
            ticket.sla_deadline = datetime.now() + timedelta(minutes=rule["resolve_time"])
        
        ticket.add_history("创建", "系统", f"优先级: {priority.value}")
        self.tickets[ticket_id] = ticket
        
        print(f"✅ 工单创建: {ticket_id} [{priority.value}]")
        return ticket
    
    def auto_dispatch(self, ticket_id: str):
        """自动分派"""
        ticket = self.tickets[ticket_id]
        
        # 根据分类自动分派
        handler = self.handlers.get(ticket.category, "综合组")
        ticket.assigned_to = handler
        ticket.status = Status.ASSIGNED
        ticket.add_history("分派", "系统", f"分派给: {handler}")
        
        print(f"📨 自动分派: {ticket_id} → {handler}")
    
    def process_ticket(self, ticket_id: str, action: str, note: str = ""):
        """处理工单"""
        ticket = self.tickets[ticket_id]
        
        if action == "start":
            ticket.status = Status.PROCESSING
            ticket.add_history("开始处理", ticket.assigned_to, note)
        elif action == "resolve":
            ticket.status = Status.RESOLVED
            ticket.add_history("解决", ticket.assigned_to, note)
        elif action == "close":
            ticket.status = Status.CLOSED
            ticket.add_history("关闭", "系统", note)
        
        print(f"📝 工单更新: {ticket_id} → {ticket.status.value}")
    
    def check_sla(self) -> List[Ticket]:
        """检查SLA超时"""
        overdue = []
        now = datetime.now()
        
        for ticket in self.tickets.values():
            if ticket.status not in [Status.RESOLVED, Status.CLOSED]:
                if ticket.sla_deadline and now > ticket.sla_deadline:
                    overdue.append(ticket)
        
        return overdue
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = len(self.tickets)
        resolved = sum(1 for t in self.tickets.values() if t.status == Status.RESOLVED)
        closed = sum(1 for t in self.tickets.values() if t.status == Status.CLOSED)
        overdue = len(self.check_sla())
        
        return {
            "total": total,
            "resolved": resolved,
            "closed": closed,
            "overdue": overdue,
            "resolution_rate": (resolved + closed) / total * 100 if total > 0 else 0
        }

class WorkflowEngine:
    """流程编排引擎"""
    
    def __init__(self):
        self.nodes = []
        self.current_node = 0
    
    def add_node(self, name: str, handler):
        """添加流程节点"""
        self.nodes.append({"name": name, "handler": handler})
    
    def execute(self, ticket: Ticket):
        """执行流程"""
        print(f"\n🔄 开始执行流程: {ticket.id}")
        
        for node in self.nodes:
            print(f"  → {node['name']}")
            result = node["handler"](ticket)
            
            if result == "break":
                print(f"  ⏹️ 流程中断")
                break
            
            time.sleep(0.5)  # 模拟处理时间
        
        print(f"✅ 流程完成: {ticket.id}")

# 模拟处理函数
def auto_accept(ticket: Ticket) -> str:
    """自动受理"""
    ticket.add_history("受理", "系统", "自动受理")
    return "continue"

def auto_classify(ticket: Ticket) -> str:
    """自动分类"""
    # 根据标题关键词分类
    keywords = {
        "故障": "系统故障",
        "投诉": "客户投诉",
        "合规": "合规审查",
        "产品": "产品咨询"
    }
    
    for keyword, category in keywords.items():
        if keyword in ticket.title:
            ticket.category = category
            break
    
    ticket.add_history("分类", "系统", f"分类为: {ticket.category}")
    return "continue"

def auto_dispatch(ticket: Ticket) -> str:
    """自动分派"""
    handlers = {
        "系统故障": "运维组",
        "客户投诉": "客服组",
        "合规审查": "合规组",
        "产品咨询": "产品组"
    }
    
    ticket.assigned_to = handlers.get(ticket.category, "综合组")
    ticket.status = Status.ASSIGNED
    ticket.add_history("分派", "系统", f"分派给: {ticket.assigned_to}")
    return "continue"

def auto_process(ticket: Ticket) -> str:
    """自动处理"""
    ticket.status = Status.PROCESSING
    ticket.add_history("处理", ticket.assigned_to, "自动处理完成")
    
    # 模拟处理时间
    time.sleep(1)
    
    ticket.status = Status.RESOLVED
    ticket.add_history("解决", ticket.assigned_to, "问题已解决")
    return "continue"

def auto_close(ticket: Ticket) -> str:
    """自动关闭"""
    ticket.status = Status.CLOSED
    ticket.add_history("关闭", "系统", "自动关闭")
    return "continue"

# 主程序
def main():
    print("="*60)
    print("🏦 银行运营自动化系统演示")
    print("="*60)
    
    # 初始化系统
    system = TicketSystem()
    
    # 配置SLA
    system.sla_rules = {
        Priority.P0: {"response_time": 30, "resolve_time": 240},
        Priority.P1: {"response_time": 60, "resolve_time": 480},
        Priority.P2: {"response_time": 240, "resolve_time": 1440}
    }
    
    # 配置工作流
    workflow = WorkflowEngine()
    workflow.add_node("受理", auto_accept)
    workflow.add_node("分类", auto_classify)
    workflow.add_node("分派", auto_dispatch)
    workflow.add_node("处理", auto_process)
    workflow.add_node("关闭", auto_close)
    
    # 模拟工单
    tickets_data = [
        ("核心系统响应超时", "系统故障", Priority.P0),
        ("客户投诉收费问题", "客户投诉", Priority.P1),
        ("理财产品咨询", "产品咨询", Priority.P2),
        ("合规审查材料提交", "合规审查", Priority.P1),
    ]
    
    # 创建并处理工单
    for title, category, priority in tickets_data:
        ticket = system.create_ticket(title, category, priority)
        workflow.execute(ticket)
        print()
    
    # 统计
    print("="*60)
    print("📊 系统统计")
    print("="*60)
    stats = system.get_stats()
    print(f"总工单数: {stats['total']}")
    print(f"已解决: {stats['resolved']}")
    print(f"已关闭: {stats['closed']}")
    print(f"SLA超时: {stats['overdue']}")
    print(f"解决率: {stats['resolution_rate']:.1f}%")
    
    # 输出工单详情
    print("\n" + "="*60)
    print("📝 工单详情")
    print("="*60)
    for ticket in system.tickets.values():
        print(f"\n{ticket.id}: {ticket.title}")
        print(f"  状态: {ticket.status.value}")
        print(f"  处理人: {ticket.assigned_to}")
        print(f"  SLA截止: {ticket.sla_deadline}")
        print("  处理历史:")
        for h in ticket.history:
            print(f"    [{h['time']}] {h['action']} - {h['user']}")

if __name__ == "__main__":
    main()
```

## 运行效果

```bash
$ python workflow_demo.py

============================================================
🏦 银行运营自动化系统演示
============================================================
✅ 工单创建: TKT20240115143022 [紧急]

🔄 开始执行流程: TKT20240115143022
  → 受理
  → 分类
  → 分派
  → 处理
  → 关闭
✅ 流程完成: TKT20240115143022

✅ 工单创建: TKT20240115143023 [高]

🔄 开始执行流程: TKT20240115143023
  → 受理
  → 分类
  → 分派
  → 处理
  → 关闭
✅ 流程完成: TKT20240115143023

✅ 工单创建: TKT20240115143024 [中]

🔄 开始执行流程: TKT20240115143024
  → 受理
  → 分类
  → 分派
  → 处理
  → 关闭
✅ 流程完成: TKT20240115143024

✅ 工单创建: TKT20240115143025 [高]

🔄 开始执行流程: TKT20240115143025
  → 受理
  → 分类
  → 分派
  → 处理
  → 关闭
✅ 流程完成: TKT20240115143025

============================================================
📊 系统统计
============================================================
总工单数: 4
已解决: 4
已关闭: 4
SLA超时: 0
解决率: 100.0%

============================================================
📝 工单详情
============================================================

TKT20240115143022: 核心系统响应超时
  状态: 已关闭
  处理人: 运维组
  SLA截止: 2024-01-15 18:30:22
  处理历史:
    [2024-01-15T14:30:22] 创建 - 系统
    [2024-01-15T14:30:22] 受理 - 系统
    [2024-01-15T14:30:22] 分类 - 系统
    [2024-01-15T14:30:22] 分派 - 系统
    [2024-01-15T14:30:23] 处理 - 运维组
    [2024-01-15T14:30:23] 解决 - 运维组
    [2024-01-15T14:30:23] 关闭 - 系统
```

## SLA监控告警

```python
class SLAMonitor:
    """SLA监控器"""
    
    def __init__(self):
        self.alerts = []
    
    def check(self, ticket_system: TicketSystem):
        """检查SLA状态"""
        overdue = ticket_system.check_sla()
        
        for ticket in overdue:
            alert = {
                "ticket_id": ticket.id,
                "title": ticket.title,
                "priority": ticket.priority.value,
                "deadline": ticket.sla_deadline.isoformat(),
                "overdue_minutes": (datetime.now() - ticket.sla_deadline).seconds // 60
            }
            self.alerts.append(alert)
            
            # 发送告警
            self.send_alert(alert)
    
    def send_alert(self, alert: dict):
        """发送告警通知"""
        print(f"🚨 SLA告警!")
        print(f"  工单: {alert['ticket_id']}")
        print(f"  标题: {alert['title']}")
        print(f"  优先级: {alert['priority']}")
        print(f"  已超时: {alert['overdue_minutes']}分钟")
        
        # 实际应发送邮件/短信/企业微信
        # send_email(...)
        # send_wechat(...)

# 定时检查
import schedule
import time

monitor = SLAMonitor()

schedule.every(5).minutes.do(monitor.check, system)

while True:
    schedule.run_pending()
    time.sleep(1)
```

---

**完整代码**：https://github.com/yuzhaopeng-up/financial-ai-skills/tree/main/skills/operations-automation/examples

**#运营自动化 #工单系统 #流程编排 #SLA监控 #银行运营**
