# -*- coding: utf-8 -*-
"""
费用报销引擎 v1.0

核心能力:
- 费用智能分类
- 合规性检查
- 审批流建议
- 重复报销检测

协同: RemoteAgentB (自动化) / RemoteAgentA (规则分析)
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime


class ExpenseEngine:
    """费用报销引擎"""
    
    # 费用类别映射
    EXPENSE_CATEGORIES = {
        "差旅": ["机票", "酒店", "火车票", "出租车", "网约车", "过路费", "停车费"],
        "餐饮": ["餐费", "招待", "宴请", "工作餐", "加班餐"],
        "办公": ["文具", "打印", "快递", "办公用品", "耗材"],
        "通讯": ["话费", "流量", "宽带", "通讯费"],
        "培训": ["培训", "课程", "考试", "认证", "书籍"],
        "设备": ["电脑", "手机", "平板", "显示器", "配件"],
    }
    
    # 报销规则
    REIMBURSEMENT_RULES = {
        "差旅": {
            "hotel_limit": 800,  # 每晚上限
            "meal_limit": 200,   # 每天上限
            "transport_limit": 5000,  # 单次上限
        },
        "餐饮": {
            "per_meal_limit": 500,
            "monthly_limit": 3000,
        },
        "办公": {
            "single_limit": 1000,
            "monthly_limit": 2000,
        },
    }
    
    # 模拟报销记录（用于重复检测）
    MOCK_HISTORY = [
        {"date": "2026-04-10", "amount": 580, "category": "差旅", "desc": "北京出差机票"},
        {"date": "2026-04-12", "amount": 320, "category": "餐饮", "desc": "客户招待"},
        {"date": "2026-04-15", "amount": 120, "category": "办公", "desc": "打印耗材"},
    ]
    
    def __init__(self):
        self.engine_name = "ExpenseEngine"
        self.version = "1.0.0"
    
    def process(
        self,
        description: str,
        amount: float,
        date: Optional[str] = None,
        receipt_url: Optional[str] = None,
        employee_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        费用报销处理主入口
        
        Args:
            description: 费用描述
            amount: 金额
            date: 日期（默认今天）
            receipt_url: 发票/收据图片URL
            employee_id: 员工ID
            
        Returns:
            处理结果
        """
        start_time = datetime.now()
        expense_date = date or datetime.now().strftime("%Y-%m-%d")
        
        # 1. 智能分类
        category = self._classify(description)
        
        # 2. 合规检查
        compliance = self._check_compliance(category, amount, description)
        
        # 3. 重复检测
        duplicate = self._check_duplicate(description, amount, expense_date)
        
        # 4. 审批建议
        approval = self._suggest_approval(category, amount, compliance, duplicate)
        
        result = {
            "success": True,
            "scenario": "expense",
            "expense": {
                "description": description,
                "amount": amount,
                "date": expense_date,
                "category": category,
            },
            "classification": {
                "category": category,
                "confidence": "high",
                "method": "规则匹配"
            },
            "compliance": compliance,
            "duplicate_check": duplicate,
            "approval": approval,
            "recommendations": self._generate_recommendations(compliance, approval),
            "timestamp": datetime.now().isoformat(),
            "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000)
        }
        
        return result
    
    def batch_process(self, expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量费用处理
        
        Args:
            expenses: 费用列表 [{"description": "...", "amount": 100}, ...]
            
        Returns:
            批量处理结果
        """
        results = []
        total_amount = 0
        issues = []
        
        for exp in expenses:
            result = self.process(
                description=exp.get("description", ""),
                amount=exp.get("amount", 0),
                date=exp.get("date")
            )
            results.append(result)
            total_amount += exp.get("amount", 0)
            
            if not result["compliance"]["passed"]:
                issues.append({
                    "expense": exp.get("description", ""),
                    "issue": result["compliance"]["flags"][0]["msg"]
                })
        
        return {
            "success": True,
            "scenario": "expense_batch",
            "total_count": len(expenses),
            "total_amount": total_amount,
            "passed_count": len(expenses) - len(issues),
            "issue_count": len(issues),
            "issues": issues,
            "details": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _classify(self, description: str) -> str:
        """智能分类费用"""
        desc_lower = description.lower()
        
        for category, keywords in self.EXPENSE_CATEGORIES.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    return category
        
        # 默认分类
        if any(kw in desc_lower for kw in ["票", "车", "机", "酒", "住"]):
            return "差旅"
        elif any(kw in desc_lower for kw in ["吃", "饭", "餐", "喝", "茶", "咖啡"]):
            return "餐饮"
        elif any(kw in desc_lower for kw in ["电", "脑", "手机", "设备", "硬件"]):
            return "设备"
        
        return "其他"
    
    def _check_compliance(
        self,
        category: str,
        amount: float,
        description: str
    ) -> Dict[str, Any]:
        """合规性检查"""
        flags = []
        passed = True
        
        rules = self.REIMBURSEMENT_RULES.get(category, {})
        
        # 检查金额上限
        if "single_limit" in rules and amount > rules["single_limit"]:
            flags.append({
                "level": "error",
                "msg": f"金额¥{amount}超过{category}单笔限额¥{rules['single_limit']}"
            })
            passed = False
        
        # 检查描述完整性
        if len(description) < 5:
            flags.append({
                "level": "warning",
                "msg": "费用描述过于简单，建议补充详细信息"
            })
        
        # 检查金额合理性
        if amount <= 0:
            flags.append({"level": "error", "msg": "金额必须大于0"})
            passed = False
        elif amount > 10000:
            flags.append({
                "level": "warning",
                "msg": "单笔金额超过1万元，需额外审批"
            })
        
        # 检查敏感词
        sensitive = ["礼品", "购物卡", "现金", "红包"]
        for word in sensitive:
            if word in description:
                flags.append({
                    "level": "error",
                    "msg": f"描述包含敏感词「{word}」，不符合报销规定"
                })
                passed = False
        
        return {
            "passed": passed,
            "flags": flags,
            "score": 100 - len([f for f in flags if f["level"] == "error"]) * 30 - len([f for f in flags if f["level"] == "warning"]) * 10
        }
    
    def _check_duplicate(
        self,
        description: str,
        amount: float,
        date: str
    ) -> Dict[str, Any]:
        """重复报销检测"""
        for record in self.MOCK_HISTORY:
            # 简单匹配：金额相同且描述相似
            if abs(record["amount"] - amount) < 1:
                similarity = self._text_similarity(record["desc"], description)
                if similarity > 0.6:
                    return {
                        "is_duplicate": True,
                        "confidence": similarity,
                        "matched_record": record,
                        "message": f"⚠️ 疑似重复报销: {record['date']} 已报销「{record['desc']}」¥{record['amount']}"
                    }
        
        return {
            "is_duplicate": False,
            "confidence": 0,
            "message": "✅ 未检测到重复报销"
        }
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """简单文本相似度"""
        # 使用共同字符比例
        set1 = set(text1)
        set2 = set(text2)
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    
    def _suggest_approval(
        self,
        category: str,
        amount: float,
        compliance: Dict[str, Any],
        duplicate: Dict[str, Any]
    ) -> Dict[str, Any]:
        """审批建议"""
        # 确定审批级别
        if amount <= 500:
            level = "直接审批"
            approvers = ["部门经理"]
        elif amount <= 2000:
            level = "一级审批"
            approvers = ["部门经理", "财务审核"]
        elif amount <= 10000:
            level = "二级审批"
            approvers = ["部门经理", "财务经理", "分管领导"]
        else:
            level = "三级审批"
            approvers = ["部门经理", "财务经理", "分管领导", "总经理"]
        
        # 根据合规情况调整
        if not compliance["passed"]:
            status = "驳回"
            reason = compliance["flags"][0]["msg"] if compliance["flags"] else "合规检查未通过"
        elif duplicate["is_duplicate"]:
            status = "需核实"
            reason = duplicate["message"]
        elif amount > 5000:
            status = "待审批"
            reason = "金额较大，需逐级审批"
        else:
            status = "通过"
            reason = "合规检查通过"
        
        return {
            "status": status,
            "level": level,
            "approvers": approvers,
            "reason": reason,
            "estimated_time": "1-3个工作日" if status == "待审批" else "即时"
        }
    
    def _generate_recommendations(
        self,
        compliance: Dict[str, Any],
        approval: Dict[str, Any]
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if not compliance["passed"]:
            recommendations.append(f"🚨 请先处理合规问题: {compliance['flags'][0]['msg']}")
        
        if approval["status"] == "需核实":
            recommendations.append(f"⚠️ {approval['reason']}")
        
        if approval["level"] in ["二级审批", "三级审批"]:
            recommendations.append(f"📋 当前需{approval['level']}，预计耗时{approval['estimated_time']}")
        
        if not recommendations:
            recommendations.append("✅ 报销申请合规，可提交审批")
        
        return recommendations
