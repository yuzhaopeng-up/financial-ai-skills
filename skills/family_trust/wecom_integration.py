"""
企微卡片集成 - 家族信托方案
用法：python3 wecom_integration.py <客户画像>
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from family_trust import FamilyTrustEngine

def build_card(result) -> dict:
    """构建企微消息卡片。"""
    profile = result.client_profile
    structure = result.trust_structure

    return {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"🏛️ {result.title}"},
                "color": "woro",
            },
            "elements": [
                {"tag": "markdown", "content": f"**客户画像：**{profile['年龄']} | 资产{profile['资产规模']} | {profile['客户类型']}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【推荐信托架构】**\n类型：{structure['recommended_type']}\n层级：{structure['tier']}\n境内：{structure[' onshore_location']} | 境外：{structure['offshore_location']}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【核心需求】**\n{profile['核心需求']}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【费用估算】**\n设立费：{result.fee_estimate['设立费']} | 年管理费：{result.fee_estimate['年度管理费']}"},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": f"生成时间：{result.generated_at}"}]},
            ],
        },
    }

if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "家族信托 客户50岁 资产3亿 传承子女"
    eng = FamilyTrustEngine()
    result = eng.generate(text)
    card = build_card(result)
    print(card)
