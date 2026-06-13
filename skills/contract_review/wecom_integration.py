#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合同智能审查 - 企微集成
"""

import json
from contract_review_engine import ContractReviewEngine


class ContractReviewWecom:
    def __init__(self):
        self.engine = ContractReviewEngine(api_mode=True)
    
    def handle_message(self, text: str, user_id: str = None) -> dict:
        text = text.strip()
        
        if text.startswith("合同审查") or text.startswith("审查"):
            content = text.replace("合同审查", "").replace("审查", "").strip()
            if content:
                result = self.engine.review_contract(content)
                return self._build_card(result)
            return {"type": "text", "content": "请输入合同内容，例如：`合同审查 [合同文本]`"}
        
        elif text in ["合同帮助", "帮助"]:
            return self._build_help()
        
        return self._build_help()
    
    def _build_help(self) -> dict:
        return {
            "type": "text",
            "content": """🦞 **合同智能审查引擎**

📋 功能：自动审查合同条款，识别风险点

📝 命令：`合同审查 [合同文本]`

⚠️ 风险等级：🔴高 🟡中 🟢低

示例：
`合同审查 利率按另行约定 担保范围包括一切债务`"""
        }
    
    def _build_card(self, result: dict) -> dict:
        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"📋 合同审查 - {result['risk_label']}",
                    "template": {"high": "red", "medium": "orange", "low": "green"}.get(result["risk_level"], "gray")
                },
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"**合同类型**: {result['contract_type']}"}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"**风险评分**: {result['risk_score']:.1f}/100\n**合规评分**: {result['compliance_score']:.1f}/100"}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"**风险统计**: 🔴{result['risk_stats']['high']} 🟡{result['risk_stats']['medium']} 🟢{result['risk_stats']['low']}"}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"**摘要**: {result['summary']}"}},
                ]
            }
        }


def handle(text: str, user_id: str = None) -> dict:
    return ContractReviewWecom().handle_message(text, user_id)


if __name__ == "__main__":
    result = handle("合同审查 利率按另行约定执行 违约金30%")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:500])
