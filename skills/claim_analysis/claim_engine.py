"""
理赔分析引擎 (Claim Analysis Engine)

核心类：ClaimAnalysisEngine
输入理赔案件信息，返回责任认定、反欺诈检查、理赔金额计算、审核要点、处理时效
"""

import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional


# ============================================================
# 数据结构定义
# ============================================================

class ClaimCase:
    """理赔案件输入"""

    def __init__(
        self,
        insurance_type: str = "",
        accident_type: str = "",
        accident_reason: str = "",
        hospital_level: str = "",
        total_expense: float = 0.0,
        insurance_paid: float = 0.0,
        policy_terms: Optional[dict] = None,
        patient_history: Optional[dict] = None,
        invoice_list: Optional[list] = None,
        admission_date: str = "",
        discharge_date: str = "",
        policy_start: str = "",
        policy_end: str = "",
        beneficiary: str = "",
        id_card: str = "",
    ):
        self.insurance_type = insurance_type      # 医疗险/意外险/重疾险/寿险
        self.accident_type = accident_type        # 疾病/意外/手术
        self.accident_reason = accident_reason    # 出险原因
        self.hospital_level = hospital_level      # 三甲/三乙/二甲/其他
        self.total_expense = total_expense        # 总费用
        self.insurance_paid = insurance_paid      # 医保已报
        self.policy_terms = policy_terms or self._default_policy_terms()
        self.patient_history = patient_history or {}
        self.invoice_list = invoice_list or []
        self.admission_date = admission_date
        self.discharge_date = discharge_date
        self.policy_start = policy_start
        self.policy_end = policy_end
        self.beneficiary = beneficiary
        self.id_card = id_card

    @staticmethod
    def _default_policy_terms() -> dict:
        return {
            "deductible": 10000,           # 免赔额
            "co_insurance_rate": 0.8,       # 赔付比例 80%
            "annual_limit": 500000,          # 年度限额
            "waiting_period": 30,            # 等待期天数
            "covered_hospitals": ["三甲", "三乙", "二甲", "其他"],
            "exclusions": ["美容", "整形", "口腔正畸", "实验性治疗"],
            "pre_existing_period": 2 * 365,  # 既往症追溯期（天）
        }

    def from_text(text: str) -> "ClaimCase":
        """从自然语言文本解析理赔案件"""
        case = ClaimCase()
        text_lower = text.lower()

        # 险种识别
        if "医疗险" in text or "医疗" in text:
            case.insurance_type = "医疗险"
        elif "意外险" in text or "意外" in text:
            case.insurance_type = "意外险"
        elif "重疾" in text:
            case.insurance_type = "重疾险"
        elif "寿险" in text or "身故" in text:
            case.insurance_type = "寿险"

        # 金额提取
        money_patterns = [
            r"(\d+(?:\.\d+)?)\s*万",
            r"(\d+(?:\.\d+)?)\s*元",
        ]
        for pattern in money_patterns:
            matches = re.findall(pattern, text)
            if matches:
                val = float(matches[0])
                if val > 1000 and case.total_expense == 0:
                    # 判断是总费用还是医保报销
                    if "医保" in text or "报销" in text:
                        case.insurance_paid = val * 10000 if "万" in pattern else val
                    else:
                        case.total_expense = val * 10000 if "万" in pattern else val

        # 医保报销金额
        insurance_m = re.findall(r"医保[报报销]*(\d+(?:\.\d+)?)\s*万", text)
        if insurance_m:
            case.insurance_paid = float(insurance_m[0]) * 10000
        insurance_m2 = re.findall(r"医保[报报销]*(\d+(?:\.\d+)?)\s*元", text)
        if insurance_m2:
            case.insurance_paid = float(insurance_m2[0])

        # 医院等级
        if "三甲" in text:
            case.hospital_level = "三甲医院"
        elif "三乙" in text:
            case.hospital_level = "三乙医院"
        elif "二甲" in text:
            case.hospital_level = "二甲医院"

        # 出险类型
        if "住院" in text:
            case.accident_type = "住院"
        elif "门诊" in text:
            case.accident_type = "门诊"
        elif "手术" in text:
            case.accident_type = "手术"

        return case


