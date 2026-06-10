"""
保单管理技能 (Policy Management Skill)

提供完整的保单检视与保全服务。
"""

from policy_management.policy_engine import (
    PolicyManagementEngine,
    CoverageGapAnalysis,
    CashValueAnalysis,
    PolicySuggestion,
    RenewalReminder,
    FamilyProtectionOverview,
    review_policy,
    review_policy_from_text,
)

__all__ = [
    "PolicyManagementEngine",
    "CoverageGapAnalysis",
    "CashValueAnalysis",
    "PolicySuggestion",
    "RenewalReminder",
    "FamilyProtectionOverview",
    "review_policy",
    "review_policy_from_text",
]

__version__ = "1.0.0"
