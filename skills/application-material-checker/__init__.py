"""Application Material Checker —— 进件材料自动核对。"""

from .checker_engine import (
    MaterialDoc, CheckIssue, CheckReport,
    FIELD_RULES, SCENARIO_RULES,
)
from .rule_runner import RuleRunner
from .material_checker import MaterialChecker, MaterialReportFormatter

__version__ = "1.0.0"
__all__ = [
    "MaterialDoc", "CheckIssue", "CheckReport",
    "FIELD_RULES", "SCENARIO_RULES",
    "RuleRunner",
    "MaterialChecker", "MaterialReportFormatter",
]
