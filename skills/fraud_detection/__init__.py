"""
反欺诈检测技能 (fraud_detection)
FraudDetectionEngine - 30+规则 · 0-100风险评分 · 风险等级 · 建议行动
"""

from fraud_detection.fraud_engine import (
    FraudDetectionEngine,
    FraudDetectionResult,
    TriggeredRule,
)

__all__ = [
    "FraudDetectionEngine",
    "FraudDetectionResult",
    "TriggeredRule",
]

__version__ = "1.0.0"
