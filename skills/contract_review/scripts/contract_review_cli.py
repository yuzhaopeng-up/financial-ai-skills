#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合同智能审查引擎 CLI
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contract_review_engine import ContractReviewEngine


def main():
    engine = ContractReviewEngine()
    
    print("🦞 合同智能审查引擎 v1.0")
    print()
    
    # 示例合同
    sample = """
    贷款合同样本：
    利率按另行约定执行
    担保范围包括一切债务
    违约金为本金的30%
    管辖法院待定
    """
    
    result = engine.review_contract(sample)
    print(engine.format_text(result))


if __name__ == "__main__":
    sys.exit(main())
