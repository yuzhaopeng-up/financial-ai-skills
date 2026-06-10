"""
fraud_alert - 实时欺诈预警技能
FraudAlertEngine: 毫秒级实时交易预警，红色/橙色/黄色分级
"""

from fraud_alert.fraud_alert_engine import FraudAlertEngine, FraudAlertResult, AlertRule

__all__ = ["FraudAlertEngine", "FraudAlertResult", "AlertRule"]
__version__ = "1.0.0"
