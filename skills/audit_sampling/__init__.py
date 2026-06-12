"""
审计智能抽样引擎 (Audit Sampling Engine)

支持随机抽样、分层抽样、整群抽样、PPS抽样四种方法，
基于统计学原理和审计准则提供科学的样本量计算和误差推断。
"""

from audit_sampling_engine import (
    AuditSamplingEngine,
    SamplingMethod,
    RiskLevel,
    SamplingPlan,
    SamplingResult,
    AuditFindings,
    PopulationConclusion,
    SampledItem,
)

__all__ = [
    "AuditSamplingEngine",
    "SamplingMethod",
    "RiskLevel",
    "SamplingPlan",
    "SamplingResult",
    "AuditFindings",
    "PopulationConclusion",
    "SampledItem",
]

__version__ = "1.0.0"
