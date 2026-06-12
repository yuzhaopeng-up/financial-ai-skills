"""
Tax Planning Engine - 企业税务筹划引擎
输入企业信息，输出税务筹划方案（主要税种+节税空间+风险点+筹划建议）
"""

import json
import re
from typing import Dict, List, Optional, Any


class TaxPlanningEngine:
    """企业税务筹划引擎"""

    # 2024年最新政策阈值
    SMALL_MICRO_THRESHOLD = 3000000  # 年应纳税所得额≤300万
    SMALL_MICRO_EMPLOYEE_LIMIT = 300
    SMALL_MICRO_ASSET_LIMIT = 50000000

    # 税率配置
    STANDARD_RATE = 0.25       # 标准企业所得税率 25%
    HIGH_TECH_RATE = 0.15      # 高新企业优惠税率 15%
    SMALL_MICRO_RATE_TIER1 = 0.025  # 小微100万以下实际税负 2.5%
    SMALL_MICRO_RATE_TIER2 = 0.05   # 小微100-300万实际税负 5%

    RD_EXTRA_DEDUCTION_RATE = 1.2    # 研发加计扣除比例 120%

    def __init__(self):
        self.name = "TaxPlanningEngine"
        self.version = "1.0.0"

    def generate(
        self,
        company_name: str = "",
        industry: str = "一般",
        annual_revenue: float = 0,
        rd_expense: float = 0,
        employee_count: int = 0,
        total_assets: float = 0,
        is_high_tech: bool = False,
        is_small_micro: bool = False,
        estimated_profit_rate: float = 0.15,
        vat_type: str = "一般纳税人",
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成税务筹划方案

        Args:
            company_name: 企业名称
            industry: 行业（科技/制造/服务/一般）
            annual_revenue: 年营收（元）
            rd_expense: 年研发投入（元）
            employee_count: 员工人数
            total_assets: 资产总额（元）
            is_high_tech: 是否为高新技术企业
            is_small_micro: 是否为小型微利企业
            estimated_profit_rate: 预估利润率（默认15%）
            vat_type: 增值税纳税人类型（一般纳税人/小规模纳税人）

        Returns:
            Dict 包含: company_info, tax_types, savings_space, risk_points, suggestions
        """
        # 计算应纳税所得额
        estimated_profit = annual_revenue * estimated_profit_rate

        # 判断小微资格
        is_small_micro_eligible = (
            estimated_profit <= 3000000 and
            employee_count <= 300 and
            total_assets <= 50000000
        )

        # 计算研发加计扣除
        rd_deduction_extra = rd_expense * (self.RD_EXTRA_DEDUCTION_RATE - 1) if rd_expense > 0 else 0

        # 企业所得税分析
        et_analysis = self._analyze_enterprise_tax(
            estimated_profit, is_high_tech, is_small_micro_eligible, rd_deduction_extra
        )

        # 增值税分析
        vat_analysis = self._analyze_vat(annual_revenue, vat_type)

        # 附加税分析
        surtax_analysis = self._analyze_surtax(vat_analysis)

        # 综合节税空间
        savings = self._calculate_savings(
            et_analysis, vat_analysis, surtax_analysis, is_high_tech, is_small_micro_eligible
        )

        # 风险点识别
        risks = self._identify_risks(
            is_high_tech, is_small_micro_eligible, rd_expense, rd_deduction_extra
        )

        # 筹划建议
        suggestions = self._generate_suggestions(
            is_high_tech, is_small_micro_eligible, rd_expense, annual_revenue, industry
        )

        return {
            "company_info": {
                "name": company_name,
                "industry": industry,
                "annual_revenue": annual_revenue,
                "annual_revenue_str": self._format_currency(annual_revenue),
                "rd_expense": rd_expense,
                "rd_expense_str": self._format_currency(rd_expense),
                "employee_count": employee_count,
                "total_assets": total_assets,
                "is_high_tech": is_high_tech,
                "is_small_micro_eligible": is_small_micro_eligible,
                "estimated_profit": estimated_profit,
                "estimated_profit_str": self._format_currency(estimated_profit),
            },
            "tax_types": {
                "enterprise_tax": et_analysis,
                "vat": vat_analysis,
                "surtax": surtax_analysis,
            },
            "savings_space": savings,
            "risk_points": risks,
            "suggestions": suggestions,
            "summary": self._generate_summary(company_name, savings, et_analysis),
        }

    def _analyze_enterprise_tax(
        self,
        profit: float,
        is_high_tech: bool,
        is_small_micro: bool,
        rd_extra: float
    ) -> Dict[str, Any]:
        """分析企业所得税"""

        # 基准情况（无任何优惠）
        base_tax = profit * self.STANDARD_RATE
        base_rate = self.STANDARD_RATE

        # 研发加计扣除减少的应纳税所得额
        adjusted_profit = max(0, profit - rd_extra)

        if is_high_tech:
            # 高新技术企业
            effective_rate = self.HIGH_TECH_RATE
            scheme = "高新技术企业"
            # 如果高新+小微，优先小微（更优惠）
            if is_small_micro and adjusted_profit <= 3000000:
                effective_rate = self._get_small_micro_rate(adjusted_profit)
                scheme = "高新+小型微利企业（更优惠）"
            tax_amount = adjusted_profit * effective_rate
        elif is_small_micro:
            # 小型微利企业
            effective_rate = self._get_small_micro_rate(adjusted_profit)
            scheme = "小型微利企业"
            tax_amount = adjusted_profit * effective_rate
        else:
            # 标准25%
            effective_rate = base_rate
            tax_amount = adjusted_profit * base_rate
            scheme = "一般企业"

        savings_vs_base = base_tax - tax_amount
        savings_vs_base = max(0, savings_vs_base)

        return {
            "type": "企业所得税",
            "estimated_profit": profit,
            "after_rd_deduction": adjusted_profit,
            "rd_deduction_benefit": rd_extra,
            "applicable_scheme": scheme,
            "tax_rate": effective_rate,
            "tax_rate_display": f"{effective_rate*100:.1f}%",
            "estimated_tax": tax_amount,
            "estimated_tax_str": self._format_currency(tax_amount),
            "base_tax_without_benefits": base_tax,
            "base_tax_str": self._format_currency(base_tax),
            "savings_vs_base": savings_vs_base,
            "savings_vs_base_str": self._format_currency(savings_vs_base),
        }

    def _get_small_micro_rate(self, profit: float) -> float:
        """计算小微实际税率"""
        if profit <= 1000000:
            return self.SMALL_MICRO_RATE_TIER1  # 2.5%
        else:
            # 100万-300万部分：25%*20%=5%
            tier1_profit = 1000000
            tier2_profit = profit - tier1_profit
            tier1_tax = tier1_profit * self.SMALL_MICRO_RATE_TIER1
            tier2_tax = tier2_profit * self.SMALL_MICRO_RATE_TIER2
            return (tier1_tax + tier2_tax) / profit if profit > 0 else 0

    def _analyze_vat(self, revenue: float, vat_type: str) -> Dict[str, Any]:
        """分析增值税"""
        if vat_type == "小规模纳税人":
            # 月销售额≤10万免征增值税（季度30万）
            monthly_avg = revenue / 12
            tax_exempt = monthly_avg <= 100000
            vat_rate = 0.01  # 1%征收率
            vat_tax = revenue * vat_rate if not tax_exempt else 0
            scheme = "小规模纳税人（月销≤10万免征）" if tax_exempt else "小规模纳税人（1%征收率）"
        else:
            # 一般纳税人 6%
            vat_rate = 0.06
            # 进项税额抵扣，假设可抵扣50%
            effective_vat_rate = vat_rate * 0.5
            vat_tax = revenue * effective_vat_rate
            scheme = "一般纳税人（6%，进项抵扣50%）"

        return {
            "type": "增值税",
            "vat_type": vat_type,
            "applicable_scheme": scheme,
            "vat_rate": vat_rate,
            "estimated_tax": vat_tax,
            "estimated_tax_str": self._format_currency(vat_tax),
        }

    def _analyze_surtax(self, vat_analysis: Dict) -> Dict[str, Any]:
        """分析附加税（城建税+教育费附加+地方教育附加）"""
        vat_tax = vat_analysis.get("estimated_tax", 0)
        # 附加税税率：城建7%+教育3%+地方2%=12%
        surtax_rate = 0.12
        surtax_amount = vat_tax * surtax_rate

        return {
            "type": "增值税附加税",
            "tax_rate": surtax_rate,
            "tax_rate_display": "12%（城建7%+教育3%+地方2%）",
            "estimated_tax": surtax_amount,
            "estimated_tax_str": self._format_currency(surtax_amount),
        }

    def _calculate_savings(
        self,
        et_analysis: Dict,
        vat_analysis: Dict,
        surtax_analysis: Dict,
        is_high_tech: bool,
        is_small_micro: bool
    ) -> Dict[str, Any]:
        """计算综合节税空间"""
        et_savings = et_analysis.get("savings_vs_base", 0)
        rd_savings = et_analysis.get("rd_deduction_benefit", 0) * (is_small_micro or is_high_tech)

        # 增值税优惠节省（仅小规模）
        vat_base = vat_analysis.get("estimated_tax", 0)
        if "小规模" in vat_analysis.get("applicable_scheme", "") and "免征" in vat_analysis.get("applicable_scheme", ""):
            vat_savings = vat_base  # 全部节省
        else:
            vat_savings = 0

        total_savings = et_savings + rd_savings + vat_savings

        return {
            "enterprise_tax_savings": et_savings,
            "enterprise_tax_savings_str": self._format_currency(et_savings),
            "rd_deduction_savings": rd_savings,
            "rd_deduction_savings_str": self._format_currency(rd_savings),
            "vat_savings": vat_savings,
            "vat_savings_str": self._format_currency(vat_savings),
            "total_savings": total_savings,
            "total_savings_str": self._format_currency(total_savings),
            "savings_ratio": f"{(total_savings / (et_analysis.get("estimated_tax", 1) + 1)) * 100:.1f}%" if total_savings > 0 else "0%",
        }

    def _identify_risks(
        self,
        is_high_tech: bool,
        is_small_micro: bool,
        rd_expense: float,
        rd_extra: float
    ) -> List[Dict[str, str]]:
        """识别税务风险点"""
        risks = []

        if is_high_tech:
            risks.append({
                "level": "高",
                "category": "资格维持",
                "description": "高新资格需每年认定，研发投入比例需≥3%，知识产权需持续更新",
                "mitigation": "提前规划知识产权布局，确保研发费用占比符合要求"
            })
            risks.append({
                "level": "中",
                "category": "税会差异",
                "description": "研发费用加计扣除与会计准则存在差异，需规范归集",
                "mitigation": "建立研发费用辅助账，规范凭证管理"
            })

        if is_small_micro:
            risks.append({
                "level": "高",
                "category": "规模临界",
                "description": "年应纳税所得额超过300万将失去小微优惠，税率从5%跳升至25%",
                "mitigation": "关注应纳税所得额临界点，合理安排收入与成本"
            })
            risks.append({
                "level": "中",
                "category": "人员/资产限制",
                "description": "从业人数>300人或资产>5000万将失去小微资格",
                "mitigation": "监控员工人数和资产规模变化"
            })

        if rd_expense > 0:
            risks.append({
                "level": "中",
                "category": "研发费用归集",
                "description": "研发费用归集不规范可能被税务机关调整",
                "mitigation": "严格按照研发费用加计扣除政策归集，保留完整备查资料"
            })

        # 一般性风险
        risks.extend([
            {
                "level": "低",
                "category": "关联交易",
                "description": "关联企业间交易需符合独立交易原则",
                "mitigation": "关联交易定价应有商业合理性"
            },
            {
                "level": "低",
                "category": "发票管理",
                "description": "虚开发票风险，需确保业务真实性",
                "mitigation": "严格审核发票真实性，三流合一（合同、发票、资金）"
            }
        ])

        return risks

    def _generate_suggestions(
        self,
        is_high_tech: bool,
        is_small_micro: bool,
        rd_expense: float,
        annual_revenue: float,
        industry: str
    ) -> List[Dict[str, Any]]:
        """生成筹划建议"""
        suggestions = []

        if is_small_micro:
            suggestions.append({
                "priority": "高",
                "title": "确保小微优惠资格",
                "detail": "年应纳税所得额控制在300万以内，特别关注100万临界点（2.5% vs 5%实际税负）",
                "action": "建立应纳税所得额监控系统，提前预警"
            })
            suggestions.append({
                "priority": "高",
                "title": "合理规划收入确认时点",
                "detail": "在临界点附近时，可适当调整收入确认时间，平滑税负",
                "action": "与财务协商，合理安排合同执行和收入确认节奏"
            })

        if not is_high_tech and industry.lower() in ["科技", "技术", "软件"]:
            suggestions.append({
                "priority": "高",
                "title": "申请高新技术企业资格",
                "detail": f"年营收{self._format_currency(annual_revenue)}的科技企业，符合条件应积极申请高新资格，享受15%优惠税率",
                "action": "梳理知识产权、研发项目、研发人员，准备高新认定材料"
            })

        if rd_expense > 0:
            suggestions.append({
                "priority": "中",
                "title": "研发费用规范归集",
                "detail": "建立研发费用辅助账，分项目归集人员人工、直接投入、折旧摊销等费用",
                "action": "使用财务软件辅助核算，保留完整备查资料应对税务机关核查"
            })

        if annual_revenue >= 50000000:
            suggestions.append({
                "priority": "中",
                "title": "考虑区域性税收优惠",
                "detail": "部分国家级高新区、经济开发区有增值税、企业所得税返还政策",
                "action": "了解当地园区政策，评估迁移或设立分支机构的可行性"
            })

        if not is_small_micro and not is_high_tech:
            suggestions.append({
                "priority": "高",
                "title": "业务架构筹划",
                "detail": "考虑通过设立子公司分流业务，利用小微优惠降低整体税负",
                "action": "评估子公司设立的合规性和管理成本"
            })

        # 通用建议
        suggestions.append({
            "priority": "低",
            "title": "充分利用研发加计扣除",
            "detail": "制造业/科技型中小企业研发费用加计扣除比例120%，是重要的节税工具",
            "action": "确保研发项目立项、过程管理、结题验收资料完整"
        })

        return suggestions

    def _generate_summary(
        self,
        company_name: str,
        savings: Dict,
        et_analysis: Dict
    ) -> str:
        """生成税务筹划摘要"""
        name = company_name or "该企业"
        total = savings.get("total_savings", 0)
        et_savings = savings.get("enterprise_tax_savings", 0)
        rd_savings = savings.get("rd_deduction_savings", 0)

        summary = f"【税务筹划摘要 - {name}】\n\n"
        summary += f"▶ 综合节税空间：约 {savings.get('total_savings_str', '0元')}（企业所得税节省 {savings.get('enterprise_tax_savings_str', '0元')}）\n"
        summary += f"▶ 研发加计扣除节省：约 {savings.get('rd_deduction_savings_str', '0元')}\n"
        summary += f"▶ 适用税优方案：{et_analysis.get('applicable_scheme', '一般企业')}\n"
        summary += f"▶ 优惠税率：{et_analysis.get('tax_rate_display', '25%')}\n"
        summary += f"▶ 预估企业所得税：{et_analysis.get('estimated_tax_str', '0元')}\n"

        if total > 0:
            summary += f"\n💡 通过合理税务筹划，{name}可有效降低税负，建议优先确保小微/高新资格，规范研发费用归集。"

        return summary

    def _format_currency(self, amount: float) -> str:
        """格式化货币显示"""
        if amount >= 100000000:
            return f"{amount/100000000:.2f}亿元"
        elif amount >= 10000:
            return f"{amount/10000:.2f}万元"
        else:
            return f"{amount:.2f}元"

    def format_json(self, result: Dict) -> str:
        """格式化输出为JSON"""
        return json.dumps(result, ensure_ascii=False, indent=2)

    def format_text(self, result: Dict) -> str:
        """格式化输出为文本"""
        lines = []
        company_info = result["company_info"]
        tax_types = result["tax_types"]
        savings = result["savings_space"]
        risks = result["risk_points"]
        suggestions = result["suggestions"]

        lines.append("=" * 60)
        lines.append(f"       企业税务筹划分析报告")
        lines.append("=" * 60)
        lines.append(f"\n【企业基本信息】")
        lines.append(f"  企业名称：{company_info['name'] or '未提供'}")
        lines.append(f"  所属行业：{company_info['industry']}")
        lines.append(f"  年营业收入：{company_info['annual_revenue_str']}")
        lines.append(f"  研发投入：{company_info['rd_expense_str']}")
        lines.append(f"  员工人数：{company_info['employee_count']}人")
        lines.append(f"  资产总额：{self._format_currency(company_info['total_assets'])}")
        lines.append(f"  高新技术企业：{'是' if company_info['is_high_tech'] else '否'}")
        lines.append(f"  小型微利企业资格：{'符合' if company_info['is_small_micro_eligible'] else '不符合'}")
        lines.append(f"  预估应纳税所得额：{company_info['estimated_profit_str']}（利润率15%估算）")

        lines.append(f"\n【主要税种分析】")
        et = tax_types["enterprise_tax"]
        lines.append(f"\n  ▶ 企业所得税")
        lines.append(f"    适用方案：{et['applicable_scheme']}")
        lines.append(f"    优惠税率：{et['tax_rate_display']}")
        lines.append(f"    研发加计扣除节省：{self._format_currency(et['rd_deduction_benefit'])}")
        lines.append(f"    预估企业所得税：{et['estimated_tax_str']}")
        lines.append(f"    vs一般企业节省：{et['savings_vs_base_str']}")

        vat = tax_types["vat"]
        lines.append(f"\n  ▶ 增值税")
        lines.append(f"    纳税人类型：{vat['vat_type']}")
        lines.append(f"    适用政策：{vat['applicable_scheme']}")
        lines.append(f"    预估增值税：{vat['estimated_tax_str']}")

        st = tax_types["surtax"]
        lines.append(f"\n  ▶ 附加税（城建+教育+地方教育）")
        lines.append(f"    税率：{st['tax_rate_display']}")
        lines.append(f"    预估附加税：{st['estimated_tax_str']}")

        lines.append(f"\n【节税空间汇总】")
        lines.append(f"  企业所得税节省：{savings['enterprise_tax_savings_str']}")
        lines.append(f"  研发加计扣除节省：{savings['rd_deduction_savings_str']}")
        lines.append(f"  增值税节省：{savings['vat_savings_str']}")
        lines.append(f"  ─────────────────")
        lines.append(f"  💰 综合节税空间：{savings['total_savings_str']}")

        lines.append(f"\n【风险点提示】")
        for i, risk in enumerate(risks, 1):
            lines.append(f"  {i}. [{risk['level']}级] {risk['category']}：{risk['description']}")
            lines.append(f"     → 应对：{risk['mitigation']}")

        lines.append(f"\n【筹划建议】")
        for i, s in enumerate(suggestions, 1):
            lines.append(f"  {i}. 【{s['priority']}优先级】{s['title']}")
            lines.append(f"     {s['detail']}")
            lines.append(f"     ▶ 行动：{s['action']}")

        lines.append(f"\n{'=' * 60}")
        lines.append(result["summary"])
        lines.append("=" * 60)

        return "\n".join(lines)


def parse_input_text(text: str) -> Dict:
    """从自然语言解析税务筹划输入参数"""
    result = {}

    # 提取公司名称
    name_match = re.search(r'公司|企业|集团', text)
    if name_match:
        result['company_name'] = re.search(r'([^多余多余\s,，,]{2,10})(?:公司|企业|集团)', text)
        if result.get('company_name'):
            result['company_name'] = result['company_name'].group(1) + '公司'
        else:
            result['company_name'] = '某企业'
    else:
        result['company_name'] = '某企业'

    # 提取营收
    revenue_patterns = [
        r'年?营?收?[:：\s]*(\d+(?:\.\d+)?)\s*(?:亿|万元?|元)',
        r'营?收?[:：\s]*(\d+(?:\.\d+)?)\s*(?:亿|万元?|元)',
        r'年?营?业?收?入?[:：\s]*(\d+(?:\.\d+)?)\s*(?:亿|万元?|元)',
    ]
    for pattern in revenue_patterns:
        match = re.search(pattern, text)
        if match:
            amount = float(match.group(1))
            if '亿' in match.group(0):
                result['annual_revenue'] = amount * 100000000
            elif '万' in match.group(0):
                result['annual_revenue'] = amount * 10000
            else:
                result['annual_revenue'] = amount
            break

    # 提取研发投入
    rd_patterns = [
        r'研发?投?入?[:：\s]*(\d+(?:\.\d+)?)\s*(?:亿|万元?|元)',
        r'研发?费?用?[:：\s]*(\d+(?:\.\d+)?)\s*(?:亿|万元?|元)',
    ]
    for pattern in rd_patterns:
        match = re.search(pattern, text)
        if match:
            amount = float(match.group(1))
            if '亿' in match.group(0):
                result['rd_expense'] = amount * 100000000
            elif '万' in match.group(0):
                result['rd_expense'] = amount * 10000
            else:
                result['rd_expense'] = amount
            break

    # 行业判断
    if '制造' in text:
        result['industry'] = '制造'
    elif '科技' in text or '软件' in text or '互联' in text:
        result['industry'] = '科技'
    elif '服务' in text:
        result['industry'] = '服务'
    else:
        result['industry'] = '一般'

    # 是否高新
    result['is_high_tech'] = '高新' in text

    # 是否小微
    result['is_small_micro'] = '小微' in text or ('小' in text and '微' in text)

    # 员工人数
    emp_match = re.search(r'员?工?[:：\s]*(\d+)\s*(?:人|名)', text)
    if emp_match:
        result['employee_count'] = int(emp_match.group(1))
    else:
        result['employee_count'] = 50  # 默认50人

    # 资产总额
    asset_match = re.search(r'资产[:：\s]*(\d+(?:\.\d+)?)\s*(?:亿|万元?|元)', text)
    if asset_match:
        amount = float(asset_match.group(1))
        if '亿' in asset_match.group(0):
            result['total_assets'] = amount * 100000000
        elif '万' in asset_match.group(0):
            result['total_assets'] = amount * 10000
        else:
            result['total_assets'] = amount
    else:
        result['total_assets'] = result.get('annual_revenue', 50000000)

    return result


if __name__ == "__main__":
    # 测试
    engine = TaxPlanningEngine()
    params = parse_input_text("税务筹划 某科技公司 年营收5000万 研发投入300万")
    print("解析参数:", params)
    result = engine.generate(**params)
    print(engine.format_text(result))
