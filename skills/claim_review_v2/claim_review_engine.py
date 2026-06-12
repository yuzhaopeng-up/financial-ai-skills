"""
寿险理赔审核引擎 V2 (Claim Review V2 Engine)

专注寿险理赔场景，输入理赔案件信息，返回审核结果：
- 理赔审核结果（正常赔付/比例赔付/拒赔/需补充材料）
- 审核要点（病史关联性/免赔条款/保单有效性）
- 理赔金额计算
- 反欺诈检查
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional


# ============================================================
# 数据结构
# ============================================================

@dataclass
class ClaimReviewCase:
    """理赔审核案件输入"""
    insurance_type: str = ""           # 险种类型
    accident_type: str = ""             # 出险类型：疾病/意外/全残/身故
    accident_reason: str = ""          # 出险原因
    hospital_level: str = ""           # 就诊医院等级
    total_expense: float = 0.0         # 住院总花费
    insurance_paid: float = 0.0       # 医保已报销
    policy_terms: dict = field(default_factory=dict)
    patient_history: dict = field(default_factory=dict)
    admission_date: str = ""           # YYYY-MM-DD
    discharge_date: str = ""           # YYYY-MM-DD
    policy_start_date: str = ""        # YYYY-MM-DD
    policy_years: int = 0             # 保单生效年限
    premium_paid: bool = True         # 保费是否正常缴纳
    beneficiary: str = ""             # 受益人
    beneficiary_relation: str = ""     # 受益人关系
    claim_amount: float = 0.0         # 申请理赔金额
    death_certificate: bool = False     # 死亡证明
    accident_report: bool = False     # 事故证明
    sobriety_test: bool = True        # 酒测是否通过（True=通过/无饮酒）
    license_valid: bool = True         # 驾驶证是否有效
    vehicle_type: str = ""             # 车辆类型


# ============================================================
# 审核决策常量
# ============================================================

DECISION_APPROVED = "APPROVED"           # 正常赔付
DECISION_PROPORTIONAL = "PROPORTIONAL"   # 比例赔付
DECISION_REJECTED = "REJECTED"           # 拒赔
DECISION_PENDING = "PENDING_MATERIALS"    # 需补充材料

DECISION_LABELS = {
    DECISION_APPROVED: "正常赔付",
    DECISION_PROPORTIONAL: "比例赔付",
    DECISION_REJECTED: "拒赔",
    DECISION_PENDING: "需补充材料",
}


# ============================================================
# 核心引擎
# ============================================================

class ClaimReviewV2Engine:
    """
    寿险理赔审核引擎 V2

    支持险种：终身寿险/定期寿险/两全险/重疾险/医疗险/意外险
    审核规则：等待期、既往症、酒驾/无证驾驶拒赔、保单有效性
    """

    def __init__(self):
        self._case_counter = 0
        # 险种代码映射
        self._type_map = {
            "终身寿险": "whole_life",
            "定期寿险": "term_life",
            "两全险": "endowment",
            "重疾险": "critical_illness",
            "医疗险": "medical",
            "意外险": "accident",
        }
        # 等待期（天）
        self._waiting_periods = {
            "whole_life": 180,    # 终身寿险疾病等待期
            "term_life": 180,     # 定期寿险疾病等待期
            "endowment": 180,     # 两全险疾病等待期
            "critical_illness": 90,  # 重疾等待期（部分产品90天）
            "medical": 180,       # 医疗险疾病等待期
            "accident": 3,        # 意外险等待期
        }
        # 默认赔付比例（无医保情况）
        self._default_coinsurance = {
            "whole_life": 1.0,       # 寿险：100%保额
            "term_life": 1.0,         # 寿险：100%保额
            "endowment": 1.0,         # 两全险：100%保额
            "critical_illness": 1.0,  # 重疾：一次性给付
            "medical": 0.8,            # 医疗险：80%
            "accident": 1.0,          # 意外险：100%保额
        }
        # 意外险医疗费用赔付比例（按医院等级）
        self._accident_coinsurance = {
            "三甲医院": 0.8,
            "三乙医院": 0.85,
            "二甲医院": 0.9,
            "其他": 0.9,
        }
        # 默认免赔额
        self._default_deductible = {
            "whole_life": 0.0,
            "term_life": 0.0,
            "endowment": 0.0,
            "critical_illness": 0.0,
            "medical": 10000.0,
            "accident": 0.0,
        }

    def _get_insurance_code(self, insurance_type: str) -> str:
        """获取险种代码"""
        return self._type_map.get(insurance_type, "whole_life")

    def _calculate_waiting_period(self, insurance_code: str) -> int:
        """获取等待期天数"""
        return self._waiting_periods.get(insurance_code, 180)

    def _is_waiting_period_active(self, policy_start_date: str,
                                  accident_date: str,
                                  waiting_days: int) -> bool:
        """检查等待期是否有效"""
        try:
            policy_start = datetime.strptime(policy_start_date, "%Y-%m-%d")
            accident = datetime.strptime(accident_date, "%Y-%m-%d")
            return (accident - policy_start).days < waiting_days
        except (ValueError, TypeError):
            return False

    def _check_drunken_driving(self, case: ClaimReviewCase) -> tuple:
        """检查酒驾"""
        if not case.sobriety_test:
            return True, "存在酒驾行为，属于责任免除"
        return False, ""

    def _check_no_license(self, case: ClaimReviewCase) -> tuple:
        """检查无证驾驶"""
        vehicle_types_no_license = ["汽车", "摩托车", "机动车", ""]
        if case.vehicle_type in vehicle_types_no_license and not case.license_valid:
            return True, f"无证驾驶{case.vehicle_type}，属于责任免除"
        return False, ""

    def _check_policy_validity(self, case: ClaimReviewCase) -> dict:
        """检查保单有效性"""
        issues = []
        valid = True

        if not case.premium_paid:
            issues.append("保费未正常缴纳，保单效力中止")
            valid = False

        if case.policy_years <= 0 and case.policy_start_date:
            try:
                policy_start = datetime.strptime(case.policy_start_date, "%Y-%m-%d")
                now = datetime.now()
                years = (now - policy_start).days / 365.25
                if years < 0:
                    issues.append("保单生效日期早于当前日期")
                    valid = False
            except (ValueError, TypeError):
                issues.append("保单生效日期格式错误")
                valid = False
        elif case.policy_years <= 0:
            issues.append("保单生效年限不足")
            valid = False

        return {"valid": valid, "issues": issues}

    def _check_pre_existing_conditions(self, case: ClaimReviewCase) -> dict:
        """检查既往症"""
        details = []
        has_pre_existing = False
        related = False

        history_diseases = case.patient_history.get("diseases", [])
        if history_diseases:
            has_pre_existing = True
            details.append(f"既往病史：{', '.join(history_diseases)}")

            # 检查与出险原因关联性
            accident_lower = case.accident_reason.lower()
            for disease in history_diseases:
                disease_lower = disease.lower()
                # 关联关键词
                related_keywords = {
                    "恶性肿瘤": ["癌", "肿瘤", "恶性"],
                    "心脑血管": ["心", "脑", "梗", "中风"],
                    "肝脏疾病": ["肝", "炎", "硬化"],
                    "肾脏疾病": ["肾", "尿毒", "透析"],
                    "糖尿病": ["糖", "糖尿病"],
                }
                for category, keywords in related_keywords.items():
                    if any(kw in disease_lower for kw in keywords):
                        if any(kw in accident_lower for kw in keywords):
                            related = True
                            details.append(f"既往症{disease}与出险原因{case.accident_reason}存在关联")

        return {
            "has_pre_existing": has_pre_existing,
            "related": related,
            "details": details
        }

    def _check_exclusion_clauses(self, case: ClaimReviewCase) -> dict:
        """检查责任免除条款"""
        triggered = []
        not_triggered = []

        # 酒驾
        is_drunk, drunk_msg = self._check_drunken_driving(case)
        if is_drunk:
            triggered.append(drunk_msg)
        else:
            not_triggered.append("酒驾")

        # 无证驾驶
        is_no_license, no_license_msg = self._check_no_license(case)
        if is_no_license:
            triggered.append(no_license_msg)
        else:
            not_triggered.append("无证驾驶")

        # 自杀/故意行为
        if "故意" in case.accident_reason or "自杀" in case.accident_reason:
            triggered.append("故意行为/自杀，属于责任免除")
        else:
            not_triggered.append("故意行为/自杀")

        # 先天性疾病
        if "先天" in case.accident_reason:
            triggered.append("先天性疾病，属于责任免除")
        else:
            not_triggered.append("先天性疾病")

        # 违法犯罪
        crime_keywords = ["犯罪", "刑事", "拘捕", "逃逸"]
        if any(kw in case.accident_reason for kw in crime_keywords):
            triggered.append("违法犯罪行为，属于责任免除")
        else:
            not_triggered.append("违法犯罪")

        return {"triggered": triggered, "not_triggered": not_triggered}

    def _calculate_claim_amount(self, case: ClaimReviewCase) -> dict:
        """计算理赔金额"""
        ins_code = self._get_insurance_code(case.insurance_type)

        claim_amount = case.claim_amount
        deductible = case.policy_terms.get("deductible",
                                           self._default_deductible.get(ins_code, 0.0))
        co_insurance = case.policy_terms.get("co_insurance_rate",
                                              self._default_coinsurance.get(ins_code, 1.0))

        breakdown = []
        final_payment = 0.0
        approved_amount = 0.0

        if ins_code in ("whole_life", "term_life", "endowment", "accident"):
            # 寿险/意外险身故或全残：按保额赔付
            if case.accident_type in ("身故", "全残"):
                final_payment = claim_amount
                approved_amount = claim_amount
                breakdown.append(f"险种：{case.insurance_type}，出险类型：{case.accident_type}")
                breakdown.append(f"申请理赔金额：¥{claim_amount:,.2f}")
                breakdown.append(f"赔付比例：100%")
                breakdown.append(f"最终赔付额：¥{final_payment:,.2f}")
            else:
                # 意外医疗
                total_expense = case.total_expense
                insurance_paid = case.insurance_paid
                hospital_rate = self._accident_coinsurance.get(case.hospital_level, 0.9)
                net = max(0, total_expense - insurance_paid - deductible)
                final_payment = net * co_insurance * hospital_rate
                approved_amount = final_payment
                breakdown.append(f"住院总花费：¥{total_expense:,.2f}")
                breakdown.append(f"医保已报销：¥{insurance_paid:,.2f}")
                breakdown.append(f"免赔额：¥{deductible:,.2f}")
                breakdown.append(f"赔付比例：{co_insurance*100:.0f}%（医院等级：{case.hospital_level}）")
                breakdown.append(f"最终赔付额：¥{final_payment:,.2f}")

        elif ins_code == "critical_illness":
            # 重疾险：确诊即赔
            final_payment = claim_amount
            approved_amount = claim_amount
            breakdown.append(f"险种：{case.insurance_type}，出险类型：{case.accident_type}")
            breakdown.append(f"重疾确诊给付保险金：¥{final_payment:,.2f}")

        elif ins_code == "medical":
            # 医疗险：报销型
            total_expense = case.total_expense
            insurance_paid = case.insurance_paid
            net = max(0, total_expense - insurance_paid - deductible)
            final_payment = net * co_insurance
            approved_amount = final_payment
            breakdown.append(f"住院总花费：¥{total_expense:,.2f}")
            breakdown.append(f"医保已报销：¥{insurance_paid:,.2f}")
            breakdown.append(f"免赔额：¥{deductible:,.2f}")
            breakdown.append(f"赔付比例：{co_insurance*100:.0f}%")
            breakdown.append(f"最终赔付额：¥{final_payment:,.2f}")

        else:
            final_payment = claim_amount * co_insurance
            approved_amount = final_payment
            breakdown.append(f"申请理赔金额：¥{claim_amount:,.2f}")
            breakdown.append(f"赔付比例：{co_insurance*100:.0f}%")
            breakdown.append(f"最终赔付额：¥{final_payment:,.2f}")

        return {
            "claim_amount": claim_amount,
            "approved_amount": approved_amount,
            "deductible": deductible,
            "co_insurance_rate": co_insurance,
            "final_payment": final_payment,
            "breakdown": breakdown,
        }

    def _fraud_check(self, case: ClaimReviewCase) -> dict:
        """反欺诈检查"""
        score = 0
        flags = []
        details = []

        # 1. 刚过等待期索赔（等待期结束后30天内）
        if case.policy_years < 1 and case.policy_start_date:
            try:
                policy_start = datetime.strptime(case.policy_start_date, "%Y-%m-%d")
                now = datetime.now()
                days_since_start = (now - policy_start).days
                ins_code = self._get_insurance_code(case.insurance_type)
                waiting = self._calculate_waiting_period(ins_code)
                if days_since_start < waiting + 30:
                    score += 25
                    flags.append("刚过等待期即申请理赔，建议重点关注")
                    details.append(f"保单生效{days_since_start}天，等待期{waiting}天")
            except (ValueError, TypeError):
                pass

        # 2. 高额理赔异常（超过50万）
        if case.claim_amount > 500000:
            score += 15
            flags.append(f"高额理赔：申请金额¥{case.claim_amount/10000:.0f}万")
            details.append(f"申请理赔金额{case.claim_amount}元，超过50万阈值")

        # 3. 无死亡证明/事故证明
        if case.accident_type == "身故" and not case.death_certificate:
            score += 20
            flags.append("身故理赔缺少死亡证明")
            details.append("未提供死亡证明，材料不完整")

        if case.accident_type == "意外" and not case.accident_report:
            score += 10
            flags.append("意外事故缺少事故证明")

        # 4. 酒驾/无证驾驶
        if not case.sobriety_test:
            score += 30
            flags.append("存在酒驾行为")
            details.append("酒驾属于责任免除，触发反欺诈预警")

        if not case.license_valid and case.vehicle_type:
            score += 20
            flags.append("无证驾驶")
            details.append("无证驾驶属于责任免除")

        # 5. 既往症未告知
        history = case.patient_history
        if history.get("diseases") and not history.get("declared", False):
            score += 15
            flags.append("既往症未如实告知")
            details.append(f"存在既往病史：{', '.join(history.get('diseases', []))}")

        # 6. 保费未正常缴纳
        if not case.premium_paid:
            score += 20
            flags.append("保费未正常缴纳")
            details.append("保单效力中止期间发生保险事故")

        # 7. 受益人异常
        if case.beneficiary_relation in ("未知", "无", "") and case.claim_amount > 100000:
            score += 5
            flags.append("受益人关系不明确")

        # 8. 无医院记录
        if case.hospital_level == "" and case.total_expense > 0:
            score += 10
            flags.append("缺少就诊医院信息")

        # 风险等级
        if score >= 60:
            risk_level = "极高风险"
        elif score >= 40:
            risk_level = "高风险"
        elif score >= 20:
            risk_level = "中风险"
        else:
            risk_level = "低风险"

        return {
            "score": score,
            "risk_level": risk_level,
            "flags": flags,
            "details": details,
        }

    def _determine_decision(self, case: ClaimReviewCase,
                           policy_validity: dict,
                           history_check: dict,
                           exclusion_check: dict,
                           fraud: dict) -> dict:
        """综合判断审核决策"""
        reasons = []
        result_code = DECISION_APPROVED

        # 1. 保单无效
        if not policy_validity["valid"]:
            result_code = DECISION_REJECTED
            reasons.extend(policy_validity["issues"])
            return {"result": DECISION_LABELS[result_code], "code": result_code, "reason": "; ".join(reasons)}

        # 2. 责任免除触发
        if exclusion_check["triggered"]:
            result_code = DECISION_REJECTED
            reasons.extend(exclusion_check["triggered"])
            return {"result": DECISION_LABELS[result_code], "code": result_code, "reason": "; ".join(reasons)}

        # 3. 等待期未过
        ins_code = self._get_insurance_code(case.insurance_type)
        waiting_days = self._calculate_waiting_period(ins_code)
        accident_date = case.admission_date or datetime.now().strftime("%Y-%m-%d")
        if self._is_waiting_period_active(case.policy_start_date, accident_date, waiting_days):
            result_code = DECISION_REJECTED
            reasons.append(f"等待期{waiting_days}天尚未结束（普通疾病/重疾险180天，意外3天）")
            return {"result": DECISION_LABELS[result_code], "code": result_code, "reason": "; ".join(reasons)}

        # 4. 既往症关联
        if history_check["has_pre_existing"] and history_check["related"]:
            result_code = DECISION_REJECTED
            reasons.append("既往症与出险原因存在关联，属于责任免除")
            return {"result": DECISION_LABELS[result_code], "code": result_code, "reason": "; ".join(reasons)}

        # 5. 材料不完整
        if case.accident_type == "身故" and not case.death_certificate:
            result_code = DECISION_PENDING
            reasons.append("缺少死亡证明，需补充材料")
            return {"result": DECISION_LABELS[result_code], "code": result_code, "reason": "; ".join(reasons)}

        if case.accident_type == "意外" and not case.accident_report:
            result_code = DECISION_PENDING
            reasons.append("缺少事故证明，需补充材料")
            return {"result": DECISION_LABELS[result_code], "code": result_code, "reason": "; ".join(reasons)}

        # 6. 反欺诈高风险
        if fraud["risk_level"] in ("极高风险", "高风险"):
            if result_code == DECISION_APPROVED:
                result_code = DECISION_PROPORTIONAL
                reasons.append(f"反欺诈风险{fraud['risk_level']}，建议比例赔付或进一步调查")

        return {"result": DECISION_LABELS.get(result_code, "正常赔付"), "code": result_code, "reason": "; ".join(reasons)}

    def _generate_next_steps(self, case: ClaimReviewCase,
                            decision: dict,
                            policy_validity: dict,
                            exclusion_check: dict,
                            history_check: dict) -> list:
        """生成后续步骤"""
        steps = []
        code = decision["code"]

        if code == DECISION_PENDING:
            steps.append("补充缺失材料")
            if not case.death_certificate:
                steps.append("提供死亡证明原件")
            if not case.accident_report:
                steps.append("提供事故证明或警方报告")
            steps.append("材料补充完整后重新提交审核")
            return steps

        if code == DECISION_REJECTED:
            steps.append("向受益人出具拒赔通知书")
            steps.append("说明拒赔原因及依据")
            if exclusion_check["triggered"]:
                steps.append("告知受益人申诉渠道")
            steps.append("退还相关材料原件")
            return steps

        # APPROVED / PROPORTIONAL
        steps.append("审核通过，准备理赔付款")
        if code == DECISION_PROPORTIONAL:
            steps.append("通知受益人比例赔付决定及金额")
        else:
            steps.append("通知受益人理赔决定及金额")
        steps.append("核实受益人账户信息")
        steps.append("执行付款操作")
        steps.append("完成结案归档")

        return steps

    def _estimate_processing_time(self, case: ClaimReviewCase, fraud: dict) -> dict:
        """估算处理时效"""
        base_days = 7

        if fraud["risk_level"] in ("极高风险", "高风险"):
            base_days = 30
            category = "复杂件"
        elif case.claim_amount > 500000:
            base_days = 15
            category = "高额件"
        elif case.accident_type == "身故":
            base_days = 15
            category = "身故事件"
        else:
            category = "普通件"

        deadline = datetime.now() + timedelta(days=base_days)
        return {
            "category": category,
            "days": base_days,
            "deadline": deadline.strftime("%Y-%m-%d"),
        }

    def review(self,
               insurance_type: str = "终身寿险",
               accident_type: str = "身故",
               accident_reason: str = "",
               hospital_level: str = "三甲医院",
               total_expense: float = 0.0,
               insurance_paid: float = 0.0,
               policy_terms: Optional[dict] = None,
               patient_history: Optional[dict] = None,
               admission_date: str = "",
               discharge_date: str = "",
               policy_start_date: str = "",
               policy_years: int = 0,
               premium_paid: bool = True,
               beneficiary: str = "",
               beneficiary_relation: str = "",
               claim_amount: float = 0.0,
               death_certificate: bool = False,
               accident_report: bool = False,
               sobriety_test: bool = True,
               license_valid: bool = True,
               vehicle_type: str = "",
               ) -> dict:
        """
        执行理赔审核

        参数：
            insurance_type: 险种类型（终身寿险/定期寿险/两全险/重疾险/医疗险/意外险）
            accident_type: 出险类型（疾病/意外/全残/身故）
            accident_reason: 出险原因
            hospital_level: 就诊医院等级
            total_expense: 住院总花费
            insurance_paid: 医保已报销
            policy_terms: 保单条款
            patient_history: 既往病史
            admission_date: 入院日期
            discharge_date: 出院日期
            policy_start_date: 保单生效日期
            policy_years: 保单生效年限
            premium_paid: 保费是否正常缴纳
            beneficiary: 受益人
            beneficiary_relation: 受益人关系
            claim_amount: 申请理赔金额
            death_certificate: 死亡证明
            accident_report: 事故证明
            sobriety_test: 酒测是否通过（True=无饮酒/检测正常）
            license_valid: 驾驶证是否有效
            vehicle_type: 车辆类型

        返回：
            审核结果字典
        """
        self._case_counter += 1
        claim_id = f"CLM-V2-{datetime.now().strftime('%Y%m%d')}-{self._case_counter:03d}"

        # 构建案件对象
        case = ClaimReviewCase(
            insurance_type=insurance_type,
            accident_type=accident_type,
            accident_reason=accident_reason,
            hospital_level=hospital_level,
            total_expense=total_expense,
            insurance_paid=insurance_paid,
            policy_terms=policy_terms or {},
            patient_history=patient_history or {},
            admission_date=admission_date or datetime.now().strftime("%Y-%m-%d"),
            discharge_date=discharge_date,
            policy_start_date=policy_start_date,
            policy_years=policy_years,
            premium_paid=premium_paid,
            beneficiary=beneficiary,
            beneficiary_relation=beneficiary_relation,
            claim_amount=claim_amount,
            death_certificate=death_certificate,
            accident_report=accident_report,
            sobriety_test=sobriety_test,
            license_valid=license_valid,
            vehicle_type=vehicle_type,
        )

        # 执行各项检查
        policy_validity = self._check_policy_validity(case)
        history_check = self._check_pre_existing_conditions(case)
        exclusion_check = self._check_exclusion_clauses(case)
        fraud = self._fraud_check(case)
        claim_calc = self._calculate_claim_amount(case)
        decision = self._determine_decision(case, policy_validity, history_check,
                                           exclusion_check, fraud)
        proc_time = self._estimate_processing_time(case, fraud)
        next_steps = self._generate_next_steps(case, decision, policy_validity,
                                               exclusion_check, history_check)

        # 组装审核要点
        audit_points = {
            "history_relevance": history_check,
            "exclusion_clauses": exclusion_check,
            "policy_validity": policy_validity,
        }

        # 根据决策调整最终赔付金额
        if decision["code"] == DECISION_REJECTED:
            final_payment = 0.0
            claim_calc["final_payment"] = 0.0
            claim_calc["approved_amount"] = 0.0
        elif decision["code"] == DECISION_PROPORTIONAL:
            # 比例赔付按60%计算
            final_payment = claim_calc["final_payment"] * 0.6
            claim_calc["final_payment"] = final_payment
            claim_calc["approved_amount"] = final_payment

        return {
            "claim_id": claim_id,
            "timestamp": datetime.now().isoformat(timespec='seconds') + "+08:00",
            "review_decision": decision,
            "audit_points": audit_points,
            "claim_calculation": claim_calc,
            "fraud_check": fraud,
            "processing_time": proc_time,
            "next_steps": next_steps,
        }


# ============================================================
# 示例 / 测试
# ============================================================

if __name__ == "__main__":
    engine = ClaimReviewV2Engine()

    # 测试1：终身寿险身故理赔
    print("=" * 60)
    print("测试1：终身寿险身故理赔")
    result = engine.review(
        insurance_type="终身寿险",
        accident_type="身故",
        accident_reason="疾病身故",
        claim_amount=500000,
        policy_start_date="2023-01-01",
        policy_years=3,
        premium_paid=True,
        beneficiary="张三",
        beneficiary_relation="配偶",
        death_certificate=True,
        sobriety_test=True,
        license_valid=True,
    )
    print(f"审核结果：{result['review_decision']}")
    print(f"最终赔付：¥{result['claim_calculation']['final_payment']:,.2f}")
    print(f"反欺诈：{result['fraud_check']['risk_level']}（{result['fraud_check']['score']}分）")
    print(f"审核要点：{result['audit_points']}")
