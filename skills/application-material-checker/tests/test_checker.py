"""单元 + 集成测试。"""
import os
import sys
import json
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, SKILL)

from material_checker import MaterialChecker, MaterialReportFormatter
from checker_engine import MaterialDoc
from rule_runner import parse_date, to_float


# ------------------ 辅助函数 ------------------

def _load(name):
    p = os.path.join(SKILL, "samples", name)
    with open(p) as f:
        data = json.load(f)
    docs = [MaterialDoc(doc_type=d["doc_type"], fields=d.get("fields", {})) for d in data["documents"]]
    return data["scenario"], docs


# ------------------ 基础工具 ------------------

def test_parse_date_iso():
    d = parse_date("2026-06-07")
    assert d and d.year == 2026 and d.month == 6


def test_parse_date_slash():
    d = parse_date("2030/12/31")
    assert d and d.year == 2030


def test_parse_date_long_term():
    d = parse_date("长期")
    assert d and d.year == 9999


def test_to_float():
    assert to_float("1,200,000.50") == 1200000.50
    assert to_float("500元") == 500.0
    assert to_float(None) is None


# ------------------ 场景：通过样本 ------------------

def test_sme_loan_pass():
    scenario, docs = _load("sme_loan_pass.json")
    today = datetime(2026, 6, 7)
    rep = MaterialChecker().check(scenario, docs, today=today)
    assert rep.pass_, MaterialReportFormatter.to_text(rep)
    assert len(rep.missing) == 0
    critical = [i for i in rep.issues if i.severity in ("missing", "expired", "invalid", "mismatch")]
    assert len(critical) == 0, [i.message for i in critical]
    assert rep.score >= 90


# ------------------ 场景：多问题样本 ------------------

def test_sme_loan_fail_detects_all_issues():
    scenario, docs = _load("sme_loan_fail.json")
    today = datetime(2026, 6, 7)
    rep = MaterialChecker().check(scenario, docs, today=today)
    assert not rep.pass_
    rule_ids = {i.rule_id for i in rep.issues}
    # 必备项缺失：tax_payment_record
    assert any("tax_payment_record" in i.doc_type for i in rep.issues if i.severity == "missing"), rule_ids
    # 法人身份证过期
    assert "SME-001" in rule_ids
    # 企业经营时长不足
    assert "SME-002" in rule_ids
    # 流水不足 12 个月
    assert "SME-003" in rule_ids
    # 用途违规
    assert "SME-004" in rule_ids
    # 金额超限
    assert "SME-005" in rule_ids


# ------------------ 场景：房贷部分问题 ------------------

def test_mortgage_partial():
    scenario, docs = _load("mortgage_partial.json")
    today = datetime(2026, 6, 7)
    rep = MaterialChecker().check(scenario, docs, today=today)
    rule_ids = {i.rule_id for i in rep.issues}
    # 已婚未提交配偶证件
    assert "MORT-002" in rule_ids
    # 首付比例不足（1.2M / 6M = 20%）
    assert "MORT-005" in rule_ids
    # 应缺失 spouse_id_card
    assert "spouse_id_card" in rep.missing


# ------------------ 报告渲染 ------------------

def test_report_text_render():
    scenario, docs = _load("sme_loan_fail.json")
    rep = MaterialChecker().check(scenario, docs, today=datetime(2026, 6, 7))
    txt = MaterialReportFormatter.to_text(rep)
    assert "核对报告" in txt
    assert "缺失材料" in txt or "已提交" in txt


def test_report_markdown():
    scenario, docs = _load("sme_loan_pass.json")
    rep = MaterialChecker().check(scenario, docs, today=datetime(2026, 6, 7))
    md = MaterialReportFormatter.to_markdown(rep)
    assert "# 进件材料核对报告" in md


def test_report_wecom_card():
    scenario, docs = _load("mortgage_partial.json")
    rep = MaterialChecker().check(scenario, docs, today=datetime(2026, 6, 7))
    card = MaterialReportFormatter.to_wecom_card(rep)
    assert card["card_type"] == "text_notice"
    assert "horizontal_content_list" in card


# ------------------ 场景列表 ------------------

def test_list_scenarios():
    s = MaterialChecker().list_scenarios()
    assert len(s) >= 3
    keys = {x["key"] for x in s}
    assert "sme_loan" in keys and "personal_mortgage" in keys


def run_all():
    failures = 0
    funcs = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    for fn in funcs:
        try:
            fn()
            print(f"  ✅ {fn.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"  ❌ {fn.__name__}: {e}")
        except Exception as e:
            failures += 1
            print(f"  💥 {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{'='*40}\n{len(funcs)-failures}/{len(funcs)} passed.")
    return failures


if __name__ == "__main__":
    raise SystemExit(run_all())