# ============================================================
# 反欺诈规则引擎
# ============================================================

class FraudCheckRule:
    """反欺诈规则基类"""

    def __init__(self, code: str, name: str, severity: str):
        self.code = code
        self.name = name
        self.severity = severity  # high/medium/low

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        """返回None表示通过，返回dict表示触发规则"""
        raise NotImplementedError


class FraudRuleEngine:
    """反欺诈规则引擎（20+规则）"""

    RULES: list[FraudCheckRule] = []

    @classmethod
    def register(cls, rule: FraudCheckRule):
        cls.RULES.append(rule)

    @classmethod
    def check_all(cls, case: ClaimCase, context: dict) -> dict:
        """执行所有规则，返回检查结果"""
        flags = []
        details = []
        total_score = 0

        for rule in cls.RULES:
            result = rule.check(case, context)
            if result:
                flags.append({
                    "code": rule.code,
                    "name": rule.name,
                    "severity": rule.severity,
                    "description": result.get("description", ""),
                    "evidence": result.get("evidence", []),
                })
                # 计分
                if rule.severity == "high":
                    total_score += 30
                elif rule.severity == "medium":
                    total_score += 15
                else:
                    total_score += 5

        # 风险等级
        if total_score >= 60:
            risk_level = "高风险"
        elif total_score >= 30:
            risk_level = "中风险"
        elif total_score >= 15:
            risk_level = "低风险"
        else:
            risk_level = "正常"

        return {
            "score": min(total_score, 100),
            "risk_level": risk_level,
            "flags": flags,
            "details": details,
            "rule_count": len(cls.RULES),
            "triggered_count": len(flags),
        }


# ---- 规则1: 虚假发票 ----
class FakeInvoiceRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_001", "虚假发票", "high")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        invoices = case.invoice_list
        if not invoices:
            return None
        invoice_numbers = [inv.get("invoice_no", "") for inv in invoices]
        if len(invoice_numbers) != len(set(invoice_numbers)):
            return {
                "description": "存在重复发票号",
                "evidence": [f"重复发票号列表: {[n for n in invoice_numbers if invoice_numbers.count(n) > 1]}"]
            }
        return None


# ---- 规则2: 过度医疗 ----
class OverTreatmentRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_002", "过度医疗", "medium")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        # 规则：住院天数异常 or 人均费用显著高于同类
        total = case.total_expense
        hospital = case.hospital_level

        # 三甲医院住院花费>10万且为普通疾病
        if hospital == "三甲医院" and total > 100000:
            reason = case.accident_reason.lower()
            if any(kw in reason for kw in ["感冒", "发烧", "咳嗽", "普通", "一般"]):
                return {
                    "description": "三甲医院普通疾病高额花费，疑似过度医疗",
                    "evidence": [f"总费用: {total}元", f"医院等级: {hospital}"]
                }
        return None


# ---- 规则3: 挂名住院 ----
class NominalHospitalizationRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_003", "挂名住院", "high")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        # 规则：住院天数很长但费用偏低（床位费占主导）
        # 简化版：若住院天数>30天且日均费用<500元
        days = context.get("hospital_days", 0)
        if days > 30:
            avg = case.total_expense / max(days, 1)
            if avg < 500:
                return {
                    "description": "超长住院但日均费用极低，疑似挂名住院",
                    "evidence": [f"住院天数: {days}", f"日均费用: {avg:.0f}元"]
                }
        return None


# ---- 规则4: 分解住院 ----
class FragmentedHospitalizationRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_004", "分解住院", "medium")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        # 规则：30天内多次入院且诊断相似
        admission_count = context.get("admission_count_30d", 0)
        if admission_count >= 3:
            return {
                "description": "30天内多次分解住院",
                "evidence": [f"30天内入院次数: {admission_count}"]
            }
        return None


