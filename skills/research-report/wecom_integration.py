"""research-report WeCom 集成 —— 企微卡片入口。"""
from __future__ import annotations
import os, sys, json
from typing import Any, Dict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from report_engine import ReportEngine, _load_templates
from report_formatter import ReportFormatter


def build_home_card() -> Dict[str, Any]:
    t = _load_templates()
    industries = [k for k in t["industries"] if k != "通用"]
    return {
        "card_type": "button_interaction",
        "main_title": {"title": "📈 投研报告自动生成", "desc": "输入行业/公司/年度"},
        "horizontal_content_list": [
            {"keyname": "支持行业", "value": " / ".join(industries[:4])},
            {"keyname": "已收录公司", "value": f"{len(t['companies'])} 家龙头"},
        ],
        "button_list": [
            {"text": "🔍 输入研究主题", "action_url": "/research/input"},
            {"text": "📚 浏览已收录公司", "action_url": "/research/companies"},
            {"text": "🗂️ 历史报告", "action_url": "/research/history"},
        ],
        "quote_area": {
            "title": "💡 输入示例",
            "quote_text": "研报生成 新能源 宁德时代 2025\n研报 招商银行 2025\n研报 半导体 2025",
        },
    }


def generate_card_from_text(text: str) -> Dict[str, Any]:
    eng = ReportEngine()
    report = eng.generate(text)
    return ReportFormatter.to_wecom_card(report)


if __name__ == "__main__":
    print(json.dumps(build_home_card(), ensure_ascii=False, indent=2))
    print("---")
    print(json.dumps(generate_card_from_text("研报生成 新能源 宁德时代 2025"),
                     ensure_ascii=False, indent=2))
