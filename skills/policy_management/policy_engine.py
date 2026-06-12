"""
保单管理核心引擎
Policy Management Engine

提供保单检视、保障缺口分析、现金价值计算、保全建议等功能。
"""

import re
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class CoverageGapAnalysis:
    """保障缺口分析结果"""
    needed_life_cover: float       # 应有寿险保额
    current_life_cover: float      # 当前寿险保额
    life_gap: float                # 寿险缺口
    needed_critical_illness: float  # 应有重疾保额
    current_critical_illness: float # 当前重疾保额
    critical_gap: float           # 重疾缺口
    needed_medical_cover: float    # 应有医疗险保额
    current_medical_cover: float   # 当前医疗险保额
    medical_gap: float            # 医疗险缺口
    assessment: str                # 综合评估


@dataclass
class CashValueAnalysis:
    """现金价值分析"""
    current_cv: float              # 当前现金价值
    total_premium_paid: float      # 已缴保费总额
    surrender_rate: float          # 折算比例（退保率）
    projection_years: List[int]    # 未来年度
    projection_values: List[float] # 未来年度现金价值
    break_even_year: int           # 回本年度
    assessment: str                # 评估意见


@dataclass
class PolicySuggestion:
    """保全建议"""
    action: str          # 建议动作（加保/减保/转换/退保/垫交/到期处理）
    priority: str         # 优先级（高/中/低）
    target: str           # 目标险种
    amount: float         # 建议金额
    reason: str           # 建议理由
    detail: str           # 详细说明


@dataclass
class RenewalReminder:
    """续期提醒"""
    next_due_date: str           # 下次缴费日期
    next_due_amount: float       # 下次缴费金额
    payment_progress: str        # 缴费进度
    lapse_risk: str              # 失效风险
    days_until_due: int          # 距缴费日天数


@dataclass
class FamilyProtectionOverview:
    """家庭保障全景"""
    total_annual_premium: float      # 家庭年缴保费
    total_coverage: float           # 家庭总保额
    per_capita_coverage: float      # 人均保额
    coverage_ratio: str             # 保障充足率
    risk_exposure: List[Dict]       # 风险敞口
    gaps: List[Dict]                # 保障缺口
    heatmap: Dict[str, float]       # 保障热力图


