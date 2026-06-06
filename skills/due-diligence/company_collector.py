#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业信息采集模块
模拟多源数据采集：工商、司法、舆情、财务
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class CompanyBasicInfo:
    """企业基本信息"""
    name: str
    credit_code: str
    legal_representative: str
    registered_capital: float  # 万元
    establishment_date: str
    business_status: str
    business_scope: str
    registered_address: str
    contact_phone: str
    email: str
    industry: str
    enterprise_type: str  # 有限责任公司/股份有限公司等


@dataclass
class JudicialInfo:
    """司法信息"""
    court_cases: List[Dict] = field(default_factory=list)
    dishonest_records: List[Dict] = field(default_factory=list)
    execution_records: List[Dict] = field(default_factory=list)
    administrative_penalties: List[Dict] = field(default_factory=list)


@dataclass
class PublicOpinion:
    """舆情信息"""
    news_articles: List[Dict] = field(default_factory=list)
    social_media_mentions: List[Dict] = field(default_factory=list)
    risk_keywords: List[str] = field(default_factory=list)


@dataclass
class FinancialData:
    """财务数据"""
    total_assets: float = 0.0
    total_liabilities: float = 0.0
    revenue: float = 0.0
    net_profit: float = 0.0
    operating_cash_flow: float = 0.0
    total_equity: float = 0.0
    current_assets: float = 0.0
    current_liabilities: float = 0.0
    inventory: float = 0.0
    accounts_receivable: float = 0.0
    year: int = 2025


class CompanyDataCollector:
    """企业数据采集器"""

    def __init__(self):
        self.collected_data = {}

    def collect_basic_info(self, company_name: str, credit_code: str) -> CompanyBasicInfo:
        """采集企业基本信息（模拟）"""
        # 模拟数据 - 实际应调用天眼查/企查查 API
        mock_data = {
            "示例科技有限公司": {
                "legal_representative": "张三",
                "registered_capital": 5000.0,
                "establishment_date": "2018-03-15",
                "business_status": "存续",
                "business_scope": "软件开发、技术咨询、技术服务",
                "registered_address": "上海市浦东新区张江高科技园区",
                "contact_phone": "021-12345678",
                "email": "contact@example.com",
                "industry": "软件和信息技术服务业",
                "enterprise_type": "有限责任公司"
            }
        }

        data = mock_data.get(company_name, mock_data["示例科技有限公司"])

        return CompanyBasicInfo(
            name=company_name,
            credit_code=credit_code,
            **data
        )

    def collect_judicial_info(self, company_name: str) -> JudicialInfo:
        """采集司法信息（模拟）"""
        # 模拟司法数据
        judicial = JudicialInfo()

        # 模拟诉讼案件
        judicial.court_cases = [
            {
                "case_no": "(2025)沪01民初123号",
                "case_type": "合同纠纷",
                "amount": 1500000,
                "status": "已判决",
                "date": "2025-01-15",
                "is_defendant": True
            }
        ]

        # 模拟行政处罚
        judicial.administrative_penalties = [
            {
                "penalty_no": "沪市监处罚〔2025〕456号",
                "reason": "广告违法",
                "amount": 50000,
                "date": "2025-02-20",
                "authority": "上海市市场监督管理局"
            }
        ]

        return judicial

    def collect_public_opinion(self, company_name: str) -> PublicOpinion:
        """采集舆情信息（模拟）"""
        opinion = PublicOpinion()

        opinion.news_articles = [
            {
                "title": f"{company_name} 完成新一轮融资",
                "source": "36氪",
                "date": "2025-05-20",
                "sentiment": "positive",
                "url": "https://36kr.com/xxx"
            },
            {
                "title": f"{company_name} 产品获行业认可",
                "source": "界面新闻",
                "date": "2025-04-15",
                "sentiment": "positive",
                "url": "https://jiemian.com/xxx"
            }
        ]

        opinion.risk_keywords = ["融资", "行业认可", "技术创新"]

        return opinion

    def collect_financial_data(self, company_name: str, year: int = 2025) -> FinancialData:
        """采集财务数据（模拟）"""
        mock_financial = {
            "示例科技有限公司": {
                2025: {
                    "total_assets": 15000.0,
                    "total_liabilities": 8000.0,
                    "revenue": 12000.0,
                    "net_profit": 1800.0,
                    "operating_cash_flow": 2200.0,
                    "current_assets": 9000.0,
                    "current_liabilities": 5000.0,
                    "inventory": 1500.0,
                    "accounts_receivable": 3000.0
                }
            }
        }

        data = mock_financial.get(company_name, {}).get(year, {})

        return FinancialData(
            total_assets=data.get("total_assets", 0),
            total_liabilities=data.get("total_liabilities", 0),
            revenue=data.get("revenue", 0),
            net_profit=data.get("net_profit", 0),
            operating_cash_flow=data.get("operating_cash_flow", 0),
            current_assets=data.get("current_assets", 0),
            current_liabilities=data.get("current_liabilities", 0),
            inventory=data.get("inventory", 0),
            accounts_receivable=data.get("accounts_receivable", 0),
            year=year
        )

    def full_collection(self, company_name: str, credit_code: str) -> Dict:
        """执行完整采集"""
        return {
            "basic_info": self.collect_basic_info(company_name, credit_code),
            "judicial_info": self.collect_judicial_info(company_name),
            "public_opinion": self.collect_public_opinion(company_name),
            "financial_data": self.collect_financial_data(company_name),
            "collection_time": datetime.now().isoformat()
        }
