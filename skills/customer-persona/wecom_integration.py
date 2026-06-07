"""customer-persona WeCom 集成 —— 企微卡片入口。"""
from __future__ import annotations
import os, sys, json
from typing import Any, Dict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from persona_engine import PersonaEngine, parse_natural_language
from persona_formatter import PersonaFormatter


def build_home_card() -> Dict[str, Any]:
    return {
        "card_type": "button_interaction",
        "main_title": {"title": "📊 客户 360° 画像", "desc": "输入客户信息生成画像"},
        "horizontal_content_list": [
            {"keyname": "📝 自然语言", "value": "如 '张伟 35岁 月收入2万 已婚'"},
            {"keyname": "📋 结构化", "value": "字段填写"},
        ],
        "button_list": [
            {"text": "📝 自然语言输入", "action_url": "/persona/input?mode=nl"},
            {"text": "📋 结构化输入", "action_url": "/persona/input?mode=struct"},
            {"text": "🗂️ 历史画像", "action_url": "/persona/history"},
        ],
        "quote_area": {
            "title": "💡 输入示例",
            "quote_text": "客户画像 张伟 35岁 月收入2万 已婚 有房贷 风险偏好稳健",
        },
    }


def generate_card_from_text(text: str) -> Dict[str, Any]:
    eng = PersonaEngine()
    persona = eng.generate(text)
    return PersonaFormatter.to_wecom_card(persona)


if __name__ == "__main__":
    print(json.dumps(build_home_card(), ensure_ascii=False, indent=2))
    print("---")
    print(json.dumps(generate_card_from_text("张伟 35岁 月收入2万 已婚 有房贷 风险偏好稳健"),
                     ensure_ascii=False, indent=2))
