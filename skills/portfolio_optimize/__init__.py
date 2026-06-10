"""
portfolio_optimize - 投资组合优化引擎
基于有效前沿理论（Efficient Frontier）的 Markowitz 均值-方差优化
"""

from .port_opt_engine import (
    PortfolioOptimizeEngine,
    PortfolioMetrics,
    AdjustmentItem,
    Asset,
    BUILTIN_ASSETS,
    parse_cli_args,
)

__all__ = [
    "PortfolioOptimizeEngine",
    "PortfolioMetrics",
    "AdjustmentItem",
    "Asset",
    "BUILTIN_ASSETS",
    "parse_cli_args",
]

__version__ = "1.0.0"
