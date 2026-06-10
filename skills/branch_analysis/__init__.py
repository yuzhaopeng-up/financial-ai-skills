"""
网点分析技能 (Branch Analysis Skill)
"""

from .branch_engine import (
    BranchAnalysisEngine,
    BranchAnalysisResult,
    CustomerProfile,
    TrafficEstimate,
    SWOT,
    YearForecast,
    ResourceAllocation,
    InputOutputRecommendation,
    parse_cli_input,
)

__version__ = "1.0.0"
__all__ = [
    "BranchAnalysisEngine",
    "BranchAnalysisResult",
    "CustomerProfile",
    "TrafficEstimate",
    "SWOT",
    "YearForecast",
    "ResourceAllocation",
    "InputOutputRecommendation",
    "parse_cli_input",
]
