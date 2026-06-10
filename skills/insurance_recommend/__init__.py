"""
insurance_recommend - 保险产品智能推荐技能
"""

from .ins_rec_engine import (
    InsuranceRecommendEngine,
    CustomerProfile,
    FamilyInfo,
    Liabilities,
    ExistingPolicy,
    ProtectionGap,
    Recommendation,
    FamilyProtectionOverview
)

__all__ = [
    "InsuranceRecommendEngine",
    "CustomerProfile",
    "FamilyInfo",
    "Liabilities",
    "ExistingPolicy",
    "ProtectionGap",
    "Recommendation",
    "FamilyProtectionOverview",
]

__version__ = "1.0.0"