# ---- 规则5: 既往症未告知 ----
class PreExistingConditionRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_005", "既往症未告知", "high")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        history = case.patient_history
        if not history:
            return None
        undisclosed = history.get("undisclosed_conditions", [])
        if undisclosed:
            return {
                "description": "存在未如实告知的既往症",
                "evidence": [f"未告知既往症: {undisclosed}"]
            }
        return None


# ---- 规则6: 带病投保（等待期） ----
class WaitingPeriodRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_006", "等待期出险", "high")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        waiting_days = case.policy_terms.get("waiting_period", 30)
        policy_start = case.policy_start
        admission = case.admission_date

        if not policy_start or not admission:
            return None

        try:
            ps = datetime.strptime(policy_start, "%Y-%m-%d")
            ad = datetime.strptime(admission, "%Y-%m-%d")
            days_diff = (ad - ps).days
            if 0 <= days_diff < waiting_days:
                return {
                    "description": f"等待期{waiting_days}天内出险",
                    "evidence": [f"投保日期: {policy_start}", f"出险日期: {admission}", f"间隔: {days_diff}天"]
                }
        except (ValueError, TypeError):
            pass
        return None


# ---- 规则7: 保障范围外 ----
class OutOfCoverageRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_007", "保障范围外", "medium")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        exclusions = case.policy_terms.get("exclusions", [])
        reason = case.accident_reason

        triggered = [ex for ex in exclusions if ex in reason]
        if triggered:
            return {
                "description": f"就诊项目属于免责范围: {triggered}",
                "evidence": [f"出险原因: {reason}", f"免责条款匹配: {triggered}"]
            }
        return None


# ---- 规则8: 未指定医院 ----
class UnauthorizedHospitalRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_008", "未指定医院", "medium")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        allowed = case.policy_terms.get("covered_hospitals", [])
        level = case.hospital_level

        if level and level not in allowed:
            return {
                "description": f"就诊医院不符合条款要求: {level}",
                "evidence": [f"就诊医院: {level}", f"条款允许: {allowed}"]
            }
        return None


# ---- 规则9: 高额理赔异常 ----
class HighValueClaimRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_009", "高额理赔异常", "medium")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        annual_limit = case.policy_terms.get("annual_limit", 500000)
        if case.total_expense > annual_limit:
            return {
                "description": f"理赔金额超过年度限额",
                "evidence": [f"申请金额: {case.total_expense}元", f"年度限额: {annual_limit}元"]
            }
        return None


# ---- 规则10: 多家重复索赔 ----
class DuplicateClaimRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_010", "多家重复索赔", "high")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        other_claims = context.get("other_insurance_claims", [])
        if len(other_claims) > 0:
            return {
                "description": "发现其他保险公司索赔记录",
                "evidence": other_claims
            }
        return None


# ---- 规则11: 刚过等待期索赔 ----
class JustAfterWaitingRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_011", "刚过等待期索赔", "medium")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        waiting_days = case.policy_terms.get("waiting_period", 30)
        policy_start = case.policy_start
        admission = case.admission_date

        if not policy_start or not admission:
            return None

        try:
            ps = datetime.strptime(policy_start, "%Y-%m-%d")
            ad = datetime.strptime(admission, "%Y-%m-%d")
            days_diff = (ad - ps).days
            if waiting_days <= days_diff < waiting_days + 15:
                return {
                    "description": "等待期刚过即申请大额理赔",
                    "evidence": [f"等待期: {waiting_days}天", f"实际间隔: {days_diff}天"]
                }
        except (ValueError, TypeError):
            pass
        return None


# ---- 规则12: 短期内频繁索赔 ----
class FrequentClaimRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_012", "短期内频繁索赔", "low")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        claim_count = context.get("claim_count_6m", 0)
        if claim_count >= 3:
            return {
                "description": "6个月内频繁索赔",
                "evidence": [f"6个月内索赔次数: {claim_count}"]
            }
        return None