class PolicyManagementEngine:
    """
    保单管理引擎
    
    输入客户保单信息（险种/保额/保费/缴费年限/已缴年限/当前现金价值），
    返回保单检视报告（保障缺口分析/保费合理性/现金价值走势）+ 
    保全建议（加保/减保/转换/退保）+ 续期提醒 + 家庭保障全景图
    """

    # 保障缺口计算参数
    INCOME_REPLACEMENT_YEARS = 10      # 收入替代年数
    DEBT_COVERAGE_RATIO = 1.0          # 负债覆盖比例
    CHILD_EDUCATION_PER_CHILD = 500000 # 每个孩子教育金预留
    ELDERLY_SUPPORT_ANNUAL = 60000     # 每位老人年赡养费
    CRITICAL_ILLNESS_EXPENSE = 300000  # 重疾治疗费用基准
    MEDICAL_ANNUAL_LIMIT = 1000000     # 医疗险年度限额基准

    # 现金价值计算参数
    ASSUMED_INTEREST_RATE = 0.035     # 假定年复利率 3.5%
    ANNUAL_EXPENSE_RATE = 0.03        # 附加费用率

    def __init__(self, interest_rate: float = 0.035):
        """
        初始化引擎
        
        Args:
            interest_rate: 假定年复利率（用于现金价值计算）
        """
        self.assumed_rate = interest_rate

    def generate_review(
        self,
        policies: List[Dict[str, Any]],
        total_annual_premium: float,
        years_paid: int,
        client_info: Optional[Dict[str, Any]] = None,
        current_cash_value: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        生成完整保单检视报告
        
        Args:
            policies: 保单列表，每项包含:
                - type: 险种类型（寿险/重疾/医疗/意外/年金）
                - sum_insured: 保额
                - annual_premium: 年缴保费
                - payment_years: 缴费年限（可选）
                - insured_term: 保险期间（可选）
            total_annual_premium: 年缴保费总额
            years_paid: 已缴年限
            client_info: 客户信息，包含:
                - annual_income: 年收入
                - total_debt: 总负债
                - family_size: 家庭人口
                - children_count: 子女数量
                - elderly_count: 需赡养老人数量
                - age: 年龄
            current_cash_value: 当前现金价值（如有）
        
        Returns:
            完整检视报告字典
        """
        # 解析客户信息
        ci = client_info or {}
        annual_income = ci.get("annual_income", 0)
        total_debt = ci.get("total_debt", 0)
        family_size = ci.get("family_size", 1)
        children_count = ci.get("children_count", 0)
        elderly_count = ci.get("elderly_count", 0)
        age = ci.get("age", 30)

        # 1. 保障缺口分析
        coverage_gap = self._analyze_coverage_gap(
            policies, annual_income, total_debt, family_size,
            children_count, elderly_count, age
        )

        # 2. 保费合理性分析
        premium_analysis = self._analyze_premium(annual_income, total_annual_premium, policies)

        # 3. 现金价值分析
        cash_value = self._analyze_cash_value(
            policies, years_paid, total_annual_premium, current_cash_value
        )

        # 4. 保全建议
        suggestions = self._generate_suggestions(
            policies, coverage_gap, cash_value, years_paid, annual_income
        )

        # 5. 续期提醒
        renewal = self._generate_renewal_reminder(years_paid, policies, total_annual_premium)

        # 6. 家庭保障全景（简化版：单客户）
        family_overview = self._generate_family_overview(
            policies, total_annual_premium, coverage_gap, ci
        )

        return {
            "coverage_gap": coverage_gap.__dict__,
            "premium_analysis": premium_analysis,
            "cash_value": cash_value.__dict__,
            "policy_suggestions": [s.__dict__ for s in suggestions],
            "renewal_reminder": renewal.__dict__,
            "family_overview": family_overview,
            "summary": self._generate_summary(coverage_gap, suggestions, renewal)
        }

    def _analyze_coverage_gap(
        self,
        policies: List[Dict],
        annual_income: float,
        total_debt: float,
        family_size: int,
        children_count: int,
        elderly_count: int,
        age: int
    ) -> CoverageGapAnalysis:
        """
        计算保障缺口
        
        使用双十原则 + 生命价值法综合计算
        """
        # 提取各险种当前保额
        current_life = 0
        current_critical = 0
        current_medical = 0
        current_accident = 0

        for p in policies:
            ptype = p.get("type", "")
            sum_insured = p.get("sum_insured", 0)
            if "寿险" in ptype or "定期寿险" in ptype or "终身寿险" in ptype:
                current_life += sum_insured
            elif "重疾" in ptype:
                current_critical += sum_insured
            elif "医疗" in ptype or "住院" in ptype:
                current_medical += sum_insured
            elif "意外" in ptype:
                current_accident += sum_insured

        # 计算应有保额（生命价值法）
        # 寿险应有保额 = 年收入 × 收入替代年数 + 负债 + 子女教育金 + 老人赡养费 - 现有储蓄
        years_to_retirement = max(0, 60 - age)
        needed_life = (
            annual_income * min(self.INCOME_REPLACEMENT_YEARS, years_to_retirement)
            + total_debt * self.DEBT_COVERAGE_RATIO
            + children_count * self.CHILD_EDUCATION_PER_CHILD
            + elderly_count * self.ELDERLY_SUPPORT_ANNUAL * 10  # 假设10年
        )

        # 重疾应有保额
        needed_critical = self.CRITICAL_ILLNESS_EXPENSE + annual_income * 1  # 1年收入补偿

        # 医疗险应有保额
        needed_medical = self.MEDICAL_ANNUAL_LIMIT

        # 计算缺口
        life_gap = max(0, needed_life - current_life)
        critical_gap = max(0, needed_critical - current_critical)
        medical_gap = max(0, needed_medical - current_medical)

        # 综合评估
        if life_gap == 0 and critical_gap == 0 and medical_gap == 0:
            assessment = "✅ 保障充足，各类风险均有覆盖"
        elif life_gap > 0 and critical_gap > 0:
            assessment = "⚠️ 保障存在较大缺口，建议优先加保寿险和重疾险"
        elif life_gap > 0:
            assessment = "⚠️ 寿险保障不足，建议加保"
        elif critical_gap > 0:
            assessment = "⚠️ 重疾保障不足，建议加保"
        else:
            assessment = "💡 基础保障基本覆盖，可考虑完善高端医疗保障"

        return CoverageGapAnalysis(
            needed_life_cover=round(needed_life, 0),
            current_life_cover=current_life,
            life_gap=round(life_gap, 0),
            needed_critical_illness=round(needed_critical, 0),
            current_critical_illness=current_critical,
            critical_gap=round(critical_gap, 0),
            needed_medical_cover=needed_medical,
            current_medical_cover=current_medical,
            medical_gap=medical_gap,
            assessment=assessment
        )

    def _analyze_premium(
        self,
        annual_income: float,
        total_annual_premium: float,
        policies: List[Dict]
    ) -> Dict[str, Any]:
        """
        分析保费合理性
        
        使用保费占年收入比例（双十原则）
        """
        ratio = (total_annual_premium / annual_income * 100) if annual_income > 0 else 0

        # 险种结构分析
        policy_types = {}
        for p in policies:
            ptype = p.get("type", "未知")
            premium = p.get("annual_premium", 0)
            policy_types[ptype] = policy_types.get(ptype, 0) + premium

        # 评估
        if ratio <= 10:
            premium_assessment = "✅ 保费占比合理，在年收入的10%以内"
        elif ratio <= 15:
            premium_assessment = "💡 保费占比略高，但尚可接受"
        elif ratio <= 20:
            premium_assessment = "⚠️ 保费占比较高，可能造成缴费压力"
        else:
            premium_assessment = "🚨 保费负担过重，建议优化保障结构"

        return {
            "total_annual_premium": total_annual_premium,
            "annual_income": annual_income,
            "premium_to_income_ratio": round(ratio, 2),
            "assessment": premium_assessment,
            "policy_type_breakdown": policy_types
        }

    def _analyze_cash_value(
        self,
        policies: List[Dict],
        years_paid: int,
        total_annual_premium: float,
        current_cv: Optional[float]
    ) -> CashValueAnalysis:
        """
        计算现金价值走势
        
        使用精算复利公式模拟现金价值增长
        """
        total_paid = total_annual_premium * years_paid

        # 如果有实际现金价值，以实际为准
        if current_cv is not None:
            cv = current_cv
        else:
            # 估算：简化假设现金价值按复利累积
            # 初期现金价值约为已缴保费的30-70%（具体看产品）
            # 这里用线性估算配合复利因子
            payment_year_rate = min(0.7, 0.3 + years_paid * 0.08)  # 每年增长8%
            cv = total_paid * payment_year_rate

        # 现金价值折算比例
        surrender_rate = (cv / total_paid * 100) if total_paid > 0 else 0

        # 预测未来现金价值（假设按复利3.5%增长）
        projection_years = list(range(years_paid + 1, years_paid + 11))
        projection_values = []
        future_cv = cv
        break_even_year = years_paid

        for yr in projection_years:
            future_cv = future_cv * (1 + self.assumed_rate)
            projection_values.append(round(future_cv, 0))
            if break_even_year == years_paid and future_cv >= total_paid:
                break_even_year = yr

        # 评估
        if surrender_rate >= 80:
            cv_assessment = "✅ 现金价值积累良好，退保损失较小"
        elif surrender_rate >= 50:
            cv_assessment = "💡 现金价值中等，如需退保会有一定损失"
        elif surrender_rate >= 20:
            cv_assessment = "⚠️ 现金价值较低，前期退保损失较大，建议谨慎处理"
        else:
            cv_assessment = "🚨 现金价值积累较少，如非必要不建议退保"

        return CashValueAnalysis(
            current_cv=round(cv, 0),
            total_premium_paid=round(total_paid, 0),
            surrender_rate=round(surrender_rate, 1),
            projection_years=projection_years,
            projection_values=projection_values,
            break_even_year=break_even_year,
            assessment=cv_assessment
        )

    def _generate_suggestions(
        self,
        policies: List[Dict],
        coverage_gap: CoverageGapAnalysis,
        cash_value: CashValueAnalysis,
        years_paid: int,
        annual_income: float
    ) -> List[PolicySuggestion]:
        """
        生成保全建议
        
        场景：加保、减保、险种转换、到期处理、自动垫交、退保
        """
        suggestions = []

        # 1. 加保建议
        if coverage_gap.life_gap > 0:
            suggestions.append(PolicySuggestion(
                action="加保",
                priority="高",
                target="寿险",
                amount=coverage_gap.life_gap,
                reason="寿险保障存在缺口",
                detail=f"建议增加 {coverage_gap.life_gap/10000:.1f} 万元寿险保额，"
                       f"可通过定期寿险以较低保费提升保障。"
            ))

        if coverage_gap.critical_gap > 0:
            suggestions.append(PolicySuggestion(
                action="加保",
                priority="高",
                target="重疾险",
                amount=coverage_gap.critical_gap,
                reason="重疾保障存在缺口",
                detail=f"建议增加 {coverage_gap.critical_gap/10000:.1f} 万元重疾保额，"
                       f"重疾治疗费用+收入补偿建议覆盖3-5年年收入。"
            ))

        # 2. 减保建议（如果保费负担过重）
        if years_paid >= 5 and cash_value.surrender_rate >= 50:
            suggestions.append(PolicySuggestion(
                action="减保",
                priority="中",
                target="部分保单",
                amount=cash_value.current_cv * 0.3,
                reason="如缴费压力较大，可考虑减保",
                detail=f"当前现金价值 {cash_value.current_cv/10000:.2f} 万元，"
                       f"减保30%可释放 {cash_value.current_cv*0.3/10000:.2f} 万元，"
                       f"同时保留部分保障。"
            ))

        # 3. 险种转换建议
        has_low_coverage = any(
            p.get("sum_insured", 0) < 100000 for p in policies if "重疾" in p.get("type", "")
        )
        if has_low_coverage:
            suggestions.append(PolicySuggestion(
                action="转换",
                priority="中",
                target="重疾险升级",
                amount=0,
                reason="现有重疾保额偏低",
                detail="建议将低保额重疾险转换为保障更全面的产品，"
                       "或叠加购买以提升重疾保障。"
            ))

        # 4. 自动垫交建议
        total_premium = sum(p.get("annual_premium", 0) for p in policies)
        if years_paid >= 3 and cash_value.current_cv > total_premium * 2:
            suggestions.append(PolicySuggestion(
                action="垫交",
                priority="低",
                target="下一年度保费",
                amount=0,
                reason="现金价值充足，可设置自动垫交",
                detail=f"当前现金价值 {cash_value.current_cv/10000:.2f} 万元，"
                       f"超过2年保费，可设置自动垫交功能防止临时缴费困难导致保单失效。"
            ))

        # 5. 到期处理建议
        for p in policies:
            ptype = p.get("type", "")
            payment_years = p.get("payment_years", 0)
            if "年金" in ptype and payment_years > 0 and years_paid >= payment_years:
                suggestions.append(PolicySuggestion(
                    action="到期处理",
                    priority="高",
                    target="年金险",
                    amount=0,
                    reason="年金缴费期满",
                    detail="年金险缴费期满，建议选择满期金领取方式，"
                           "可考虑转入万能账户持续增值。"
                ))

        # 6. 退保建议（最后手段）
        if years_paid < 2 and cash_value.surrender_rate < 30:
            suggestions.append(PolicySuggestion(
                action="退保",
                priority="低",
                target="早期低现金价值保单",
                amount=0,
                reason="如需止损，早期退保损失相对较小",
                detail=f"当前退保仅能拿回 {cash_value.surrender_rate:.1f}% 已缴保费，"
                       f"建议优先考虑减保而非直接退保。"
            ))

        return suggestions

    def _generate_renewal_reminder(
        self,
        years_paid: int,
        policies: List[Dict],
        total_annual_premium: float
    ) -> RenewalReminder:
        """
        生成续期提醒
        """
        # 简化：假设下次缴费为一年后
        days_until = 365 - (years_paid % 365)

        # 缴费进度
        max_payment_years = max([p.get("payment_years", 0) for p in policies], default=20)
        if max_payment_years > 0:
            progress = years_paid / max_payment_years * 100
            payment_progress = f"已完成 {years_paid}/{max_payment_years} 年 ({progress:.0f}%)"
        else:
            payment_progress = f"已缴费 {years_paid} 年"

        # 失效风险
        if years_paid >= max_payment_years:
            lapse_risk = "✅ 缴费期满"
        elif days_until <= 30:
            lapse_risk = "🚨 即将失效，请尽快缴费"
        else:
            lapse_risk = "✅ 正常"

        return RenewalReminder(
            next_due_date="缴费日后15日内",
            next_due_amount=total_annual_premium,
            payment_progress=payment_progress,
            lapse_risk=lapse_risk,
            days_until_due=days_until
        )

    def _generate_family_overview(
        self,
        policies: List[Dict],
        total_annual_premium: float,
        coverage_gap: CoverageGapAnalysis,
        client_info: Dict
    ) -> Dict[str, Any]:
        """
        生成家庭保障全景图
        """
        family_size = client_info.get("family_size", 1)

        # 总保额
        total_coverage = sum(p.get("sum_insured", 0) for p in policies)

        # 人均保额
        per_capita = total_coverage / family_size if family_size > 0 else 0

        # 保障充足率
        needed_total = (
            coverage_gap.needed_life_cover +
            coverage_gap.needed_critical_illness +
            coverage_gap.needed_medical_cover
        )
        coverage_ratio = (total_coverage / needed_total * 100) if needed_total > 0 else 0

        # 风险敞口
        risk_exposure = [
            {"type": "身故风险", "covered": coverage_gap.current_life_cover,
             "gap": coverage_gap.life_gap, "status": "充足" if coverage_gap.life_gap == 0 else "不足"},
            {"type": "重疾风险", "covered": coverage_gap.current_critical_illness,
             "gap": coverage_gap.critical_gap, "status": "充足" if coverage_gap.critical_gap == 0 else "不足"},
            {"type": "医疗风险", "covered": coverage_gap.current_medical_cover,
             "gap": coverage_gap.medical_gap, "status": "充足" if coverage_gap.medical_gap == 0 else "不足"},
        ]

        # 保障缺口
        gaps = []
        if coverage_gap.life_gap > 0:
            gaps.append({"risk": "寿险缺口", "amount": coverage_gap.life_gap})
        if coverage_gap.critical_gap > 0:
            gaps.append({"risk": "重疾缺口", "amount": coverage_gap.critical_gap})
        if coverage_gap.medical_gap > 0:
            gaps.append({"risk": "医疗缺口", "amount": coverage_gap.medical_gap})

        # 保障热力图
        heatmap = {
            "身故保障": min(100, coverage_gap.current_life_cover / coverage_gap.needed_life_cover * 100) if coverage_gap.needed_life_cover > 0 else 100,
            "重疾保障": min(100, coverage_gap.current_critical_illness / coverage_gap.needed_critical_illness * 100) if coverage_gap.needed_critical_illness > 0 else 100,
            "医疗保障": min(100, coverage_gap.current_medical_cover / coverage_gap.needed_medical_cover * 100) if coverage_gap.needed_medical_cover > 0 else 100,
        }

        return {
            "total_annual_premium": total_annual_premium,
            "total_coverage": total_coverage,
            "per_capita_coverage": round(per_capita, 0),
            "coverage_ratio": f"{coverage_ratio:.1f}%",
            "risk_exposure": risk_exposure,
            "gaps": gaps,
            "heatmap": {k: f"{v:.1f}%" for k, v in heatmap.items()}
        }

    def _generate_summary(
        self,
        coverage_gap: CoverageGapAnalysis,
        suggestions: List[PolicySuggestion],
        renewal: RenewalReminder
    ) -> str:
        """
        生成检视摘要
        """
        high_priority = [s for s in suggestions if s.priority == "高"]
        
        summary_parts = [
            f"【保单检视摘要】",
            f"",
            f"📊 保障评估：{coverage_gap.assessment}",
            f"",
        ]

        if high_priority:
            summary_parts.append("📋 高优先级建议：")
            for s in high_priority:
                summary_parts.append(f"  • {s.action} {s.target}：{s.detail[:50]}...")
            summary_parts.append("")

        summary_parts.append(f"💰 续期提醒：{renewal.lapse_risk}，下次缴费 {renewal.next_due_amount/10000:.2f} 万元")

        return "\n".join(summary_parts)

    def parse_cli_input(self, text: str) -> Dict[str, Any]:
        """
        解析CLI输入文本
        
        支持格式：
        "保单检视 寿险50万 重疾30万 年缴保费2万 已缴5年"
        "保单检视 寿险50万 重疾30万 年缴保费2万 已缴5年 年收入30万 负债80万 家庭4口"
        
        Returns:
            解析后的参数字典
        """
        result = {
            "policies": [],
            "total_annual_premium": 0,
            "years_paid": 0,
            "client_info": {}
        }

        # 提取寿险
        life_match = re.search(r'寿险(\d+(?:\.\d+)?)([万千])', text)
        if life_match:
            amount = float(life_match.group(1))
            unit = life_match.group(2)
            amount *= 10000 if unit == '万' else 1000
            result["policies"].append({"type": "寿险", "sum_insured": amount})

        # 提取重疾
        ci_match = re.search(r'重疾(\d+(?:\.\d+)?)([万千])', text)
        if ci_match:
            amount = float(ci_match.group(1))
            unit = ci_match.group(2)
            amount *= 10000 if unit == '万' else 1000
            result["policies"].append({"type": "重疾", "sum_insured": amount})

        # 提取医疗
        med_match = re.search(r'医疗(\d+(?:\.\d+)?)([万千])', text)
        if med_match:
            amount = float(med_match.group(1))
            unit = med_match.group(2)
            amount *= 10000 if unit == '万' else 1000
            result["policies"].append({"type": "医疗", "sum_insured": amount})

        # 提取意外
        acc_match = re.search(r'意外(\d+(?:\.\d+)?)([万千])', text)
        if acc_match:
            amount = float(acc_match.group(1))
            unit = acc_match.group(2)
            amount *= 10000 if unit == '万' else 1000
            result["policies"].append({"type": "意外", "sum_insured": amount})

        # 提取年缴保费
        premium_match = re.search(r'年缴保费(\d+(?:\.\d+)?)([万千])?', text)
        if premium_match:
            amount = float(premium_match.group(1))
            unit = premium_match.group(2) or ''
            if '万' in unit or '千' in unit:
                amount *= 10000 if unit == '万' else 1000
            result["total_annual_premium"] = amount

        # 提取已缴年限
        years_match = re.search(r'已缴(\d+)年', text)
        if years_match:
            result["years_paid"] = int(years_match.group(1))

        # 提取年收入
        income_match = re.search(r'年收入(\d+(?:\.\d+)?)([万千])?', text)
        if income_match:
            amount = float(income_match.group(1))
            unit = income_match.group(2) or ''
            if '万' in unit or '千' in unit:
                amount *= 10000 if unit == '万' else 1000
            result["client_info"]["annual_income"] = amount

        # 提取负债
        debt_match = re.search(r'负债(\d+(?:\.\d+)?)([万千])?', text)
        if debt_match:
            amount = float(debt_match.group(1))
            unit = debt_match.group(2) or ''
            if '万' in unit or '千' in unit:
                amount *= 10000 if unit == '万' else 1000
            result["client_info"]["total_debt"] = amount

        # 提取家庭人口
        family_match = re.search(r'家庭(\d+)口', text)
        if family_match:
            result["client_info"]["family_size"] = int(family_match.group(1))

        # 提取子女数量
        child_match = re.search(r'子女(\d+)个', text)
        if child_match:
            result["client_info"]["children_count"] = int(child_match.group(1))

        return result

    def format_report(self, result: Dict[str, Any]) -> str:
        """
        格式化输出报告为可读文本
        """
        lines = []
        lines.append("=" * 60)
        lines.append("                    保 单 检 视 报 告")
        lines.append("=" * 60)
        lines.append("")

        # 1. 保障缺口分析
        cg = result["coverage_gap"]
        lines.append("【保障缺口分析】")
        lines.append(f"  寿险应有保额：{cg['needed_life_cover']/10000:.1f} 万元")
        lines.append(f"  当前寿险保额：{cg['current_life_cover']/10000:.1f} 万元")
        lines.append(f"  寿险缺口：{cg['life_gap']/10000:.1f} 万元")
        lines.append(f"  重疾应有保额：{cg['needed_critical_illness']/10000:.1f} 万元")
        lines.append(f"  当前重疾保额：{cg['current_critical_illness']/10000:.1f} 万元")
        lines.append(f"  重疾缺口：{cg['critical_gap']/10000:.1f} 万元")
        lines.append(f"  综合评估：{cg['assessment']}")
        lines.append("")

        # 2. 保费合理性
        pa = result["premium_analysis"]
        lines.append("【保费合理性】")
        lines.append(f"  年缴保费：{pa['total_annual_premium']/10000:.2f} 万元")
        lines.append(f"  年收入：{pa['annual_income']/10000:.2f} 万元")
        lines.append(f"  保费收入比：{pa['premium_to_income_ratio']:.1f}%")
        lines.append(f"  评估：{pa['assessment']}")
        lines.append("")

        # 3. 现金价值
        cv = result["cash_value"]
        lines.append("【现金价值分析】")
        lines.append(f"  当前现金价值：{cv['current_cv']/10000:.2f} 万元")
        lines.append(f"  已缴保费总额：{cv['total_premium_paid']/10000:.2f} 万元")
        lines.append(f"  退保折算比例：{cv['surrender_rate']:.1f}%")
        lines.append(f"  回本年度：第 {cv['break_even_year']} 年")
        lines.append(f"  评估：{cv['assessment']}")
        lines.append("  未来走势：")
        for yr, val in zip(cv['projection_years'], cv['projection_values']):
            lines.append(f"    第{yr}年：{val/10000:.2f} 万元")
        lines.append("")

        # 4. 保全建议
        lines.append("【保全建议】")
        if result["policy_suggestions"]:
            for i, s in enumerate(result["policy_suggestions"], 1):
                lines.append(f"  {i}. [{s['priority']}级] {s['action']} {s['target']}")
                lines.append(f"     {s['detail']}")
        else:
            lines.append("  暂无需处理的保全事项")
        lines.append("")

        # 5. 续期提醒
        rn = result["renewal_reminder"]
        lines.append("【续期提醒】")
        lines.append(f"  下次缴费日期：{rn['next_due_date']}")
        lines.append(f"  下次缴费金额：{rn['next_due_amount']/10000:.2f} 万元")
        lines.append(f"  缴费进度：{rn['payment_progress']}")
        lines.append(f"  失效风险：{rn['lapse_risk']}")
        lines.append("")

        # 6. 家庭保障全景
        fo = result["family_overview"]
        lines.append("【家庭保障全景】")
        lines.append(f"  家庭年缴保费：{fo['total_annual_premium']/10000:.2f} 万元")
        lines.append(f"  家庭总保额：{fo['total_coverage']/10000:.2f} 万元")
        lines.append(f"  人均保额：{fo['per_capita_coverage']/10000:.2f} 万元")
        lines.append(f"  保障充足率：{fo['coverage_ratio']}")
        lines.append("  保障热力图：")
        for k, v in fo['heatmap'].items():
            bar = "█" * int(float(v.rstrip('%')) / 5)
            lines.append(f"    {k}：{bar} {v}")
        lines.append("")

        lines.append("=" * 60)
        lines.append(result["summary"])
        lines.append("=" * 60)

        return "\n".join(lines)


# 快捷函数
def review_policy(
    policies: List[Dict],
    total_annual_premium: float,
    years_paid: int,
    **kwargs
) -> Dict[str, Any]:
    """
    快捷保单检视函数
    """
    engine = PolicyManagementEngine()
    return engine.generate_review(policies, total_annual_premium, years_paid, **kwargs)


def review_policy_from_text(text: str) -> Dict[str, Any]:
    """
    从文本快捷检视保单
    """
    engine = PolicyManagementEngine()
    params = engine.parse_cli_input(text)
    return engine.generate_review(**params)
