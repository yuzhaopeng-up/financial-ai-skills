#!/usr/bin/env python3
"""
寿险理赔审核 V2 CLI 入口

用法：
    python3 scripts/claim_review_cli.py generate "理赔审核 寿险 身故理赔 受益人申请 既往无相关病史 保费缴纳正常"
    python3 scripts/claim_review_cli.py generate "理赔审核 重疾险 恶性肿瘤 初次确诊"
    python3 scripts/claim_review_cli.py generate "理赔审核 意外险 意外身故 无证驾驶"
    python3 scripts/claim_review_cli.py --help
"""

import argparse
import json
import re
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from claim_review_engine import ClaimReviewV2Engine


def parse_natural_language(text: str) -> dict:
    """将自然语言理赔描述解析为结构化参数"""
    text = text.strip()
    result = {
        "insurance_type": "终身寿险",
        "accident_type": "身故",
        "accident_reason": "",
        "hospital_level": "三甲医院",
        "total_expense": 0.0,
        "insurance_paid": 0.0,
        "claim_amount": 0.0,
        "policy_start_date": "",
        "policy_years": 0,
        "premium_paid": True,
        "beneficiary": "",
        "beneficiary_relation": "",
        "death_certificate": False,
        "accident_report": False,
        "sobriety_test": True,
        "license_valid": True,
        "vehicle_type": "",
        "patient_history": {},
    }

    # 险种
    if re.search(r"终身寿险|终身寿", text):
        result["insurance_type"] = "终身寿险"
    elif re.search(r"定期寿险|定期寿", text):
        result["insurance_type"] = "定期寿险"
    elif re.search(r"两全险|两全", text):
        result["insurance_type"] = "两全险"
    elif re.search(r"重疾险|重大疾病|恶性肿瘤", text):
        result["insurance_type"] = "重疾险"
    elif re.search(r"医疗险", text):
        result["insurance_type"] = "医疗险"
    elif re.search(r"意外险|意外", text):
        result["insurance_type"] = "意外险"

    # 出险类型
    if re.search(r"身故|死亡", text):
        result["accident_type"] = "身故"
    elif re.search(r"全残", text):
        result["accident_type"] = "全残"
    elif re.search(r"意外", text):
        result["accident_type"] = "意外"
    elif re.search(r"重疾|确诊", text):
        result["accident_type"] = "重疾"
    elif re.search(r"疾病|住院", text):
        result["accident_type"] = "疾病"

    # 出险原因
    if re.search(r"意外(身故|死亡|伤害)?$", text) or "意外" in text:
        if re.search(r"交通", text):
            result["accident_reason"] = "交通事故意外身故"
        elif re.search(r"溺水", text):
            result["accident_reason"] = "意外溺亡"
        elif re.search(r"坠落", text):
            result["accident_reason"] = "意外高空坠落"
        else:
            result["accident_reason"] = "意外事故"
    elif re.search(r"恶性肿瘤|癌症|癌", text):
        result["accident_reason"] = "恶性肿瘤"
        result["accident_type"] = "重疾"
    elif re.search(r"心梗|心肌梗死", text):
        result["accident_reason"] = "急性心肌梗死"
        result["accident_type"] = "重疾"
    elif re.search(r"脑中风|脑卒中", text):
        result["accident_reason"] = "脑中风后遗症"
        result["accident_type"] = "重疾"
    elif re.search(r"疾病身故|病故", text):
        result["accident_reason"] = "疾病身故"
    elif re.search(r"意外", text):
        result["accident_reason"] = "意外事故"
    else:
        result["accident_reason"] = result["accident_type"]

    # 保单年限
    m = re.search(r"保单(\d+)\s*年", text)
    if m:
        result["policy_years"] = int(m.group(1))
    elif re.search(r"投保(\d+)年|生效(\d+)年|缴费(\d+)年|年", text):
        years_m = re.search(r"(\d+)\s*年", text)
        if years_m:
            result["policy_years"] = int(years_m.group(1))

    # 保费缴纳
    if re.search(r"保费.*未缴|欠费|未缴保费|保费不正常", text):
        result["premium_paid"] = False
    else:
        result["premium_paid"] = True

    # 受益人
    if re.search(r"受益人", text):
        if re.search(r"配偶", text):
            result["beneficiary_relation"] = "配偶"
        elif re.search(r"子女|孩子|儿子|女儿", text):
            result["beneficiary_relation"] = "子女"
        elif re.search(r"父母", text):
            result["beneficiary_relation"] = "父母"
        result["beneficiary"] = "指定受益人"

    # 既往病史
    if re.search(r"既往.*无|无相关.*病史|无既往症|无.*病史", text):
        result["patient_history"] = {"diseases": [], "declared": True}
    elif re.search(r"有.*既往|既往.*有病|带病", text):
        result["patient_history"] = {"diseases": ["未告知疾病"], "declared": False}

    # 死亡证明
    if re.search(r"死亡证明|死亡.*有|已.*死亡", text):
        result["death_certificate"] = True
    elif re.search(r"无.*死亡证明|缺少.*死亡", text):
        result["death_certificate"] = False

    # 事故证明
    if re.search(r"事故证明|事故.*有|已.*事故", text):
        result["accident_report"] = True
    elif re.search(r"无.*事故证明|缺少.*事故", text):
        result["accident_report"] = False

    # 酒驾
    if re.search(r"酒驾|醉酒|饮酒", text):
        result["sobriety_test"] = False
    elif re.search(r"无.*酒驾|未.*饮酒|正常", text):
        result["sobriety_test"] = True

    # 无证驾驶
    if re.search(r"无证驾驶|无驾照", text):
        result["license_valid"] = False
        result["vehicle_type"] = "汽车"
    elif re.search(r"有驾照|驾照正常", text):
        result["license_valid"] = True

    # 理赔金额
    m = re.search(r"理赔(\d+\.?\d*)\s*[万wW]?", text)
    if m:
        result["claim_amount"] = float(m.group(1)) * 10000
    else:
        m = re.search(r"(\d+\.?\d*)\s*[万wW]?(?:理赔|赔付)", text)
        if m:
            result["claim_amount"] = float(m.group(1)) * 10000

    # 住院花费
    m = re.search(r"花费?(\d+\.?\d*)\s*[万wW]?", text)
    if m:
        result["total_expense"] = float(m.group(1)) * 10000
    else:
        m = re.search(r"花费?(\d+\.?\d*)\s*元", text)
        if m:
            result["total_expense"] = float(m.group(1))

    # 医院等级
    if re.search(r"三甲", text):
        result["hospital_level"] = "三甲医院"
    elif re.search(r"三乙", text):
        result["hospital_level"] = "三乙医院"
    elif re.search(r"二甲", text):
        result["hospital_level"] = "二甲医院"

    # 医保报销
    m = re.search(r"医保(报销)?(\d+\.?\d*)\s*[万wW]?", text)
    if m:
        result["insurance_paid"] = float(m.group(2)) * 10000
    else:
        m = re.search(r"医保(报销)?(\d+\.?\d*)\s*元", text)
        if m:
            result["insurance_paid"] = float(m.group(2))

    # 默认保单生效日期
    if result["policy_years"] > 0:
        years_ago = datetime.now().year - result["policy_years"]
        result["policy_start_date"] = f"{years_ago}-01-01"

    # 默认理赔金额（寿险身故默认50万）
    if result["claim_amount"] == 0 and result["insurance_type"] in ("终身寿险", "定期寿险", "两全险"):
        if result["accident_type"] in ("身故", "全残"):
            result["claim_amount"] = 500000.0

    return result