# ---- 规则13: 非本人领取 ----
class NonBeneficiaryRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_013", "非本人领取理赔款", "medium")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        collector = context.get("benefit_collector", "")
        beneficiary = case.beneficiary
        if collector and beneficiary and collector != beneficiary:
            return {
                "description": "理赔款由非受益人领取",
                "evidence": [f"受益人: {beneficiary}", f"领款人: {collector}"]
            }
        return None


# ---- 规则14: 理赔后退保 ----
class ClaimThenSurrenderRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_014", "理赔后退保", "low")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        if context.get("surrendered_after_claim", False):
            return {
                "description": "大额理赔后退保",
                "evidence": ["存在理赔后退保行为"]
            }
        return None


# ---- 规则15: 受益人异常变更 ----
class BeneficiaryChangeRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_015", "受益人异常变更", "medium")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        changes = context.get("beneficiary_changes", 0)
        if changes >= 2:
            return {
                "description": "理赔前频繁变更受益人",
                "evidence": [f"变更次数: {changes}"]
            }
        return None


# ---- 规则16: 保险期间外 ----
class OutOfPolicyPeriodRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_016", "保险期间外出险", "high")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        policy_end = case.policy_end
        admission = case.admission_date

        if not policy_end or not admission:
            return None

        try:
            pe = datetime.strptime(policy_end, "%Y-%m-%d")
            ad = datetime.strptime(admission, "%Y-%m-%d")
            if ad > pe:
                return {
                    "description": "出险日期在保险期间外",
                    "evidence": [f"保单到期: {policy_end}", f"出险日期: {admission}"]
                }
        except (ValueError, TypeError):
            pass
        return None


# ---- 规则17: 免赔额不达标 ----
class BelowDeductibleRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_017", "免赔额不达标", "low")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        deductible = case.policy_terms.get("deductible", 0)
        net_expense = case.total_expense - case.insurance_paid
        if net_expense <= deductible:
            return {
                "description": f"费用未超过免赔额{deductible}元",
                "evidence": [f"自付费用: {net_expense}元", f"免赔额: {deductible}元"]
            }
        return None


# ---- 规则18: 症状倒签 ----
class BackdatingSymptomRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_018", "症状倒签", "high")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        symptom_date = context.get("symptom_first_date", "")
        admission = case.admission_date
        if symptom_date and admission:
            try:
                sd = datetime.strptime(symptom_date, "%Y-%m-%d")
                ad = datetime.strptime(admission, "%Y-%m-%d")
                if sd > ad:
                    return {
                        "description": "症状出现日期晚于入院日期，疑似倒签",
                        "evidence": [f"症状首次出现: {symptom_date}", f"入院日期: {admission}"]
                    }
            except (ValueError, TypeError):
                pass
        return None


# ---- 规则19: 发票金额篡改 ----
class InvoiceTamperingRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_019", "发票金额篡改", "high")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        # 简化规则：若存在多个发票，检查总费用是否匹配
        invoices = case.invoice_list
        if len(invoices) >= 2:
            invoice_total = sum(inv.get("amount", 0) for inv in invoices)
            if invoice_total > 0 and abs(invoice_total - case.total_expense) > 1:
                return {
                    "description": "发票金额汇总与申报总费用不符",
                    "evidence": [f"发票汇总: {invoice_total}元", f"申报总费用: {case.total_expense}元"]
                }
        return None


# ---- 规则20: 冒名就医 ----
class ImpersonationRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_020", "冒名就医", "high")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        if context.get("id_verification_failed", False):
            return {
                "description": "身份核验未通过，疑似冒名就医",
                "evidence": ["身份证信息与医保卡信息不一致"]
            }
        return None


