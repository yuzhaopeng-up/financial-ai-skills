# -*- coding: utf-8 -*-
"""
财报速读引擎 v1.0

核心能力:
- 财报关键指标提取
- 同比/环比分析
- 行业对比
- 风险信号扫描

协同: ArkClaw (长文本分析+报告生成) / KimiClaw (数据抓取)
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime


class ReportEngine:
    """财报速读引擎"""
    
    # 模拟财报数据库（演示用）
    MOCK_REPORTS = {
        "美的集团": {
            "year": 2025,
            "period": "年报",
            "revenue": 384700000000,  # 3847亿
            "revenue_yoy": 8.2,
            "net_profit": 33700000000,  # 337亿
            "net_profit_yoy": 12.5,
            "gross_margin": 26.8,
            "roe": 22.1,
            "debt_ratio": 58.3,
            "cash_flow": 45200000000,
            "rd_expense": 18500000000,
            "rd_ratio": 4.8,
            "eps": 4.85,
            "dividend": 2.20,
            "highlights": [
                "海外营收占比38%，同比下降3个百分点",
                "ToB业务营收增长25%，成为第二增长曲线",
                "研发投入185亿，占营收4.8%",
            ],
            "risks": [
                "汇率波动影响海外毛利率",
                "原材料价格波动风险",
                "房地产市场下行影响家电需求",
            ],
            "industry_rank": {
                "revenue": 1,
                "profit": 1,
                "roe": 2,
                "rd": 1,
            }
        },
        "招商银行": {
            "year": 2025,
            "period": "年报",
            "revenue": 331000000000,
            "revenue_yoy": 3.5,
            "net_profit": 14800000000,
            "net_profit_yoy": 5.2,
            "npl_ratio": 0.95,
            "provision_coverage": 450,
            "roe": 16.8,
            "core_capital": 13.5,
            "highlights": [
                "不良贷款率0.95%，资产质量行业最优",
                "财富管理AUM突破13万亿",
                "数字化转型投入增长30%",
            ],
            "risks": [
                "净息差持续收窄",
                "房地产贷款风险暴露",
                "零售信贷增速放缓",
            ],
            "industry_rank": {
                "revenue": 3,
                "profit": 2,
                "roe": 1,
                "asset_quality": 1,
            }
        }
    }
    
    def __init__(self):
        self.engine_name = "ReportEngine"
        self.version = "1.0.0"
    
    def analyze(
        self,
        company_name: str,
        year: Optional[int] = None,
        focus: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        财报分析主入口
        
        Args:
            company_name: 公司名称
            year: 年度（默认最新）
            focus: 关注重点（revenue/profit/risk/industry）
            
        Returns:
            财报分析结果
        """
        start_time = datetime.now()
        
        # 1. 查找公司财报
        report_data = None
        for key, data in self.MOCK_REPORTS.items():
            if key in company_name or company_name in key:
                report_data = data
                break
        
        if not report_data:
            # 生成演示数据
            report_data = self._generate_demo_data(company_name)
        
        # 2. 计算关键指标
        revenue = report_data["revenue"]
        profit = report_data["net_profit"]
        
        # 格式化大数字
        revenue_yi = revenue / 100000000
        profit_yi = profit / 100000000
        
        # 3. 构建分析结果
        result = {
            "success": True,
            "scenario": "financial_report",
            "company_name": company_name,
            "year": report_data.get("year", 2025),
            "period": report_data.get("period", "年报"),
            "summary": {
                "revenue": revenue_yi,
                "revenue_yoy": report_data.get("revenue_yoy", 0),
                "net_profit": profit_yi,
                "net_profit_yoy": report_data.get("net_profit_yoy", 0),
                "gross_margin": report_data.get("gross_margin"),
                "roe": report_data.get("roe"),
                "debt_ratio": report_data.get("debt_ratio"),
                "eps": report_data.get("eps"),
            },
            "highlights": report_data.get("highlights", []),
            "risks": report_data.get("risks", []),
            "industry_rank": report_data.get("industry_rank", {}),
            "timestamp": datetime.now().isoformat(),
            "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000)
        }
        
        # 4. 根据关注重点过滤
        if focus:
            result["focus"] = self._build_focus_section(focus, report_data)
        
        # 5. 生成速读结论
        result["conclusion"] = self._generate_conclusion(report_data)
        
        return result
    
    def compare(
        self,
        companies: List[str],
        metric: str = "revenue"
    ) -> Dict[str, Any]:
        """
        多公司财报对比
        
        Args:
            companies: 公司名称列表
            metric: 对比指标
            
        Returns:
            对比结果
        """
        results = []
        for company in companies:
            report = self.analyze(company)
            if report.get("success"):
                results.append({
                    "company": company,
                    "metric_value": report["summary"].get(metric, 0),
                    "data": report["summary"]
                })
        
        # 排序
        results.sort(key=lambda x: x["metric_value"], reverse=True)
        
        return {
            "success": True,
            "scenario": "report_compare",
            "metric": metric,
            "companies": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_demo_data(self, company_name: str) -> Dict[str, Any]:
        """生成演示用财报数据"""
        # 根据公司名称哈希生成稳定的数据
        hash_val = sum(ord(c) for c in company_name)
        
        revenue_base = 100 + (hash_val % 900)  # 100-1000亿
        profit_margin = 5 + (hash_val % 15)  # 5-20%
        profit_base = revenue_base * profit_margin / 100
        
        return {
            "year": 2025,
            "period": "年报",
            "revenue": revenue_base * 100000000,
            "revenue_yoy": round((hash_val % 20) - 5, 1),  # -5% ~ +15%
            "net_profit": profit_base * 100000000,
            "net_profit_yoy": round((hash_val % 30) - 10, 1),
            "gross_margin": 20 + (hash_val % 20),
            "roe": 10 + (hash_val % 15),
            "debt_ratio": 40 + (hash_val % 40),
            "eps": round(profit_base / 100, 2),
            "highlights": [
                f"{company_name}营收突破{revenue_base:.0f}亿元",
                "数字化转型成效显著",
                "核心业务保持稳定增长",
            ],
            "risks": [
                "市场竞争加剧",
                "原材料成本上升",
                "宏观经济不确定性",
            ],
            "industry_rank": {
                "revenue": (hash_val % 10) + 1,
                "profit": (hash_val % 10) + 1,
            }
        }
    
    def _build_focus_section(self, focus: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """构建关注重点分析"""
        if focus == "revenue":
            return {
                "title": "营收分析",
                "content": f"营收{data.get('revenue_yoy', 0):.1f}%增长，"
                          f"{'高于' if data.get('revenue_yoy', 0) > 5 else '低于'}行业平均"
            }
        elif focus == "profit":
            return {
                "title": "盈利分析",
                "content": f"净利润{data.get('net_profit_yoy', 0):.1f}%增长，"
                          f"ROE {data.get('roe', 0):.1f}%"
            }
        elif focus == "risk":
            return {
                "title": "风险扫描",
                "content": f"发现{len(data.get('risks', []))}项风险信号",
                "risks": data.get("risks", [])
            }
        elif focus == "industry":
            rank = data.get("industry_rank", {})
            return {
                "title": "行业地位",
                "content": f"行业排名: 营收第{rank.get('revenue', '-')}位",
                "rank": rank
            }
        return {}
    
    def _generate_conclusion(self, data: Dict[str, Any]) -> str:
        """生成速读结论"""
        revenue_yoy = data.get("revenue_yoy", 0)
        profit_yoy = data.get("net_profit_yoy", 0)
        roe = data.get("roe", 0)
        
        parts = []
        
        # 增长判断
        if revenue_yoy > 10 and profit_yoy > 10:
            parts.append("高速增长")
        elif revenue_yoy > 0 and profit_yoy > 0:
            parts.append("稳健增长")
        elif revenue_yoy > 0:
            parts.append("增收不增利")
        else:
            parts.append("业绩承压")
        
        # 盈利质量
        if roe > 15:
            parts.append("盈利能力强")
        elif roe > 10:
            parts.append("盈利能力良好")
        else:
            parts.append("盈利能力一般")
        
        # 风险
        risks = data.get("risks", [])
        if len(risks) >= 3:
            parts.append("需关注多项风险")
        elif risks:
            parts.append("存在部分风险")
        else:
            parts.append("风险可控")
        
        return "，".join(parts)
