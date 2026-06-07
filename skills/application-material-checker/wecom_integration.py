"""
WeCom 集成 —— 进件材料自动核对。
"""
from __future__ import annotations
import os
import sys
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from material_checker import MaterialChecker, MaterialReportFormatter
from checker_engine import MaterialDoc, SCENARIO_RULES


def build_scenario_picker_card() -> Dict[str, Any]:
    """主页：选择业务场景。"""
    scenarios = MaterialChecker().list_scenarios()
    items = [
        {"keyname": f"📋 {s['name']}", "value": f"{s['required_count']} 类必备材料"}
        for s in scenarios
    ]
    return {
        "card_type": "button_interaction",
        "main_title": {"title": "📋 进件材料自动核对", "desc": "选择业务场景"},
        "horizontal_content_list": items,
        "button_list": [
            {"text": "🏢 对公开户", "action_url": "/checker/upload?s=corporate_account_opening"},
            {"text": "💼 小微贷款", "action_url": "/checker/upload?s=sme_loan"},
            {"text": "🏠 个人房贷", "action_url": "/checker/upload?s=personal_mortgage"},
            {"text": "📚 查看规则库", "action_url": "/checker/rules"},
        ],
        "quote_area": {
            "title": "💡 使用提示",
            "quote_text": (
                "1. 选择业务场景\n"
                "2. 上传 OCR 识别后的材料字段\n"
                "3. AI 秒级生成核对报告\n"
                "4. 缺失项一键高亮，整改建议自动给出"
            ),
        },
    }


def build_upload_guide_card(scenario_key: str) -> Dict[str, Any]:
    """场景上传指引：列出本场景需要哪些材料。"""
    scenario = SCENARIO_RULES.get(scenario_key)
    if not scenario:
        return {"error": f"未知场景: {scenario_key}"}
    return {
        "card_type": "text_notice",
        "main_title": {"title": f"📋 {scenario['name']} - 材料清单", "desc": "请上传以下材料"},
        "emphasis_content": {
            "title": f"{len(scenario['required_docs'])} 类必备材料",
            "desc": "支持身份证/营业执照/流水/合同等",
        },
        "horizontal_content_list": [
            {"keyname": f"📄 {d}", "value": "必备"} for d in scenario["required_docs"]
        ],
        "button_list": [
            {"text": "📤 立即上传", "action_url": f"/checker/upload-files?s={scenario_key}"},
            {"text": "🔙 返回选择场景", "action_url": "/checker/home"},
        ],
    }


def check_and_card(scenario_key: str, docs: List[MaterialDoc]) -> Dict[str, Any]:
    """核对 + 返回卡片。"""
    rep = MaterialChecker().check(scenario_key, docs)
    return MaterialReportFormatter.to_wecom_card(rep)


if __name__ == "__main__":
    import json
    print("=== 主页 ===")
    print(json.dumps(build_scenario_picker_card(), ensure_ascii=False, indent=2))
    print("\n=== 上传指引 (sme_loan) ===")
    print(json.dumps(build_upload_guide_card("sme_loan"), ensure_ascii=False, indent=2))
