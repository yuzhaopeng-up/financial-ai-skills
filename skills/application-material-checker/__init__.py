"""Application Material Checker —— 进件材料自动核对。"""

import sys
from pathlib import Path

# 支持直接运行测试时的绝对导入
if __name__ == "__main__" or not __package__:
    sys.path.insert(0, str(Path(__file__).parent))
    from checker_engine import (
        MaterialDoc, CheckIssue, CheckReport,
        FIELD_RULES, SCENARIO_RULES,
    )
    from rule_runner import RuleRunner
    from material_checker import MaterialChecker, MaterialReportFormatter
else:
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
