"""
credit_approval - 信用审批核心引擎
CreditApprovalEngine: 企业/个人信用评估，返回信用评分、杜邦分析、Z-score预警、贷款额度建议、利率建议
"""

import math
import json
from typing import Optional, Dict, Any


# 行业风险系数表
INDUSTRY_RISK_SCORES = {
    "制造业": 10,
    "服务业": 12,
    "零售业": 8,
    "科技业": 15,
    "建筑业": 6,
    "农业": 7,
    "物流业": 9,
    "金融业": 5,
    "房地产": 4,
    "能源业": 8,
    "医疗业": 13,
    "教育业": 11,
    "default": 10,
}

# 信用等级定义
GRADE_THRESHOLDS = [
    (90, "AAA"),
    (80, "AA"),
    (70, "A"),
    (60, "BBB"),
    (50, "BB"),
    (40, "B"),
    (30, "CCC"),
    (20, "CC"),
    (10, "C"),
    (0, "D"),
]

# 期限选项（月）
TENOR_OPTIONS = [12, 24, 36]


def get_grade(score: float) -> str:
    """根据评分获取信用等级"""
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "D"


def get_industry_score(industry: str) -> int:
    """获取行业风险评分（1-20，越高风险越低）"""
    return INDUSTRY_RISK_SCORES.get(industry, INDUSTRY_RISK_SCORES["default"])


def calc_dupont(
    annual_revenue: float,
    total_assets: float,
    net_profit: float,
    total_debt: float,
    equity: float,
) -> Dict[str, Any]:
    """
    杜邦分析
    ROE = 净利率 × 资产周转率 × 权益乘数
    """
    if annual_revenue <= 0 or total_assets <= 0:
        return {
            "ROE": 0.0,
            "net_margin": 0.0,
            "asset_turnover": 0.0,
            "equity_multiplier": 0.0,
            "breakdown": "数据不足，无法计算",
        }

    net_margin = net_profit / annual_revenue  # 净利率
    asset_turnover = annual_revenue / total_assets  # 资产周转率
    equity_multiplier = total_assets / equity if equity > 0 else 0  # 权益乘数
    roe = net_margin * asset_turnover * equity_multiplier  # ROE

    breakdown = (
        f"ROE = {net_margin:.4f}(净利率) × {asset_turnover:.4f}(资产周转率) × "
        f"{equity_multiplier:.4f}(权益乘数) = {roe:.4f}"
    )

    return {
        "ROE": round(roe, 4),
        "net_margin": round(net_margin, 4),
        "asset_turnover": round(asset_turnover, 4),
        "equity_multiplier": round(equity_multiplier, 4),
        "breakdown": breakdown,
    }


def calc_z_score(
    working_capital: float,
    total_assets: float,
    retained_earnings: float,
    ebit: float,
    equity: float,
    total_debt: float,
    annual_revenue: float,
) -> Dict[str, Any]:
    """
    Altman Z-score 计算（适用于私营企业）
    Z = 1.2X1 + 1.4X2 + 3.3X3 + 0.6X4 + 1.0X5

    X1 = 营运资本 / 总资产
    X2 = 留存收益 / 总资产
    X3 = EBIT / 总资产
    X4 = 股东权益 / 总负债
    X5 = 营业收入 / 总资产
    """
    if total_assets <= 0:
        return {
            "value": 0.0,
            "zone": "数据不足",
            "warning": "无法计算 Z-score",
            "x1": 0, "x2": 0, "x3": 0, "x4": 0, "x5": 0,
        }

    x1 = working_capital / total_assets
    x2 = retained_earnings / total_assets
    x3 = ebit / total_assets
    x4 = equity / total_debt if total_debt > 0 else 0
    x5 = annual_revenue / total_assets

    z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5

    if z > 2.99:
        zone = "安全区"
        warning = "财务状况良好，破产风险低"
    elif z > 1.81:
        zone = "灰色区"
        warning = "财务状况中等，需密切关注财务指标变化"
    else:
        zone = "破产区"
        warning = "财务状况堪忧，存在较高破产风险"

    return {
        "value": round(z, 4),
        "zone": zone,
        "warning": warning,
        "x1": round(x1, 4),
        "x2": round(x2, 4),
        "x3": round(x3, 4),
        "x4": round(x4, 4),
        "x5": round(x5, 4),
    }


