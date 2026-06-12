"""
大宗交易技能 (Block Trade Analyzer)
大宗交易分析引擎，支持折溢价率分析、市场冲击评估、流动性评价、合规提示及历史案例参考
"""

from block_engine import (
    BlockTradeEngine,
    BlockTradeResult,
    ComplianceAlert,
    SimilarCase,
    HISTORICAL_CASES,
    analyze_block_trade,
)

__all__ = [
    "BlockTradeEngine",
    "BlockTradeResult",
    "ComplianceAlert",
    "SimilarCase",
    "HISTORICAL_CASES",
    "analyze_block_trade",
]

__version__ = "1.0.0"
