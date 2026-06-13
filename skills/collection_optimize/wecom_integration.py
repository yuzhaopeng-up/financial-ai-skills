#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
催收策略优化 - 企微集成
"""

import json
from collection_optimize_engine import CollectionOptimizeEngine


class CollectionOptimizeWecom:
    def __init__(self):
        self.engine = CollectionOptimizeEngine(api_mode=True)

    def handle_message(self, text: str, user_id: str = None) -> dict:
        text = text.strip()

        # 解析命令格式: 催收策略 [逾期天数] [逾期金额] [客户姓名]
        # 例如: 催收策略 45 58000 张三
        # 或: 催收分析 逾期45天 金额58000
        if any(text.startswith(p) for p in ["催收策略", "催收分析", "催收生成"]):
            return self._handle_strategy(text)

        elif text in ["催收帮助", "帮助", "collection help"]:
            return self._build_help()

        else:
            return self._build_help()

    def _handle_strategy(self, text: str) -> dict:
        # 解析参数
        parts = text.replace("催收策略", "").replace("催收分析", "").replace("催收生成", "").strip()

        customer_info = {"customer_name": "客户", "overdue_days": 0, "overdue_amount": 0}

        # 尝试多种格式解析
        # 格式1: "45 58000 张三"
        tokens = parts.split()
        if len(tokens) >= 2:
            try:
                customer_info["overdue_days"] = int(tokens[0])
                customer_info["overdue_amount"] = float(tokens[1])
                if len(tokens) >= 3:
                    customer_info["customer_name"] = tokens[2]
            except ValueError:
                pass

        # 格式2: "逾期45天 金额58000"
        m_days = self._extract_number(parts, r"逾期(\d+)天")
        m_amount = self._extract_number(parts, r"金额?(\d+(?:\.\d+)?)")
        if m_days is not None:
            customer_info["overdue_days"] = m_days
        if m_amount is not None:
            customer_info["overdue_amount"] = m_amount

        if customer_info["overdue_days"] <= 0 or customer_info["overdue_amount"] <= 0:
            return {
                "type": "text",
                "content": "参数格式有误，请使用：\n`催收策略 [逾期天数] [逾期金额] [客户姓名]`\n\n示例：\n`催收策略 45 58000 张三`\n`催收分析 逾期45天 金额58000`"
            }

        result = self.engine.generate_strategy(customer_info)
        return self._build_card(result)

    def _extract_number(self, text: str, pattern: str) -> float:
        import re
        m = re.search(pattern, text)
        if m:
            try:
                return int(m.group(1)) if "." not in m.group(1) else float(m.group(1))
            except ValueError:
                return None
        return None

    def _build_help(self) -> dict:
        return {
            "type": "text",
            "content": """🦞 **催收策略优化引擎**

📋 功能：输入客户逾期信息，生成个性化催收策略与话术

📝 命令：
`催收策略 [逾期天数] [逾期金额] [客户姓名]`

示例：
`催收策略 45 58000 张三`
`催收分析 逾期45天 金额58000`

📊 分层标准：M0(正常) → M1(1-30天) → M2(31-60天) → M3(61-90天) → M4(91-180天) → M5(180天+)

✅ 验收标准：回收率提升≥10%"""
        }

    def _build_card(self, result: dict) -> dict:
        tier = result["tier"]
        recovery = result["recovery_rate_estimate"]

        # 根据等级选择颜色
        color_map = {
            "M0": "grey", "M1": "blue", "M2": "orange",
            "M3": "red", "M4": "red", "M5": "grey"
        }
        template = color_map.get(tier, "grey")

        # 话术预览（取前100字）
        script_preview = result["scripts"]["full_script"][:100] + "..." if len(result["scripts"]["full_script"]) > 100 else result["scripts"]["full_script"]

        # 渠道
        channels = " / ".join([c["channel"] for c in result["channels"][:3]])

        elements = [
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"**客户**: {result['customer_info']['name']} | **逾期**: {result['customer_info']['overdue_days']}天 / ¥{result['customer_info']['overdue_amount']:,.2f}"}
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"**分层等级**: {result['tier']} - {result['tier_name']}\n**金额层级**: {result['amount_tier']}\n**综合优先级**: {result['priority_score']:.1f}"}
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"**还款意愿**: {result['willingness']['score']}/100（{result['willingness']['level']}）\n**催收渠道**: {channels}\n**催收频率**: {result['frequency']}"}
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"**📊 回收率预估**\n预估回收率: {recovery['estimated_rate']}%\n策略提升: +{recovery['improvement_vs_baseline']}%\n验收标准: {'✅ 达标' if recovery['meets_acceptance'] else '⚠️ 未达标'}"}
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"**📝 话术类型**: {result['scripts']['script_type']}\n\n{script_preview}"}
            },
        ]

        # 推荐还款方案
        if result["repayment_plan"]["recommended"]:
            plan = result["repayment_plan"]["recommended"]
            elements.append({
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"**💼 推荐方案**: {plan['type']}\n{plan['description']}（可行性:{plan['feasibility']}）"}
            })

        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"催收策略 - {result['tier']} {result['tier_name']}",
                    "template": template
                },
                "elements": elements
            }
        }


def handle(text: str, user_id: str = None) -> dict:
    return CollectionOptimizeWecom().handle_message(text, user_id)


if __name__ == "__main__":
    test_cases = [
        "催收策略 45 58000 张三",
        "催收分析 逾期10天 金额5000",
    ]
    for tc in test_cases:
        print(f"\n{'='*40}")
        print(f"输入: {tc}")
        result = handle(tc)
        print(f"类型: {result['type']}")
        if result["type"] == "interactive":
            print(f"卡片标题: {result['card']['header']['title']}")
        else:
            print(f"内容: {result.get('content', '')[:100]}")
