#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尽调报告生成模块
生成标准化 Markdown 格式的尽职调查报告
"""

from datetime import datetime
from typing import Dict, List


class DueDiligenceReport:
    """尽调报告生成器"""

    def __init__(self):
        self.sections = []

    def generate_report(self, company_data: dict, industry_report: dict,
                        financial_scores: dict, risk_assessment: dict) -> str:
        """生成完整尽调报告"""
        report = []

        # 报告标题
        report.append(self._generate_header(company_data))

        # 一、企业基本信息
        report.append(self._generate_basic_info(company_data))

        # 二、行业分析
        report.append(self._generate_industry_analysis(industry_report))

        # 三、财务健康评分
        report.append(self._generate_financial_analysis(financial_scores))

        # 四、风险评估
        report.append(self._generate_risk_assessment(risk_assessment))

        # 五、综合结论与建议
        report.append(self._generate_conclusion(risk_assessment))

        return "\n\n".join(report)

    def _generate_header(self, company_data: dict) -> str:
        """生成报告头部"""
        basic = company_data.get("basic_info", {})
        # 处理 dataclass 对象
        if hasattr(basic, 'name'):
            name = basic.name
            credit_code = basic.credit_code
        else:
            name = basic.get("name", "未知")
            credit_code = basic.get("credit_code", "未知")
        return f"""# 📋 对公客户尽职调查报告

**企业名称**：{name}
**统一社会信用代码**：{credit_code}
**报告生成时间**：{datetime.now().strftime("%Y-%m-%d %H:%M")}
**报告版本**：v1.0

---
"""

    def _generate_basic_info(self, company_data: dict) -> str:
        """生成企业基本信息部分"""
        basic = company_data.get("basic_info", {})
        # 处理 dataclass 对象
        if hasattr(basic, 'name'):
            return f"""## 一、企业基本信息

| 项目 | 内容 |
|------|------|
| 企业名称 | {basic.name} |
| 法定代表人 | {basic.legal_representative} |
| 注册资本 | {basic.registered_capital:,.0f} 万元 |
| 成立日期 | {basic.establishment_date} |
| 经营状态 | {basic.business_status} |
| 企业类型 | {basic.enterprise_type} |
| 所属行业 | {basic.industry} |
| 注册地址 | {basic.registered_address} |
| 联系电话 | {basic.contact_phone} |
| 电子邮箱 | {basic.email} |

**经营范围**：{basic.business_scope}
"""

        return f"""## 一、企业基本信息

| 项目 | 内容 |
|------|------|
| 企业名称 | {basic.get("name", "-")} |
| 法定代表人 | {basic.get("legal_representative", "-")} |
| 注册资本 | {basic.get("registered_capital", 0):,.0f} 万元 |
| 成立日期 | {basic.get("establishment_date", "-")} |
| 经营状态 | {basic.get("business_status", "-")} |
| 企业类型 | {basic.get("enterprise_type", "-")} |
| 所属行业 | {basic.get("industry", "-")} |
| 注册地址 | {basic.get("registered_address", "-")} |
| 联系电话 | {basic.get("contact_phone", "-")} |
| 电子邮箱 | {basic.get("email", "-")} |

**经营范围**：{basic.get("business_scope", "-")}
"""

    def _generate_industry_analysis(self, industry_report: dict) -> str:
        """生成行业分析部分"""
        overview = industry_report.get("industry_overview", {})
        position = industry_report.get("company_position", {})

        # 处理 dataclass 对象
        if hasattr(overview, 'name'):
            trend_label = overview.trend.value if hasattr(overview.trend, 'value') else str(overview.trend)
            return f"""## 二、行业分析

### 2.1 行业概况

| 指标 | 数值 |
|------|------|
| 行业名称 | {overview.name} |
| 行业代码 | {overview.code} |
| 发展趋势 | {trend_label} |
| 年增长率 | {overview.growth_rate}% |
| 市场规模 | {overview.market_size:,.0f} 亿元 |
| 政策支持 | {overview.policy_support} |
| 行业风险 | {overview.risk_level} |

### 2.2 企业行业地位

| 指标 | 数值 |
|------|------|
| 市场排名 | 第 {position.market_rank} 位 |
| 市场份额 | {position.market_share}% |

**竞争优势**：
{chr(10).join([f"- {adv}" for adv in position.competitive_advantage])}

**风险因素**：
{chr(10).join([f"- {risk}" for risk in position.risk_factors])}

