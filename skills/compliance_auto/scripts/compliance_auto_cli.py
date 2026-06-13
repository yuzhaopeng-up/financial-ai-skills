#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务流程合规性自动检查引擎 CLI
用法:
    python compliance_auto_cli.py
    python compliance_auto_cli.py --text "操作记录"
    python compliance_auto_cli.py --text "操作记录" --type "贷款业务" --format json
"""

import argparse
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compliance_auto_engine import ComplianceAutoEngine


def main():
    parser = argparse.ArgumentParser(description="业务流程合规性自动检查引擎")
    parser.add_argument("--text", "-t", type=str, help="操作记录文本")
    parser.add_argument("--type", "-b", type=str, help="业务类型")
    parser.add_argument("--rules", "-r", type=str, help="指定规则ID，逗号分隔，如: C001,C002")
    parser.add_argument("--format", "-f", type=str, choices=["text", "json", "card"], default="text", help="输出格式")
    args = parser.parse_args()

    engine = ComplianceAutoEngine(api_mode=(args.format == "json"))

    # 默认测试用例
    default_text = """
    客户张三分期购买手机贷款15000元，
    年化利率18%，略超LPR4倍，
    贷款用途为日常消费，核对贷款去向时发现资金流入股市，
    客户风险测评已过期13个月，
    未签署产品风险揭示书，
    销售人员未进行双录
    """

    text = args.text if args.text else default_text
    business_type = args.type if args.type else None

    # 指定规则
    specific_rules = None
    if args.rules:
        specific_rules = [r.strip() for r in args.rules.split(",")]

    # 执行检查
    result = engine.check_compliance(text, business_type, specific_rules)

    # 输出
    if args.format == "json":
        print(engine.format_json(result))
    elif args.format == "card":
        card = engine.format_wecom_card(result)
        print(json.dumps(card, ensure_ascii=False, indent=2))
    else:
        print(engine.format_text(result))

    # 返回状态码
    if result["risk_level"] == "high":
        return 2
    elif result["risk_level"] == "medium":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
