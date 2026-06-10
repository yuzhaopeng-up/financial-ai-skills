"""
KPI 绩效考核引擎
Bank Performance Evaluation Engine

支持岗位：客户经理、柜员、风控经理、产品经理、网点负责人
KPI维度：存款类、贷款类、中间业务收入、客户类、风险合规类
"""

from .kpi_engine import (
    KPIPerformanceEngine,
    KPIIndicator,
    KPICategory,
    KPIResult,
    generate_kpi,
)

__all__ = [
    "KPIPerformanceEngine",
    "KPIIndicator",
    "KPICategory",
    "KPIResult",
    "generate_kpi",
]

__version__ = "1.0.0"
