#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险综合评级模块
复用 risk-compliance 评分能力，整合多维度风险
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    LOW = ("低风险", "🟢", 1)
    MEDIUM = ("中风险", "🟡", 2)
    HIGH = ("高风险", "🟠", 3)
    CRITICAL = ("极高风险", "🔴", 4)

    def __init__(self, label, emoji, priority):
        self.label = label
        self.emoji = emoji
        self.priority = priority


@dataclass
class RiskFactor:
    """风险因子"""
    category: str
    factor_name: str
    risk_level: RiskLevel
    score: float  # 0-100，越低越差
    description: str
    suggestions: List[str] = field(default_factory=list)


@dataclass
class RiskAssessment:
    """风险评估结果"""
    overall_risk: RiskLevel
    overall_score: float
    risk_factors: List[RiskFactor]
    key_warnings: List[str]
    mitigation_suggestions: List[str]


class RiskAssessor:
    """风险综合评估器"""

    def __init__(self):
        self.risk_factors = []

    def assess_financial_risk(self, financial_scores: dict) -> RiskFactor:
        """评估财务风险"""
        overall = financial_scores.get("综合评分", {}).get("score", 50)

        if overall >= 80:
            level = RiskLevel.LOW
        elif overall >= 60:
            level = RiskLevel.MEDIUM
        elif overall >= 40:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.CRITICAL

        return RiskFactor(
            category="财务风险",
            factor_name="财务健康度",
            risk_level=level,
            score=overall,
            description=f"财务综合评分 {overall} 分",
            suggestions=[
                "关注现金流状况",
                "优化资产负债结构",
                "提升盈利能力"]
            if level.priority >= 3 else []
        )

    def assess_judicial_risk(self, judicial_info: dict) -> RiskFactor:
        """评估司法风险"""
        cases = judicial_info.get("court_cases", [])
        penalties = judicial_info.get("administrative_penalties", [])
        dishonest = judicial_info.get("dishonest_records", [])

        risk_score = 100

        # 诉讼扣分
        for case in cases:
            if case.get("is_defendant"):
                risk_score -= 15
            if case.get("amount", 0) > 1000000:
                risk_score -= 10

        # 行政处罚扣分
        for penalty in penalties:
            risk_score -= 10

        # 失信记录扣分
        risk_score -= len(dishonest) * 30

        risk_score = max(0, risk_score)

        if risk_score >= 80:
            level = RiskLevel.LOW
        elif risk_score >= 60:
            level = RiskLevel.MEDIUM
        elif risk_score >= 40:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.CRITICAL

        return RiskFactor(
            category="司法风险",
            factor_name="涉诉与处罚",
            risk_level=level,
            score=risk_score,
            description=f"涉及 {len(cases)} 起诉讼，{len(penalties)} 项处罚",
            suggestions=["核实诉讼进展", "评估处罚影响"] if level.priority >= 3 else []
        )

    def assess_opinion_risk(self, opinion_info: dict) -> RiskFactor:
        """评估舆情风险"""
        articles = opinion_info.get("news_articles", [])
        keywords = opinion_info.get("risk_keywords", [])

        # 分析情感倾向
        negative_count = sum(1 for a in articles if a.get("sentiment") == "negative")
        total = len(articles) if articles else 1

        risk_score = 100 - (negative_count / total * 50)

        # 风险关键词扣分
        high_risk_keywords = ["违约", "破产", "跑路", "查封", "冻结", "失信"]
        for kw in keywords:
            if kw in high_risk_keywords:
                risk_score -= 20

        risk_score = max(0, risk_score)

        if risk_score >= 80:
            level = RiskLevel.LOW
        elif risk_score >= 60:
            level = RiskLevel.MEDIUM
        elif risk_score >= 40:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.CRITICAL

        return RiskFactor(
            category="舆情风险",
            factor_name="媒体舆情",
            risk_level=level,
            score=risk_score,
            description=f"负面报道 {negative_count} 条，风险关键词 {len(keywords)} 个",
            suggestions=["加强舆情监控", "准备危机公关预案"] if level.priority >= 3 else []
        )

    def assess_industry_risk(self, industry_info: dict) -> RiskFactor:
        """评估行业风险"""
        risk_level_str = industry_info.get("risk_level", "中")

        level_map = {
            "低": RiskLevel.LOW,
            "中": RiskLevel.MEDIUM,
            "高": RiskLevel.HIGH
        }
        level = level_map.get(risk_level_str, RiskLevel.MEDIUM)

        score_map = {
            "低": 85,
            "中": 65,
            "高": 35
        }
        score = score_map.get(risk_level_str, 65)

        return RiskFactor(
            category="行业风险",
            factor_name="行业系统性风险",
            risk_level=level,
            score=score,
            description=f"行业风险等级：{risk_level_str}",
            suggestions=["关注行业政策变化", "分散行业集中度"] if level.priority >= 3 else []
        )

    def comprehensive_assessment(self, financial_scores: dict,
                                  judicial_info: dict,
                                  opinion_info: dict,
                                  industry_info: dict) -> RiskAssessment:
        """综合风险评估"""
        self.risk_factors = [
            self.assess_financial_risk(financial_scores),
            self.assess_judicial_risk(judicial_info),
            self.assess_opinion_risk(opinion_info),
            self.assess_industry_risk(industry_info)
        ]

        # 计算综合得分（加权平均）
        weights = {
            "财务风险": 0.35,
            "司法风险": 0.25,
            "舆情风险": 0.20,
            "行业风险": 0.20
        }

        overall_score = sum(
            f.score * weights.get(f.category, 0.25)
            for f in self.risk_factors
        )

        # 确定综合风险等级
        if overall_score >= 80:
            overall_risk = RiskLevel.LOW
        elif overall_score >= 60:
            overall_risk = RiskLevel.MEDIUM
        elif overall_score >= 40:
            overall_risk = RiskLevel.HIGH
        else:
            overall_risk = RiskLevel.CRITICAL

        # 提取关键预警
        key_warnings = [
            f"{f.category}: {f.description}"
            for f in self.risk_factors
            if f.risk_level.priority >= 3
        ]

        # 汇总建议
        mitigation_suggestions = []
        for f in self.risk_factors:
            mitigation_suggestions.extend(f.suggestions)

        return RiskAssessment(
            overall_risk=overall_risk,
            overall_score=round(overall_score, 1),
            risk_factors=self.risk_factors,
            key_warnings=key_warnings,
            mitigation_suggestions=list(set(mitigation_suggestions))
        )
