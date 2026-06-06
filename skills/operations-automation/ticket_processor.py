#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能工单处理模块
工单分类、自动分派、优先级排序
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class TicketCategory(Enum):
    """工单分类"""
    ACCOUNT = "账户问题"
    TRANSACTION = "交易问题"
    LOAN = "贷款问题"
    CARD = "卡片问题"
    SECURITY = "安全问题"
    COMPLAINT = "投诉建议"
    INQUIRY = "业务咨询"
    TECHNICAL = "技术故障"


class TicketPriority(Enum):
    """工单优先级"""
    CRITICAL = ("紧急", 1, "🔴")
    HIGH = ("高", 2, "🟠")
    MEDIUM = ("中", 3, "🟡")
    LOW = ("低", 4, "🟢")
    
    def __init__(self, label, level, emoji):
        self.label = label
        self.level = level
        self.emoji = emoji


class TicketStatus(Enum):
    """工单状态"""
    NEW = "新建"
    ASSIGNED = "已分派"
    PROCESSING = "处理中"
    PENDING = "待确认"
    RESOLVED = "已解决"
    CLOSED = "已关闭"
    ESCALATED = "已升级"


@dataclass
class Ticket:
    """工单"""
    ticket_id: str
    title: str
    description: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    customer_id: str
    
    created_time: str
    assigned_to: Optional[str] = None
    sla_deadline: Optional[str] = None
    
    resolution: Optional[str] = None
    closed_time: Optional[str] = None


