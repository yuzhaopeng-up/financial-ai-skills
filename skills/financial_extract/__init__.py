"""
financial_extract — 财报智能提取
"""

from .extract_engine import (
    FinancialExtractEngine,
    FinancialIndicators,
    DupontAnalysis,
    IndustryBenchmark,
    IndustryComparison,
    AlertReport,
    Alert,
)

__all__ = [
    "FinancialExtractEngine",
    "FinancialIndicators",
    "DupontAnalysis",
    "IndustryBenchmark",
    "IndustryComparison",
    "AlertReport",
    "Alert",
]

__version__ = "1.0.0"
