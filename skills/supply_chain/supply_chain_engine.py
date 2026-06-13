#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
供应链金融方案引擎 v1.0

支持5种供应链金融模式：
1. 应收账款融资
2. 订单融资
3. 存货融资
4. 预付款融资
5. 核心企业担保模式

Author: ArkClaw
Version: 1.0.0
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional


class SupplyChainFinanceEngine:
    """供应链金融方案引擎"""

    VERSION = "1.0.0"

    # 核心企业信用评级映射
    CREDIT_RATINGS = {
        "AAA": {"score": 95, "rate": 3.5, "description": "极强信用"},
        "AA": {"score": 85, "rate": 4.0, "description": "强信用"},
        "A": {"score": 75, "rate": 5.0, "description": "良好信用"},
        "BBB": {"score": 65, "rate": 6.0, "description": "中等信用"},
        "BB": {"score": 55, "rate": 7.5, "description": "较弱信用"},
        "B": {"score": 45, "rate": 9.0, "description": "弱信用"},
    }

    # 供应链模式定义
    FINANCE_MODES = {
        "accounts_receivable": {
            "name": "应收账款融资",
            "name_en": "Accounts Receivable Financing",
            "description": "供应商将应收账款转让或质押给金融机构，获取融资",
            "suitable_for": ["核心企业账期较长", "供应商流动资金紧张"],
            "key_requirements": ["核心企业确权", "应收账款无争议", "账期明确"],
            "financing_ratio": 0.70,  # 融资比例
            "rate_premium": 1.5,     # 利率加成
            "min_history_months": 6,
        },
        "order": {
            "name": "订单融资",
            "name_en": "Order Financing",
            "description": "供应商以有效订单合同获取预融资，用于采购生产",
            "suitable_for": ["订单驱动型企业", "季节性备货需求"],
            "key_requirements": ["核心企业订单", "订单不可撤销", "交期明确"],
            "financing_ratio": 0.50,
            "rate_premium": 2.0,
            "min_history_months": 3,
        },
        "inventory": {
            "name": "存货融资",
            "name_en": "Inventory Financing",
            "description": "供应商以库存商品作为抵质押物获取融资",
            "suitable_for": ["存货周转慢", "有形资产丰富"],
            "key_requirements": ["存货可变现", "第三方仓储", "价值可评估"],
            "financing_ratio": 0.40,
            "rate_premium": 2.5,
            "min_history_months": 6,
        },
        "prepayment": {
            "name": "预付款融资",
            "name_en": "Prepayment Financing",
            "description": "核心企业担保，金融机构为供应商提供预付款融资",
            "suitable_for": ["核心企业强势", "供应商议价能力弱"],
            "key_requirements": ["核心企业担保", "采购协议", "定向支付"],
            "financing_ratio": 0.60,
            "rate_premium": 1.8,
            "min_history_months": 12,
        },
        "core_guarantee": {
            "name": "核心企业担保模式",
            "name_en": "Core Enterprise Guarantee",
            "description": "核心企业为链上供应商提供连带责任担保",
            "suitable_for": ["核心企业强信用", "希望稳定供应链", "供应商资质较弱"],
            "key_requirements": ["核心企业担保函", "额度共享", "定期确权"],
            "financing_ratio": 0.80,
            "rate_premium": 1.2,
            "min_history_months": 12,
        },
    }

    # 风险规则
    RISK_RULES = {
        "core_enterprise": [
            {"id": "CR001", "name": "核心企业信用过低", "threshold": 55, "weight": 0.3, "description": "核心企业信用评级低于BB，风险较高"},
            {"id": "CR002", "name": "核心企业无评级", "threshold": 0, "weight": 0.2, "description": "核心企业无公开评级，信息不透明"},
        ],
        "supplier": [
            {"id": "SP001", "name": "供应商信用过低", "threshold": 45, "weight": 0.25, "description": "供应商信用评级低于B，违约风险高"},
            {"id": "SP002", "name": "合作历史过短", "threshold": 6, "weight": 0.15, "description": "与核心企业合作不足6个月"},
            {"id": "SP003", "name": "交易规模异常", "threshold": 0, "weight": 0.1, "description": "交易规模与供应商营收不匹配"},
        ],
        "transaction": [
            {"id": "TX001", "name": "账期过长", "threshold": 180, "weight": 0.1, "description": "应收账款账期超过180天"},
            {"id": "TX002", "name": "交易不稳定", "threshold": 0, "weight": 0.08, "description": "交易金额波动超过50%"},
        ],
    }

    # 风险控制措施
    RISK_CONTROLS = {
        "core_enterprise_confirm": {"name": "核心企业确权", "description": "核心企业书面确认应收账款/订单真实性"},
        "closed_loop_payment": {"name": "资金闭环", "description": "融资款项定向支付给核心企业或供应商账户受托支付"},
        "inventory_supervision": {"name": "存货监管", "description": "引入第三方仓储对抵质押物进行监管"},
        "transaction_verification": {"name": "交易核验", "description": "发票、合同、物流单据交叉验证"},
        "credit_insurance": {"name": "信用保险", "description": "引入信用保险覆盖核心企业或买方信用风险"},
        "pledge_registration": {"name": "质押登记", "description": "应收账款/存货在征信系统进行质押登记"},
        "core_guarantee_letter": {"name": "担保函", "description": "核心企业出具连带责任担保函"},
        "regular_reconciliation": {"name": "定期对账", "description": "核心企业与供应商定期对账确权"},
    }

    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode
        self._log("初始化供应链金融方案引擎 v%s" % self.VERSION)

    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)

    def parse_input(self, text: str) -> Dict[str, Any]:
        """解析输入文本，提取关键信息"""
        result = {
            "core_enterprise": None,
            "supplier": None,
            "transaction_amount": None,  # 万元
            "credit_period": None,       # 天
            "history_months": None,
            "core_rating": None,
            "supplier_rating": None,
            "finance_mode": None,
            "raw_text": text,
        }

        # 提取核心企业
        ce_match = re.search(r"核心企业[：:]([A-Za-z0-9\u4e00-\u9fa5]{2,20})", text)
        if ce_match:
            result["core_enterprise"] = ce_match.group(1).strip()

        # 提取供应商
        sup_match = re.search(r"供应商[：:]([A-Za-z0-9\u4e00-\u9fa5]{2,20})", text)
        if sup_match:
            result["supplier"] = sup_match.group(1).strip()

        # 提取交易规模
        amt_match = re.search(r"交易规模[：:]?\s*(\d+(?:\.\d+)?)\s*(?:万|亿元|万亿)?", text)
        if amt_match:
            result["transaction_amount"] = float(amt_match.group(1))
            if "亿" in amt_match.group(0):
                result["transaction_amount"] *= 10000
            if "万" not in amt_match.group(0) and "亿" not in amt_match.group(0):
                result["transaction_amount"] /= 10000

        # 提取年限
        year_match = re.search(r"年限[：:]?\s*(\d+)\s*年", text)
        if year_match:
            result["history_months"] = int(year_match.group(1)) * 12

        # 提取合作月数
        month_match = re.search(r"合作[历历史]?[：:]?\s*(\d+)\s*月", text)
        if month_match:
            result["history_months"] = int(month_match.group(1))

        # 提取账期
        period_match = re.search(r"账期[：:]?\s*(\d+)\s*天", text)
        if period_match:
            result["credit_period"] = int(period_match.group(1))

        # 提取信用评级
        rating_match = re.search(r"核心评级[：:]?\s*([A-Z]{1,3})", text)
        if rating_match:
            result["core_rating"] = rating_match.group(1).upper()

        # 提取融资模式
        for mode_key in self.FINANCE_MODES:
            if mode_key.replace("_", "") in text.replace(" ", "") or \
               self.FINANCE_MODES[mode_key]["name"] in text:
                result["finance_mode"] = mode_key
                break

        # 默认值设置
        if not result["history_months"]:
            result["history_months"] = 12  # 默认12个月
        if not result["credit_period"]:
            result["credit_period"] = 90   # 默认90天账期

        return result

    def detect_finance_mode(self, params: Dict) -> str:
        """根据参数推荐最佳融资模式"""
        transaction_amount = params.get("transaction_amount") or 500
        history_months = params.get("history_months") or 12
        core_rating = params.get("core_rating") or "A"
        raw_text = params.get("raw_text", "")

        # 显式指定模式关键词 -> 优先匹配
        for mode_key, mode_info in self.FINANCE_MODES.items():
            if mode_key.replace("_", "") in raw_text.replace(" ", "") or \
               mode_info["name"] in raw_text or \
               mode_info["name_en"] in raw_text:
                return mode_key

        # 核心企业强信用 + 供应商合作久 -> 核心企业担保模式
        core_score = self.CREDIT_RATINGS.get(core_rating, {}).get("score", 60)
        if core_score >= 75 and history_months >= 12:
            return "core_guarantee"

        # 账期明确 -> 应收账款融资
        if params.get("credit_period") and params.get("credit_period") <= 180:
            return "accounts_receivable"

        # 短期合作 + 小规模 -> 订单融资
        if history_months < 6 and transaction_amount < 1000:
            return "order"

        # 存货/库存关键词 -> 存货融资
        if "存货" in raw_text or "库存" in raw_text:
            return "inventory"

        # 默认应收账款融资
        return "accounts_receivable"

    def calculate_financing_amount(self, params: Dict, mode: str) -> Dict[str, Any]:
        """计算可融资额度"""
        mode_info = self.FINANCE_MODES[mode]
        transaction_amount = params.get("transaction_amount") or 500  # 默认500万

        # 基础可融资额度
        base_amount = transaction_amount * mode_info["financing_ratio"]

        # 核心企业评级加成
        core_rating = params.get("core_rating") or "A"
        core_score = self.CREDIT_RATINGS.get(core_rating, {}).get("score", 60)
        rating_multiplier = core_score / 70.0
        rating_multiplier = max(0.5, min(1.2, rating_multiplier))

        # 合作历史加成
        history_months = params.get("history_months") or 12
        if history_months >= 24:
            history_multiplier = 1.1
        elif history_months >= 12:
            history_multiplier = 1.0
        else:
            history_multiplier = 0.85

        final_amount = base_amount * rating_multiplier * history_multiplier

        # 年化利率计算
        base_rate = self.CREDIT_RATINGS.get(core_rating, {}).get("rate", 5.0)
        financing_rate = base_rate + mode_info["rate_premium"]

        return {
            "amount": round(final_amount, 2),
            "amount_unit": "万元",
            "financing_ratio": mode_info["financing_ratio"] * 100,
            "annual_rate": round(financing_rate, 2),
            "rate_unit": "%",
            "transaction_amount": transaction_amount,
        }

    def assess_risk(self, params: Dict, mode: str) -> Dict[str, Any]:
        """评估风险"""
        risk_factors = []
        total_risk_score = 0

        # 核心企业风险
        core_rating = params.get("core_rating") or "A"
        core_score = self.CREDIT_RATINGS.get(core_rating, {}).get("score", 60)

        for rule in self.RISK_RULES["core_enterprise"]:
            if core_score < rule["threshold"]:
                risk_factors.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "weight": rule["weight"],
                    "category": "core_enterprise",
                })
                total_risk_score += rule["weight"] * (100 - core_score)

        # 供应商风险
        supplier_rating = params.get("supplier_rating") or "BBB"
        supplier_score = self.CREDIT_RATINGS.get(supplier_rating, {}).get("score", 65)
        history_months = params.get("history_months") or 12

        for rule in self.RISK_RULES["supplier"]:
            if rule["id"] == "SP001" and supplier_score < rule["threshold"]:
                risk_factors.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "weight": rule["weight"],
                    "category": "supplier",
                })
                total_risk_score += rule["weight"] * (100 - supplier_score)
            elif rule["id"] == "SP002" and history_months < rule["threshold"]:
                risk_factors.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "weight": rule["weight"],
                    "category": "supplier",
                })
                total_risk_score += rule["weight"] * 50

        # 交易风险
        credit_period = params.get("credit_period") or 90
        for rule in self.RISK_RULES["transaction"]:
            if rule["id"] == "TX001" and credit_period > rule["threshold"]:
                risk_factors.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "weight": rule["weight"],
                    "category": "transaction",
                })
                total_risk_score += rule["weight"] * (credit_period - 90)

        # 标准化风险评分
        risk_score = min(100, max(0, total_risk_score))

        if risk_score >= 60:
            risk_level = "high"
            risk_label = "🔴 高风险"
        elif risk_score >= 30:
            risk_level = "medium"
            risk_label = "🟡 中风险"
        else:
            risk_level = "low"
            risk_label = "🟢 低风险"

        return {
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level,
            "risk_label": risk_label,
            "risk_factors": risk_factors,
        }

    def generate_risk_controls(self, params: Dict, mode: str, risk_level: str) -> List[Dict]:
        """生成风险控制措施"""
        controls = []

        # 基础措施（所有模式都需要）
        controls.append(self.RISK_CONTROLS["transaction_verification"])
        controls.append(self.RISK_CONTROLS["regular_reconciliation"])

        # 模式特定措施
        if mode == "accounts_receivable":
            controls.append(self.RISK_CONTROLS["core_enterprise_confirm"])
            controls.append(self.RISK_CONTROLS["pledge_registration"])
            if risk_level == "high":
                controls.append(self.RISK_CONTROLS["credit_insurance"])

        elif mode == "order":
            controls.append(self.RISK_CONTROLS["closed_loop_payment"])

        elif mode == "inventory":
            controls.append(self.RISK_CONTROLS["inventory_supervision"])
            controls.append(self.RISK_CONTROLS["pledge_registration"])

        elif mode == "prepayment":
            controls.append(self.RISK_CONTROLS["core_guarantee_letter"])
            controls.append(self.RISK_CONTROLS["closed_loop_payment"])

        elif mode == "core_guarantee":
            controls.append(self.RISK_CONTROLS["core_guarantee_letter"])
            if risk_level in ["medium", "high"]:
                controls.append(self.RISK_CONTROLS["credit_insurance"])

        # 高风险额外措施
        if risk_level == "high":
            controls.append(self.RISK_CONTROLS["credit_insurance"])

        # 去重
        seen = set()
        unique = []
        for c in controls:
            if c["name"] not in seen:
                seen.add(c["name"])
                unique.append(c)

        return unique

    def design_financing_plan(self, params: Dict, mode: str) -> Dict[str, Any]:
        """设计融资方案"""
        mode_info = self.FINANCE_MODES[mode]
        amount_info = self.calculate_financing_amount(params, mode)
        risk_info = self.assess_risk(params, mode)
        controls = self.generate_risk_controls(params, mode, risk_info["risk_level"])

        # 方案名称
        plan_name = f"{mode_info['name']}方案"

        # 融资成本估算
        financing_cost = amount_info["amount"] * amount_info["annual_rate"] / 100

        return {
            "plan_name": plan_name,
            "finance_mode": mode,
            "mode_description": mode_info["description"],
            "suitable_for": mode_info["suitable_for"],
            "key_requirements": mode_info["key_requirements"],
            "financing_amount": amount_info["amount"],
            "amount_unit": amount_info["amount_unit"],
            "financing_ratio": amount_info["financing_ratio"],
            "annual_rate": amount_info["annual_rate"],
            "rate_unit": "%",
            "transaction_amount": amount_info["transaction_amount"],
            "annual_financing_cost": round(financing_cost, 2),
            "cost_unit": "万元/年",
            "risk_assessment": risk_info,
            "risk_controls": controls,
        }

    def generate_full_report(self, params: Dict) -> Dict[str, Any]:
        """生成完整报告"""
        core_enterprise = params.get("core_enterprise") or "核心企业A"
        supplier = params.get("supplier") or "供应商X"

        # 检测/确认融资模式
        mode = params.get("finance_mode") or self.detect_finance_mode(params)

        # 生成方案
        plan = self.design_financing_plan(params, mode)

        return {
            "report_type": "供应链金融方案",
            "version": self.VERSION,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input": {
                "core_enterprise": core_enterprise,
                "supplier": supplier,
                "transaction_amount": params.get("transaction_amount"),
                "credit_period": params.get("credit_period"),
                "history_months": params.get("history_months"),
                "core_rating": params.get("core_rating"),
                "supplier_rating": params.get("supplier_rating"),
                "recommended_mode": mode,
            },
            "plan": plan,
            "summary": self._generate_summary(core_enterprise, supplier, plan),
        }

    def _generate_summary(self, ce: str, sup: str, plan: Dict) -> str:
        """生成摘要"""
        risk = plan["risk_assessment"]
        amount = plan["financing_amount"]
        rate = plan["annual_rate"]

        summary = f"为【{ce}】与【{sup}】设计{plan['plan_name']}，"
        summary += f"可融资额度{amount:.0f}万元（占交易额{plan['financing_ratio']:.0f}%），"
        summary += f"年化利率约{rate:.1f}%，"
        summary += f"综合风险{risk['risk_label']}。"

        if plan["risk_controls"]:
            ctrl_names = "、".join([c["name"] for c in plan["risk_controls"][:3]])
            summary += f"建议风控措施：{ctrl_names}。"

        return summary

    def format_text(self, report: Dict) -> str:
        """格式化输出为文本"""
        plan = report["plan"]
        risk = plan["risk_assessment"]
        inp = report["input"]

        lines = [
            f"🏭 **供应链金融方案报告**",
            f"",
            f"⏰ 生成时间: {report['generated_at']}",
            f"",
            f"{'='*32}",
            f"",
            f"📋 **基本信息**",
            f"",
            f"核心企业: {inp['core_enterprise']}",
            f"供应商: {inp['supplier']}",
            f"交易规模: {inp.get('transaction_amount', '未提供')}万元",
            f"账期: {inp.get('credit_period', '未提供')}天",
            f"合作历史: {inp.get('history_months', '未提供')}个月",
            f"核心企业评级: {inp.get('core_rating', '未提供')}",
            f"",
            f"{'='*32}",
            f"",
            f"📊 **融资方案**",
            f"",
            f"方案名称: {plan['plan_name']}",
            f"融资模式: {plan['mode_description']}",
            f"",
            f"💰 **额度与成本**",
            f"可融资额度: **{plan['financing_amount']:.2f}万元**",
            f"融资比例: {plan['financing_ratio']:.0f}%（相对于交易额）",
            f"年化利率: **{plan['annual_rate']:.2f}%**",
            f"年融资成本: {plan['annual_financing_cost']:.2f}万元/年",
            f"",
            f"{'='*32}",
            f"",
            f"⚠️ **风险评估**",
            f"",
            f"风险评分: {risk['risk_score']:.1f}/100",
            f"风险等级: {risk['risk_label']}",
        ]

        if risk["risk_factors"]:
            lines.append(f"风险因素:")
            for rf in risk["risk_factors"]:
                lines.append(f"  • {rf['name']}: {rf['description']}")

        if plan["risk_controls"]:
            lines.extend([
                f"",
                f"🔒 **风控措施**",
            ])
            for ctrl in plan["risk_controls"]:
                lines.append(f"  ✓ {ctrl['name']}: {ctrl['description']}")

        lines.extend([
            f"",
            f"{'='*32}",
            f"",
            f"📝 **方案摘要**",
            f"",
            report["summary"],
        ])

        return "\n".join(lines)

    def format_json(self, report: Dict) -> str:
        """格式化输出为JSON"""
        return json.dumps(report, ensure_ascii=False, indent=2)


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("🏭 供应链金融方案引擎 v1.0")
    print("=" * 50)
    print()

    engine = SupplyChainFinanceEngine()

    # 示例输入
    sample_params = {
        "core_enterprise": "华润集团",
        "supplier": "深圳供应链公司",
        "transaction_amount": 2000,
        "credit_period": 90,
        "history_months": 24,
        "core_rating": "AAA",
        "supplier_rating": "A",
    }

    print("📋 输入参数:")
    for k, v in sample_params.items():
        print(f"  {k}: {v}")
    print()

    report = engine.generate_full_report(sample_params)
    print(engine.format_text(report))


if __name__ == "__main__":
    main()