**发展机遇**：
{chr(10).join([f"- {opp}" for opp in position.opportunities])}
"""

        return f"""## 二、行业分析

### 2.1 行业概况

| 指标 | 数值 |
|------|------|
| 行业名称 | {overview.get("name", "-")} |
| 行业代码 | {overview.get("code", "-")} |
| 发展趋势 | {trend_label} |
| 年增长率 | {overview.get("growth_rate", 0)}% |
| 市场规模 | {overview.get("market_size", 0):,.0f} 亿元 |
| 政策支持 | {overview.get("policy_support", "-")} |
| 行业风险 | {overview.get("risk_level", "-")} |

### 2.2 企业行业地位

| 指标 | 数值 |
|------|------|
| 市场排名 | 第 {position.get("market_rank", "-")} 位 |
| 市场份额 | {position.get("market_share", 0)}% |

**竞争优势**：
{chr(10).join([f"- {adv}" for adv in position.get("competitive_advantage", [])])}

**风险因素**：
{chr(10).join([f"- {risk}" for risk in position.get("risk_factors", [])])}

**发展机遇**：
{chr(10).join([f"- {opp}" for opp in position.get("opportunities", [])])}
"""

    def _generate_financial_analysis(self, financial_scores: dict) -> str:
        """生成财务分析部分"""
        lines = ["## 三、财务健康评分"]
        lines.append("")
        lines.append("| 维度 | 评分 | 等级 |")
        lines.append("|------|------|------|")

        dimensions = ["偿债能力", "盈利能力", "运营能力", "成长能力", "综合评分"]
        for dim in dimensions:
            if dim in financial_scores:
                score_data = financial_scores[dim]
                lines.append(f"| {dim} | {score_data.get('score', 0)} | {score_data.get('emoji', '')} {score_data.get('level', '-')} |")

        return "\n".join(lines)

    def _generate_risk_assessment(self, risk_assessment: dict) -> str:
        """生成风险评估部分"""
        overall = risk_assessment.get("overall_risk", {})
        factors = risk_assessment.get("risk_factors", [])

        lines = ["## 四、风险评估"]
        lines.append("")
        lines.append(f"**综合风险等级**：{overall.get('emoji', '')} {overall.get('label', '-')} ({risk_assessment.get('overall_score', 0)} 分)")
        lines.append("")
        lines.append("### 4.1 风险因子明细")
        lines.append("")
        lines.append("| 风险类别 | 风险因子 | 等级 | 评分 |")
        lines.append("|----------|----------|------|------|")

        for factor in factors:
            risk_level = factor.get("risk_level", {})
            lines.append(f"| {factor.get('category', '-')} | {factor.get('factor_name', '-')} | {risk_level.get('emoji', '')} {risk_level.get('label', '-')} | {factor.get('score', 0)} |")

        # 关键预警
        warnings = risk_assessment.get("key_warnings", [])
        if warnings:
            lines.append("")
            lines.append("### 4.2 ⚠️ 关键预警")
            lines.append("")
            for warning in warnings:
                lines.append(f"- 🔴 {warning}")

        return "\n".join(lines)

    def _generate_conclusion(self, risk_assessment: dict) -> str:
        """生成结论与建议"""
        overall = risk_assessment.get("overall_risk", {})
        suggestions = risk_assessment.get("mitigation_suggestions", [])

        risk_label = overall.get("label", "未知")

        conclusion_map = {
            "低风险": "该企业整体风险可控，财务状况良好，建议正常开展业务合作。",
            "中风险": "该企业存在一定风险因素，建议加强贷后管理，定期跟踪关键指标。",
            "高风险": "该企业风险较高，建议审慎介入，要求提供增信措施或降低授信额度。",
            "极高风险": "该企业风险极高，建议暂缓合作，待风险因素消除后再评估。"
        }

        conclusion = conclusion_map.get(risk_label, "请结合具体情况综合判断。")

        lines = ["## 五、综合结论与建议"]
        lines.append("")
        lines.append(f"**风险评级**：{overall.get('emoji', '')} {risk_label} ({risk_assessment.get('overall_score', 0)} 分)")
        lines.append("")
        lines.append(f"**综合结论**：{conclusion}")
        lines.append("")

        if suggestions:
            lines.append("**风控建议**：")
            lines.append("")
            for i, suggestion in enumerate(suggestions, 1):
                lines.append(f"{i}. {suggestion}")

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*本报告基于公开信息和模拟数据生成，仅供参考，不构成投资决策依据。*")

        return "\n".join(lines)