def calc_loan_amount(
    credit_score: float,
    annual_revenue: float,
    equity: float,
    grade: str,
) -> Dict[str, Any]:
    """
    贷款额度建议
    max_loan = min(年营收 × 信用系数, 净资产 × 抵押折扣)
    """
    grade_config = {
        "AAA": (0.5, 0.8),
        "AA": (0.4, 0.7),
        "A": (0.3, 0.6),
        "BBB": (0.2, 0.5),
        "BB": (0.15, 0.4),
        "B": (0.1, 0.3),
        "CCC": (0.05, 0.2),
        "CC": (0.0, 0.1),
        "C": (0.0, 0.0),
        "D": (0.0, 0.0),
    }

    coeff, mortgage_discount = grade_config.get(grade, (0.0, 0.0))

    if coeff == 0:
        return {
            "max_amount": 0.0,
            "currency": "CNY",
            "unit": "万元",
            "tenor": "N/A",
            "note": "信用等级过低，不建议发放贷款",
        }

    by_revenue = annual_revenue * coeff
    by_equity = equity * mortgage_discount
    max_amount = min(by_revenue, by_equity)

    # 建议期限（根据信用等级）
    if grade in ["AAA", "AA", "A"]:
        tenor = 36
    elif grade in ["BBB", "BB", "B"]:
        tenor = 24
    else:
        tenor = 12

    return {
        "max_amount": round(max_amount, 2),
        "currency": "CNY",
        "unit": "万元",
        "tenor": f"{tenor}个月",
        "note": f"年营收×{coeff}={by_revenue:.2f}万，净资产×{mortgage_discount}={by_equity:.2f}万，取较小值",
    }


def calc_interest_rate(grade: str, tenor_months: int = 12) -> Dict[str, Any]:
    """
    利率建议
    基准利率：4.35%（1年期LPR）
    风险溢价 + 期限溢价
    """
    base_rate = 4.35

    risk_spread = {
        "AAA": 0.5,
        "AA": 0.8,
        "A": 1.2,
        "BBB": 1.8,
        "BB": 2.5,
        "B": 3.5,
        "CCC": 5.0,
        "CC": 7.0,
        "C": 9.0,
        "D": 99.0,  # 拒绝
    }

    risk = risk_spread.get(grade, 99.0)

    if risk >= 99:
        return {
            "base_rate": base_rate,
            "spread": 0,
            "final_rate": 0,
            "description": "信用等级D，拒绝贷款",
        }

    tenor_spread = {
        12: 0.0,
        24: 0.2,
        36: 0.4,
    }
    tenor_sp = tenor_spread.get(tenor_months, 0.0)

    final = base_rate + risk + tenor_sp

    return {
        "base_rate": base_rate,
        "spread": risk + tenor_sp,
        "final_rate": round(final, 2),
        "description": f"基准{base_rate}% + 风险溢价{risk}% + 期限溢价{tenor_sp}% = {final:.2f}%",
    }


