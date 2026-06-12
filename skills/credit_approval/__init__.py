"""
credit_approval - 信用审批技能
CreditApprovalEngine: 企业/个人信用评估 + 杜邦分析 + Z-score + 贷款额度建议
"""

from credit_engine import (
    CreditApprovalEngine,
    calc_dupont,
    calc_z_score,
    calc_loan_amount,
    calc_interest_rate,
    calc_scoring_details,
    get_grade,
    get_approval_conclusion,
)

__version__ = "1.0.0"
__all__ = [
    "CreditApprovalEngine",
    "calc_dupont",
    "calc_z_score",
    "calc_loan_amount",
    "calc_interest_rate",
    "calc_scoring_details",
    "get_grade",
    "get_approval_conclusion",
]
