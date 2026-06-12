"""
企业对公开户 - 企微卡片集成
将开户指引生成为企微消息卡片格式
"""

import json
from typing import Optional

# 企微卡片元素类型
CARD_ELEMENT_TYPE_TEXT = "plain_text"
CARD_ELEMENT_TYPE_MARKDOWN = "markdown"
CARD_ELEMENT_TYPE_IMAGE = "image"
CARD_ELEMENT_TYPE_DIVIDER = "divider"


class WeComCardBuilder:
    """企微消息卡片构建器"""

    def __init__(self):
        self.elements = []

    def add_header(self, title: str, subtitle: Optional[str] = None):
        """添加卡片头部"""
        header = {"title": {"tag": "plain_text", "text": title}}
        if subtitle:
            header["subtitle"] = {"tag": "plain_text", "text": subtitle}
        self.elements.append({"tag": "header", **header})
        return self

    def add_divider(self):
        """添加分割线"""
        self.elements.append({"tag": "divider"})
        return self

    def add_text(self, text: str, type: str = CARD_ELEMENT_TYPE_TEXT):
        """添加文本元素"""
        tag = "markdown" if type == CARD_ELEMENT_TYPE_MARKDOWN else "plain_text"
        self.elements.append({"tag": "plain_text", "text": text, "lang": 0})
        return self

    def add_field(self, fields: list):
        """添加字段组（多列布局）"""
        field_elements = []
        for f in fields:
            if isinstance(f, dict):
                field_elements.append({
                    "tag": "element",
                    "type": "markdown",
                    "content": f.get("content", ""),
                })
            else:
                field_elements.append({
                    "tag": "element",
                    "type": "markdown",
                    "content": str(f),
                })
        self.elements.append({
            "tag": "columns",
            "fields": field_elements
        })
        return self

    def add_note(self, content: str):
        """添加备注"""
        self.elements.append({
            "tag": "note",
            "elements": [{"tag": "plain_text", "text": content, "lang": 0}]
        })
        return self

    def build(self) -> dict:
        """构建卡片 JSON"""
        return {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "text": "企业对公开户办理指南"},
                    "template": "blue"
                },
                "elements": self.elements
            }
        }


def build_account_opening_card(engine_result: dict) -> dict:
    """
    将 engine 结果转换为企微卡片格式

    Args:
        engine_result: CorpAccountEngine.generate() 返回的 dict

    Returns:
        dict: 企微卡片 JSON
    """
    builder = WeComCardBuilder()

    # 企业信息
    etype = engine_result.get("enterprise_type", "有限责任公司")
    cap = engine_result.get("registered_capital", "未明确")
    acc_type = engine_result.get("account_type", "基本户")

    builder.add_header(
        title=f"企业对公开户 — {etype}",
        subtitle=f"注册资本：{cap} | 开户类型：{acc_type}"
    )

    # 账户类型说明
    diff = engine_result.get("account_difference", {})
    basic = diff.get("basic", {})
    general = diff.get("general", {})

    builder.add_text("📋 账户类型说明", type=CARD_ELEMENT_TYPE_MARKDOWN)
    builder.add_field([
        {"content": f"**基本户**\n{basic.get('quantity', '1个/企业')}\n功能：{basic.get('function', '日常结算')}"},
        {"content": f"**一般户**\n{general.get('quantity', '可开多个')}\n功能：{general.get('function', '借款归集')}"}
    ])

    # 材料清单
    materials = engine_result.get("materials", [])
    builder.add_divider()
    builder.add_text(f"📑 所需材料清单（共{len(materials)}项）", type=CARD_ELEMENT_TYPE_MARKDOWN)

    for i, m in enumerate(materials[:8], 1):  # 企微卡片限制，最多显示8项
        note = f"\n💡 {m['note']}" if m.get("note") else ""
        builder.add_text(f"{i}. **{m['name']}**：{m['desc']}{note}")

    if len(materials) > 8:
        builder.add_text(f"⋯⋯ 还有 {len(materials) - 8} 项材料，完整清单请查看完整报告")

    # 开户流程
    process = engine_result.get("process", [])
    builder.add_divider()
    builder.add_text("📝 开户流程", type=CARD_ELEMENT_TYPE_MARKDOWN)

    for step in process[:5]:  # 显示前5步
        builder.add_text(f"**{step['step']}. {step['name']}**：{step['desc']}")

    # 办理时长和费用
    dur = engine_result.get("duration", {})
    fees = engine_result.get("fees", "")

    builder.add_divider()
    builder.add_field([
        {"content": f"⏱ **办理时长**\n总时长：{dur.get('total', '3-5个工作日')}\n银行审核：{dur.get('bank_review', '1-3个工作日')}"},
        {"content": f"💰 **费用参考**\n{fees.split('；')[0] if '；' in fees else fees}"}
    ])

    # 注意事项
    notes = engine_result.get("notes", [])
    if notes:
        builder.add_divider()
        builder.add_text("⚠️ 注意事项", type=CARD_ELEMENT_TYPE_MARKDOWN)
        for note in notes[:3]:
            builder.add_text(f"• {note}")

    # 常见问题
    faq = engine_result.get("faq", [])
    if faq:
        builder.add_divider()
        builder.add_text("❓ 常见问题", type=CARD_ELEMENT_TYPE_MARKDOWN)
        for qa in faq[:3]:
            builder.add_text(f"**Q：{qa['q']}**\nA：{qa['a'][:50]}...")

    # 页脚
    builder.add_divider()
    builder.add_note("本指南仅供参考，具体以当地银行要求为准。如有疑问请咨询银行客服。")

    return builder.build()


def send_wecom_card(card_json: dict, chat_id: Optional[str] = None) -> dict:
    """
    发送企微卡片（需配合飞书/企微机器人 API 使用）

    Args:
        card_json: build_account_opening_card() 生成的卡片 JSON
        chat_id: 群聊 ID（可选）

    Returns:
        dict: 发送结果
    """
    # 此处仅为卡片生成，实际发送需通过飞书/企微 API
    # 卡片可通过 feishu_im_user_message 工具发送
    return {
        "status": "card_built",
        "card": card_json,
        "chat_id": chat_id,
        "note": "请使用飞书消息工具发送此卡片"
    }


if __name__ == "__main__":
    # 测试
    from account_engine import CorpAccountEngine

    engine = CorpAccountEngine()
    result = engine.generate("对公开户 科技公司 注册资本500万", format="json")
    card = build_account_opening_card(result)
    print(json.dumps(card, ensure_ascii=False, indent=2))
