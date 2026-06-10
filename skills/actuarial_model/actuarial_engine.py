"""
精算模型引擎
实现保费定价、准备金评估、偿付能力评估
内置中国人寿保险业经验生命表（CL1/CL2）
"""

import math
from typing import Dict, Any, Optional, Literal


# ============================================================
# 中国人寿保险业经验生命表（简化版，0-105岁）
# CL1: 非养老类业务一表（男）
# CL2: 非养老类业务二表（男）
# ============================================================

# CL1 男性死亡率表 (每千分率)
CL1_MORTALITY_MALE = {
    0: 5.0, 1: 3.5, 2: 2.5, 3: 2.0, 4: 1.8, 5: 1.6,
    6: 1.4, 7: 1.3, 8: 1.2, 9: 1.1, 10: 1.0,
    11: 1.0, 12: 1.0, 13: 1.1, 14: 1.2, 15: 1.3,
    16: 1.4, 17: 1.5, 18: 1.6, 19: 1.7, 20: 1.8,
    21: 1.9, 22: 2.0, 23: 2.1, 24: 2.2, 25: 2.3,
    26: 2.4, 27: 2.5, 28: 2.6, 29: 2.7, 30: 2.8,
    31: 2.9, 32: 3.1, 33: 3.3, 34: 3.5, 35: 3.7,
    36: 3.9, 37: 4.1, 38: 4.3, 39: 4.6, 40: 4.9,
    41: 5.2, 42: 5.6, 43: 6.0, 44: 6.5, 45: 7.0,
    46: 7.5, 47: 8.1, 48: 8.7, 49: 9.4, 50: 10.1,
    51: 10.9, 52: 11.8, 53: 12.8, 54: 13.9, 55: 15.1,
    56: 16.5, 57: 18.1, 58: 19.9, 59: 21.9, 60: 24.2,
    61: 26.8, 62: 29.7, 63: 33.0, 64: 36.8, 65: 41.0,
    66: 45.8, 67: 51.2, 68: 57.3, 69: 64.0, 70: 71.5,
    71: 79.8, 72: 88.8, 73: 98.2, 74: 107.8, 75: 117.6,
    76: 127.8, 77: 138.6, 78: 150.0, 79: 161.0, 80: 171.8,
    81: 182.3, 82: 192.5, 83: 202.1, 84: 211.4, 85: 220.4,
    86: 228.8, 87: 236.6, 88: 244.1, 89: 251.2, 90: 258.0,
    91: 264.5, 92: 270.7, 93: 276.5, 94: 282.1, 95: 287.5,
    96: 292.6, 97: 297.5, 98: 302.2, 99: 306.7, 100: 311.0,
    101: 315.0, 102: 318.8, 103: 322.4, 104: 325.8, 105: 329.0
}

# CL2 男性死亡率表 (每千分率) - 略低于CL1
CL2_MORTALITY_MALE = {
    0: 4.5, 1: 3.0, 2: 2.2, 3: 1.7, 4: 1.5, 5: 1.3,
    6: 1.2, 7: 1.1, 8: 1.0, 9: 0.9, 10: 0.9,
    11: 0.9, 12: 0.9, 13: 1.0, 14: 1.0, 15: 1.1,
    16: 1.2, 17: 1.3, 18: 1.4, 19: 1.5, 20: 1.6,
    21: 1.7, 22: 1.8, 23: 1.9, 24: 2.0, 25: 2.1,
    26: 2.2, 27: 2.3, 28: 2.4, 29: 2.5, 30: 2.6,
    31: 2.7, 32: 2.8, 33: 3.0, 34: 3.2, 35: 3.4,
    36: 3.6, 37: 3.8, 38: 4.0, 39: 4.3, 40: 4.6,
    41: 4.9, 42: 5.2, 43: 5.6, 44: 6.0, 45: 6.5,
    46: 7.0, 47: 7.5, 48: 8.1, 49: 8.7, 50: 9.4,
    51: 10.2, 52: 11.0, 53: 11.9, 54: 12.9, 55: 14.0,
    56: 15.3, 57: 16.7, 58: 18.3, 59: 20.1, 60: 22.2,
    61: 24.6, 62: 27.3, 63: 30.3, 64: 33.8, 65: 37.7,
    66: 42.0, 67: 46.8, 68: 52.2, 69: 58.2, 70: 65.0,
    71: 72.4, 72: 80.5, 73: 89.2, 74: 98.1, 75: 107.2,
    76: 116.6, 77: 126.5, 78: 136.8, 79: 147.1, 80: 157.4,
    81: 167.7, 82: 177.9, 83: 187.9, 84: 197.6, 85: 206.8,
    86: 215.7, 87: 224.2, 88: 232.3, 89: 240.1, 90: 247.5,
    91: 254.6, 92: 261.4, 93: 267.8, 94: 273.9, 95: 279.7,
    96: 285.2, 97: 290.4, 98: 295.2, 99: 299.8, 100: 304.1,
    101: 308.1, 102: 311.8, 103: 315.3, 104: 318.5, 105: 321.5
}

