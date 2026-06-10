#!/usr/bin/env python3
"""
quant_fund CLI - 量化基金分析命令行工具

用法:
    python3 quant_cli.py generate "量化基金分析 F000001"
    python3 quant_cli.py factor F000001
    python3 quant_cli.py style F000001
    python3 quant_cli.py brinson F000001
    python3 quant_cli.py json F000001
"""

import sys
import re
import argparse
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from quant_engine import QuantFundEngine


def parse_fund_from_command(command: str) -> tuple:
    """
    从命令中解析基金代码和名称
    
    支持格式:
    - "量化基金分析 F000001"
    - "量化基金分析 某量化基金F000001"
    - "F000001"
    """
    # 匹配 F + 6位数字
    match = re.search(r'F(\d{6})', command)
    if match:
        fund_code = f"F{match.group(1)}"
    else:
        fund_code = "F000001"  # 默认
    
    # 提取名称（如果有）
    name_match = re.search(r'分析\s*([^\sF]+)', command)
    fund_name = name_match.group(1).strip() if name_match else None
    
    return fund_code, fund_name


def cmd_generate(fund_code: str, fund_name: str = None, output_format: str = "text"):
    """生成完整分析报告"""
    engine = QuantFundEngine()
    result = engine.analyze(fund_code, fund_name)
    
    if output_format == "json":
        print(result.to_json())
    else:
        print(result.summary())


def cmd_factor(fund_code: str, fund_name: str = None):
    """因子暴露分析"""
    engine = QuantFundEngine()
    exposure = engine.factor_exposure(fund_code, fund_name)
    
    print("=== 因子暴露分析 ===")
    print(f"基金: {fund_code} {fund_name or '某量化基金'}")
    print(f"Alpha (超额收益): {exposure.alpha:+.2%}")
    print(f"Beta (市场敏感度): {exposure.beta:.2f}")
    print(f"SMB (市值因子): {exposure.smb:+.2f}")
    print(f"HML (价值因子): {exposure.hml:+.2f}")
    print(f"RMW (盈利因子): {exposure.rmw:+.2f}")
    print(f"CMA (投资因子): {exposure.cma:+.2f}")
    print(f"MOM (动量因子): {exposure.mom:+.2f}")


def cmd_style(fund_code: str, fund_name: str = None):
    """风格漂移分析"""
    engine = QuantFundEngine()
    drift = engine.style_drift(fund_code, fund_name)
    
    print("=== 风格漂移检测 ===")
    print(f"基金: {fund_code} {fund_name or '某量化基金'}")
    print(f"当前实现风格:")
    for k, v in drift.current_style.items():
        print(f"  {k}: {v:.1%}")
    print(f"契约约定风格:")
    for k, v in drift.contract_style.items():
        print(f"  {k}: {v:.1%}")
    print(f"漂移得分: {drift.drift_score:.2f} (预警: {drift.alert})")


def cmd_brinson(fund_code: str, fund_name: str = None):
    """Brinson归因分析"""
    engine = QuantFundEngine()
    brinson = engine.brinson(fund_code, fund_name)
    
    print("=== Brinson归因分析 ===")
    print(f"基金: {fund_code} {fund_name or '某量化基金'}")
    print(f"选股效应: {brinson.selection_effect:+.2%}")
    print(f"行业配置效应: {brinson.allocation_effect:+.2%}")
    print(f"交互效应: {brinson.interaction_effect:+.2%}")
    print(f"总归因贡献: {brinson.total_attribution:+.2%}")


def cmd_json(fund_code: str, fund_name: str = None):
    """输出JSON格式结果"""
    engine = QuantFundEngine()
    result = engine.analyze(fund_code, fund_name)
    print(result.to_json())


def main():
    parser = argparse.ArgumentParser(
        description="量化基金分析工具 - 基于Fama-French五因子+Carhart四因子模型"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="generate",
        help="子命令: generate, factor, style, brinson, json"
    )
    parser.add_argument(
        "params",
        nargs="?",
        help="命令参数（可以是完整命令字符串或基金代码）"
    )
    
    args = parser.parse_args()
    
    # 处理 "generate" 简写
    if args.command == "generate" and args.params:
        # 可能是完整命令
        fund_code, fund_name = parse_fund_from_command(args.params)
        cmd_generate(fund_code, fund_name)
        return
    
    # 处理 "量化基金分析 xxx" 格式
    if "量化基金分析" in str(args.command) or "F" in str(args.command):
        fund_code, fund_name = parse_fund_from_command(args.command)
        cmd_generate(fund_code, fund_name)
        return
    
    # 解析基金代码
    fund_code = "F000001"
    fund_name = None
    
    if args.params:
        fund_code, fund_name = parse_fund_from_command(args.params)
    
    # 执行命令
    if args.command == "factor":
        cmd_factor(fund_code, fund_name)
    elif args.command == "style":
        cmd_style(fund_code, fund_name)
    elif args.command == "brinson":
        cmd_brinson(fund_code, fund_name)
    elif args.command == "json":
        cmd_json(fund_code, fund_name)
    elif args.command == "generate":
        cmd_generate(fund_code, fund_name)
    else:
        print(f"未知命令: {args.command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