# ---- 规则21: 诊断与治疗不符 ----
class MismatchTreatmentRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_021", "诊断与治疗方案不符", "medium")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        diagnosis = context.get("diagnosis", "")
        treatment = context.get("treatment", "")

        # 简化版：若诊断为空或治疗与诊断明显不符
        if diagnosis and treatment:
            # 检查是否有明显不相关关键词
            irrelevant = ["美容", "整形", "心理咨询", "戒烟"]
            diag_lower = diagnosis.lower()
            if any(kw in treatment for kw in irrelevant) and not any(kw in diag_lower for kw in irrelevant):
                return {
                    "description": "治疗方案与诊断明显不符",
                    "evidence": [f"诊断: {diagnosis}", f"治疗: {treatment}"]
                }
        return None


# ---- 规则22: 病历造假 ----
class MedicalRecordForgeryRule(FraudCheckRule):
    def __init__(self):
        super().__init__("FRAUD_022", "病历资料伪造", "high")

    def check(self, case: ClaimCase, context: dict) -> Optional[dict]:
        if context.get("medical_record_inconsistent", False):
            return {
                "description": "病历资料存在明显不一致",
                "evidence": ["病历签字/日期/诊断存在伪造嫌疑"]
            }
        return None


# 注册所有规则
def _register_rules():
    for rule_cls in [
        FakeInvoiceRule, OverTreatmentRule, NominalHospitalizationRule,
        FragmentedHospitalizationRule, PreExistingConditionRule, WaitingPeriodRule,
        OutOfCoverageRule, UnauthorizedHospitalRule, HighValueClaimRule,
        DuplicateClaimRule, JustAfterWaitingRule, FrequentClaimRule,
        NonBeneficiaryRule, ClaimThenSurrenderRule, BeneficiaryChangeRule,
        OutOfPolicyPeriodRule, BelowDeductibleRule, BackdatingSymptomRule,
        InvoiceTamperingRule, ImpersonationRule, MismatchTreatmentRule,
        MedicalRecordForgeryRule,
    ]:
        FraudRuleEngine.register(rule_cls())

_register_rules()


# ============================================================
# 责任认定引擎
# ============================================================

class LiabilityEngine:
    """责任认定引擎"""

    @staticmethod
    def assess(case: ClaimCase, fraud_result: dict) -> dict:
        """
        评估是否属于保险责任
        返回：decision + coverage_details + exclusions
        """
        fraud_flags = [f["code"] for f in fraud_result.get("flags", [])]
        decisions = []
        coverage_details = []
        exclusions = []

        # ---- 硬性排除 ----
        hard_exclusion_rules = {"FRAUD_001", "FRAUD_003", "FRAUD_006", "FRAUD_016", "FRAUD_018", "FRAUD_020", "FRAUD_022"}
        if any(r in fraud_flags for r in hard_exclusion_rules):
            exclusions.append("存在严重欺诈行为，不属于保险责任")
            return {
                "decision": "不属于保险责任",
                "reason": "经审核，该案件存在虚假凭证、挂名住院、等待期出险、保险期间外出险、冒名就医或病历伪造等严重违规行为，依据保险条款及《保险法》规定，不予赔付。",
                "coverage_details": coverage_details,
                "exclusions": exclusions,
            }

        # ---- 等待期 ----
        if "FRAUD_006" in fraud_flags:
            exclusions.append("等待期内确诊/出险")
            return {
                "decision": "不属于保险责任",
                "reason": "该案件在保险合同约定的等待期内出险，依据条款等待期规定，不予赔付。",
                "coverage_details": coverage_details,
                "exclusions": exclusions,
            }

        # ---- 保障范围外 ----
        if "FRAUD_007" in fraud_flags:
            exclusions.append("就诊项目属于责任免除范围")
            decisions.append("部分属于")

        # ---- 既往症 ----
        if "FRAUD_005" in fraud_flags:
            exclusions.append("既往症属于责任免除")
            decisions.append("部分属于")

        # ---- 免赔额不达标 ----
        if "FRAUD_017" in fraud_flags:
            deductible = case.policy_terms.get("deductible", 0)
            exclusions.append(f"未达到免赔额{deductible}元")
            return {
                "decision": "不属于保险责任",
                "reason": f"该案件自付金额未超过合同约定的免赔额{deductible}元，暂不满足赔付条件。",
                "coverage_details": coverage_details,
                "exclusions": exclusions,
            }

        # ---- 医院不符合 ----
        if "FRAUD_008" in fraud_flags:
            exclusions.append("就诊医院不符合条款要求")

        # ---- 综合判定 ----
        if not decisions:
            decisions.append("属于保险责任")

        decision = decisions[0]

        # 构建保障详情
        coverage_details.append({
            "项目": "符合保险责任范围",
            "说明": f"出险类型: {case.accident_type} | 险种: {case.insurance_type} | 费用: {case.total_expense}元"
        })

        if fraud_result.get("risk_level") in ["中风险", "高风险"]:
            reason = f"案件存在{fraud_result['risk_level']}反欺诈预警({fraud_result['triggered_count']}条)，需进一步调查核实后确认赔付。"
            return {
                "decision": "待核实",
                "reason": reason,
                "coverage_details": coverage_details,
                "exclusions": exclusions,
            }

        reason_map = {
            "属于保险责任": f"经审核，该案件出险属实，所涉费用{case.total_expense}元，医保已报{case.insurance_paid}元，扣除免赔额及比例后属于保险责任范围。",
            "部分属于": f"该案件部分费用({', '.join(exclusions)})属于责任免除，其余部分属于保险责任，建议按比例赔付。",
            "不属于保险责任": f"经审核，该案件因({', '.join(exclusions)})不属于保险责任范围，依据条款不予赔付。",
            "待核实": "该案件存在风险预警，需进一步调查核实后再作最终决定。"
        }

        return {
            "decision": decision,
            "reason": reason_map.get(decision, "经审核，该案件属于保险责任范围。"),
            "coverage_details": coverage_details,
            "exclusions": exclusions,
        }


