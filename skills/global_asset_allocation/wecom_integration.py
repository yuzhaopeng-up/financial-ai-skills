"""
企微卡片集成 - 全球资产配置
用法：python3 wecom_integration.py <配置需求>
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from global_asset_allocation import GlobalAssetAllocationEngine

def build_card(result) -> dict:
    """构建企微消息卡片。"""
    regional_text = "\n".join(
        f"• {r['区域']}：{r['配置比例']}"
        for r in result.regional_allocation[:5]
    )
    asset_text = "\n".join(
        f"• {a['资产类别']}：{a['配置比例']}"
        for a in result.asset_class_allocation[:4]
    )
    compliance = "\n".join(f"⚠️ {n[:50]}" for n in result.compliance_notes[:2])

    return {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"🌏 {result.title}"},
                "color": "blue",
            },
            "elements": [
                {"tag": "markdown", "content": f"**客户：**{result.client_profile['风险等级']} | {result.client_profile['配置目标']}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【区域配置】**\n{regional_text}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【资产类别】**\n{asset_text}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【合规提示】**\n{compliance}"},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": f"生成时间：{result.generated_at}"}]},
            ],
        },
    }

if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "全球配置 高净值 R3 资产1亿"
    eng = GlobalAssetAllocationEngine()
    result = eng.generate(text)
    card = build_card(result)
    print(card)
