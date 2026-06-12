"""
现金管理技能 (Cash Management)
企业现金管理方案生成引擎
"""

from .cash_engine import CashManagementEngine, CashManagementResult, CashPosition

__all__ = [
    "CashManagementEngine",
    "CashManagementResult",
    "CashPosition",
]

__version__ = "1.0.0"
