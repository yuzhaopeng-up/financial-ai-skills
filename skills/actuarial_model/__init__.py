"""
精算模型技能
提供保费定价、准备金评估、偿付能力评估功能
内置中国人寿保险业经验生命表（CL1/CL2）
"""

from .actuarial_engine import ActuarialModelEngine, quick_calculate

__all__ = ["ActuarialModelEngine", "quick_calculate"]