def calc_scoring_details(
    debt_ratio: float,
    current_ratio: float,
    profit_margin: float,
    operating_years: float,
    industry: str,
) -> Dict[str, float]:
    """
    信用评分维度打分（每项20分，满分100）
    """
    # 资产负债率评分（20分）
    if debt_ratio <= 40:
        debt_score = 20.0
    else:
        debt_score = max(0, 20 - (debt_ratio - 40) / 5 * 2)

    # 流动比率评分（20分）
    if current_ratio >= 2:
        current_score = 20.0
    elif current_ratio >= 1.5:
        current_score = 15.0
    elif current_ratio >= 1.0:
        current_score = 10.0
    else:
        current_score = 5.0

    # 利润率评分（20分）
    profit_score = max(0, min(20, 20 + (profit_margin - 15) / 2 * 2))
    # profit_margin >= 15% → 20分，每降2%扣1分

    # 经营年限评分（20分）
    if operating_years >= 10:
        years_score = 20.0
    else:
        years_score = max(0, operating_years * 2)

    # 行业风险评分（20分）
    industry_score = get_industry_score(industry)

    return {
        "debt_ratio_score": round(debt_score, 1),
        "current_ratio_score": round(current_score, 1),
        "profit_margin_score": round(profit_score, 1),
        "operating_years_score": round(years_score, 1),
        "industry_risk_score": float(industry_score),
    }


def get_approval_conclusion(
    credit_score: float,
    grade: str,
    z_zone: str,
) -> str:
    """
    审批结论
    """
    if grade in ["CC", "C", "D"]:
        return "拒绝"
    elif grade == "CCC":
        if z_zone == "破产区":
            return "拒绝"
        return "有条件通过"
    elif grade in ["BB", "B"]:
        if z_zone == "破产区":
            return "拒绝"
        return "有条件通过"
    else:
        if z_zone == "破产区":
            return "有条件通过"
        return "通过"


