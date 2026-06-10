"""
费用报销审计引擎 ExpenseAuditEngine
核心逻辑：审核报销单据，返回审计结果 + 违规类型 + 风险提示 + 合规建议
报销标准：招待费收入千分之五上限
"""

import re
import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AuditResult:
    """审计结果"""
    status: str  # 通过 | 驳回 | 需补充
    violations: list = field(default_factory=list)
    risk_level: str = "低"  # 高 | 中 | 低
    suggestions: list = field(default_factory=list)
    details: str = ""


class ExpenseAuditEngine:
    """费用报销审计引擎"""

    # 违规类型编码表
    VIOLATION_CODES = {
        "V001": "招待费超收入千分之五上限",
        "V002": "招待费事前未审批",
        "V003": "缺少正规发票",
        "V004": "发票日期晚于报销日期",
        "V005": "单笔金额超限未额外审批",
        "V006": "费用类型与部门不匹配",
        "V007": "同员工同类型费用本月累计异常",
    }

    # 费用类型与部门匹配规则
    EXPENSE_DEPT_RULES = {
        "招待费": ["市场部", "销售部", "业务部", "客户部"],
        "培训费": ["人力资源部", "培训部", "行政部"],
        "办公费": ["行政部", "综合管理部", "财务部"],
        "差旅费": ["销售部", "市场部", "业务部", "全体"],
        "交通费": ["全体"],
        "其他": ["全体"],
    }

    def __init__(self, api_mode: bool = False):
        """
        初始化审计引擎

        Args:
            api_mode: API模式 True=静默（无print）, False=正常输出
        """
        self.api_mode = api_mode

    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)

    def _get_risk_level(self, violations: list) -> str:
        """根据违规数量和类型判定风险等级"""
        if any(v in ["V001", "V002"] for v in violations):
            return "高"
        elif len(violations) >= 2:
            return "中"
        elif violations:
            return "低"
        return "低"

    def _check_expense_dept_match(self, expense_type: str, department: str) -> bool:
        """检查费用类型与部门是否匹配"""
        if expense_type not in self.EXPENSE_DEPT_RULES:
            return True  # 未知类型放行
        allowed_depts = self.EXPENSE_DEPT_RULES[expense_type]
        return department in allowed_depts or "全体" in allowed_depts

    def audit(
        self,
        employee: str,
        department: str,
        expense_type: str,
        amount: float,
        invoice: str = "有",
        pre_approval: str = "有",
        revenue: float = 1000000.0,  # 默认假设月收入100万
        remarks: str = "",
    ) -> dict:
        """
        审计单笔报销单据

        Args:
            employee: 员工姓名
            department: 部门
            expense_type: 费用类型
            amount: 报销金额（元）
            invoice: 发票（有/无/待补）
            pre_approval: 事前审批（有/无）
            revenue: 收入（用于计算招待费上限），默认100万
            remarks: 备注

        Returns:
            dict: 审计结果
        """
        violations = []
        suggestions = []

        # === 招待费专项检查 ===
        if expense_type == "招待费":
            # V001: 招待费超收入千分之五上限
            max_entertainment = revenue * 0.005  # 千分之五
            if amount > max_entertainment:
                violations.append("V001")
                suggestions.append(f"招待费上限为收入×0.5‰={max_entertainment:.0f}元，当前报销{amount:.0f}元，超出{(amount - max_entertainment):.0f}元，请提供更小规模的招待方案或分拆报销。")

            # V002: 招待费事前未审批（单笔>1000元必须事前审批）
            if amount > 1000 and pre_approval == "无":
                violations.append("V002")
                suggestions.append("招待费单笔超过1000元必须事前审批，请补充事前申请流程或降低单笔报销金额。")

        # === 通用检查 ===
        # V003: 缺少发票
        if invoice == "无":
            violations.append("V003")
            suggestions.append("缺少正规发票，请补充正规发票后重新提交。")

        # V004: 发票待补
        if invoice == "待补":
            if "V002" not in violations and "V001" not in violations:
                violations.append("V003")  # 降级为缺少发票
            suggestions.append("发票待补充，请在3个工作日内补齐发票，逾期将自动驳回。")

        # V005: 单笔金额超限未额外审批（>50000元）
        if amount > 50000:
            violations.append("V005")
            suggestions.append("单笔报销超过5万元需部门负责人额外审批，请联系部门负责人会签。")

        # V006: 费用类型与部门不匹配
        if not self._check_expense_dept_match(expense_type, department):
            violations.append("V006")
            suggestions.append(f"{expense_type}通常应由{','.join(self.EXPENSE_DEPT_RULES.get(expense_type, ['相关']))}部门报销，当前部门为{department}，请确认报销主体是否正确。")

        # === 判定状态 ===
        if not violations:
            status = "通过"
            details = f"【通过】员工{employee}报销{expense_type}{amount:.0f}元，符合公司报销规范。"
            risk_level = "低"
        elif "V001" in violations or "V003" in violations:
            status = "驳回"
            details = f"【驳回】员工{employee}报销{expense_type}{amount:.0f}元，存在严重违规项，请修正后重新提交。"
            risk_level = "高"
        elif "V002" in violations or "V005" in violations:
            status = "需补充"
            details = f"【需补充】员工{employee}报销{expense_type}{amount:.0f}元，需补充相关材料后提交。"
            risk_level = "中"
        else:
            status = "需补充"
            details = f"【需补充】员工{employee}报销{expense_type}{amount:.0f}元，需补充相关材料。"
            risk_level = "低"

        # 风险等级
        risk_level = self._get_risk_level(violations)

        result = AuditResult(
            status=status,
            violations=violations,
            risk_level=risk_level,
            suggestions=suggestions,
            details=details,
        )

        self._log(f"\n{'='*50}")
        self._log(f"费用报销审计报告")
        self._log(f"{'='*50}")
        self._log(f"员工：{employee} | 部门：{department}")
        self._log(f"费用类型：{expense_type} | 金额：{amount:.0f}元")
        self._log(f"发票：{invoice} | 事前审批：{pre_approval}")
        self._log(f"{'-'*50}")
        self._log(f"审计结果：{status}")
        self._log(f"风险等级：{risk_level}")
        if violations:
            self._log(f"违规类型：{', '.join([self.VIOLATION_CODES.get(v, v) for v in violations])}")
        if suggestions:
            self._log(f"合规建议：")
            for s in suggestions:
                self._log(f"  - {s}")
        self._log(f"说明：{details}")
        self._log(f"{'='*50}\n")

        return {
            "status": result.status,
            "violations": result.violations,
            "risk_level": result.risk_level,
            "suggestions": result.suggestions,
            "details": result.details,
        }

    def audit_from_text(self, text: str) -> dict:
        """
        从自然语言文本解析报销信息并审计

        支持格式：
        "费用报销 张三 市场部 招待费 5000元 事前未审批"
        "费用报销 李四 技术部 培训费 2000元 有发票 事前已审批"

        Args:
            text: 自然语言报销描述

        Returns:
            dict: 审计结果
        """
        # 解析文本
        # 格式：费用报销 姓名 部门 费用类型 金额 附加信息
        pattern = r'费用报销\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+(?:\.\d+)?)\s*(?:元)?\s*(.*)'
        match = re.match(pattern, text.strip())

        if not match:
            # 尝试简化解析
            parts = text.replace("费用报销", "").strip().split()
            if len(parts) >= 4:
                employee = parts[0]
                department = parts[1]
                expense_type = parts[2]
                amount_str = parts[3].replace("元", "")
                try:
                    amount = float(amount_str)
                except ValueError:
                    amount = 0
                remarks = " ".join(parts[4:]) if len(parts) > 4 else ""
            else:
                return {
                    "status": "驳回",
                    "violations": [],
                    "risk_level": "高",
                    "suggestions": ["文本格式不正确，请使用：费用报销 姓名 部门 费用类型 金额元 附加信息"],
                    "details": f"【驳回】无法解析文本：{text}，请使用标准格式提交。",
                }
        else:
            employee, department, expense_type, amount, remarks = match.groups()
            amount = float(amount)

        # 解析附加信息
        pre_approval = "有" if "事前已审批" in remarks or "有" in remarks else "无"
        invoice = "有" if "有发票" in remarks or ("无" not in remarks and "待补" not in remarks) else "待补"

        if "无发票" in remarks:
            invoice = "无"

        if "事前未审批" in remarks:
            pre_approval = "无"

        return self.audit(
            employee=employee,
            department=department,
            expense_type=expense_type,
            amount=amount,
            invoice=invoice,
            pre_approval=pre_approval,
            remarks=remarks,
        )


if __name__ == "__main__":
    # 测试
    engine = ExpenseAuditEngine()

    print("测试1：招待费超限且事前未审批")
    result1 = engine.audit_from_text("费用报销 张三 市场部 招待费 5000元 事前未审批")
    print(json.dumps(result1, ensure_ascii=False, indent=2))

    print("\n测试2：正常招待费报销")
    result2 = engine.audit_from_text("费用报销 李四 市场部 招待费 3000元 有发票 事前已审批")
    print(json.dumps(result2, ensure_ascii=False, indent=2))

    print("\n测试3：缺少发票")
    result3 = engine.audit_from_text("费用报销 王五 技术部 培训费 2000元 无发票")
    print(json.dumps(result3, ensure_ascii=False, indent=2))