# 女性死亡率表（基于男性表乘以调整系数）
FEMALE_ADJUSTMENT = 0.65


class ActuarialModelEngine:
    """精算模型引擎"""

    def __init__(
        self,
        mortality_table: Literal["CL1", "CL2"] = "CL1",
        interest_rate: float = 0.025,
        first_year_expense_rate: float = 0.25,
        renewal_expense_rate: float = 0.05,
    ):
        """
        初始化精算引擎

        Args:
            mortality_table: 死亡率表类型 CL1/CL2
            interest_rate: 预定利率
            first_year_expense_rate: 首年费用率
            renewal_expense_rate: 续年费用率
        """
        self.mortality_table = mortality_table
        self.interest_rate = interest_rate
        self.first_year_expense_rate = first_year_expense_rate
        self.renewal_expense_rate = renewal_expense_rate

        # 选择死亡率表
        self.mortality_rates = CL1_MORTALITY_MALE if mortality_table == "CL1" else CL2_MORTALITY_MALE

    def _get_mortality_rate(self, age: int, gender: str) -> float:
        """获取死亡率"""
        rate = self.mortality_rates.get(age, 1000.0) / 1000.0  # 转换为小数
        if gender == "女性":
            rate *= FEMALE_ADJUSTMENT
        return rate

    def _discount_factor(self, years: int) -> float:
        """折现因子"""
        return 1.0 / ((1 + self.interest_rate) ** years)

    def _get_lapse_rate(self, policy_year: int) -> float:
        """退保率（随保单年度递减）"""
        if policy_year == 1:
            return 0.10
        elif policy_year == 2:
            return 0.06
        elif policy_year == 3:
            return 0.04
        elif policy_year == 4:
            return 0.03
        else:
            return 0.02

    def calculate_premium(
        self,
        product_type: str,
        age: int,
        gender: str,
        sum_insured: float,
        payment_term: int,
    ) -> Dict[str, Any]:
        """
        计算保费

        Args:
            product_type: 险种类型（终身寿险/定期寿险/重疾险）
            age: 投保年龄
            gender: 性别（男性/女性）
            sum_insured: 保额
            payment_term: 缴费期限（年）

        Returns:
            保费计算结果
        """
        # 确定保障期限
        if product_type == "终身寿险":
            coverage_years = 105 - age  # 终身
        elif product_type == "定期寿险":
            coverage_years = 30
        elif product_type == "重疾险":
            coverage_years = 70 - age
        else:
            coverage_years = 65 - age

        # 计算纯保费（趸交）
        net_premium_annuity = 0.0
        for t in range(1, coverage_years + 1):
            qx = self._get_mortality_rate(age + t - 1, gender)
            v = self._discount_factor(t)
            net_premium_annuity += qx * v

        # 纯保费 = 保额 × 死亡概率现值之和
        net_premium_single = sum_insured * net_premium_annuity

        # 分期缴费纯保费
        # 每年缴纳纯保费的现值 = 纯保费 × å (1)
        annuity_due = 0.0
        for t in range(1, min(payment_term, coverage_years) + 1):
            v = self._discount_factor(t)
            annuity_due += v

        if annuity_due > 0:
            net_premium_per_year = net_premium_single / annuity_due
        else:
            net_premium_per_year = net_premium_single

        # 附加费用计算
        first_year_expense = net_premium_per_year * self.first_year_expense_rate
        renewal_expense = net_premium_per_year * self.renewal_expense_rate

        # 总保费
        gross_premium_per_year = net_premium_per_year + first_year_expense + renewal_expense

        # 趸交总保费
        gross_premium_single = net_premium_single * (1 + self.first_year_expense_rate)

        return {
            "net_premium_single": round(net_premium_single, 2),
            "net_premium_per_year": round(net_premium_per_year, 2),
            "expense_first_year": round(first_year_expense, 2),
            "expense_renewal": round(renewal_expense, 2),
            "gross_premium_single": round(gross_premium_single, 2),
            "gross_premium_per_year": round(gross_premium_per_year, 2),
        }

    def calculate_reserve(
        self,
        product_type: str,
        age: int,
        gender: str,
        sum_insured: float,
        payment_term: int,
        policy_year: int = 1,
    ) -> Dict[str, Any]:
        """
        准备金评估（未来负债现值法）

        Args:
            product_type: 险种类型
            age: 投保年龄
            gender: 性别
            sum_insured: 保额
            payment_term: 缴费期限
            policy_year: 当前保单年度

        Returns:
            准备金评估结果
        """
        # 确定保障期限
        if product_type == "终身寿险":
            coverage_years = 105 - age
        elif product_type == "定期寿险":
            coverage_years = 30
        elif product_type == "重疾险":
            coverage_years = 70 - age
        else:
            coverage_years = 65 - age

        # 未来净赔付现金流现值
        future_claims_pv = 0.0
        for t in range(policy_year, coverage_years + 1):
            qx = self._get_mortality_rate(age + t - 1, gender)
            v = self._discount_factor(t - policy_year + 1)
            future_claims_pv += sum_insured * qx * v

        # 未来保费收入现值
        future_premiums_pv = 0.0
        remaining_years = min(payment_term, coverage_years) - (policy_year - 1)
        for t in range(1, remaining_years + 1):
            v = self._discount_factor(t)
            future_premiums_pv += v

        # 净保费
        net_premium_single = sum_insured * sum(
            self._get_mortality_rate(age + t - 1, gender) * self._discount_factor(t)
            for t in range(1, coverage_years + 1)
        )
        if future_premiums_pv > 0:
            annual_net_premium = net_premium_single / sum(self._discount_factor(t) for t in range(1, min(payment_term, coverage_years) + 1))
        else:
            annual_net_premium = 0

        future_premium_pv_adjusted = annual_net_premium * future_premiums_pv

        # 准备金 = 未来负债现值 - 未来保费收入现值
        reserve = future_claims_pv - future_premium_pv_adjusted
        reserve = max(reserve, 0)  # 不能为负

        # 未决赔款准备金（按当年保费的一定比例）
        unpaid_claim_reserve = sum_insured * 0.02 * min(policy_year, 5) / 100

        # 已赚保费准备金
        earned_premium_reserve = reserve * 0.3

        return {
            "unpaid_claim_reserve": round(unpaid_claim_reserve, 2),
            "earned_premium_reserve": round(earned_premium_reserve, 2),
            "total_reserve": round(reserve, 2),
            "future_claims_pv": round(future_claims_pv, 2),
            "future_premiums_pv": round(future_premium_pv_adjusted, 2),
        }

    def calculate_solvency(
        self,
        total_reserve: float,
        gross_premium: float,
    ) -> Dict[str, Any]:
        """
        偿付能力评估

        Args:
            total_reserve: 总准备金
            gross_premium: 总保费

        Returns:
            偿付能力评估结果
        """
        # 实际资本 = 准备金 + 保费余额
        actual_capital = total_reserve * 0.05 + gross_premium * 0.1

        # 最低资本（基于风险资本）
        # 保险风险最低资本
        insurance_risk_capital = total_reserve * 0.15
        # 市场风险最低资本
        market_risk_capital = total_reserve * 0.12
        # 最低资本合计
        minimum_capital = insurance_risk_capital + market_risk_capital

        # 偿付能力充足率
        if minimum_capital > 0:
            core_solvency_ratio = (actual_capital / minimum_capital) * 100
            comprehensive_solvency_ratio = core_solvency_ratio * 1.05  # 综合偿付率略高
        else:
            core_solvency_ratio = 500.0
            comprehensive_solvency_ratio = 500.0

        # 风险边际
        risk_margin = minimum_capital * 0.05

        return {
            "actual_capital": round(actual_capital, 2),
            "minimum_capital": round(minimum_capital, 2),
            "core_solvency_ratio": round(core_solvency_ratio, 2),
            "comprehensive_solvency_ratio": round(comprehensive_solvency_ratio, 2),
            "risk_margin": round(risk_margin, 2),
        }

    def calculate(
        self,
        product_type: str,
        age: int,
        gender: str,
        sum_insured: float,
        payment_term: int,
        policy_year: int = 1,
    ) -> Dict[str, Any]:
        """
        综合精算计算

        Args:
            product_type: 险种类型
            age: 投保年龄
            gender: 性别
            sum_insured: 保额
            payment_term: 缴费期限
            policy_year: 当前保单年度

        Returns:
            完整精算结果
        """
        # 保费计算
        premium_result = self.calculate_premium(
            product_type=product_type,
            age=age,
            gender=gender,
            sum_insured=sum_insured,
            payment_term=payment_term,
        )

        # 准备金评估
        reserve_result = self.calculate_reserve(
            product_type=product_type,
            age=age,
            gender=gender,
            sum_insured=sum_insured,
            payment_term=payment_term,
            policy_year=policy_year,
        )

        # 偿付能力评估
        solvency_result = self.calculate_solvency(
            total_reserve=reserve_result["total_reserve"],
            gross_premium=premium_result["gross_premium_per_year"],
        )

        return {
            "product_type": product_type,
            "insured_info": {
                "age": age,
                "gender": gender,
                "sum_insured": sum_insured,
                "payment_term": payment_term,
                "policy_year": policy_year,
            },
            "premium_pricing": premium_result,
            "reserve_evaluation": reserve_result,
            "solvency_assessment": solvency_result,
            "actuarial_assumptions": {
                "mortality_table": self.mortality_table,
                "interest_rate": self.interest_rate,
                "first_year_expense_rate": self.first_year_expense_rate,
                "renewal_expense_rate": self.renewal_expense_rate,
                "lapse_rates": {
                    "year_1": self._get_lapse_rate(1),
                    "year_2": self._get_lapse_rate(2),
                    "year_3": self._get_lapse_rate(3),
                    "year_4+": self._get_lapse_rate(4),
                },
            },
        }

    def format_report(self, result: Dict[str, Any]) -> str:
        """格式化输出精算报告"""
        insured = result["insured_info"]
        premium = result["premium_pricing"]
        reserve = result["reserve_evaluation"]
        solvency = result["solvency_assessment"]
        assumptions = result["actuarial_assumptions"]

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    📊 精算模型定价报告                          ║
╠══════════════════════════════════════════════════════════════╣
║ 险种类型: {result['product_type']:<40} ║
║ 投保年龄: {insured['age']}岁  性别: {insured['gender']:<30} ║
║ 保额: {insured['sum_insured']:>15,.0f} 元                       ║
║ 缴费期限: {insured['payment_term']}年                                          ║
╠══════════════════════════════════════════════════════════════╣
║                      💰 保费定价                               ║
╠══════════════════════════════════════════════════════════════╣
║ 纯保费（趸交）:     {premium['net_premium_single']:>15,.2f} 元              ║
║ 纯保费（年缴）:     {premium['net_premium_per_year']:>15,.2f} 元/年          ║
║ 首年附加费用:       {premium['expense_first_year']:>15,.2f} 元              ║
║ 续年附加费用:       {premium['expense_renewal']:>15,.2f} 元/年              ║
║ ─────────────────────────────────────────────────────────── ║
║ 总保费（趸交）:     {premium['gross_premium_single']:>15,.2f} 元              ║
║ 总保费（年缴）:     {premium['gross_premium_per_year']:>15,.2f} 元/年          ║
╠══════════════════════════════════════════════════════════════╣
║                    📋 准备金评估                               ║
╠══════════════════════════════════════════════════════════════╣
║ 未决赔款准备金:     {reserve['unpaid_claim_reserve']:>15,.2f} 元              ║
║ 已赚保费准备金:     {reserve['earned_premium_reserve']:>15,.2f} 元              ║
║ 总准备金:           {reserve['total_reserve']:>15,.2f} 元              ║
╠══════════════════════════════════════════════════════════════╣
║                    🛡️ 偿付能力评估                             ║
╠══════════════════════════════════════════════════════════════╣
║ 实际资本:           {solvency['actual_capital']:>15,.2f} 元              ║
║ 最低资本:           {solvency['minimum_capital']:>15,.2f} 元              ║
║ 核心偿付率:         {solvency['core_solvency_ratio']:>14.2f}%              ║
║ 综合偿付率:         {solvency['comprehensive_solvency_ratio']:>14.2f}%              ║
║ 风险边际:           {solvency['risk_margin']:>15,.2f} 元              ║
╠══════════════════════════════════════════════════════════════╣
║                    📐 精算假设                                 ║
╠══════════════════════════════════════════════════════════════╣
║ 死亡率表:           {assumptions['mortality_table']:<15}                       ║
║ 预定利率:           {assumptions['interest_rate'] * 100:>14.1f}%              ║
║ 首年费用率:         {assumptions['first_year_expense_rate'] * 100:>14.1f}%              ║
║ 续年费用率:         {assumptions['renewal_expense_rate'] * 100:>14.1f}%              ║
╚══════════════════════════════════════════════════════════════╝
"""
        return report.strip()


# 便捷函数
def quick_calculate(
    product_type: str,
    age: int,
    gender: str,
    sum_insured: float,
    payment_term: int,
) -> Dict[str, Any]:
    """快速精算计算"""
    engine = ActuarialModelEngine()
    return engine.calculate(
        product_type=product_type,
        age=age,
        gender=gender,
        sum_insured=sum_insured,
        payment_term=payment_term,
    )