class TicketProcessor:
    """工单处理器"""

    def __init__(self):
        self.tickets = {}
        self.team_capacity = {
            "账户组": 5,
            "交易组": 4,
            "贷款组": 3,
            "卡片组": 3,
            "安全组": 2,
            "投诉组": 2,
            "咨询组": 6,
            "技术组": 4
        }
        self.team_load = {team: 0 for team in self.team_capacity}

    def create_ticket(self, ticket_id: str, title: str,
                      description: str, category: str,
                      priority: str, customer_id: str) -> Ticket:
        """创建工单"""
        
        cat = self._parse_category(category)
        pri = self._parse_priority(priority)
        
        # 计算SLA截止时间
        sla_hours = self._calculate_sla(pri)
        sla_deadline = datetime.now().isoformat()  # 简化处理
        
        ticket = Ticket(
            ticket_id=ticket_id,
            title=title,
            description=description,
            category=cat,
            priority=pri,
            status=TicketStatus.NEW,
            customer_id=customer_id,
            created_time=datetime.now().isoformat(),
            sla_deadline=sla_deadline
        )
        
        self.tickets[ticket_id] = ticket
        return ticket

    def _parse_category(self, category: str) -> TicketCategory:
        """解析分类"""
        mapping = {
            "账户": TicketCategory.ACCOUNT,
            "交易": TicketCategory.TRANSACTION,
            "贷款": TicketCategory.LOAN,
            "卡片": TicketCategory.CARD,
            "安全": TicketCategory.SECURITY,
            "投诉": TicketCategory.COMPLAINT,
            "咨询": TicketCategory.INQUIRY,
            "技术": TicketCategory.TECHNICAL
        }
        return mapping.get(category, TicketCategory.INQUIRY)

    def _parse_priority(self, priority: str) -> TicketPriority:
        """解析优先级"""
        mapping = {
            "紧急": TicketPriority.CRITICAL,
            "高": TicketPriority.HIGH,
            "中": TicketPriority.MEDIUM,
            "低": TicketPriority.LOW
        }
        return mapping.get(priority, TicketPriority.MEDIUM)

    def _calculate_sla(self, priority: TicketPriority) -> int:
        """计算SLA时限（小时）"""
        sla_map = {
            TicketPriority.CRITICAL: 1,
            TicketPriority.HIGH: 4,
            TicketPriority.MEDIUM: 24,
            TicketPriority.LOW: 72
        }
        return sla_map.get(priority, 24)

    def auto_classify(self, title: str, description: str) -> TicketCategory:
        """自动分类（基于关键词）"""
        text = (title + " " + description).lower()
        
        keywords = {
            TicketCategory.ACCOUNT: ["账户", "冻结", "开户", "销户", "密码", "登录"],
            TicketCategory.TRANSACTION: ["转账", "交易", "汇款", "支付", "退款", "到账"],
            TicketCategory.LOAN: ["贷款", "还款", "利率", "额度", "逾期", "按揭"],
            TicketCategory.CARD: ["卡片", "信用卡", "借记卡", "换卡", "挂失", "额度"],
            TicketCategory.SECURITY: ["安全", "盗刷", "诈骗", "风险", "验证", "身份"],
            TicketCategory.COMPLAINT: ["投诉", "不满", "服务差", "态度", "乱收费"],
            TicketCategory.TECHNICAL: ["系统", "故障", "bug", "错误", "无法", "崩溃"]
        }
        
        scores = {}
        for cat, words in keywords.items():
            scores[cat] = sum(1 for word in words if word in text)
        
        if scores:
            return max(scores, key=scores.get)
        return TicketCategory.INQUIRY

    def auto_assign(self, ticket_id: str) -> Dict:
        """自动分派"""
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return {"success": False, "error": "工单不存在"}
        
        # 根据分类确定团队
        team_map = {
            TicketCategory.ACCOUNT: "账户组",
            TicketCategory.TRANSACTION: "交易组",
            TicketCategory.LOAN: "贷款组",
            TicketCategory.CARD: "卡片组",
            TicketCategory.SECURITY: "安全组",
            TicketCategory.COMPLAINT: "投诉组",
            TicketCategory.INQUIRY: "咨询组",
            TicketCategory.TECHNICAL: "技术组"
        }
        
        team = team_map.get(ticket.category, "咨询组")
        
        # 检查团队负载
        if self.team_load[team] >= self.team_capacity[team]:
            # 寻找负载最低的团队
            available_teams = [t for t, load in self.team_load.items() 
                             if load < self.team_capacity[t]]
            if available_teams:
                team = min(available_teams, key=lambda t: self.team_load[t])
        
        # 更新负载
        self.team_load[team] += 1
        
        # 更新工单
        ticket.status = TicketStatus.ASSIGNED
        ticket.assigned_to = team
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "assigned_to": team,
            "team_load": f"{self.team_load[team]}/{self.team_capacity[team]}",
            "sla_hours": self._calculate_sla(ticket.priority)
        }

    def auto_resolve(self, ticket_id: str) -> Dict:
        """自动解决（基于知识库匹配）"""
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return {"success": False, "error": "工单不存在"}
        
        # 模拟知识库匹配
        resolutions = {
            TicketCategory.ACCOUNT: "已指导客户通过APP重置密码，账户已恢复正常。",
            TicketCategory.TRANSACTION: "经核实，交易因系统延迟未实时到账，已人工补录。",
            TicketCategory.LOAN: "已为客户调整还款计划，下期还款日顺延15天。",
            TicketCategory.CARD: "已为客户办理挂失并补发新卡，预计3个工作日送达。",
            TicketCategory.SECURITY: "已冻结可疑交易，建议客户修改密码并开启双重验证。",
            TicketCategory.COMPLAINT: "已记录投诉内容，将安排专人回访处理。",
            TicketCategory.INQUIRY: "已解答客户疑问，发送相关产品资料。",
            TicketCategory.TECHNICAL: "已定位系统故障，技术团队正在修复中。"
        }
        
        resolution = resolutions.get(ticket.category, "已记录问题，安排人工处理。")
        
        # 低优先级工单可自动解决
        if ticket.priority in [TicketPriority.LOW, TicketPriority.MEDIUM]:
            ticket.status = TicketStatus.RESOLVED
            ticket.resolution = resolution
            ticket.closed_time = datetime.now().isoformat()
            
            # 释放团队负载
            if ticket.assigned_to:
                self.team_load[ticket.assigned_to] = max(0, self.team_load[ticket.assigned_to] - 1)
            
            return {
                "success": True,
                "ticket_id": ticket_id,
                "status": "已自动解决",
                "resolution": resolution,
                "auto_resolved": True
            }
        
        # 高优先级需要人工处理
        ticket.status = TicketStatus.PROCESSING
        return {
            "success": True,
            "ticket_id": ticket_id,
            "status": "处理中（需人工介入）",
            "suggested_resolution": resolution,
            "auto_resolved": False
        }

    def get_ticket_summary(self, ticket_id: str) -> Dict:
        """获取工单摘要"""
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return {}
        
        return {
            "工单编号": ticket.ticket_id,
            "标题": ticket.title,
            "分类": ticket.category.value,
            "优先级": f"{ticket.priority.emoji} {ticket.priority.label}",
            "状态": ticket.status.value,
            "客户ID": ticket.customer_id,
            "创建时间": ticket.created_time,
            "分派给": ticket.assigned_to or "未分派",
            "解决方案": ticket.resolution or "-"
        }
