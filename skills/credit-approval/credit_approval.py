#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信贷审批主引擎
整合所有模块，提供一站式信贷审批服务
"""

from application import ApplicationProcessor, LoanPurpose
from credit_scorer import CreditScorer
from decision_engine import DecisionEngine


class CreditApprovalEngine:
    """信贷审批引擎"""

    def __init__(self):
        self.application_processor = ApplicationProcessor()
        self.credit_scorer = CreditScorer()
        self.decision_engine = DecisionEngine()

    def submit_application(self, application_id: str,
                           applicant_type: str,
                           name: str,
                           id_number: str,
                           phone: str,
                           loan_amount: float,
                           loan_purpose: str,
                           loan_term_months: int,
                           income_monthly: float,
                           company_name: str = None,
                           credit_code: str = None) -> dict:
        """提交申请"""
        print(f"📝 提交信贷申请 [{application_id}]...")

        # 创建申请
        application = self.application_processor.create_application(
            application_id=application_id,
            applicant_type=applicant_type,
            name=name,
            id_number=id_number,
            phone=phone,
            loan_amount=loan_amount,
            loan_purpose=loan_purpose,
            loan_term_months=loan_term_months,
            income_monthly=income_monthly,
            company_name=company_name,
            credit_code=credit_code
        )

        # 提交
        result = self.application_processor.submit_application(application_id)

        return result

    def upload_documents(self, application_id: str,
                         documents: list) -> dict:
        """上传材料"""
        print(f"📄 检查申请材料 [{application_id}]...")

        result = self.application_processor.check_documents(
            application_id=application_id,
            uploaded_documents=documents
        )

        return result

    def credit_assessment(self, application_id: str,
                          age: int,
                          education: str,
                          occupation: str,
                          housing_status: str,
                          credit_history_years: int,
                          existing_loans: int,
                          overdue_count_24m: int,
                          max_overdue_days: int,
                          credit_utilization: float,
                          query_count_6m: int,
                          payment_regularity: str) -> dict:
        """信用评估"""
        print(f"💳 执行信用评估 [{application_id}]...")

        # 获取申请信息
        app_summary = self.application_processor.get_application_summary(application_id)
        income = float(app_summary.get("月收入", "0").replace(",", "").replace(" 元", ""))

        score = self.credit_scorer.calculate_score(
            application_id=application_id,
            age=age,
            education=education,
            occupation=occupation,
            income_monthly=income,
            housing_status=housing_status,
            credit_history_years=credit_history_years,
            existing_loans=existing_loans,
            overdue_count_24m=overdue_count_24m,
            max_overdue_days=max_overdue_days,
            credit_utilization=credit_utilization,
            query_count_6m=query_count_6m,
            payment_regularity=payment_regularity
        )

        return self.credit_scorer.get_score_summary(application_id)

    def approval_decision(self, application_id: str,
                          existing_debts_monthly: float,
                          collateral_value: float = 0) -> dict:
        """审批决策"""
        print(f"⚖️ 执行审批决策 [{application_id}]...")

        # 获取信用评分
        score_summary = self.credit_scorer.get_score_summary(application_id)
        credit_score = score_summary.get("信用评分", 0)
        credit_grade = score_summary.get("信用等级", "")

        # 获取申请信息
        app_summary = self.application_processor.get_application_summary(application_id)
        loan_amount = float(app_summary.get("贷款金额", "0").replace(",", "").replace(" 元", ""))
        income = float(app_summary.get("月收入", "0").replace(",", "").replace(" 元", ""))

        decision = self.decision_engine.make_decision(
            application_id=application_id,
            credit_score=credit_score,
            credit_grade=credit_grade,
            loan_amount=loan_amount,
            income_monthly=income,
            existing_debts_monthly=existing_debts_monthly,
            overdue_count_24m=score_summary.get("风险因子", []).count("逾期") if score_summary.get("风险因子") else 0,
            max_overdue_days=0,
            collateral_value=collateral_value
        )

        return self.decision_engine.get_decision_summary(application_id)

    def full_approval_process(self, application_id: str,
                              applicant_type: str,
                              name: str,
                              id_number: str,
                              phone: str,
                              loan_amount: float,
                              loan_purpose: str,
                              loan_term_months: int,
                              income_monthly: float,
                              documents: list,
                              age: int,
                              education: str,
                              occupation: str,
                              housing_status: str,
                              credit_history_years: int,
                              existing_loans: int,
                              overdue_count_24m: int,
                              max_overdue_days: int,
                              credit_utilization: float,
                              query_count_6m: int,
                              payment_regularity: str,
                              existing_debts_monthly: float,
                              collateral_value: float = 0) -> dict:
        """执行完整审批流程"""
        print(f"\n{'='*60}")
        print(f"🏦 开始信贷审批全流程")
        print(f"{'='*60}\n")

        # 1. 提交申请
        print("步骤 1/4: 申请受理...")
        submit_result = self.submit_application(
            application_id=application_id,
            applicant_type=applicant_type,
            name=name,
            id_number=id_number,
            phone=phone,
            loan_amount=loan_amount,
            loan_purpose=loan_purpose,
            loan_term_months=loan_term_months,
            income_monthly=income_monthly
        )

        if not submit_result.get("success"):
            return {"error": submit_result.get("errors", ["申请提交失败"])}

        # 2. 材料审核
        print("步骤 2/4: 材料审核...")
        doc_result = self.upload_documents(application_id, documents)

        if not doc_result.get("success"):
            return {"error": doc_result.get("missing_documents", ["材料不完整"])}

        # 3. 信用评估
        print("步骤 3/4: 信用评估...")
        credit_result = self.credit_assessment(
            application_id=application_id,
            age=age,
            education=education,
            occupation=occupation,
            housing_status=housing_status,
            credit_history_years=credit_history_years,
            existing_loans=existing_loans,
            overdue_count_24m=overdue_count_24m,
            max_overdue_days=max_overdue_days,
            credit_utilization=credit_utilization,
            query_count_6m=query_count_6m,
            payment_regularity=payment_regularity
        )

        # 4. 审批决策
        print("步骤 4/4: 审批决策...")
        decision_result = self.approval_decision(
            application_id=application_id,
            existing_debts_monthly=existing_debts_monthly,
            collateral_value=collateral_value
        )

        # 生成报告
        report = self._generate_report(
            application_id, submit_result, doc_result,
            credit_result, decision_result
        )

        print("\n✅ 信贷审批完成！")

        return {
            "application": submit_result,
            "documents": doc_result,
            "credit": credit_result,
            "decision": decision_result,
            "report_markdown": report
        }

    def _generate_report(self, application_id: str,
                         submit: dict, doc: dict,
                         credit: dict, decision: dict) -> str:
        """生成审批报告"""
        lines = []
        lines.append("# 🏦 信贷审批报告")
        lines.append("")
        lines.append(f"**申请编号**：{application_id}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 申请信息
        app_summary = self.application_processor.get_application_summary(application_id)
        lines.append("## 一、申请信息")
        lines.append("")
        for key, value in app_summary.items():
            lines.append(f"- **{key}**：{value}")
        lines.append("")

        # 信用评估
        lines.append("## 二、信用评估")
        lines.append("")
        lines.append(f"- **信用评分**：{credit.get('信用评分', '-')} 分")
        lines.append(f"- **信用等级**：{credit.get('信用等级', '-')}")
        lines.append("")
        lines.append("### 维度得分")
        dimensions = credit.get("维度得分", {})
        for dim, score in dimensions.items():
            lines.append(f"- {dim}：{score} 分")
        lines.append("")

        if credit.get("风险因子"):
            lines.append("### ⚠️ 风险因子")
            for risk in credit["风险因子"]:
                lines.append(f"- {risk}")
            lines.append("")

        # 审批决策
        lines.append("## 三、审批决策")
        lines.append("")
        lines.append(f"- **审批结果**：{decision.get('审批结果', '-')}")
        lines.append(f"- **批准金额**：{decision.get('批准金额', '-')}")
        lines.append(f"- **批准利率**：{decision.get('批准利率', '-')}")
        lines.append("")

        if decision.get("审批理由"):
            lines.append("### 审批理由")
            for reason in decision["审批理由"]:
                lines.append(f"- {reason}")
            lines.append("")

        if decision.get("附加条件") and decision["附加条件"] != ["无"]:
            lines.append("### 附加条件")
            for condition in decision["附加条件"]:
                lines.append(f"- {condition}")
            lines.append("")

        if decision.get("风险提示") and decision["风险提示"] != ["无显著风险"]:
            lines.append("### 风险提示")
            for warning in decision["风险提示"]:
                lines.append(f"- {warning}")
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("*本报告由信贷审批 Skill 自动生成*")

        return "\n".join(lines)


if __name__ == "__main__":
    # 演示
    engine = CreditApprovalEngine()

    result = engine.full_approval_process(
        application_id="APP20250606001",
        applicant_type="个人",
        name="张三",
        id_number="31010119900101XXXX",
        phone="13800138000",
        loan_amount=500000,
        loan_purpose="住房",
        loan_term_months=240,
        income_monthly=25000,
        documents=["身份证", "收入证明", "银行流水", "购房合同", "首付证明", "征信授权书"],
        age=35,
        education="本科",
        occupation="IT工程师",
        housing_status="租房",
        credit_history_years=10,
        existing_loans=1,
        overdue_count_24m=0,
        max_overdue_days=0,
        credit_utilization=0.3,
        query_count_6m=2,
        payment_regularity="按时",
        existing_debts_monthly=5000,
        collateral_value=800000
    )

    print("\n" + "="*60)
    print("📋 审批报告预览")
    print("="*60)
    print(result["report_markdown"][:2500])
    print("\n... [报告已截断] ...")
