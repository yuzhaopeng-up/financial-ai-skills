"""
Fixed Income Plus (固收+) Skill
固收+策略技能：收益分解 + 久期管理 + 信用风险管理 + 类属配置优化 + VS纯债对比
"""

from .fi_plus_engine import (
    FixedIncomePlusEngine,
    FIPlusReport,
    BondPosition,
    ReturnDecomposition,
    DurationStrategy,
    CreditRiskAnalysis,
    AllocationResult,
    PureBondComparison,
    BondType,
)

__version__ = "1.0.0"
__all__ = [
    "FixedIncomePlusEngine",
    "FIPlusReport",
    "BondPosition",
    "ReturnDecomposition",
    "DurationStrategy",
    "CreditRiskAnalysis",
    "AllocationResult",
    "PureBondComparison",
    "BondType",
]