# ============================================================
# 理赔金额计算引擎
# ============================================================

class ClaimCalculationEngine:
    """理赔金额计算"""

    @staticmethod
    def calculate(case: ClaimCase) -> dict:
        total = case.total_expense
        insurance_paid = case.insurance_paid
        deductible = case.policy_terms.get("deductible", 0)
        co_insurance_rate = case.policy_terms.get("co_insurance_rate", 0.8)
        annual_limit = case.policy_terms.get("annual_limit", 500000)

        # 自付金额 = 总费用 - 医保已报
        self_pay = total - insurance_paid

        # 扣除免赔额
        after_deductible = max(0, self_pay - deductible)

        # 按比例赔付
        gross_reimbursement = after_deductible * co_insurance_rate

        # 不超过年度限额
        final_reimbursement = min(gross_reimbursement, annual_limit)

        # 分解明细
        breakdown = [
            {"项目": "住院总费用", "金额": total, "说明": ""},
            {"项目": "医保已报销", "金额": -insurance_paid, "说明": ""},
            {"项目": "自付金额", "金额": self_pay, "说明": "总费用-医保已报"},
            {"项目": "免赔额扣除", "金额": -min(deductible, self_pay), "说明": f"免赔额{deductible}元"},
            {"项目": "比例赔付", "金额": 0, "说明": f"赔付比例{int(co_insurance_rate*100)}%"},
            {"项目": "应赔付金额", "金额": gross_reimbursement, "说明": "扣除免赔额后×赔付比例"},
            {"项目": "年度限额校验", "金额": 0, "说明": f"年度限额{annual_limit}元"},
            {"项目": "最终赔付", "金额": final_reimbursement, "说明": "取应赔付与限额较小值"},
        ]

        return {
            "total_expense": total,
            "insurance_paid": insurance_paid,
            "self_pay": self_pay,
            "deductible": deductible,
            "co_insurance_rate": co_insurance_rate,
            "gross_reimbursement": gross_reimbursement,
            "annual_limit": annual_limit,
            "final_reimbursement": final_reimbursement,
            "breakdown": breakdown,
        }