class CreditApprovalEngine:
    """
    信用审批引擎
    输入：企业/个人信息（营业收入/负债率/利润率/经营年限等）
    输出：信用评分 + 杜邦分析 + Z-score + 贷款额度 + 利率建议 + 审批结论
    """

    def __init__(self):
        self.name = "CreditApprovalEngine"
        self.version = "1.0.0"

    def evaluate(
        self,
        company_name: str,
        annual_revenue: float,
        debt_ratio: float,
        profit_margin: float,
        operating_years: float,
        industry: str = "制造业",
        current_ratio: Optional[float] = None,
        total_assets: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        信用评估主方法

        Args:
            company_name: 企业名称
            annual_revenue: 年营收（万元）
            debt_ratio: 负债率（%）
            profit_margin: 利润率（%）
            operating_years: 经营年限（年）
            industry: 行业类型
            current_ratio: 流动比率（可选，默认1.5）
            total_assets: 资产总额（万元，可选）

        Returns:
            信用评估报告（字典）
        """
        # 估算缺失值
        if total_assets is None or total_assets <= 0:
            total_assets = annual_revenue / 0.5  # 估算：营收/资产比≈0.5

        if current_ratio is None:
            current_ratio = 1.5  # 默认流动比率

        total_debt = total_assets * debt_ratio / 100
        equity = total_assets - total_debt  # 净资产
        net_profit = annual_revenue * profit_margin / 100  # 净利润

        # 流动资产估算（假设流动比率正常）
        current_assets = current_ratio * (total_debt * 0.6)  # 假设流动负债占负债60%
        working_capital = current_assets - (total_debt * 0.6)  # 营运资本

        # 留存收益估算（假设为净利润的50%）
        retained_earnings = net_profit * 0.5

        # EBIT估算（净利润×1.3）
        ebit = net_profit * 1.3

        # --- 1. 信用评分 ---
        scoring = calc_scoring_details(
            debt_ratio, current_ratio, profit_margin, operating_years, industry
        )
        credit_score = sum(scoring.values())
        grade = get_grade(credit_score)

        # --- 2. 杜邦分析 ---
        dupont = calc_dupont(
            annual_revenue=annual_revenue,
            total_assets=total_assets,
            net_profit=net_profit,
            total_debt=total_debt,
            equity=equity,
        )

        # --- 3. Z-score ---
        z_result = calc_z_score(
            working_capital=working_capital,
            total_assets=total_assets,
            retained_earnings=retained_earnings,
            ebit=ebit,
            equity=equity,
            total_debt=total_debt,
            annual_revenue=annual_revenue,
        )

        # --- 4. 贷款额度建议 ---
        loan = calc_loan_amount(
            credit_score=credit_score,
            annual_revenue=annual_revenue,
            equity=equity,
            grade=grade,
        )

        # --- 5. 利率建议 ---
        tenor_months = 36 if grade in ["AAA", "AA", "A"] else 24
        interest = calc_interest_rate(grade, tenor_months)

        # --- 6. 审批结论 ---
        conclusion = get_approval_conclusion(credit_score, grade, z_result["zone"])

        return {
            "company_name": company_name,
            "credit_score": round(credit_score, 1),
            "grade": grade,
            "approval_conclusion": conclusion,
            "dupont_analysis": dupont,
            "z_score": z_result,
            "loan_suggestion": loan,
            "interest_rate_suggestion": interest,
            "scoring_details": scoring,
            "raw_inputs": {
                "annual_revenue": annual_revenue,
                "debt_ratio": debt_ratio,
                "profit_margin": profit_margin,
                "operating_years": operating_years,
                "industry": industry,
                "current_ratio": current_ratio,
                "total_assets": round(total_assets, 2),
                "total_debt": round(total_debt, 2),
                "equity": round(equity, 2),
                "net_profit": round(net_profit, 2),
            },
        }

    def evaluate_from_text(self, text: str) -> Dict[str, Any]:
        """
        从自然语言文本解析参数并评估
        支持格式：
        "信用审批 某制造企业 年营收5000万 负债率60% 利润率8%"
        """
        import re

        # 解析企业名称（去掉"信用审批"后第一个连续的字符串）
        text_clean = text.strip()
        if text_clean.startswith("信用审批"):
            text_clean = text_clean[4:].strip()

        # 企业名称：第一个连续非数字字符串
        name_match = re.match(r'^([^\d]+?)(?=\d|年|负|利|行|$)', text_clean)
        company_name = name_match.group(1).strip() if name_match else "未知企业"

        # 年营收（万元）
        revenue_match = re.search(r'年营收\s*(\d+(?:\.\d+)?)\s*万?', text_clean)
        annual_revenue = float(revenue_match.group(1)) if revenue_match else 0

        # 负债率（%）
        debt_match = re.search(r'负债率\s*(\d+(?:\.\d+)?)\s*%?', text_clean)
        debt_ratio = float(debt_match.group(1)) if debt_match else 50

        # 利润率（%）
        profit_match = re.search(r'利润率\s*(\d+(?:\.\d+)?)\s*%?', text_clean)
        profit_margin = float(profit_match.group(1)) if profit_match else 5

        # 经营年限（年）
        years_match = re.search(r'(?:经营年限|年限|成立)\s*(\d+(?:\.\d+)?)\s*年?', text_clean)
        operating_years = float(years_match.group(1)) if years_match else 5

        # 行业
        industry_match = re.search(r'(制造业|服务业|零售业|科技业|建筑业|农业|物流业|金融业|房地产业|能源业|医疗业|教育业)', text_clean)
        industry = industry_match.group(1) if industry_match else "制造业"

        # 流动比率
        current_match = re.search(r'流动比率\s*(\d+(?:\.\d+)?)', text_clean)
        current_ratio = float(current_match.group(1)) if current_match else None

        # 资产总额
        asset_match = re.search(r'资产\s*(\d+(?:\.\d+)?)\s*万?', text_clean)
        total_assets = float(asset_match.group(1)) if asset_match else None

        return self.evaluate(
            company_name=company_name,
            annual_revenue=annual_revenue,
            debt_ratio=debt_ratio,
            profit_margin=profit_margin,
            operating_years=operating_years,
            industry=industry,
            current_ratio=current_ratio,
            total_assets=total_assets,
        )

    def to_markdown(self, result: Dict[str, Any]) -> str:
        """将结果转换为 Markdown 格式"""
        r = result
        lines = [
            f"# 📋 信用审批报告：{r['company_name']}",
            "",
            f"## 综合评估",
            f"| 指标 | 值 |",
            f"|------|----|",
            f"| 信用评分 | **{r['credit_score']}** / 100 |",
            f"| 信用等级 | {r['grade']} |",
            f"| 审批结论 | **{r['approval_conclusion']}** |",
            "",
            f"## 信用评分维度（满分100）",
            f"| 维度 | 得分 |",
            f"|------|------|",
            f"| 资产负债率 (20分) | {r['scoring_details']['debt_ratio_score']} |",
            f"| 流动比率 (20分) | {r['scoring_details']['current_ratio_score']} |",
            f"| 利润率 (20分) | {r['scoring_details']['profit_margin_score']} |",
            f"| 经营年限 (20分) | {r['scoring_details']['operating_years_score']} |",
            f"| 行业风险 (20分) | {r['scoring_details']['industry_risk_score']} |",
            "",
            "## 杜邦分析（ROE 拆解）",
            f"- **ROE** = {r['dupont_analysis']['ROE']:.4f}",
            f"- 净利率 = {r['dupont_analysis']['net_margin']:.4f}",
            f"- 资产周转率 = {r['dupont_analysis']['asset_turnover']:.4f}",
            f"- 权益乘数 = {r['dupont_analysis']['equity_multiplier']:.4f}",
            f"- {r['dupont_analysis']['breakdown']}",
            "",
            "## Altman Z-score 财务预警",
            f"- **Z值** = {r['z_score']['value']:.4f}",
            f"- 区间：{r['z_score']['zone']}",
            f"- 预警：{r['z_score']['warning']}",
            f"- X1={r['z_score']['x1']} X2={r['z_score']['x2']} X3={r['z_score']['x3']} X4={r['z_score']['x4']} X5={r['z_score']['x5']}",
            "",
            "## 贷款额度建议",
            f"- **最高额度** = {r['loan_suggestion']['max_amount']:.2f} 万元",
            f"- 币种：{r['loan_suggestion']['currency']}",
            f"- 建议期限：{r['loan_suggestion']['tenor']}",
            f"- 说明：{r['loan_suggestion'].get('note', '')}",
            "",
            "## 利率建议",
            f"- **最终利率** = {r['interest_rate_suggestion']['final_rate']:.2f}%",
            f"- {r['interest_rate_suggestion']['description']}",
            "",
            "## 原始数据",
            f"- 年营收：{r['raw_inputs']['annual_revenue']} 万元",
            f"- 负债率：{r['raw_inputs']['debt_ratio']}%",
            f"- 利润率：{r['raw_inputs']['profit_margin']}%",
            f"- 经营年限：{r['raw_inputs']['operating_years']} 年",
            f"- 行业：{r['raw_inputs']['industry']}",
            f"- 流动比率：{r['raw_inputs']['current_ratio']}",
            f"- 资产总额：{r['raw_inputs']['total_assets']} 万元",
            f"- 净资产：{r['raw_inputs']['equity']} 万元",
            "",
            "---",
            "*本报告由 CreditApprovalEngine v1.0.0 自动生成，仅供参考*",
        ]
        return "\n".join(lines)


# 单元测试
if __name__ == "__main__":
    engine = CreditApprovalEngine()

    # 测试1：正常调用
    result = engine.evaluate(
        company_name="某制造企业",
        annual_revenue=5000,
        debt_ratio=60,
        profit_margin=8,
        operating_years=5,
        industry="制造业",
        current_ratio=1.8,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60 + "\n")

    # 测试2：从文本解析
    result2 = engine.evaluate_from_text(
        "信用审批 某制造企业 年营收5000万 负债率60% 利润率8%"
    )
    print(engine.to_markdown(result2))
