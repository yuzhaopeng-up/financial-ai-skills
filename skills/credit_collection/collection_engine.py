# -*- coding: utf-8 -*-
"""
CreditCollectionEngine - 信用卡逾期催收决策引擎

支持M1-M3+全阶段催收策略生成、合规红线检测、催收话术输出。
"""

from datetime import datetime, time
from typing import Optional


class CreditCollectionEngine:
    """信用卡逾期催收决策引擎"""

    # 催收时段限制（24小时制）
    COLLECTION_START_HOUR = 9
    COLLECTION_END_HOUR = 21

    # 逾期阶段阈值
    STAGE_M1_MAX = 30
    STAGE_M2_MAX = 60
    STAGE_M3_MAX = 90

    def __init__(self):
        self.current_time = datetime.now()

    def _check_time_compliance(self) -> dict:
        """检测当前时间是否符合催收时段要求"""
        current_hour = self.current_time.hour
        is_compliant = self.COLLECTION_START_HOUR <= current_hour < self.COLLECTION_END_HOUR
        return {
            "compliant": is_compliant,
            "current_hour": current_hour,
            "allowed_range": f"{self.COLLECTION_START_HOUR}:00-{self.COLLECTION_END_HOUR}:00",
            "violation": not is_compliant
        }

    def _determine_stage(self, overdue_days: int) -> str:
        """确定逾期阶段"""
        if overdue_days <= self.STAGE_M1_MAX:
            return "M1"
        elif overdue_days <= self.STAGE_M2_MAX:
            return "M2"
        elif overdue_days <= self.STAGE_M3_MAX:
            return "M3"
        else:
            return "M3+"

    def _determine_priority(self, overdue_days: int, outstanding_amount: float, payment_history: list) -> str:
        """确定催收优先级"""
        score = 0

        # 逾期天数评分
        if overdue_days > 90:
            score += 4
        elif overdue_days > 60:
            score += 3
        elif overdue_days > 30:
            score += 2
        else:
            score += 1

        # 欠款金额评分
        if outstanding_amount > 100000:
            score += 3
        elif outstanding_amount > 50000:
            score += 2
        elif outstanding_amount > 10000:
            score += 1

        # 历史还款记录评分
        late_count = sum(1 for h in payment_history if "逾期" in h or "延期" in h or "违约" in h)
        score += min(late_count, 3)

        if score >= 8:
            return "紧急"
        elif score >= 5:
            return "高"
        elif score >= 3:
            return "中"
        else:
            return "低"

    def _generate_strategies(self, stage: str, contact_valid: bool, customer_type: str) -> list:
        """生成催收策略列表"""
        strategies = []

        # 基础策略（按阶段）
        stage_strategies = {
            "M1": ["短信提醒", "APP推送", "邮件通知"],
            "M2": ["电话催收", "短信提醒", "APP推送"],
            "M3": ["上门催收", "电话催收", "律师函"],
            "M3+": ["移交法务", "诉讼准备", "资产查封申请"]
        }
        strategies.extend(stage_strategies.get(stage, []))

        # 联系方式有效性调整
        if not contact_valid:
            strategies.append("外访确认地址")
            if stage in ["M2", "M3", "M3+"]:
                strategies.append("联系紧急联系人核实信息")

        # 客户类型调整
        if customer_type in ["enterprise", "企业"]:
            strategies.append("企业账户专项催收")
            strategies.append("银行保函核查")

        return list(dict.fromkeys(strategies))  # 去重保持顺序

    def _generate_installment_advice(self, overdue_days: int, outstanding_amount: float, payment_history: list) -> dict:
        """生成分期还款建议"""
        # 计算建议分期期数
        if outstanding_amount <= 5000:
            installments = [1, 2, 3]
        elif outstanding_amount <= 20000:
            installments = [3, 6, 12]
        elif outstanding_amount <= 50000:
            installments = [6, 12, 24]
        else:
            installments = [12, 24, 36]

        # 根据逾期天数调整建议
        if overdue_days > 90:
            recommendation = "建议一次性还清或最短分期"
        elif overdue_days > 60:
            recommendation = f"建议{installments[0]}-{installments[1]}期分期"
        elif overdue_days > 30:
            recommendation = f"建议{installments[1]}期分期"
        else:
            recommendation = f"可选{installments[0]}-{installments[1]}期分期"

        # 计算每期最低还款估算
        min_monthly = outstanding_amount / max(installments[-1], 1)
        handling_fee_rate = 0.006  # 假设月手续费0.6%
        monthly_payment = outstanding_amount / installments[1] * (1 + handling_fee_rate)

        return {
            "recommended_installments": installments,
            "suggested_plan": installments[1],
            "min_monthly_payment": round(monthly_payment, 2),
            "handling_fee_rate": f"{handling_fee_rate * 100}%/月",
            "recommendation": recommendation
        }

    def _generate_legal_warning(self, stage: str, outstanding_amount: float) -> str:
        """生成法律后果提示"""
        warnings = {
            "M1": "根据《商业银行信用卡业务监督管理办法》，逾期还款将产生罚息，并影响个人征信记录。请尽快处理欠款，避免产生更多费用。",
            "M2": "逾期超过60天将可能被冻结信用卡账户，恶意透支将承担法律责任。根据《刑法》第196条，信用卡诈骗罪最高可判处无期徒刑。",
            "M3": "经多次催收仍不归还欠款，银行有权向人民法院提起诉讼。届时将承担诉讼费、律师费及全部欠款。",
            "M3+": "案件已移交法务部门，即将进入诉讼程序。如仍不归还，法院将采取强制执行措施，包括但不限于：冻结银行账户、查封财产、限制高消费、纳入失信被执行人名单。"
        }

        base_warning = warnings.get(stage, warnings["M1"])

        if outstanding_amount > 50000:
            base_warning += f" 另根据相关法规，欠款金额{outstanding_amount:.0f}元已达到立案标准，请高度重视。"

        return base_warning

    def _generate_scripts(self, stage: str, customer_name: str = "客户") -> dict:
        """生成标准化催收话术"""
        scripts = {
            "initial": {
                "channel": "短信",
                "template": f"【银行提醒】尊敬的{customer_name}，您的信用卡已逾期，请尽快还款。如有疑问请致电客服热线。",
                "tone": "礼貌提醒"
            },
            "phone": {
                "channel": "电话",
                "template": f"您好{customer_name}，我是XX银行信用卡中心客服，您账户已逾期，请尽快处理欠款。请问您方便什么时候还款？",
                "tone": "专业询问"
            },
            "visit": {
                "channel": "上门",
                "template": f"您好{customer_name}，我是XX银行催收人员，这是第X次上门沟通。根据合同约定，您需要在X日前归还欠款，否则我行将采取法律措施。",
                "tone": "严肃正式"
            },
            "legal": {
                "channel": "法务",
                "template": f"您的案件已移交我行法务部门，我行已准备相关诉讼材料。如您在收函后X日内仍不归还欠款，我行将向人民法院提起诉讼。",
                "tone": "严肃警告"
            }
        }

        # 按阶段返回对应话术
        if stage == "M1":
            return {"current": scripts["initial"]}
        elif stage == "M2":
            return {
                "current": scripts["phone"],
                "fallback": scripts["initial"]
            }
        elif stage == "M3":
            return {
                "current": scripts["visit"],
                "fallback": scripts["phone"]
            }
        else:
            return {
                "current": scripts["legal"],
                "fallback": scripts["visit"]
            }

    def generate_collection_plan(
        self,
        overdue_days: int,
        outstanding_amount: float,
        customer_type: str = "personal",
        payment_history: Optional[list] = None,
        contact_valid: bool = True,
        customer_name: str = "客户"
    ) -> dict:
        """
        生成完整催收方案

        Args:
            overdue_days: 逾期天数
            outstanding_amount: 欠款金额（元）
            customer_type: 客户类型 ("personal"/"enterprise"/"企业")
            payment_history: 历史还款记录列表
            contact_valid: 联系方式是否有效
            customer_name: 客户姓名

        Returns:
            催收方案字典
        """
        if payment_history is None:
            payment_history = ["按时"]

        # 基本判断
        stage = self._determine_stage(overdue_days)
        priority = self._determine_priority(overdue_days, outstanding_amount, payment_history)
        strategies = self._generate_strategies(stage, contact_valid, customer_type)
        time_check = self._check_time_compliance()

        # 生成各部分内容
        installment_advice = self._generate_installment_advice(overdue_days, outstanding_amount, payment_history)
        legal_warning = self._generate_legal_warning(stage, outstanding_amount)
        scripts = self._generate_scripts(stage, customer_name)

        # 违规检测
        red_line_violations = []
        if time_check["violation"]:
            red_line_violations.append(f"时间违规：当前{time_check['current_hour']}:00不符合催收时段{time_check['allowed_range']}")

        if not contact_valid:
            red_line_violations.append("联系方式失效：需通过其他渠道核实债务人信息")

        return {
            "stage": stage,
            "priority": priority,
            "overdue_days": overdue_days,
            "outstanding_amount": outstanding_amount,
            "customer_type": customer_type,
            "contact_valid": contact_valid,
            "strategies": strategies,
            "installment_advice": installment_advice,
            "legal_warning": legal_warning,
            "scripts": scripts,
            "compliance_check": {
                "time_check": time_check,
                "can_proceed": len(red_line_violations) == 0
            },
            "red_line_violations": red_line_violations,
            "generated_at": datetime.now().isoformat()
        }

    def parse_input(self, text: str) -> dict:
        """
        解析自然语言输入

        Args:
            text: 输入文本，如 "催收 客户逾期30天 欠款5万 首次逾期 联系方式有效"

        Returns:
            解析后的参数字典
        """
        import re

        params = {
            "overdue_days": 30,  # 默认值
            "outstanding_amount": 50000,  # 默认值
            "customer_type": "personal",
            "payment_history": ["按时"],
            "contact_valid": True,
            "customer_name": "客户"
        }

        # 提取逾期天数
        days_match = re.search(r"逾期(\d+)天", text)
        if days_match:
            params["overdue_days"] = int(days_match.group(1))

        # 提取欠款金额
        amount_match = re.search(r"欠款(\d+(?:\.\d+)?)\s*(?:万|元)", text)
        if amount_match:
            amount = float(amount_match.group(1))
            if "万" in amount_match.group(0):
                amount *= 10000
            params["outstanding_amount"] = amount

        # 判断是否首次逾期
        if "首次" in text or "首次逾期" in text:
            params["payment_history"] = ["按时"]
        elif "多次" in text or "经常" in text:
            params["payment_history"] = ["逾期1次", "逾期2次", "逾期3次"]

        # 判断联系方式有效性
        params["contact_valid"] = "有效" in text or "正常" in text or "可以联系" in text

        # 判断客户类型
        if "企业" in text:
            params["customer_type"] = "enterprise"

        return params