# ============================================================
# 审核要点引擎
# ============================================================

class AuditPointEngine:
    """生成审核要点"""

    @staticmethod
    def generate(case: ClaimCase, liability: dict, fraud: dict, calculation: dict) -> list[dict]:
        points = []

        # 基础信息核查
        points.append({
            "category": "基础信息核查",
            "priority": "必须",
            "items": [
                "核对被保险人身份信息与保单一致",
                "核实入院日期、出院日期与发票日期一致",
                "核查就诊医院等级与条款要求一致",
                "核实保单有效期间",
            ]
        })

        # 费用核查
        points.append({
            "category": "费用核查",
            "priority": "必须",
            "items": [
                f"核查总费用明细清单与发票金额一致",
                f"核实医保报销金额{case.insurance_paid}元是否准确",
                f"核查药品/检查项目是否属于保障范围",
                "核查是否存在第三方责任（如有则应由第三方先行赔付）",
            ]
        })

        # 反欺诈关注点
        fraud_flags = [f"{f['code']}:{f['name']}" for f in fraud.get("flags", [])]
        if fraud_flags:
            points.append({
                "category": "反欺诈关注",
                "priority": "高优先级",
                "items": [f"注意核查: {'; '.join(fraud_flags)}"] + [
                    f"{flag['name']}: {flag['description']}"
                    for flag in fraud.get("flags", [])
                ]
            })

        # 计算校验
        points.append({
            "category": "计算校验",
            "priority": "必须",
            "items": [
                f"免赔额: {calculation['deductible']}元 是否扣除正确",
                f"赔付比例: {int(calculation['co_insurance_rate']*100)}% 是否适用正确",
                f"最终赔付金额: {calculation['final_reimbursement']}元 核对无误",
            ]
        })

        # 既往症核查
        if case.patient_history:
            points.append({
                "category": "既往症核查",
                "priority": "重要",
                "items": [
                    "核查被保险人投保前健康状况",
                    "核查是否存在既往症未告知情形",
                    "核查既往症与本次出险关联性",
                ]
            })

        # 复杂件升级
        if fraud.get("risk_level") in ["高风险", "中风险"]:
            points.append({
                "category": "案件升级",
                "priority": "高优先级",
                "items": [
                    f"反欺诈风险评级: {fraud['risk_level']}，建议转交调查岗",
                    "建议核查就诊记录/病历真实性",
                    "建议与医院核实费用明细",
                ]
            })

        return points


# ============================================================
# 处理时效
# ============================================================

class ProcessingTimeEngine:
    """处理时效评估"""

    @staticmethod
    def evaluate(case: ClaimCase, liability: dict, fraud: dict) -> dict:
        risk_level = fraud.get("risk_level", "正常")
        decision = liability.get("decision", "属于保险责任")

        # 分类
        if decision == "不属于保险责任":
            category = "普通件"
            days = 7
            reason = "案件事实清晰，可快速结案"
        elif risk_level == "高风险":
            category = "复杂件"
            days = 30
            reason = "涉及高风险反欺诈预警，需深入调查"
        elif risk_level == "中风险":
            category = "复杂件"
            days = 15
            reason = "存在中风险预警，需进一步核实"
        elif case.total_expense > 100000:
            category = "复杂件"
            days = 15
            reason = "高额理赔案件，需加强审核"
        else:
            category = "普通件"
            days = 7
            reason = "案件材料齐全，事实清晰"

        deadline = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

        return {
            "category": category,
            "days": days,
            "deadline": deadline,
            "reason": reason,
        }


# ============================================================
# 主引擎
# ============================================================

