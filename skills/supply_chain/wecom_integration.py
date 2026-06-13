#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
供应链金融方案引擎 - 企微集成
"""

import json
from supply_chain_engine import SupplyChainFinanceEngine


class SupplyChainFinanceWecom:
    def __init__(self):
        self.engine = SupplyChainFinanceEngine(api_mode=True)

    def handle_message(self, text: str, user_id: str = None) -> dict:
        text = text.strip()

        if text.startswith("融资方案") or text.startswith("供应链融资"):
            content = text.replace("融资方案", "").replace("供应链融资", "").strip()
            if content:
                params = self.engine.parse_input(content)
                report = self.engine.generate_full_report(params)
                return self._build_card(report)
            return {"type": "text", "content": "请输入完整信息，格式：`融资方案 核心企业:XXX 供应商:XXX 交易规模:XXX万`"}

        elif text.startswith("风险评估"):
            content = text.replace("风险评估", "").strip()
            if content:
                params = self.engine.parse_input(content)
                params["finance_mode"] = params.get("finance_mode") or self.engine.detect_finance_mode(params)
                risk = self.engine.assess_risk(params, params["finance_mode"])
                return self._build_risk_card(params, risk)
            return {"type": "text", "content": "请输入信息进行风险评估，格式：`风险评估 核心企业:XXX 供应商:XXX`"}

        elif text.startswith("额度测算"):
            content = text.replace("额度测算", "").strip()
            if content:
                params = self.engine.parse_input(content)
                params["finance_mode"] = params.get("finance_mode") or self.engine.detect_finance_mode(params)
                amount_info = self.engine.calculate_financing_amount(params, params["finance_mode"])
                return self._build_amount_card(params, amount_info)
            return {"type": "text", "content": "请输入信息进行额度测算，格式：`额度测算 核心企业:XXX 供应商:XXX 交易规模:XXX万`"}

        elif text in ["供应链帮助", "帮助", "scf帮助"]:
            return self._build_help()

        return self._build_help()

    def _build_help(self) -> dict:
        return {
            "type": "text",
            "content": """🏭 **供应链金融方案引擎**

📋 功能：供应链金融方案设计、风险评估、额度测算

📝 命令：
`融资方案 核心企业:XXX 供应商:XXX 交易规模:XXX万 账期:XXX天`
`风险评估 核心企业:XXX 供应商:XXX`
`额度测算 核心企业:XXX 供应商:XXX 交易规模:XXX万`

支持5种模式：应收账款融资、订单融资、存货融资、预付款融资、核心企业担保模式"""
        }

    def _build_card(self, report: dict) -> dict:
        plan = report["plan"]
        risk = plan["risk_assessment"]
        inp = report["input"]

        risk_template = {"high": "red", "medium": "orange", "low": "green"}.get(risk["risk_level"], "gray")

        elements = [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**核心企业**: {inp.get('core_enterprise', '未提供')}\n**供应商**: {inp.get('supplier', '未提供')}"}},
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**方案**: {plan['plan_name']}\n**融资比例**: {plan['financing_ratio']:.0f}%\n**年化利率**: {plan['annual_rate']:.2f}%"}},
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**可融资额度**: {plan['financing_amount']:.2f}万元\n**年融资成本**: {plan['annual_financing_cost']:.2f}万元/年"}},
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**风险等级**: {risk['risk_label']}（{risk['risk_score']:.1f}分）"}},
        ]

        if plan["risk_controls"]:
            ctrl_text = "、".join([c["name"] for c in plan["risk_controls"][:3]])
            elements.append({"tag": "hr"})
            elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"**风控措施**: {ctrl_text}"}})

        elements.append({"tag": "hr"})
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"📝 {report['summary']}"}})

        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"🏭 {plan['plan_name']} - {risk['risk_label']}",
                    "template": risk_template
                },
                "elements": elements
            }
        }

    def _build_risk_card(self, params: dict, risk: dict) -> dict:
        core_ce = params.get("core_enterprise", "未提供")
        core_sup = params.get("supplier", "未提供")

        elements = [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**核心企业**: {core_ce}\n**供应商**: {core_sup}"}},
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**风险评分**: {risk['risk_score']:.1f}/100\n**风险等级**: {risk['risk_label']}"}},
        ]

        if risk["risk_factors"]:
            for rf in risk["risk_factors"]:
                elements.append({"tag": "hr"})
                elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"⚠️ **{rf['name']}**\n{rf['description']}"}})

        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"⚠️ 风险评估 - {risk['risk_label']}",
                    "template": {"high": "red", "medium": "orange", "low": "green"}.get(risk["risk_level"], "gray")
                },
                "elements": elements
            }
        }

    def _build_amount_card(self, params: dict, amount_info: dict) -> dict:
        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": "💰 额度测算结果",
                    "template": "blue"
                },
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"**交易规模**: {amount_info['transaction_amount']:.2f}万元\n**融资比例**: {amount_info['financing_ratio']:.0f}%"}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"**可融资额度**: {amount_info['amount']:.2f}万元\n**年化利率**: {amount_info['annual_rate']:.2f}%"}},
                ]
            }
        }


def handle(text: str, user_id: str = None) -> dict:
    return SupplyChainFinanceWecom().handle_message(text, user_id)


if __name__ == "__main__":
    # 测试
    test_text = "融资方案 核心企业:华润集团 供应商:深圳供应链公司 交易规模:2000万 账期:90天 合作历史:24个月 核心评级:AAA"
    result = handle(test_text)
    print(json.dumps(result, ensure_ascii=False, indent=2)[:500])
