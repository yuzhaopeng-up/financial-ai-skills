"""
quant_fund - 量化基金分析引擎
"""

from .quant_engine import (
    QuantFundEngine,
    QuantFundAnalysis,
    FactorExposure,
    StyleDrift,
    BrinsonAttribution,
    PerformanceAttribution,
)

__all__ = [
    "QuantFundEngine",
    "QuantFundAnalysis",
    "FactorExposure",
    "StyleDrift",
    "BrinsonAttribution",
    "PerformanceAttribution",
]

__version__ = "1.0.0"
