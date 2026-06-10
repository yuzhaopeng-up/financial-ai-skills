#!/usr/bin/env python3
"""
Tax Planning CLI - 税务筹划命令行工具
用法:
    python3 scripts/tax_cli.py generate "税务筹划 某科技公司 年营收5000万 研发投入300万"
    python3 scripts/tax_cli.py generate "税务筹划 某制造企业 年营收2亿元 研发投入2000万 员工500人"
    python3 scripts/tax_cli.py compare "对比 A公司（高新，年营收1亿）vs B公司（小微，年营收8000万）"
    python3 scripts/tax_cli.py parse "年营收5000万 研发投入300万"
"""

import sys
import os
import json
import argparse

# 将父目录加入路径以便导入 tax_engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tax_engine import TaxPlanningEngine, parse_input_text


def cmd_generate(text: str, output_format: str = "text"):
    """生成税务筹划方案"""
    engine = TaxPlanningEngine()

    # 解析输入文本
    params = parse_input_text(text)

    # 生成筹划结果
    result = engine.generate(**params)

    if output_format == "json":
        print(engine.format_json(result))
    else:
        print(engine.format_text(result))

    return result


def cmd_compare(text: str, output_format: str = "text"):
    """对比两个公司的税务筹划方案"""
    engine = TaxPlanningEngine()

    # 解析对比文本
    # 格式: "对比 A公司（高新，年营收1亿）vs B公司（小微，年营收8000万）"
    import re
    match = re.search(r'([^（vs]+)\s*vs\s*([^（]+)', text)
    if not match:
        print("对比格式有误，请使用: 对比 A公司（条件）vs B公司（条件）")
        return

    company_a_text = match.group(1).strip()
    company_b_text = match.group(2).strip()

    # 简单解析公司名称和条件
    params_a = _simple_parse(company_a_text)
    params_b = _simple_parse(company_b_text)

    result_a = engine.generate(**params_a)
    result_b = engine.generate(**params_b)

    if output_format == "json":
        print(json.dumps({"company_a": result_a, "company_b": result_b}, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"       税务筹划对比分析")
        print(f"{'='*60}")
        print(f"\n▶ 公司A: {params_a.get('company_name', 'A公司')}")
        print(engine.format_text(result_a).split('=')[2])  # 只取summary部分

        print(f"\n{'='*60}")
        print(f"\n▶ 公司B: {params_b.get('company_name', 'B公司')}")
        print(engine.format_text(result_b).split('=')[2])


def _simple_parse(text: str) -> dict:
    """简化解析公司条件"""
    params = {"company_name": text if len(text) < 10 else text[:8] + "公司"}

    # 提取营收
    revenue_match = re.search(r'营?收?(\d+(?:\.\d+)?)\s*(?:亿|万)', text)
    if revenue_match:
        amount = float(revenue_match.group(1))
        if '亿' in text:
            params['annual_revenue'] = amount * 100000000
        else:
            params['annual_revenue'] = amount * 10000

    # 提取研发
    rd_match = re.search(r'研发?(\d+(?:\.\d+)?)\s*(?:亿|万)', text)
    if rd_match:
        amount = float(rd_match.group(1))
        if '亿' in text:
            params['rd_expense'] = amount * 100000000
        else:
            params['rd_expense'] = amount * 10000

    # 判断类型
    params['is_high_tech'] = '高新' in text
    params['is_small_micro'] = '小微' in text

    # 默认值
    params.setdefault('annual_revenue', 50000000)
    params.setdefault('rd_expense', 3000000)
    params.setdefault('employee_count', 50)
    params.setdefault('total_assets', 20000000)
    params.setdefault('industry', '科技')
    params.setdefault('estimated_profit_rate', 0.15)
    params.setdefault('vat_type', '一般纳税人')

    return params


def cmd_parse(text: str):
    """解析输入文本，查看参数提取结果"""
    params = parse_input_text(text)
    print("解析结果:")
    print(json.dumps(params, ensure_ascii=False, indent=2))
    return params


def main():
    parser = argparse.ArgumentParser(description="税务筹划CLI工具")
    parser.add_argument("command", choices=["generate", "compare", "parse"], help="命令")
    parser.add_argument("text", help="输入文本")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="输出格式")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args.text, args.format)
    elif args.command == "compare":
        cmd_compare(args.text, args.format)
    elif args.command == "parse":
        cmd_parse(args.text)


if __name__ == "__main__":
    main()
