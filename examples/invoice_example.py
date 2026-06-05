# -*- coding: utf-8 -*-
"""
发票查验示例

演示如何使用 InvoiceEngine 进行发票查验
"""

import sys
sys.path.insert(0, "/home/ubuntu/Workspace/financial-ai-skills")

from skills.financial_intelligence.engines import InvoiceEngine


def main():
    engine = InvoiceEngine()
    
    # 示例1: 查验单张发票
    print("=" * 60)
    print("示例1: 单张发票查验")
    print("=" * 60)
    
    result = engine.verify(invoice_code="011001900111", invoice_no="12345678")
    print(f"状态: {result['status']}")
    print(f"开票单位: {result.get('seller_name', '-')}")
    print(f"金额: ¥{result.get('amount', 0):,.2f}")
    print(f"合规评分: {result.get('compliance', {}).get('score', 0)}/100")
    print()
    
    # 示例2: 批量查验
    print("=" * 60)
    print("示例2: 批量发票查验")
    print("=" * 60)
    
    invoices = [
        {"code": "011001900111", "no": "12345678"},
        {"code": "011001900111", "no": "87654321"},
        {"code": "011001900111", "no": "11111112"},
    ]
    
    batch_result = engine.batch_verify(invoices)
    print(f"{batch_result['summary']}")
    print(f"总金额: ¥{batch_result['total_amount']:,.2f}")
    print()
    
    # 示例3: 从文本提取
    print("=" * 60)
    print("示例3: 从文本提取发票信息")
    print("=" * 60)
    
    text = "发票代码: 011001900111, 发票号码: 12345678"
    result = engine.verify(invoice_text=text)
    print(f"提取结果: {result['status']}")


if __name__ == "__main__":
    main()
