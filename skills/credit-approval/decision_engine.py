#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
审批决策引擎
规则引擎+模型决策、自动审批
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class DecisionResult(Enum):
    """审批结果"""
    AUTO_APPROVE = ("自动通过", "🟢")
    MANUAL_REVIEW = ("人工复核", "🟡")
    REJECT = ("拒绝", "🔴")
    SUPPLEMENT = ("补充材料", "🟠")
    
    def __init__(self, label, emoji):
        self.label = label
        self.emoji = emoji


@dataclass
class ApprovalDecision:
    """审批决策"""
    application_id: str
    decision: DecisionResult
    approved_amount: float
    approved_rate: float
    approved_term: int
    
    reasons: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    risk_warnings: List[str] = field(default_factory=list)
    
    approval_time: Optional[str] = None
    approver: Optional[str] = None


class DecisionEngine:
    """审批决策引擎"""

    def __init__(self):
        self.decisions = {}
        
        # 审批规则配置
        self.rules = {
            "auto_approve": {
                "min_credit_score": 80,
                "max_debt_ratio": 0.5,
                "max_overdue_count": 0,
                "min_income": 10000,
                "max_loan_amount": 1000000
            },
            "manual_review": {
                "min_credit_score": 60,
                "max_debt_ratio": 0.7,
                "max_overdue_count": 2,
                "min_income": 5000
            }
        }

    def make_decision(self, application_id: str,
                      credit_score: float,
                      credit_grade: str,
                      loan_amount: float,
                      income_monthly: float,
                      existing_debts_monthly: float,
                      overdue_count_24m: int,
                      max_overdue_days: int,
                      collateral_value: float = 0) -> ApprovalDecision:
        """做出审批决策"""
        
        reasons = []
        conditions = []
        risk_warnings = []
        
        # 计算债务收入比
        debt_ratio = (existing_debts_monthly + 
                      self._estimate_monthly_payment(loan_amount)) / income_monthly if income_monthly > 0 else 1.0
        
        # 计算抵押率
        collateral_ratio = loan_amount / collateral_value if collateral_value > 0 else 1.0
        
        # 规则判断
        auto_rules = self.rules["auto_approve"]
        manual_rules = self.rules["manual_review"]
        
        # 自动通过条件
        if (credit_score >= auto_rules["min_credit_score"] and
            debt_ratio <= auto_rules["max_debt_ratio"] and
            overdue_count_24m <= auto_rules["max_overdue_count"] and
            income_monthly >= auto_rules["min_income"] and
            loan_amount <= auto_rules["max_loan_amount"] and
            max_overdue_days == 0):
            
            decision = DecisionResult.AUTO_APPROVE
            reasons.append("信用评分优秀，符合自动审批条件")
            approved_amount = loan_amount
            approved_rate = self._get_optimal_rate(credit_score, collateral_value > 0)
            
        # 人工复核条件
        elif (credit_score >= manual_rules["min_credit_score"] and
              debt_ratio <= manual_rules["max_debt_ratio"] and
              overdue_count_24m <= manual_rules["max_overdue_count"] and
              income_monthly >= manual_rules["min_income"]):
            
            decision = DecisionResult.MANUAL_REVIEW
            reasons.append("需要人工复核")
            
            if debt_ratio > 0.5:
                risk_warnings.append(f"债务收入比偏高 ({debt_ratio:.1%})")
                conditions.append("要求提供额外收入证明")
            
            if overdue_count_24m > 0:
                risk_warnings.append(f"有逾期记录 ({overdue_count_24m}次)")
                conditions.append("要求说明逾期原因")
            
            approved_amount = loan_amount * 0.8  # 人工复核降低额度
            approved_rate = self._get_optimal_rate(credit_score, collateral_value > 0) + 0.5
            
        # 拒绝条件
        else:
            decision = DecisionResult.REJECT
            
            if credit_score < manual_rules["min_credit_score"]:
                reasons.append(f"信用评分不足 ({credit_score} < {manual_rules['min_credit_score']})")
            
            if debt_ratio > manual_rules["max_debt_ratio"]:
                reasons.append(f"债务收入比过高 ({debt_ratio:.1%} > {manual_rules['max_debt_ratio']})")
            
            if overdue_count_24m > manual_rules["max_overdue_count"]:
                reasons.append(f"逾期次数过多 ({overdue_count_24m} > {manual_rules['max_overdue_count']})")
            
            if income_monthly < manual_rules["min_income"]:
                reasons.append(f"收入不足 ({income_monthly} < {manual_rules['min_income']})")
            
            approved_amount = 0
            approved_rate = 0
        
        # 抵押物优惠
        if collateral_value > 0 and decision != DecisionResult.REJECT:
            if collateral_ratio <= 0.7:
                approved_rate -= 0.3
                reasons.append("抵押物充足，利率优惠")
            elif collateral_ratio <= 0.8:
                approved_rate -= 0.1
                reasons.append("抵押物较充足")
            else:
                risk_warnings.append(f"抵押率偏高 ({collateral_ratio:.1%})")
                conditions.append("要求补充抵押物或降低额度")
        
        approval_decision = ApprovalDecision(
            application_id=application_id,
            decision=decision,
            approved_amount=approved_amount,
            approved_rate=max(0, approved_rate),
            approved_term=0,  # 由申请决定
            reasons=reasons,
            conditions=conditions,
            risk_warnings=risk_warnings
        )
        
        self.decisions[application_id] = approval_decision
        return approval_decision

    def _estimate_monthly_payment(self, loan_amount: float, 
                                   annual_rate: float = 0.0435,
                                   term_months: int = 240) -> float:
        """估算月供（等额本息）"""
        monthly_rate = annual_rate / 12
        if monthly_rate == 0:
            return loan_amount / term_months
        
        # 等额本息公式
        payment = loan_amount * monthly_rate * (1 + monthly_rate) ** term_months / \
                  ((1 + monthly_rate) ** term_months - 1)
        return payment

    def _get_optimal_rate(self, credit_score: float, has_collateral: bool) -> float:
        """获取最优利率"""
        base_rate = 4.35  # LPR基准
        
        # 信用评分调整
        if credit_score >= 90:
            adjustment = 0.5
        elif credit_score >= 80:
            adjustment = 1.0
        elif credit_score >= 70:
            adjustment = 1.5
        elif credit_score >= 60:
            adjustment = 2.5
        else:
            adjustment = 4.0
        
        # 抵押物调整
        if has_collateral:
            adjustment -= 0.5
        
        return base_rate + adjustment

    def get_decision_summary(self, application_id: str) -> Dict:
        """获取决策摘要"""
        decision = self.decisions.get(application_id)
        if not decision:
            return {}
        
        return {
            "申请编号": decision.application_id,
            "审批结果": f"{decision.decision.emoji} {decision.decision.label}",
            "批准金额": f"{decision.approved_amount:,.0f} 元" if decision.approved_amount > 0 else "未批准",
            "批准利率": f"{decision.approved_rate:.2f}%" if decision.approved_rate > 0 else "-",
            "审批理由": decision.reasons,
            "附加条件": decision.conditions if decision.conditions else ["无"],
            "风险提示": decision.risk_warnings if decision.risk_warnings else ["无显著风险"]
        }