class ClaimAnalysisEngine:
    """理赔分析主引擎"""

    def __init__(self):
        self.liability_engine = LiabilityEngine()
        self.fraud_engine = FraudRuleEngine()
        self.calc_engine = ClaimCalculationEngine()
        self.audit_engine = AuditPointEngine()
        self.time_engine = ProcessingTimeEngine()

    def analyze(
        self,
        insurance_type: str = "",
        accident_type: str = "",
        accident_reason: str = "",
        hospital_level: str = "",
        total_expense: float = 0.0,
        insurance_paid: float = 0.0,
        policy_terms: Optional[dict] = None,
        patient_history: Optional[dict] = None,
        invoice_list: Optional[list] = None,
        admission_date: str = "",
        discharge_date: str = "",
        policy_start: str = "",
        policy_end: str = "",
        beneficiary: str = "",
        id_card: str = "",
        context: Optional[dict] = None,
    ) -> dict:
        """
        完整理赔分析
        """
        # 构建案件
        case = ClaimCase(
            insurance_type=insurance_type,
            accident_type=accident_type,
            accident_reason=accident_reason,
            hospital_level=hospital_level,
            total_expense=total_expense,
            insurance_paid=insurance_paid,
            policy_terms=policy_terms,
            patient_history=patient_history,
            invoice_list=invoice_list or [],
            admission_date=admission_date,
            discharge_date=discharge_date,
            policy_start=policy_start,
            policy_end=policy_end,
            beneficiary=beneficiary,
            id_card=id_card,
        )

        # 执行各项分析
        fraud_result = self.fraud_engine.check_all(case, context or {})
        liability_result = self.liability_engine.assess(case, fraud_result)
        calc_result = self.calc_engine.calculate(case)
        audit_points = self.audit_engine.generate(case, liability_result, fraud_result, calc_result)
        time_result = self.time_engine.evaluate(case, liability_result, fraud_result)

        # 生成下一步
        next_steps = self._generate_next_steps(liability_result, fraud_result, time_result)

        return {
            "claim_id": f"CLM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "liability_assessment": liability_result,
            "fraud_check": {
                "score": fraud_result["score"],
                "risk_level": fraud_result["risk_level"],
                "flags": fraud_result["flags"],
                "details": fraud_result["details"],
                "total_rules": fraud_result["rule_count"],
                "triggered_rules": fraud_result["triggered_count"],
            },
            "claim_calculation": calc_result,
            "audit_points": audit_points,
            "processing_time": time_result,
            "next_steps": next_steps,
            "summary": self._make_summary(case, liability_result, fraud_result, calc_result),
        }

    def _generate_next_steps(self, liability: dict, fraud: dict, time: dict) -> list[str]:
        steps = []
        decision = liability.get("decision", "")

        if decision == "不属于保险责任":
            steps.append("出具拒赔通知书并说明原因")
            steps.append("通知客户并提供申诉渠道")
        elif decision == "待核实":
            steps.append("转交调查岗进行实地核查")
            steps.append("联系医院核实病历及费用明细")
            steps.append(f"在{time['days']}个工作日内完成调查")
        elif decision == "部分属于":
            steps.append("与客户沟通除外责任项目")
            steps.append("按比例计算赔付金额并通知客户")
            steps.append("确认客户无异议后支付赔款")
        else:
            steps.append("核对计算金额无误")
            steps.append("提交审批并支付赔款")
            steps.append(f"在{time['days']}个工作日内完成支付")

        return steps

    def _make_summary(
        self, case: ClaimCase, liability: dict, fraud: dict, calc: dict
    ) -> str:
        lines = [
            f"【理赔分析摘要】",
            f"险种: {case.insurance_type}",
            f"总费用: {case.total_expense:,.0f}元 | 医保已报: {case.insurance_paid:,.0f}元",
            f"责任认定: {liability.get('decision', '未知')}",
            f"反欺诈: {fraud['risk_level']}（{fraud['triggered_count']}/{fraud['rule_count']}条规则触发）",
            f"最终赔付: {calc['final_reimbursement']:,.0f}元",
            f"处理时效: {liability.get('decision', '普通件') == '不属于保险责任' and '7' or calc.get('processing_days', '7')}个工作日",
        ]
        return " | ".join(lines)
