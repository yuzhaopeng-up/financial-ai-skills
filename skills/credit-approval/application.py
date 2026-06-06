#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信贷申请受理模块
申请信息校验、材料完整性检查
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class ApplicantType(Enum):
    """申请人类型"""
    PERSONAL = "个人"
    CORPORATE = "企业"


class LoanPurpose(Enum):
    """贷款用途"""
    CONSUMPTION = "消费贷"
    HOUSING = "住房按揭"
    CAR = "汽车贷"
    EDUCATION = "教育贷"
    BUSINESS = "经营贷"
    WORKING_CAPITAL = "流动资金"
    PROJECT = "项目融资"


class ApplicationStatus(Enum):
    """申请状态"""
    DRAFT = "草稿"
    SUBMITTED = "已提交"
    DOCUMENT_CHECK = "材料审核中"
    CREDIT_CHECK = "征信查询中"
    SCORING = "评分中"
    APPROVAL = "审批中"
    APPROVED = "已批准"
    REJECTED = "已拒绝"
    COMPLETED = "已完成"


@dataclass
class LoanApplication:
    """贷款申请"""
    application_id: str
    applicant_type: ApplicantType
    
    # 基本信息
    name: str
    id_number: str
    phone: str
    
    # 贷款信息
    loan_amount: float
    loan_purpose: LoanPurpose
    loan_term_months: int
    
    # 财务信息
    income_monthly: float
    existing_debts: List[Dict] = field(default_factory=list)
    
    # 材料清单
    documents: List[str] = field(default_factory=list)
    
    # 状态
    status: ApplicationStatus = ApplicationStatus.DRAFT
    submit_time: Optional[str] = None
    
    # 企业特有
    company_name: Optional[str] = None
    credit_code: Optional[str] = None
    business_license: Optional[str] = None


class ApplicationProcessor:
    """申请处理器"""

    # 各类贷款所需材料
    REQUIRED_DOCUMENTS = {
        LoanPurpose.CONSUMPTION: [
            "身份证", "收入证明", "银行流水", "征信授权书"
        ],
        LoanPurpose.HOUSING: [
            "身份证", "收入证明", "银行流水", "购房合同", "首付证明", "征信授权书"
        ],
        LoanPurpose.CAR: [
            "身份证", "收入证明", "银行流水", "购车合同", "征信授权书"
        ],
        LoanPurpose.BUSINESS: [
            "身份证", "营业执照", "经营流水", "财务报表", "征信授权书"
        ],
        LoanPurpose.WORKING_CAPITAL: [
            "营业执照", "财务报表", "银行流水", "贸易合同", "征信授权书"
        ],
        LoanPurpose.PROJECT: [
            "营业执照", "项目可研报告", "财务报表", "环评报告", "土地证", "征信授权书"
        ]
    }

    def __init__(self):
        self.applications = {}

    def create_application(self, application_id: str,
                           applicant_type: str,
                           name: str,
                           id_number: str,
                           phone: str,
                           loan_amount: float,
                           loan_purpose: str,
                           loan_term_months: int,
                           income_monthly: float,
                           company_name: Optional[str] = None,
                           credit_code: Optional[str] = None) -> LoanApplication:
        """创建申请"""
        
        app_type = ApplicantType.PERSONAL if applicant_type == "个人" else ApplicantType.CORPORATE
        purpose = self._parse_loan_purpose(loan_purpose)
        
        application = LoanApplication(
            application_id=application_id,
            applicant_type=app_type,
            name=name,
            id_number=id_number,
            phone=phone,
            loan_amount=loan_amount,
            loan_purpose=purpose,
            loan_term_months=loan_term_months,
            income_monthly=income_monthly,
            company_name=company_name,
            credit_code=credit_code
        )
        
        self.applications[application_id] = application
        return application

    def _parse_loan_purpose(self, purpose: str) -> LoanPurpose:
        """解析贷款用途"""
        mapping = {
            "消费": LoanPurpose.CONSUMPTION,
            "住房": LoanPurpose.HOUSING,
            "汽车": LoanPurpose.CAR,
            "教育": LoanPurpose.EDUCATION,
            "经营": LoanPurpose.BUSINESS,
            "流动资金": LoanPurpose.WORKING_CAPITAL,
            "项目": LoanPurpose.PROJECT
        }
        return mapping.get(purpose, LoanPurpose.CONSUMPTION)

    def submit_application(self, application_id: str) -> Dict:
        """提交申请"""
        application = self.applications.get(application_id)
        if not application:
            return {"success": False, "error": "申请不存在"}
        
        # 基础校验
        validation = self._validate_application(application)
        if not validation["valid"]:
            return {"success": False, "errors": validation["errors"]}
        
        # 更新状态
        application.status = ApplicationStatus.SUBMITTED
        application.submit_time = datetime.now().isoformat()
        
        return {
            "success": True,
            "application_id": application_id,
            "status": application.status.value,
            "submit_time": application.submit_time,
            "next_step": "材料完整性检查"
        }

    def _validate_application(self, application: LoanApplication) -> Dict:
        """校验申请信息"""
        errors = []
        
        # 校验身份证号
        if len(application.id_number) != 18:
            errors.append("身份证号格式不正确")
        
        # 校验手机号
        if len(application.phone) != 11:
            errors.append("手机号格式不正确")
        
        # 校验贷款金额
        if application.loan_amount <= 0:
            errors.append("贷款金额必须大于0")
        elif application.loan_amount > 10000000:
            errors.append("贷款金额超过上限")
        
        # 校验期限
        if application.loan_term_months < 1 or application.loan_term_months > 360:
            errors.append("贷款期限不合法")
        
        # 校验收入
        if application.income_monthly <= 0:
            errors.append("月收入必须大于0")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def check_documents(self, application_id: str,
                        uploaded_documents: List[str]) -> Dict:
        """检查材料完整性"""
        application = self.applications.get(application_id)
        if not application:
            return {"success": False, "error": "申请不存在"}
        
        required = self.REQUIRED_DOCUMENTS.get(application.loan_purpose, [])
        
        missing = []
        for doc in required:
            if doc not in uploaded_documents:
                missing.append(doc)
        
        application.documents = uploaded_documents
        
        if missing:
            application.status = ApplicationStatus.DOCUMENT_CHECK
            return {
                "success": False,
                "status": "材料不完整",
                "missing_documents": missing,
                "uploaded": uploaded_documents,
                "required": required
            }
        
        application.status = ApplicationStatus.CREDIT_CHECK
        return {
            "success": True,
            "status": "材料完整",
            "uploaded_documents": uploaded_documents,
            "next_step": "征信查询"
        }

    def get_application_summary(self, application_id: str) -> Dict:
        """获取申请摘要"""
        app = self.applications.get(application_id)
        if not app:
            return {}
        
        return {
            "申请编号": app.application_id,
            "申请类型": app.applicant_type.value,
            "申请人": app.name,
            "贷款金额": f"{app.loan_amount:,.0f} 元",
            "贷款用途": app.loan_purpose.value,
            "贷款期限": f"{app.loan_term_months} 个月",
            "月收入": f"{app.income_monthly:,.0f} 元",
            "当前状态": app.status.value,
            "已上传材料": app.documents
        }