def main():
    """CLI测试入口"""
    engine = CreditCollectionEngine()

    # 解析输入
    import sys
    text = sys.argv[2] if len(sys.argv) > 2 else "催收 客户逾期30天 欠款5万 首次逾期 联系方式有效"

    if "generate" in sys.argv:
        params = engine.parse_input(text)
        result = engine.generate_collection_plan(**params)

        print("=" * 60)
        print(f"催收方案生成结果")
        print("=" * 60)
        print(f"逾期阶段: {result['stage']}")
        print(f"催收优先级: {result['priority']}")
        print(f"逾期天数: {result['overdue_days']}天")
        print(f"欠款金额: {result['outstanding_amount']:.2f}元")
        print(f"客户类型: {result['customer_type']}")
        print(f"联系方式有效: {'是' if result['contact_valid'] else '否'}")
        print("-" * 60)
        print(f"催收策略: {', '.join(result['strategies'])}")
        print("-" * 60)
        installment = result['installment_advice']
        print(f"分期建议: {installment['recommendation']}")
        print(f"建议期数: {installment['suggested_plan']}期")
        print(f"预计月还款: {installment['min_monthly_payment']:.2f}元")
        print(f"手续费率: {installment['handling_fee_rate']}")
        print("-" * 60)
        print(f"法律后果提示:\n{result['legal_warning']}")
        print("-" * 60)
        print(f"催收话术:")
        for stage_key, script in result['scripts'].items():
            print(f"  [{stage_key}] {script['channel']}: {script['template']}")
        print("-" * 60)
        if result['red_line_violations']:
            print("⚠️ 违规警告:")
            for v in result['red_line_violations']:
                print(f"  - {v}")
        else:
            print("✅ 合规检测: 通过")

        print("=" * 60)
        print(f"生成时间: {result['generated_at']}")
    else:
        print("用法: python collection_engine.py generate <描述>")


if __name__ == "__main__":
    main()
