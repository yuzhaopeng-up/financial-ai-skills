"""Customer Persona Skill - 360 度客户画像生成器。

输入客户基本信息（自然语言或结构化），输出：
  - RFM 标签（Recency/Frequency/Monetary）
  - 客户生命周期阶段
  - 推荐产品清单
  - 触达渠道建议
  - 营销话术钩子

零外部依赖，纯规则引擎 + 评分模型。
"""
from .persona_engine import (
    PersonaEngine, CustomerInput, CustomerPersona,
    parse_natural_language,
)
from .persona_formatter import PersonaFormatter

__version__ = "1.0.0"
__all__ = [
    "PersonaEngine", "CustomerInput", "CustomerPersona",
    "PersonaFormatter", "parse_natural_language",
]
