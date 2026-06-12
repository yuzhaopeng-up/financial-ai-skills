# -*- coding: utf-8 -*-
"""
ALM Skill - 资产负债管理引擎
Bank Asset-Liability Management Skill

导出 ALMEngine 及快捷函数
"""

from .alm_engine import (
    ALMEngine,
    GapItem,
    LCRResult,
    NSFRResult,
    DurationGapResult,
    Warning,
    RiskStatus,
    parse_chinese_input,
    analyze,
    summarize,
)

__all__ = [
    "ALMEngine",
    "GapItem",
    "LCRResult",
    "NSFRResult",
    "DurationGapResult",
    "Warning",
    "RiskStatus",
    "parse_chinese_input",
    "analyze",
    "summarize",
]

__version__ = "1.0.0"
__author__ = "龙马集群AI团队 · ArkClaw"
