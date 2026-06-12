# -*- coding: utf-8 -*-
"""
基金经理画像引擎
Fund Manager Profile Skill

导出 FundManagerEngine 及快捷函数
"""

from .manager_engine import (
    FundManagerEngine,
    get_profile,
    list_managers,
)

__all__ = [
    "FundManagerEngine",
    "get_profile",
    "list_managers",
]

__version__ = "1.0.0"
