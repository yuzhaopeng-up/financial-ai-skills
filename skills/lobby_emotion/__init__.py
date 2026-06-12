"""
lobby_emotion - 客户情绪识别技能

导出 LobbyEmotionEngine 及 EmotionResult 数据类
"""

from .emotion_engine import LobbyEmotionEngine, EmotionResult, EmotionState

__all__ = ["LobbyEmotionEngine", "EmotionResult", "EmotionState"]
__version__ = "1.0.0"
