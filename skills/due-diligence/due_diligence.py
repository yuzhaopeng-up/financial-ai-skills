#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对公尽调主引擎
整合所有模块，提供一站式尽调服务
"""

from company_collector import CompanyDataCollector
from industry_research import IndustryResearchAnalyzer
from financial_scorer import FinancialHealthScorer
from risk_assessor import RiskAssessor
from report_generator import DueDiligenceReport


class DueDiligenceEngine:
    """尽职调查引擎"""

    def __init__(self):
        self.collector = CompanyDataCollector()
        self.industry_analyzer = IndustryResearchAnalyzer()
        self.financial_scorer = FinancialHealthScorer()
        self.risk_assessor = RiskAssessor()
        self.report_generator = DueDiligenceReport()

    def conduct_due_diligence(self, company_name: str, credit_code: str,
                               industry: str = "") -> dict:
        """执行完整尽职调查"""
        print(f"🔍 开始对 [{company_name}] 进行尽职调查...")

        # 1. 采集企业信息
        print("📊 步骤 1/5: 采集企业信息...")
        company_data = self.collector.full_collection(company_name, credit_code)

        # 获取行业（如果未指定）
        if not industry:
            industry = company_data["basic_info"].industry

        # 2. 行业研究
        print("📈 步骤 2/5: 行业研究分析...")
        financial_data = company_data["financial_data"]
        industry_report = self.industry_analyzer.generate_industry_report(
            industry, company_name, financial_data.revenue
        )

        # 3. 财务评分
        print("💰 步骤 3/5: 财务健康评分...")
        financial_scores = self.financial_scorer.comprehensive_score(
            {
                "total_assets": financial_data.total_assets,
                "total_liabilities": financial_data.total_liabilities,
                "revenue": financial_data.revenue,
                "net_profit": financial_data.net_profit,
                "current_assets": financial_data.current_assets,
                "current_liabilities": financial_data.current_liabilities,
                "inventory": financial_data.inventory,
                "accounts_receivable": financial_data.accounts_receivable
            }
        ).to_dict()

        # 4. 风险评估
        print("⚠️ 步骤 4/5: 综合风险评估...")
        judicial_info = company_data["judicial_info"]
        opinion_info = company_data["public_opinion"]
        industry_overview = industry_report["industry_overview"]

        # 转换为字典格式
        judicial_dict = {
            "court_cases": judicial_info.court_cases,
            "administrative_penalties": judicial_info.administrative_penalties,
            "dishonest_records": judicial_info.dishonest_records
        }
        opinion_dict = {
            "news_articles": opinion_info.news_articles,
            "risk_keywords": opinion_info.risk_keywords
        }
        industry_dict = {
            "risk_level": industry_overview.risk_level
        }

        risk_assessment = self.risk_assessor.comprehensive_assessment(
            financial_scores, judicial_dict, opinion_dict, industry_dict
        )

        # 转换为字典
        risk_dict = {
            "overall_risk": {
                "label": risk_assessment.overall_risk.label,
                "emoji": risk_assessment.overall_risk.emoji
            },
            "overall_score": risk_assessment.overall_score,
            "risk_factors": [
                {
                    "category": f.category,
                    "factor_name": f.factor_name,
                    "risk_level": {
                        "label": f.risk_level.label,
                        "emoji": f.risk_level.emoji
                    },
                    "score": f.score,
                    "description": f.description
                }
                for f in risk_assessment.risk_factors
            ],
            "key_warnings": risk_assessment.key_warnings,
            "mitigation_suggestions": risk_assessment.mitigation_suggestions
        }

        # 5. 生成报告
        print("📝 步骤 5/5: 生成尽调报告...")
        report_md = self.report_generator.generate_report(
            company_data, industry_report, financial_scores, risk_dict
        )

        print("✅ 尽职调查完成！")

        return {
            "company_data": company_data,
            "industry_report": industry_report,
            "financial_scores": financial_scores,
            "risk_assessment": risk_dict,
            "report_markdown": report_md
        }


if __name__ == "__main__":
    # 演示
    engine = DueDiligenceEngine()
    result = engine.conduct_due_diligence(
        company_name="示例科技有限公司",
        credit_code="91310000XXXXXXXXXX",
        industry="软件和信息技术服务业"
    )

    print("\n" + "=" * 60)
    print("📋 尽调报告预览")
    print("=" * 60)
    print(result["report_markdown"][:2000])
    print("\n... [报告已截断，完整内容请查看 report_markdown 字段] ...")
