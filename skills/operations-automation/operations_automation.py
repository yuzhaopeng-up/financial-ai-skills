#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运营自动化主引擎
整合所有模块，提供一站式运营自动化服务
"""

from ticket_processor import TicketProcessor, TicketPriority
from workflow_engine import WorkflowEngine
from monitor_alert import MonitorAlert


class OperationsAutomationEngine:
    """运营自动化引擎"""

    def __init__(self):
        self.ticket_processor = TicketProcessor()
        self.workflow_engine = WorkflowEngine()
        self.monitor = MonitorAlert()

    def create_ticket(self, ticket_id: str, title: str,
                      description: str, category: str,
                      priority: str, customer_id: str) -> dict:
        """创建工单"""
        print(f"🎫 创建工单 [{ticket_id}]...")

        ticket = self.ticket_processor.create_ticket(
            ticket_id=ticket_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            customer_id=customer_id
        )

        return self.ticket_processor.get_ticket_summary(ticket_id)

    def process_ticket(self, ticket_id: str) -> dict:
        """处理工单"""
        print(f"⚙️ 处理工单 [{ticket_id}]...")

        # 1. 自动分派
        assign_result = self.ticket_processor.auto_assign(ticket_id)

        # 2. 自动解决（如适用）
        resolve_result = self.ticket_processor.auto_resolve(ticket_id)

        return {
            "assignment": assign_result,
            "resolution": resolve_result,
            "ticket": self.ticket_processor.get_ticket_summary(ticket_id)
        }

    def create_workflow(self, workflow_id: str, name: str,
                        description: str) -> dict:
        """创建工作流"""
        print(f"📋 创建工作流 [{workflow_id}]...")

        workflow = self.workflow_engine.create_workflow(
            workflow_id=workflow_id,
            name=name,
            description=description
        )

        return {
            "workflow_id": workflow_id,
            "name": name,
            "status": "已创建"
        }

    def add_workflow_nodes(self, workflow_id: str) -> dict:
        """添加工作流节点（示例：开户流程）"""
        print(f"➕ 添加工作流节点 [{workflow_id}]...")

        # 开户流程示例
        nodes = [
            ("start", "开始", "task", "notify", ["validate"]),
            ("validate", "身份验证", "task", "api_call", ["check_risk"]),
            ("check_risk", "风险检查", "condition", "api_call", ["approve", "reject"]),
            ("approve", "自动审批", "task", "notify", ["create_account"]),
            ("reject", "拒绝开户", "task", "send_sms", ["end"]),
            ("create_account", "创建账户", "task", "api_call", ["send_welcome"]),
            ("send_welcome", "发送欢迎", "task", "send_email", ["end"]),
            ("end", "结束", "task", "notify", [])
        ]

        for node_id, name, node_type, action, next_nodes in nodes:
            self.workflow_engine.add_node(
                workflow_id=workflow_id,
                node_id=node_id,
                name=name,
                node_type=node_type,
                action=action,
                next_nodes=next_nodes
            )

        return {"success": True, "node_count": len(nodes)}

    def execute_workflow(self, workflow_id: str,
                         context: dict = None) -> dict:
        """执行工作流"""
        print(f"🚀 执行工作流 [{workflow_id}]...")

        result = self.workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            context=context or {}
        )

        return result

    def register_metric(self, metric_id: str, name: str,
                        metric_type: str, unit: str,
                        warning: float, critical: float) -> dict:
        """注册监控指标"""
        print(f"📊 注册指标 [{metric_id}]...")

        metric = self.monitor.register_metric(
            metric_id=metric_id,
            name=name,
            metric_type=metric_type,
            unit=unit,
            warning_threshold=warning,
            critical_threshold=critical
        )

        return self.monitor.get_metric_summary(metric_id)

    def collect_metric(self, metric_id: str, value: float) -> dict:
        """采集指标"""
        result = self.monitor.collect_metric(metric_id, value)
        return result

    def full_operations_demo(self) -> dict:
        """执行完整运营自动化演示"""
        print(f"\n{'='*60}")
        print(f"🏭 开始运营自动化全流程演示")
        print(f"{'='*60}\n")

        results = {}

        # 1. 工单处理演示
        print("📌 场景 1: 智能工单处理")
        print("-" * 40)

        ticket_result = self.create_ticket(
            ticket_id="TKT20250606001",
            title="账户异常冻结",
            description="客户反映账户被冻结，无法转账",
            category="账户",
            priority="高",
            customer_id="C001"
        )
        print(f"创建工单: {ticket_result['标题']} ({ticket_result['优先级']})")

        process_result = self.process_ticket("TKT20250606001")
        print(f"分派结果: {process_result['assignment'].get('assigned_to', '-')}")
        print(f"处理结果: {process_result['resolution'].get('status', '-')}")
        print()

        # 2. 工作流编排演示
        print("📌 场景 2: 流程自动化编排")
        print("-" * 40)

        self.create_workflow(
            workflow_id="WF001",
            name="自动开户流程",
            description="新客户线上开户自动化流程"
        )

        self.add_workflow_nodes("WF001")

        workflow_result = self.execute_workflow(
            workflow_id="WF001",
            context={
                "phone": "13800138000",
                "email": "customer@example.com",
                "api_name": "identity_verify",
                "notify_message": "开户流程启动"
            }
        )
        print(f"工作流执行: {'成功' if workflow_result['success'] else '失败'}")
        print(f"执行路径: {' -> '.join(workflow_result.get('execution_path', []))}")
        print()

        # 3. 监控告警演示
        print("📌 场景 3: 运营监控告警")
        print("-" * 40)

        self.register_metric(
            metric_id="CPU001",
            name="核心系统CPU使用率",
            metric_type="cpu",
            unit="%",
            warning=70,
            critical=90
        )

        # 模拟指标采集
        values = [45, 52, 68, 75, 85, 92]
        for value in values:
            result = self.collect_metric("CPU001", value)
            if result.get("alert_triggered"):
                alert = result["alert"]
                print(f"⚠️ 告警触发! [{alert['level']}] {alert['message']}")
            else:
                print(f"✅ CPU: {value}% (正常)")

        print()

        # 汇总
        active_alerts = self.monitor.get_all_active_alerts()
        print(f"活跃告警数: {len(active_alerts)}")

        print("\n✅ 运营自动化演示完成！")

        return {
            "ticket": ticket_result,
            "workflow": workflow_result,
            "alerts": active_alerts
        }


if __name__ == "__main__":
    # 演示
    engine = OperationsAutomationEngine()
    result = engine.full_operations_demo()
