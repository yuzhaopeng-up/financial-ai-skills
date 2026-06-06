#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信用评分模型
多维度信用评分、行为评分
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class CreditGrade(Enum):
    """信用等级"""
    AAA = ("AAA", 95, 100, "信用极好")
    AA = ("AA", 85, 94, "信用优秀")
    A = ("A", 75, 84, "信用良好")
    BBB = ("BBB", 65, 74, "信用一般")
    BB = ("BB", 55, 64, "信用较差")
    B = ("B", 45, 54, "信用差")
    CCC = ("CCC", 0, 44, "信用极差")
    
    def __init__(self, grade, min_score, max_score, description):
        self.grade = grade
        self.min_score = min_score
        self.max_score = max_score
        self.description = description
    
    @classmethod
    def get_grade(cls, score: float) -> "CreditGrade":
        for grade in cls:
            if grade.min_score <= score <= grade.max_score:
                return grade
        return cls.CCC


@dataclass
class CreditScore:
    """信用评分结果"""
    total_score: float
    grade: CreditGrade
    
    # 维度得分
    identity_score: float      # 身份特质
    credit_history_score: float # 信用历史
    behavior_score: float      # 行为偏好
    ability_score: float       # 履约能力
    social_score: float        # 社交关系
    
    risk_factors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class CreditScorer:
    """信用评分器"""

    def __init__(self):
        self.scores = {}

    def calculate_score(self, application_id: str,
                        age: int,
                        education: str,
                        occupation: str,
                        income_monthly: float,
                        housing_status: str,
                        credit_history_years: int,
                        existing_loans: int,
                        overdue_count_24m: int,
                        max_overdue_days: int,
                        credit_utilization: float,
                        query_count_6m: int,
                        payment_regularity: str) -> CreditScore:
        """计算信用评分"""
        
        # 1. 身份特质 (最高20分)
        identity = self._score_identity(age, education, occupation, housing_status)
        
        # 2. 信用历史 (最高25分)
        credit_history = self._score_credit_history(
            credit_history_years, overdue_count_24m, max_overdue_days
        )
        
        # 3. 行为偏好 (最高20分)
        behavior = self._score_behavior(credit_utilization, query_count_6m, payment_regularity)
        
        # 4. 履约能力 (最高25分)
        ability = self._score_ability(income_monthly, existing_loans)
        
        # 5. 社交关系 (最高10分)
        social = self._score_social(occupation)
        
        total = identity + credit_history + behavior + ability + social
        grade = CreditGrade.get_grade(total)
        
        # 风险因子
        risk_factors = []
        if overdue_count_24m > 0:
            risk_factors.append(f"近24个月有{overdue_count_24m}次逾期记录")
        if max_overdue_days > 30:
            risk_factors.append(f"最长逾期{max_overdue_days}天")
        if credit_utilization > 0.8:
            risk_factors.append("信用卡使用率过高")
        if query_count_6m > 6:
            risk_factors.append("近6个月征信查询次数过多")
        if existing_loans >= 3:
            risk_factors.append("已有较多未结清贷款")
        
        # 建议
        suggestions = []
        if credit_utilization > 0.7:
            suggestions.append("降低信用卡使用率至70%以下")
        if query_count_6m > 4:
            suggestions.append("减少短期内征信查询次数")
        if overdue_count_24m > 0:
            suggestions.append("保持良好的还款记录")
        
        score = CreditScore(
            total_score=round(total, 1),
            grade=grade,
            identity_score=round(identity, 1),
            credit_history_score=round(credit_history, 1),
            behavior_score=round(behavior, 1),
            ability_score=round(ability, 1),
            social_score=round(social, 1),
            risk_factors=risk_factors,
            suggestions=suggestions
        )
        
        self.scores[application_id] = score
        return score

    def _score_identity(self, age: int, education: str,
                        occupation: str, housing_status: str) -> float:
        """身份特质评分"""
        score = 10.0  # 基础分
        
        # 年龄
        if 25 <= age <= 45:
            score += 3
        elif 45 < age <= 55:
            score += 2
        else:
            score += 1
        
        # 学历
        edu_scores = {"博士": 3, "硕士": 2.5, "本科": 2, "大专": 1, "高中": 0.5}
        score += edu_scores.get(education, 0)
        
        # 职业稳定性
        stable_jobs = ["公务员", "事业单位", "国企", "医生", "教师"]
        if occupation in stable_jobs:
            score += 3
        elif "企业" in occupation:
            score += 2
        else:
            score += 1
        
        # 住房
        if housing_status == "自有住房":
            score += 1
        
        return min(20, score)

    def _score_credit_history(self, years: int, overdue_count: int,
                              max_overdue_days: int) -> float:
        """信用历史评分"""
        score = 15.0  # 基础分
        
        # 信用历史长度
        if years >= 10:
            score += 5
        elif years >= 5:
            score += 3
        elif years >= 2:
            score += 1
        
        # 逾期扣分
        if overdue_count == 0:
            score += 5
        else:
            score -= overdue_count * 3
        
        # 最长逾期扣分
        if max_overdue_days == 0:
            score += 0
        elif max_overdue_days <= 7:
            score -= 2
        elif max_overdue_days <= 30:
            score -= 5
        elif max_overdue_days <= 90:
            score -= 10
        else:
            score -= 15
        
        return max(0, min(25, score))

    def _score_behavior(self, utilization: float, queries: int,
                        regularity: str) -> float:
        """行为偏好评分"""
        score = 10.0
        
        # 信用卡使用率
        if utilization <= 0.3:
            score += 5
        elif utilization <= 0.5:
            score += 3
        elif utilization <= 0.7:
            score += 1
        else:
            score -= 5
        
        # 查询次数
        if queries <= 2:
            score += 3
        elif queries <= 4:
            score += 1
        elif queries <= 6:
            score -= 2
        else:
            score -= 5
        
        # 还款规律性
        if regularity == "按时":
            score += 2
        elif regularity == "偶尔提前":
            score += 1
        elif regularity == "偶尔逾期":
            score -= 3
        
        return max(0, min(20, score))

    def _score_ability(self, income: float, existing_loans: int) -> float:
        """履约能力评分"""
        score = 15.0
        
        # 收入水平
        if income >= 50000:
            score += 5
        elif income >= 20000:
            score += 4
        elif income >= 10000:
            score += 3
        elif income >= 5000:
            score += 2
        else:
            score += 1
        
        # 现有贷款负担
        if existing_loans == 0:
            score += 5
        elif existing_loans == 1:
            score += 3
        elif existing_loans == 2:
            score += 1
        else:
            score -= existing_loans * 2
        
        return max(0, min(25, score))

    def _score_social(self, occupation: str) -> float:
        """社交关系评分"""
        score = 5.0
        
        # 职业社交属性
        high_social = ["销售", "市场", "公关", "管理"]
        if any(job in occupation for job in high_social):
            score += 3
        
        return min(10, score)

    def get_score_summary(self, application_id: str) -> Dict:
        """获取评分摘要"""
        score = self.scores.get(application_id)
        if not score:
            return {}
        
        return {
            "信用评分": score.total_score,
            "信用等级": f"{score.grade.grade} ({score.grade.description})",
            "维度得分": {
                "身份特质": score.identity_score,
                "信用历史": score.credit_history_score,
                "行为偏好": score.behavior_score,
                "履约能力": score.ability_score,
                "社交关系": score.social_score
            },
            "风险因子": score.risk_factors,
            "改进建议": score.suggestions
        }