def format_result(result: dict) -> str:
    """将审核结果格式化为友好文本输出"""
    decision = result.get("review_decision", {})
    audit = result.get("audit_points", {})
    calc = result.get("claim_calculation", {})
    fraud = result.get("fraud_check", {})
    proc = result.get("processing_time", {})

    # 决策颜色标记
    code = decision.get("code", "")
    if code == "APPROVED":
        result_icon = "✅"
    elif code == "PROPORTIONAL":
        result_icon = "⚠️"
    elif code == "PENDING_MATERIALS":
        result_icon = "📋"
    else:
        result_icon = "❌"

    lines = [
        "=" * 58,
        "           寿险理赔审核报告 V2",
        "=" * 58,
        f"  案件编号  ：{result.get('claim_id', 'N/A')}",
        f"  生成时间  ：{result.get('timestamp', '')}",
        "",
        f"【审核结果】 {result_icon} {decision.get('result', '未知')}",
    ]

    if decision.get("reason"):
        lines.append(f"  决策依据  ：{decision.get('reason', '')}")

    # 审核要点
    lines.append("")
    lines.append("【审核要点】")
    history = audit.get("history_relevance", {})
    if history.get("has_pre_existing"):
        lines.append(f"  📌 既往症：{'有关联 ⚠️' if history.get('related') else '无关联'}")
        for d in history.get("details", []):
            lines.append(f"     - {d}")
    else:
        lines.append("  ✅ 既往症：无既往症或已如实告知")

    excl = audit.get("exclusion_clauses", {})
    if excl.get("triggered"):
        lines.append("  ⚠️ 责任免除触发：")
        for e in excl.get("triggered", []):
            lines.append(f"     - {e}")
    else:
        lines.append("  ✅ 责任免除：未触发")

    policy = audit.get("policy_validity", {})
    if policy.get("valid"):
        lines.append("  ✅ 保单有效性：有效")
    else:
        lines.append("  ❌ 保单有效性：无效")
        for issue in policy.get("issues", []):
            lines.append(f"     - {issue}")

    # 理赔金额
    lines.extend([
        "",
        "【理赔金额】",
        f"  申请理赔额：¥{calc.get('claim_amount', 0):,.2f}",
        f"  审核赔付额：¥{calc.get('final_payment', 0):,.2f}",
    ])
    for b in calc.get("breakdown", []):
        lines.append(f"    • {b}")

    # 反欺诈
    lines.extend([
        "",
        "【反欺诈检查】",
        f"  风险评分：{fraud.get('score', 0)} / 100",
        f"  风险等级：{fraud.get('risk_level', '未知')}",
    ])
    for flag in fraud.get("flags", []):
        lines.append(f"  ⚠️  {flag}")

    # 处理时效
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

    lines.append("=" * 58)
    lines.append("  ⚠️  本报告仅供参考，最终理赔决定需人工审核确认")
    lines.append("=" * 58)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="寿险理赔审核引擎 V2 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="子命令")

    # generate 子命令
    gen = sub.add_parser("generate", help="从自然语言描述生成理赔审核报告")
    gen.add_argument("description", nargs="*", help="理赔案件描述")
    gen.add_argument("--json", action="store_true", help="输出JSON格式")
    gen.add_argument(
        "--policy-terms",
        default="{}",
        help="保单条款 JSON 字符串（可选）",
    )

    args = parser.parse_args()

    if args.command == "generate":
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

        if policy_terms:
            params["policy_terms"] = policy_terms

        # 调用引擎
        engine = ClaimReviewV2Engine()
        result = engine.review(
            insurance_type=params["insurance_type"],
            accident_type=params["accident_type"],
            accident_reason=params["accident_reason"],
            hospital_level=params["hospital_level"],
            total_expense=params["total_expense"],
            insurance_paid=params["insurance_paid"],
            claim_amount=params["claim_amount"],
            policy_start_date=params["policy_start_date"],
            policy_years=params["policy_years"],
            premium_paid=params["premium_paid"],
            beneficiary=params["beneficiary"],
            beneficiary_relation=params["beneficiary_relation"],
            death_certificate=params["death_certificate"],
            accident_report=params["accident_report"],
            sobriety_test=params["sobriety_test"],
            license_valid=params["license_valid"],
            vehicle_type=params["vehicle_type"],
            patient_history=params["patient_history"],
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
