#!/usr/bin/env python3
"""
续保提醒 CLI 入口

用法:
    python3 scripts/renewal_cli.py generate "续保提醒 客户张总 终身寿险 年缴2万 已缴10年 续期将至"
    python3 scripts/renewal_cli.py wecom "客户张总 终身寿险 紧急"
    python3 scripts/renewal_cli.py --help
"""

import argparse
import json
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from renewal_engine import RenewalAlertEngine


def cmd_generate(args):
    """生成续保提醒分析"""
    engine = RenewalAlertEngine()
    params = engine.parse_cli_input(args.text)

    print(f"\n{'='*60}")
    print(f"续保提醒分析")
    print(f"{'='*60}")
    print(f"客户姓名: {params['customer_name']}")
    print(f"险种: {params['product_type']}")
    print(f"年缴保费: {params['annual_premium']/10000:.2f}万元" if params['annual_premium'] else "年缴保费: 未知")
    print(f"已缴年限: {params['paid_years']}年")
    print(f"保障期限: {params['coverage_years']}年" if params['coverage_years'] else "保障期限: 终身")
    print(f"续期保费: {params['renewal_premium']/10000:.2f}万元" if params['renewal_premium'] else "续期保费: 同年缴保费")
    print(f"{'='*60}\n")

    result = engine.analyze(params)

    # 打印分析结果
    print(f"【续保建议】: {result['recommendation']}")
    print(f"【挽留优先级】: {result['priority']}")
    print(f"【风险等级】: {result['analysis']['risk_level']}")
    print(f"已缴比例: {result['analysis']['paid_ratio']*100:.1f}%")
    print(f"现金价值比例: {result['analysis']['cash_value_ratio']*100:.1f}%")
    print()

    if result['alternative']:
        print(f"【替代方案】")
        print(f"{result['alternative']}")
        print()

    print(f"【挽留策略】")
    print(f"{result['retention_strategy']}")
    print()

    print(f"【续保话术】")
    print(f"{result['renewal_script']}")
    print()

    # JSON输出
    if args.json:
        print("\n--- JSON输出 ---\n")
        print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_wecom(args):
    """生成企微卡片内容"""
    from wecom_integration import generate_wecom_card

    parts = args.text.split()
    customer_name = parts[0] if len(parts) > 0 else "客户"
    product_type = parts[1] if len(parts) > 1 else "保单"
    priority = parts[2] if len(parts) > 2 else "一般"

    card = generate_wecom_card(
        customer_name=customer_name,
        product_type=product_type,
        priority=priority,
        analysis_result=None
    )
    print(json.dumps(card, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="续保提醒技能 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 scripts/renewal_cli.py generate "续保提醒 客户张总 终身寿险 年缴2万 已缴10年 续期将至"
  python3 scripts/renewal_cli.py generate "续保提醒 客户李女士 年金险 年缴5万 已缴5年 保障期限20年" --json
  python3 scripts/renewal_cli.py wecom "客户张总 终身寿险 紧急"
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成续保提醒分析")
    gen_parser.add_argument("text", help="续保提醒文本描述")
    gen_parser.add_argument("--json", action="store_true", help="输出JSON格式")

    # wecom 命令
    wecom_parser = subparsers.add_parser("wecom", help="生成企微卡片")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "wecom":
        cmd_wecom(args)
    else:
        # 默认当作generate处理
        if args.text or len(sys.argv) > 1:
            gen_parser = argparse.ArgumentParser()
            gen_parser.add_argument("text", help="续保提醒文本描述")
            gen_parser.add_argument("--json", action="store_true", help="输出JSON格式")
            gen_parser.add_argument("remainder", nargs=argparse.REMAINDER)
            args_text = args.text or " ".join(sys.argv[1:])
            args_obj = gen_parser.parse_args([args_text])
            cmd_generate(args_obj)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
