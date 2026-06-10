#!/usr/bin/env python3
"""
现金管理CLI入口
用法：
    python3 scripts/cash_cli.py generate "现金管理 制造企业 月现金流5000万"
    python3 scripts/cash_cli.py generate --company 制造企业 --cash-flow 50000000 --volatility 中等波动
    python3 scripts/cash_cli.py info
"""

import sys
import json
import argparse
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from cash_engine import CashManagementEngine


def cmd_generate(args):
    """生成现金管理方案"""
    engine = CashManagementEngine()
    
    # 解析输入
    if args.text:
        text = args.text
        company = None
        cash_flow = None
        volatility = None
    else:
        text = None
        company = args.company
        cash_flow = args.cash_flow
        volatility = args.volatility
    
    # 生成方案
    if args.format == "json":
        output = engine.generate_json(
            text=text,
            company_type=company,
            monthly_cash_flow=cash_flow,
            volatility=volatility,
        )
    else:
        output = engine.generate_text(
            text=text,
            company_type=company,
            monthly_cash_flow=cash_flow,
            volatility=volatility,
        )
    
    print(output)


def cmd_info(args):
    """显示引擎信息"""
    engine = CashManagementEngine()
    print(f"""
【现金管理引擎 v{engine.version}】

支持企业类型：
  - 制造企业（波动特征：高/中/低）
  - 贸易企业（波动特征：高/中/低）
  - 科技企业（波动特征：高/中/低）
  - 房地产企业（波动特征：高/中/低）
  - 建筑企业（波动特征：高/中/低）
  - 医药企业（波动特征：高/中/低）
  - 一般企业

支持产品：
  - 活期存款（0.35%）
  - 通知存款（0.9%，1天/7天）
  - 协定存款（1.15%）
  - 定期存款（1.5%，3月/6月/1年）
  - 大额存单（2.3%，20万起）
  - 结构性存款（2.5%，本金保障）
  - 货币基金（1.8%，T+1）
  - 现金管理类理财（2.0%）

使用示例：
  python3 scripts/cash_cli.py generate "现金管理 制造企业 月现金流5000万"
  python3 scripts/cash_cli.py generate --company 制造企业 --cash-flow 50000000 --volatility 中等波动
  python3 scripts/cash_cli.py generate --format json "制造企业 月现金流5000万 高波动"
""")


def main():
    parser = argparse.ArgumentParser(
        description="现金管理方案生成CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # generate子命令
    gen_parser = subparsers.add_parser("generate", help="生成现金管理方案")
    gen_parser.add_argument("text", nargs="?", help="原始文本输入，如：现金管理 制造企业 月现金流5000万")
    gen_parser.add_argument("--company", "-c", help="企业类型")
    gen_parser.add_argument("--cash-flow", type=float, help="月度现金流规模（元）")
    gen_parser.add_argument("--volatility", "-v", choices=["低波动", "中等波动", "高波动"], help="现金流波动特征")
    gen_parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="输出格式")
    gen_parser.set_defaults(func=cmd_generate)
    
    # info子命令
    info_parser = subparsers.add_parser("info", help="显示引擎信息")
    info_parser.set_defaults(func=cmd_info)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
