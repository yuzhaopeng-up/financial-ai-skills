"""
企业对公开户技能（corp_account_opening）
CorpAccountEngine: 企业对公开户全流程智能指引引擎
"""

from .account_engine import CorpAccountEngine, generate_account_opening_report

__all__ = ["CorpAccountEngine", "generate_account_opening_report"]
__version__ = "1.0.0"
