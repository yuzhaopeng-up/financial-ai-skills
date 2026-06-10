#!/usr/bin/env python3
"""
理赔分析 CLI 入口

用法：
    python3 scripts/claim_cli.py generate "理赔分析 医疗险 住院花费8万 就诊三甲医院 医保报销3万"
    python3 scripts/claim_cli.py --help
"""

import argparse
import json
import re
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from claim_engine import ClaimAnalysisEngine


def parse_natural_language(text: str) -> dict:
    """将自然语言理赔描述解析为结构化参数"""
    text = text.strip()
    result = {
        "insurance_type": "医疗险",
        "total_expense": 0.0,
        "hospital_level": "",
        "insurance_paid": 0.0,
        "accident_type": "疾病",
        "admission_date": "",
        "discharge_date": "",
    }

    # 险种
    if re.search(r"医疗险|住院医疗|门诊医疗", text):
        result["insurance_type"] = "医疗险"
    elif re.search(r"意外险|意外医疗", text):
        result["insurance_type"] = "意外险"
    elif re.search(r"重疾险|重大疾病", text):
        result["insurance_type"] = "重疾险"
    elif re.search(r"寿险|人寿保险", text):
        result["insurance_type"] = "寿险"

    # 总花费
    m = re.search(r"花费?(\d+\.?\d*)\s*[万wW]?", text)
    if m:
        result["total_expense"] = float(m.group(1)) * 10000
    else:
        m = re.search(r"花费?(\d+\.?\d*)\s*元", text)
        if m:
            result["total_expense"] = float(m.group(1))

    # 医院等级
    if re.search(r"三甲|三甲医院", text):
        result["hospital_level"] = "三甲医院"
    elif re.search(r"三乙|三乙医院", text):
        result["hospital_level"] = "三乙医院"
    elif re.search(r"二甲|二甲医院", text):
        result["hospital_level"] = "二甲医院"
    else:
        result["hospital_level"] = "其他"

    # 医保报销
    m = re.search(r"医保(报销)?(\d+\.?\d*)\s*[万wW]?", text)
    if m:
        result["insurance_paid"] = float(m.group(2)) * 10000
    else:
        m = re.search(r"医保(报销)?(\d+\.?\d*)\s*元", text)
        if m:
            result["insurance_paid"] = float(m.group(2))

    # 出险类型
    if re.search(r"意外", text):
        result["accident_type"] = "意外"
    elif re.search(r"手术", text):
        result["accident_type"] = "手术"
    else:
        result["accident_type"] = "疾病"

    return result


def format_result(result: dict) -> str:
    """将分析结果格式化为友好文本输出"""
    liability = result.get("liability_assessment", {})
    fraud = result.get("fraud_check", {})
    calc = result.get("claim_calculation", {})
    proc = result.get("processing_time", {})

    lines = [
        "=" * 56,
        "           理赔分析报告",
        "=" * 56,
        f"  案件编号  ：{result.get('claim_id', 'N/A')}",
        f"  生成时间  ：{result.get('timestamp', '')}",
        "",
        "【责任认定】",
        f"  结论：{liability.get('decision', '未知')}",
        "  保障明细：",
    ]
    for detail in liability.get("coverage_details", []):
        lines.append(f"    ✅ {detail}")
    if liability.get("exclusions"):
        lines.append("  除外责任：")
        for ex in liability.get("exclusions", []):
            lines.append(f"    ❌ {ex}")

    lines.extend([
        "",
        "【反欺诈检查】",
        f"  风险评分  ：{fraud.get('score', 0)} / 100",
        f"  风险等级  ：{fraud.get('risk_level', '未知')}",
    ])
    for flag in fraud.get("flags", []):
        lines.append(f"  ⚠️  {flag}")

    lines.extend([
        "",
        "【理赔金额计算】",
        f"  住院总花费  ：¥{calc.get('total_expense', 0):,.2f}",
        f"  医保已报销  ：¥{calc.get('insurance_paid', 0):,.2f}",
        f"  免赔额      ：¥{calc.get('deductible', 0):,.2f}",
        f"  赔付比例    ：{calc.get('co_insurance_rate', 0) * 100:.0f}%",
        f"  最终赔付额  ：¥{calc.get('final_reimbursement', 0):,.2f}",
    ])

    lines.extend([
        "",
        "【审核要点】",
    ])
    for point in result.get("audit_points", []):
        lines.append(f"  📋 {point}")

    lines.extend([
        "",
        "【处理时效】",
        f"  类型：{proc.get('category', '普通件')}（{proc.get('days', 7)}个工作日）",
        f"  时效截止：{proc.get('deadline', '未知')}",
    ])

    if result.get("next_steps"):
        lines.append("")
        lines.append("【后续步骤】")
        for step in result.get("next_steps", []):
            lines.append(f"  ▶ {step}")

    lines.append("=" * 56)
    lines.append("  ⚠️  本报告仅供参考，最终理赔决定需人工审核确认")
    lines.append("=" * 56)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="理赔分析引擎 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="子命令")

    # generate 子命令
    gen = sub.add_parser("generate", help="从自然语言描述生成理赔分析报告")
    gen.add_argument("description", nargs="*", help="理赔案件描述")
    gen.add_argument("--json", action="store_true", help="输出JSON格式")
    gen.add_argument(
        "--policy-terms",
        default="{}",
        help="保单条款 JSON 字符串（可选，覆盖默认条款）",
    )

    args = parser.parse_args()

    if args.command == "generate":
        # 拼接描述
        if not args.description:
            print("错误：需要提供理赔案件描述", file=sys.stderr)
            sys.exit(1)

        raw_text = " ".join(args.description)

        # 解析参数
        params = parse_natural_language(raw_text)
        print(f"[解析参数] {json.dumps(params, ensure_ascii=False, indent=2)}")

        # 读取自定义保单条款
        try:
            policy_terms = json.loads(args.policy_terms)
        except Exception:
            policy_terms = {}

        # 调用引擎
        engine = ClaimAnalysisEngine()
        result = engine.analyze(
            insurance_type=params["insurance_type"],
            accident_type=params["accident_type"],
            hospital_level=params["hospital_level"],
            total_expense=params["total_expense"],
            insurance_paid=params["insurance_paid"],
            policy_terms=policy_terms if policy_terms else None,
        )

        # 输出
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(format_result(result))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
