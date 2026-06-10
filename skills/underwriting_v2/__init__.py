"""
UnderwritingV2 券商两融智能核保引擎
"""

from .underwriting_v2_engine import (
    UnderwritingV2Engine,
    underwrite,
    underwrite_from_text,
)

__all__ = [
    "UnderwritingV2Engine",
    "underwrite",
    "underwrite_from_text",
]

__version__ = "2.0.0"
