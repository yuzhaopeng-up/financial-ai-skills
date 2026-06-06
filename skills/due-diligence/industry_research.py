#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行业研究分析模块
行业地位、竞争格局、发展趋势分析
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class IndustryTrend(Enum):
    """行业趋势"""
    RAPID_GROWTH = "高速增长"
    STEADY_GROWTH = "稳定增长"
    MATURE = "成熟稳定"
    DECLINE = "衰退调整"
    TRANSFORMATION = "转型期"


@dataclass
class IndustryInfo:
    """行业信息"""
    name: str
    code: str  # 国民经济行业分类代码
    trend: IndustryTrend
    growth_rate: float  # 年增长率
    market_size: float  # 市场规模（亿元）
    policy_support: str  # 政策支持度
    risk_level: str  # 行业风险等级


@dataclass
class CompetitorInfo:
    """竞争对手信息"""
    name: str
    market_share: float
    revenue: float
    advantage: str
    threat_level: str  # high/medium/low


@dataclass
class IndustryPosition:
    """行业地位评估"""
    market_rank: int
    market_share: float
    competitive_advantage: List[str]
    risk_factors: List[str]
    opportunities: List[str]


class IndustryResearchAnalyzer:
    """行业研究分析器"""

    # 行业数据库（模拟）
    INDUSTRY_DB = {
        "软件和信息技术服务业": {
            "code": "I65",
            "trend": IndustryTrend.RAPID_GROWTH,
            "growth_rate": 15.2,
            "market_size": 120000.0,
            "policy_support": "强",
            "risk_level": "中",
            "avg_profit_margin": 12.5,
            "avg_debt_ratio": 45.0
        },
        "制造业": {
            "code": "C35",
            "trend": IndustryTrend.STEADY_GROWTH,
            "growth_rate": 6.8,
            "market_size": 3500000.0,
            "policy_support": "中",
            "risk_level": "中",
            "avg_profit_margin": 8.2,
            "avg_debt_ratio": 55.0
        },
        "金融业": {
            "code": "J66",
            "trend": IndustryTrend.MATURE,
            "growth_rate": 5.5,
            "market_size": 450000.0,
            "policy_support": "强",
            "risk_level": "低",
            "avg_profit_margin": 25.0,
            "avg_debt_ratio": 85.0
        }
    }

    def __init__(self):
        self.analysis_result = {}

    def analyze_industry(self, industry_name: str) -> IndustryInfo:
        """分析行业整体情况"""
        data = self.INDUSTRY_DB.get(industry_name, self.INDUSTRY_DB["软件和信息技术服务业"])

        return IndustryInfo(
            name=industry_name,
            code=data["code"],
            trend=data["trend"],
            growth_rate=data["growth_rate"],
            market_size=data["market_size"],
            policy_support=data["policy_support"],
            risk_level=data["risk_level"]
        )

    def analyze_competitors(self, company_name: str, industry: str) -> List[CompetitorInfo]:
        """分析竞争格局"""
        # 模拟竞争对手数据
        competitors = [
            CompetitorInfo(
                name="行业龙头A公司",
                market_share=25.5,
                revenue=500000.0,
                advantage="品牌优势、渠道覆盖广",
                threat_level="high"
            ),
            CompetitorInfo(
                name="主要竞争对手B公司",
                market_share=15.2,
                revenue=300000.0,
                advantage="技术领先、研发能力强",
                threat_level="high"
            ),
            CompetitorInfo(
                name="新兴企业C公司",
                market_share=5.8,
                revenue=80000.0,
                advantage="创新模式、增长快",
                threat_level="medium"
            )
        ]

        return competitors

    def assess_industry_position(self, company_name: str, industry: str,
                                  company_revenue: float) -> IndustryPosition:
        """评估企业在行业中的地位"""
        industry_data = self.INDUSTRY_DB.get(industry, self.INDUSTRY_DB["软件和信息技术服务业"])
        market_size = industry_data["market_size"]

        # 计算市场份额
        market_share = (company_revenue / market_size) * 100 if market_size > 0 else 0

        # 模拟排名
        if market_share > 20:
            rank = 1
        elif market_share > 10:
            rank = 3
        elif market_share > 5:
            rank = 5
        else:
            rank = 10

        return IndustryPosition(
            market_rank=rank,
            market_share=round(market_share, 2),
            competitive_advantage=[
                "技术创新能力",
                "客户粘性高",
                "成本控制优势"
            ],
            risk_factors=[
                "行业竞争加剧",
                "技术迭代风险",
                "政策监管趋严"
            ],
            opportunities=[
                "数字化转型需求增长",
                "海外市场拓展",
                "产业链整合机会"
            ]
        )

    def generate_industry_report(self, industry: str, company_name: str,
                                  company_revenue: float) -> Dict:
        """生成行业研究报告"""
        return {
            "industry_overview": self.analyze_industry(industry),
            "competitive_landscape": self.analyze_competitors(company_name, industry),
            "company_position": self.assess_industry_position(
                company_name, industry, company_revenue
            ),
            "industry_benchmarks": {
                "avg_profit_margin": self.INDUSTRY_DB[industry]["avg_profit_margin"],
                "avg_debt_ratio": self.INDUSTRY_DB[industry]["avg_debt_ratio"]
            }
        }
