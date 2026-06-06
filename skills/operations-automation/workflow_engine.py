#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流程自动化编排模块
工作流定义、节点编排、状态管理
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum
from datetime import datetime
import time


class NodeStatus(Enum):
    """节点状态"""
    PENDING = "待执行"
    RUNNING = "执行中"
    SUCCESS = "成功"
    FAILED = "失败"
    SKIPPED = "跳过"


class WorkflowStatus(Enum):
    """工作流状态"""
    PENDING = "待启动"
    RUNNING = "运行中"
    COMPLETED = "已完成"
    FAILED = "失败"
    PAUSED = "暂停"


@dataclass
class WorkflowNode:
    """工作流节点"""
    node_id: str
    name: str
    node_type: str  # task/condition/parallel/loop
    action: str
    
    # 执行配置
    timeout_seconds: int = 300
    retry_count: int = 0
    retry_delay: int = 5
    
    # 状态
    status: NodeStatus = NodeStatus.PENDING
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    output: Optional[Dict] = None
    error: Optional[str] = None
    
    # 连接
    next_nodes: List[str] = field(default_factory=list)
    condition: Optional[str] = None  # 条件表达式


@dataclass
class Workflow:
    """工作流"""
    workflow_id: str
    name: str
    description: str
    nodes: Dict[str, WorkflowNode]
    start_node: str
    
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_node: Optional[str] = None
    context: Dict = field(default_factory=dict)
    
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class WorkflowEngine:
    """工作流引擎"""

    def __init__(self):
        self.workflows = {}
        
        # 预定义动作
        self.actions = {
            "send_sms": self._action_send_sms,
            "send_email": self._action_send_email,
            "api_call": self._action_api_call,
            "data_transform": self._action_data_transform,
            "human_approval": self._action_human_approval,
            "delay": self._action_delay,
            "notify": self._action_notify
        }

    def create_workflow(self, workflow_id: str, name: str,
                        description: str) -> Workflow:
        """创建工作流"""
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            nodes={},
            start_node=""
        )
        self.workflows[workflow_id] = workflow
        return workflow

    def add_node(self, workflow_id: str, node_id: str, name: str,
                 node_type: str, action: str,
                 next_nodes: List[str] = None,
                 condition: str = None,
                 timeout: int = 300) -> WorkflowNode:
        """添加节点"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
        
        node = WorkflowNode(
            node_id=node_id,
            name=name,
            node_type=node_type,
            action=action,
            next_nodes=next_nodes or [],
            condition=condition,
            timeout_seconds=timeout
        )
        
        workflow.nodes[node_id] = node
        
        # 设置起始节点
        if not workflow.start_node:
            workflow.start_node = node_id
        
        return node

    def execute_workflow(self, workflow_id: str,
                         context: Dict = None) -> Dict:
        """执行工作流"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"success": False, "error": "工作流不存在"}
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.start_time = datetime.now().isoformat()
        workflow.context = context or {}
        
        print(f"🚀 启动工作流 [{workflow.name}]...")
        
        current_node_id = workflow.start_node
        execution_path = []
        
        while current_node_id:
            node = workflow.nodes.get(current_node_id)
            if not node:
                break
            
            workflow.current_node = current_node_id
            execution_path.append(current_node_id)
            
            # 执行节点
            result = self._execute_node(workflow, node)
            
            if not result["success"]:
                workflow.status = WorkflowStatus.FAILED
                workflow.end_time = datetime.now().isoformat()
                return {
                    "success": False,
                    "workflow_id": workflow_id,
                    "failed_at": current_node_id,
                    "error": result.get("error"),
                    "execution_path": execution_path
                }
            
            # 确定下一个节点
            current_node_id = self._get_next_node(workflow, node, result)
        
        workflow.status = WorkflowStatus.COMPLETED
        workflow.end_time = datetime.now().isoformat()
        
        print(f"✅ 工作流 [{workflow.name}] 执行完成")
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "execution_path": execution_path,
            "context": workflow.context,
            "duration": self._calculate_duration(workflow.start_time, workflow.end_time)
        }

    def _execute_node(self, workflow: Workflow, node: WorkflowNode) -> Dict:
        """执行单个节点"""
        print(f"  📍 执行节点 [{node.name}]...")
        
        node.status = NodeStatus.RUNNING
        node.start_time = datetime.now().isoformat()
        
        # 获取动作函数
        action_func = self.actions.get(node.action)
        if not action_func:
            node.status = NodeStatus.FAILED
            node.error = f"未知动作: {node.action}"
            return {"success": False, "error": node.error}
        
        try:
            # 执行动作
            result = action_func(workflow.context, node)
            
            node.status = NodeStatus.SUCCESS
            node.end_time = datetime.now().isoformat()
            node.output = result
            
            print(f"  ✅ 节点 [{node.name}] 执行成功")
            return {"success": True, "output": result}
            
        except Exception as e:
            node.status = NodeStatus.FAILED
            node.error = str(e)
            node.end_time = datetime.now().isoformat()
            
            print(f"  ❌ 节点 [{node.name}] 执行失败: {e}")
            return {"success": False, "error": str(e)}

    def _get_next_node(self, workflow: Workflow, node: WorkflowNode,
                       result: Dict) -> Optional[str]:
        """确定下一个节点"""
        if not node.next_nodes:
            return None
        
        if len(node.next_nodes) == 1:
            return node.next_nodes[0]
        
        # 条件分支
        if node.condition:
            # 简化条件判断
            condition_met = self._evaluate_condition(
                workflow.context, node.condition
            )
            return node.next_nodes[0] if condition_met else node.next_nodes[1]
        
        return node.next_nodes[0]

    def _evaluate_condition(self, context: Dict, condition: str) -> bool:
        """评估条件"""
        # 简化实现，实际应使用表达式引擎
        try:
            return eval(condition, {"__builtins__": {}}, context)
        except:
            return True

    def _calculate_duration(self, start: str, end: str) -> str:
        """计算执行时长"""
        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            duration = (end_dt - start_dt).total_seconds()
            return f"{duration:.2f}秒"
        except:
            return "未知"

    # 预定义动作实现
    def _action_send_sms(self, context: Dict, node: WorkflowNode) -> Dict:
        """发送短信"""
        phone = context.get("phone", "")
        message = context.get("sms_content", "")
        print(f"    📱 发送短信至 {phone}: {message[:50]}...")
        return {"channel": "sms", "recipient": phone, "status": "sent"}

    def _action_send_email(self, context: Dict, node: WorkflowNode) -> Dict:
        """发送邮件"""
        email = context.get("email", "")
        subject = context.get("email_subject", "")
        print(f"    📧 发送邮件至 {email}: {subject}")
        return {"channel": "email", "recipient": email, "status": "sent"}

    def _action_api_call(self, context: Dict, node: WorkflowNode) -> Dict:
        """API调用"""
        api_name = context.get("api_name", "")
        print(f"    🔌 调用API: {api_name}")
        return {"api": api_name, "status": "success", "data": {}}

    def _action_data_transform(self, context: Dict, node: WorkflowNode) -> Dict:
        """数据转换"""
        print(f"    🔄 数据转换")
        return {"transformed": True}

    def _action_human_approval(self, context: Dict, node: WorkflowNode) -> Dict:
        """人工审批"""
        print(f"    👤 等待人工审批")
        return {"approved": True, "approver": "system"}

    def _action_delay(self, context: Dict, node: WorkflowNode) -> Dict:
        """延迟"""
        delay = context.get("delay_seconds", 1)
        print(f"    ⏱️ 延迟 {delay} 秒")
        time.sleep(min(delay, 2))  # 最多延迟2秒
        return {"delayed": delay}

    def _action_notify(self, context: Dict, node: WorkflowNode) -> Dict:
        """通知"""
        message = context.get("notify_message", "")
        print(f"    📢 通知: {message}")
        return {"notified": True}

    def get_workflow_summary(self, workflow_id: str) -> Dict:
        """获取工作流摘要"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {}
        
        node_statuses = {}
        for node_id, node in workflow.nodes.items():
            node_statuses[node_id] = {
                "name": node.name,
                "status": node.status.value,
                "duration": self._calculate_duration(
                    node.start_time, node.end_time
                ) if node.start_time else "未执行"
            }
        
        return {
            "工作流ID": workflow.workflow_id,
            "名称": workflow.name,
            "描述": workflow.description,
            "状态": workflow.status.value,
            "节点数": len(workflow.nodes),
            "节点状态": node_statuses,
            "上下文": workflow.context
        }
