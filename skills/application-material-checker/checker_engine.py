"""
Application Material Checker - 进件材料自动核对引擎
=====================================================
基于规则的"完整性 + 合规性"双维核对引擎。

输入：业务场景 + 已上传材料列表（OCR 后的结构化字段）
输出：缺失项 / 合规问题 / 自动核对报告（含整改建议）

设计目标：
- 覆盖银行 3 大典型业务场景：对公开户、小微贷款、个人房贷
- 单据类型 ≥ 10 种（身份证/营业执照/银行流水/合同/收入证明 等）
- 规则可配置（rules/*.yaml 风格，使用 JSON 持久化）
- 与 financial-intelligence/invoice_engine 复用 OCR 字段
- 零外部依赖

作者: ArkClaw (Financial AI Community)
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# ============================================================
# 数据结构
# ============================================================


@dataclass
class MaterialDoc:
    """已上传的单据 —— 由 OCR 系统填充。"""
    doc_type: str                       # "id_card" | "business_license" | "bank_statement" | ...
    file_name: str = ""
    fields: Dict[str, Any] = field(default_factory=dict)  # OCR 抽取字段
    confidence: float = 1.0
    upload_time: str = ""

    def get(self, k: str, default=None):
        return self.fields.get(k, default)


@dataclass
class CheckIssue:
    """单条问题。"""
    severity: str          # "missing" | "expired" | "mismatch" | "invalid" | "warning"
    doc_type: str
    field: str = ""
    message: str = ""
    suggestion: str = ""
    rule_id: str = ""


@dataclass
class CheckReport:
    """核对报告。"""
    scenario: str
    submitted: List[str]                # 已提交的 doc_type
    required: List[str]                 # 应提交的
    missing: List[str]                  # 缺失的
    issues: List[CheckIssue]
    score: float                        # 0-100
    pass_: bool
    summary: str
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["pass"] = d.pop("pass_")
        return d


# ============================================================
# 场景规则库
# ============================================================

# 关键字段校验规则 (key → (regex, hint))
FIELD_RULES: Dict[str, Tuple[str, str]] = {
    "id_no":           (r"^\d{17}[\dXx]$",                 "身份证号必须为 18 位"),
    "phone":           (r"^1[3-9]\d{9}$",                  "手机号格式不正确"),
    "uscc":            (r"^[0-9A-HJ-NPQRTUWXY]{18}$",      "统一社会信用代码 18 位字母数字组合"),
    "amount":          (r"^\d+(\.\d{1,2})?$",              "金额格式应为数字（最多 2 位小数）"),
    "date":            (r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$",  "日期格式应为 YYYY-MM-DD"),
    "bank_card":       (r"^\d{15,19}$",                    "银行卡号应为 15-19 位数字"),
}


def _scenario_rules() -> Dict[str, Dict[str, Any]]:
    """业务场景规则字典 —— 描述每个场景需要哪些材料和必备字段。"""
    return {
        # ----------- 对公开户 -----------
        "corporate_account_opening": {
            "name": "对公账户开户",
            "required_docs": [
                "business_license",     # 营业执照
                "legal_id_card",        # 法人身份证
                "tax_registration",     # 税务登记
                "company_seal_sample",  # 印鉴样本
                "account_opening_form", # 开户申请书
            ],
            "optional_docs": ["articles_of_association", "shareholder_list"],
            "doc_field_requirements": {
                "business_license": ["uscc", "company_name", "legal_person", "registered_capital", "establish_date", "business_scope"],
                "legal_id_card": ["id_no", "name", "valid_to"],
                "tax_registration": ["tax_no", "company_name"],
                "company_seal_sample": ["seal_image"],
                "account_opening_form": ["company_name", "applicant", "purpose", "signature_date"],
            },
            "extra_rules": [
                {"id": "RG-001", "type": "match_name",
                 "src": ("business_license", "company_name"),
                 "dst": ("account_opening_form", "company_name"),
                 "msg": "营业执照与开户申请书的公司名称不一致"},
                {"id": "RG-002", "type": "match_name",
                 "src": ("business_license", "legal_person"),
                 "dst": ("legal_id_card", "name"),
                 "msg": "营业执照法人与身份证姓名不一致"},
                {"id": "RG-003", "type": "not_expired",
                 "src": ("legal_id_card", "valid_to"),
                 "msg": "法人身份证已过期"},
                {"id": "RG-004", "type": "uscc_match",
                 "src": ("business_license", "uscc"),
                 "dst": ("tax_registration", "tax_no"),
                 "msg": "营业执照统一社会信用代码与税务登记号不一致"},
            ],
        },

        # ----------- 小微贷款 -----------
        "sme_loan": {
            "name": "小微企业贷款",
            "required_docs": [
                "business_license",
                "legal_id_card",
                "bank_statement",   # 近 12 个月对公流水
                "tax_payment_record",
                "loan_application", # 贷款申请表
            ],
            "optional_docs": ["financial_statement", "industry_license", "collateral_evaluation"],
            "doc_field_requirements": {
                "business_license": ["uscc", "company_name", "legal_person", "establish_date"],
                "legal_id_card": ["id_no", "name", "valid_to"],
                "bank_statement": ["account_no", "period_start", "period_end", "total_credit", "total_debit"],
                "tax_payment_record": ["tax_no", "amount", "period"],
                "loan_application": ["amount", "purpose", "term_months", "applicant"],
            },
            "extra_rules": [
                {"id": "SME-001", "type": "not_expired",
                 "src": ("legal_id_card", "valid_to"),
                 "msg": "法人身份证已过期"},
                {"id": "SME-002", "type": "operating_age",
                 "src": ("business_license", "establish_date"),
                 "min_months": 12,
                 "msg": "企业经营时长不足 12 个月，不满足申请条件"},
                {"id": "SME-003", "type": "statement_period",
                 "src": ("bank_statement", "period_start", "period_end"),
                 "min_months": 12,
                 "msg": "银行流水不足 12 个月"},
                {"id": "SME-004", "type": "loan_purpose_compliant",
                 "src": ("loan_application", "purpose"),
                 "blacklist": ["房地产", "炒股", "股票", "证券", "比特币", "虚拟币", "理财", "信托"],
                 "msg": "贷款用途包含禁止性内容（如房地产/股市/虚拟币等）"},
                {"id": "SME-005", "type": "amount_limit",
                 "src": ("loan_application", "amount"),
                 "max": 5000000,
                 "msg": "申请金额超过单户最高 500 万元"},
            ],
        },

        # ----------- 个人房贷 -----------
        "personal_mortgage": {
            "name": "个人住房按揭贷款",
            "required_docs": [
                "id_card",                  # 主借款人身份证
                "spouse_id_card",           # 配偶身份证（已婚）—— 由 logic_rule 校验
                "marriage_certificate",     # 婚姻证明
                "income_proof",             # 收入证明
                "bank_statement",           # 个人流水
                "purchase_contract",        # 购房合同
                "down_payment_proof",       # 首付款支付凭证
            ],
            "optional_docs": ["credit_report", "asset_proof"],
            "doc_field_requirements": {
                "id_card": ["id_no", "name", "valid_to"],
                "spouse_id_card": ["id_no", "name", "valid_to"],
                "marriage_certificate": ["status"],  # married | single | divorced
                "income_proof": ["monthly_income", "employer", "issued_date"],
                "bank_statement": ["period_start", "period_end", "avg_monthly_credit"],
                "purchase_contract": ["property_address", "total_price", "buyer_name", "signature_date"],
                "down_payment_proof": ["amount", "payment_date"],
            },
            "extra_rules": [
                {"id": "MORT-001", "type": "not_expired",
                 "src": ("id_card", "valid_to"),
                 "msg": "主借款人身份证已过期"},
                {"id": "MORT-002", "type": "spouse_required_if_married",
                 "src": ("marriage_certificate", "status"),
                 "required_doc": "spouse_id_card",
                 "msg": "婚姻状态为已婚但未提交配偶身份证"},
                {"id": "MORT-003", "type": "match_name",
                 "src": ("id_card", "name"),
                 "dst": ("purchase_contract", "buyer_name"),
                 "msg": "身份证姓名与购房合同买方不一致"},
                {"id": "MORT-004", "type": "income_to_loan_ratio",
                 "income_src": ("income_proof", "monthly_income"),
                 "price_src": ("purchase_contract", "total_price"),
                 "min_ratio": 1.0 / 60,
                 "msg": "月收入与贷款总额比过低（建议月供 ≤ 月收入 50%）"},
                {"id": "MORT-005", "type": "down_payment_ratio",
                 "down_src": ("down_payment_proof", "amount"),
                 "price_src": ("purchase_contract", "total_price"),
                 "min_ratio": 0.30,
                 "msg": "首付比例不足 30%（首套）"},
                {"id": "MORT-006", "type": "income_proof_freshness",
                 "src": ("income_proof", "issued_date"),
                 "max_days": 90,
                 "msg": "收入证明开具超过 90 天，需重新提供"},
            ],
        },
    }


SCENARIO_RULES = _scenario_rules()
