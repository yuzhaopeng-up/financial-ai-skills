"""
Lobby Queue Skill — 排队预警 + 智能开台

基于等候人数×平均办理时长/服务窗口数计算排队指数（0-100），
输出预警等级（红/黄/绿）+ 开台建议 + 客户等候预估 + 历史对比分析。
"""

from .queue_engine import (
    LobbyQueueEngine,
    QueueData,
    QueueAnalysis,
    analyze_queue,
)

__all__ = [
    "LobbyQueueEngine",
    "QueueData",
    "QueueAnalysis",
    "analyze_queue",
]

__version__ = "1.0.0"
