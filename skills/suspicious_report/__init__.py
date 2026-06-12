"""
可疑交易报告技能 (suspicious_report)
SuspiciousReportEngine: 识别可疑交易特征并生成符合人民银行格式的报告
"""

from .suspicious_engine import SuspiciousReportEngine

__all__ = ["SuspiciousReportEngine"]
