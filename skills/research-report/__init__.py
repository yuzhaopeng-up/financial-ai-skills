"""research-report Skill - 投研报告自动生成。"""
from .report_engine import ReportEngine, ReportRequest, ResearchReport, parse_request
from .report_formatter import ReportFormatter

__version__ = "1.0.0"
__all__ = ["ReportEngine", "ReportRequest", "ResearchReport",
           "ReportFormatter", "parse_request"]
