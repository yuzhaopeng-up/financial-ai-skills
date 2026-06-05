# -*- coding: utf-8 -*-
"""
基础格式化器

公共版本 - 不依赖企微特定路径
"""

from typing import Dict, Any


class BaseFormatter:
    """基础格式化器"""
    
    @staticmethod
    def format_text(result: Dict[str, Any]) -> str:
        """通用文本格式化"""
        return str(result)
