#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务健康评分模块
偿债能力、盈利能力、运营能力、成长能力四维评分
"""

from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum


class ScoreLevel(Enum):
    """评分等级"""
    EXCELLENT = (90, 100, "优秀", "🟢")
    GOOD = (75, 89, "良好", "🟢")
    NORMAL = (60, 74, "一般", "🟡")
    WARNING = (40, 59, "关注", "🟠")
    DANGER = (0, 39, "危险", "🔴")

    def __init__(self, min_score, max_score, label, emoji):
        self.min_score = min_score
        self.max_score = max_score
        self.label = label
        self.emoji = emoji

    @classmethod
    def get_level(cls, score: float) -> "ScoreLevel":
        for level in cls:
            if level.min_score <= score <= level.max_score:
                return level
        return cls.DANGER


@dataclass
class FinancialScores:
    """财务评分结果"""
    solvency_score: float      # 偿债能力
    profitability_score: float # 盈利能力
    operation_score: float     # 运营能力
    growth_score: float        # 成长能力
    overall_score: float       # 综合评分

    def to_dict(self) -> Dict:
        return {
            "偿债能力": {
                "score": round(self.solvency_score, 1),
                "level": ScoreLevel.get_level(self.solvency_score).label,
                "emoji": ScoreLevel.get_level(self.solvency_score).emoji
            },
            "盈利能力": {
                "score": round(self.profitability_score, 1),
                "level": ScoreLevel.get_level(self.profitability_score).label,
                "emoji": ScoreLevel.get_level(self.profitability_score).emoji
            },
            "运营能力": {
                "score": round(self.operation_score, 1),
                "level": ScoreLevel.get_level(self.operation_score).label,
                "emoji": ScoreLevel.get_level(self.operation_score).emoji
            },
            "成长能力": {
                "score": round(self.growth_score, 1),
                "level": ScoreLevel.get_level(self.growth_score).label,
                "emoji": ScoreLevel.get_level(self.growth_score).emoji
            },
            "综合评分": {
                "score": round(self.overall_score, 1),
                "level": ScoreLevel.get_level(self.overall_score).label,
                "emoji": ScoreLevel.get_level(self.overall_score).emoji
            }
        }


class FinancialHealthScorer:
    """财务健康评分器"""

    def __init__(self):
        self.scores = None

    def calculate_solvency(self, total_assets: float, total_liabilities: float,
                           current_assets: float, current_liabilities: float) -> float:
        """偿债能力评分"""
        if total_assets <= 0 or total_liabilities < 0:
            return 0.0

        # 资产负债率
        debt_ratio = total_liabilities / total_assets if total_assets > 0 else 1.0

        # 流动比率
        current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0

        # 评分逻辑
        score = 100.0

        # 资产负债率扣分 (理想 < 60%)
        if debt_ratio > 0.7:
            score -= 30
        elif debt_ratio > 0.6:
            score -= 15
        elif debt_ratio > 0.5:
            score -= 5

        # 流动比率加分 (理想 1.5-2.0)
        if current_ratio >= 1.5:
            score += 10
        elif current_ratio >= 1.0:
            score += 5
        elif current_ratio < 0.8:
            score -= 20

        return max(0, min(100, score))

    def calculate_profitability(self, revenue: float, net_profit: float,
                                 total_assets: float, total_equity: float) -> float:
        """盈利能力评分"""
        if revenue <= 0:
            return 0.0

        # 净利润率
        profit_margin = net_profit / revenue

        # ROA
        roa = net_profit / total_assets if total_assets > 0 else 0

        # ROE
        roe = net_profit / total_equity if total_equity > 0 else 0

        score = 60.0  # 基础分

        # 净利润率评分
        if profit_margin > 0.2:
            score += 25
        elif profit_margin > 0.1:
            score += 15
        elif profit_margin > 0.05:
            score += 5
        elif profit_margin < 0:
            score -= 30

        # ROA评分
        if roa > 0.1:
            score += 10
        elif roa > 0.05:
            score += 5
        elif roa < 0:
            score -= 10

        # ROE评分
        if roe > 0.15:
            score += 5
        elif roe < 0:
            score -= 5

        return max(0, min(100, score))

    def calculate_operation(self, revenue: float, accounts_receivable: float,
                            inventory: float, current_assets: float) -> float:
        """运营能力评分"""
        if revenue <= 0:
            return 0.0

        score = 70.0

        # 应收账款周转率
        ar_turnover = revenue / accounts_receivable if accounts_receivable > 0 else 0

        # 存货周转率 (简化)
        inventory_turnover = revenue / inventory if inventory > 0 else 0

        # 总资产周转率 (简化)
        asset_turnover = revenue / current_assets if current_assets > 0 else 0

        if ar_turnover > 10:
            score += 15
        elif ar_turnover > 5:
            score += 10
        elif ar_turnover < 2:
            score -= 15

        if inventory_turnover > 8:
            score += 10
        elif inventory_turnover < 3:
            score -= 10

        if asset_turnover > 1.5:
            score += 5
        elif asset_turnover < 0.5:
            score -= 5

        return max(0, min(100, score))

    def calculate_growth(self, current_revenue: float, previous_revenue: float = 0,
                         current_profit: float = 0, previous_profit: float = 0) -> float:
        """成长能力评分"""
        score = 60.0

        # 营收增长率
        if previous_revenue > 0:
            revenue_growth = (current_revenue - previous_revenue) / previous_revenue
            if revenue_growth > 0.5:
                score += 30
            elif revenue_growth > 0.3:
                score += 20
            elif revenue_growth > 0.1:
                score += 10
            elif revenue_growth < 0:
                score -= 20
        else:
            score += 10  # 新公司基础分

        # 利润增长率
        if previous_profit > 0 and current_profit > 0:
            profit_growth = (current_profit - previous_profit) / previous_profit
            if profit_growth > 0.3:
                score += 10
            elif profit_growth < 0:
                score -= 10

        return max(0, min(100, score))

    def comprehensive_score(self, financial_data: dict) -> FinancialScores:
        """计算综合评分"""
        fd = financial_data

        solvency = self.calculate_solvency(
            fd.get("total_assets", 0),
            fd.get("total_liabilities", 0),
            fd.get("current_assets", 0),
            fd.get("current_liabilities", 0)
        )

        total_equity = fd.get("total_assets", 0) - fd.get("total_liabilities", 0)
        profitability = self.calculate_profitability(
            fd.get("revenue", 0),
            fd.get("net_profit", 0),
            fd.get("total_assets", 0),
            total_equity
        )

        operation = self.calculate_operation(
            fd.get("revenue", 0),
            fd.get("accounts_receivable", 0),
            fd.get("inventory", 0),
            fd.get("current_assets", 0)
        )

        growth = self.calculate_growth(
            fd.get("revenue", 0),
            fd.get("previous_revenue", 0),
            fd.get("net_profit", 0),
            fd.get("previous_profit", 0)
        )

        # 加权综合评分
        overall = (solvency * 0.3 + profitability * 0.3 +
                   operation * 0.2 + growth * 0.2)

        self.scores = FinancialScores(
            solvency_score=solvency,
            profitability_score=profitability,
            operation_score=operation,
            growth_score=growth,
            overall_score=overall
        )

        return self.scores
