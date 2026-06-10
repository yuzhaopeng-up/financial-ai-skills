"""
企微（WeCom / 企业微信）集成模块
用于将供应链金融方案以卡片形式推送到企业微信

依赖：wecom_mcp 插件（OpenClaw 内置）
用法：
    from wecom_integration import send_scf_card
    send_scf_card(core_enterprise, ap, term, supplier_type)
"""

import json
from typing import Optional

# 企微 Webhook / API 配置占位
DEFAULT_WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"


def build_scf_card(
    core_enterprise: str,
    supplier_type: str,
    accounts_payable_wan: float,
    payment_term_days: int,
    recommended_solutions: list,
    industry: str = "通用制造",
) -> dict:
    """
    构建 SCF 企微卡片消息体（Interactive 格式）

    返回 dict，可直接作为企微消息接口的 content 字段。
    """
    ap_yi = accounts_payable_wan / 10000

    # 方案名称映射为 emoji + 名称
    solution_icons = {
        "应收账款质押融资": "📄",
        "订单融资": "📋",
        "核心企业反向保理": "🔐",
        "供应链票据": "🏦",
        "仓单融资": "🏭",
    }

    solution_items = ""
    for name in recommended_solutions:
        icon = solution_icons.get(name, "✅")
        solution_items += f'<li>{icon} {name}</li>'

    card = {
        "msgtype": "interactive",
        "interactive": {
            "tag": "html",
            "appid": "",  # 填写企微应用 appid
            "pagepath": "",  # 填写落地页路径（可选）
            "card": {
                "header": {
                    "title": f"🏭 供应链金融方案 | {core_enterprise}",
                    "description": f"<para>应付账款：<strong>{ap_yi:.1f}亿元</strong> | 账期：{payment_term_days}天</para>"
                                  f"<para>行业：{industry} | 供应商：{supplier_type}</para>",
                    "emphasis_style": "1",
                    "bg_color": "#1F4788",
                },
                "card_type": "news_notice",
                "source": {
                    "desc": "供应链金融方案生成器",
                    "desc_color": "0",
                },
                "quote_area": {
                    "type": "0",
                    "quote_text": f"推荐方案：{' / '.join(recommended_solutions)}",
                },
                "main_title": {
                    "title": f"贵司应付账款 {ap_yi:.1f} 亿元的 SCF 方案已生成",
                    "desc": "点击查看详细方案对比、办理流程及核心企业配合要点",
                },
                "jump_list": [
                    {
                        "type": "1",
                        "title": "📋 查看完整方案报告",
                        "desc": "五大方案详细对比 + 7步办理流程",
                        "url": "",  # 填写落地页 URL
                    },
                    {
                        "type": "1",
                        "title": "💬 联系客户经理",
                        "desc": "获取定制化报价方案",
                        "url": "",  # 填写落地页 URL
                    },
                ],
                "action_menu": {
                    "desc": "操作菜单",
                    "action_list": [
                        {
                            "text": "📊 方案对比",
                            "key": "COMPARE",
                        },
                        {
                            "text": "📝 所需材料清单",
                            "key": "MATERIALS",
                        },
                    ],
                },
                "card_type": "default_auth",
                "at_mobiles": [],  # 如需 @ 指定成员，填写手机号列表
            },
        },
    }
    return card


def build_scf_text_card(
    core_enterprise: str,
    supplier_type: str,
    accounts_payable_wan: float,
    payment_term_days: int,
    recommended_solutions: list,
    industry: str,
) -> dict:
    """
    构建纯文本企微卡片（兼容性更好的 Markdown 格式）
    用于通过 webhook 发送
    """
    ap_yi = accounts_pable_wan / 10000  # placeholder fix below
    ap_yi = accounts_payable_wan / 10000

    solution_lines = "\n".join(f"✅ **{s}**" for s in recommended_solutions)

    content = (
        f"## 🏦 供应链金融方案\n\n"
        f"**核心企业**：{core_enterprise}\n"
        f"**应付账款**：{ap_yi:.1f} 亿元（{accounts_payable_wan:.0f} 万元）\n"
        f"**账期**：{payment_term_days} 天\n"
        f"**行业**：{industry} | **供应商**：{supplier_type}\n\n"
        f"### ✅ 推荐方案\n\n"
        f"{solution_lines}\n\n"
        f"---  \n"
        f"📎 回复【详细】获取完整方案（含利率对比、办理流程、材料清单）"
    )

    return {
        "msgtype": "markdown",
        "markdown": {
            "content": content,
        },
    }


def send_wecom_message(
    webhook_url: str,
    message: dict,
    mentioned_list: Optional[list] = None,
) -> dict:
    """
    通过企微 Webhook 发送消息

    Args:
        webhook_url: 企微群机器人的 Webhook 地址
        message: 消息体（由 build_scf_card / build_scf_text_card 生成）
        mentioned_list: 需要 @ 的成员手机号列表（可选）

    Returns:
        API 响应 dict
    """
    import urllib.request
    import urllib.error

    if mentioned_list:
        if message.get("msgtype") == "markdown":
            content = message["markdown"]["content"]
            for mobile in mentioned_list:
                content += f"\n<@{mobile}}>"
            message["markdown"]["content"] = content

    payload = json.dumps(message).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {"errcode": -1, "errmsg": str(e)}


def send_scf_card(
    core_enterprise: str,
    supplier_type: str,
    accounts_payable_wan: float,
    payment_term_days: int,
    recommended_solutions: list,
    webhook_url: Optional[str] = None,
    mentioned_list: Optional[list] = None,
    industry: str = "通用制造",
    use_text_card: bool = False,
) -> dict:
    """
    一站式发送 SCF 企微卡片

    Args:
        core_enterprise: 核心企业名称
        supplier_type: 供应商类型
        accounts_payable_wan: 应付账款（万元）
        payment_term_days: 账期（天）
        recommended_solutions: 推荐方案名称列表
        webhook_url: 企微 Webhook URL（默认使用环境变量或占位 URL）
        mentioned_list: 需要 @ 的成员手机号列表
        industry: 行业
        use_text_card: True=使用 Markdown 文本格式，False=使用 Interactive 卡片

    Returns:
        发送结果 dict
    """
    url = webhook_url or DEFAULT_WEBHOOK_URL

    if use_text_card:
        message = build_scf_text_card(
            core_enterprise=core_enterprise,
            supplier_type=supplier_type,
            accounts_payable_wan=accounts_payable_wan,
            payment_term_days=payment_term_days,
            recommended_solutions=recommended_solutions,
            industry=industry,
        )
    else:
        message = build_scf_card(
            core_enterprise=core_enterprise,
            supplier_type=supplier_type,
            accounts_payable_wan=accounts_payable_wan,
            payment_term_days=payment_term_days,
            recommended_solutions=recommended_solutions,
            industry=industry,
        )

    return send_wecom_message(url, message, mentioned_list)


# ============ CLI 支持 ============
if __name__ == "__main__":
    import sys, argparse

    parser = argparse.ArgumentParser(description="发送 SCF 企微卡片")
    parser.add_argument("--core", required=True, help="核心企业名称")
    parser.add_argument("--supplier", required=True, help="供应商类型")
    parser.add_argument("--ap", type=float, required=True, help="应付账款（万元）")
    parser.add_argument("--term", type=int, required=True, help="账期（天）")
    parser.add_argument("--solutions", nargs="+", required=True, help="推荐方案列表")
    parser.add_argument("--webhook", help="企微 Webhook URL")
    parser.add_argument("--industry", default="通用制造", help="行业")
    parser.add_argument("--text-card", action="store_true", help="使用文本卡片格式")
    args = parser.parse_args()

    result = send_scf_card(
        core_enterprise=args.core,
        supplier_type=args.supplier,
        accounts_payable_wan=args.ap,
        payment_term_days=args.term,
        recommended_solutions=args.solutions,
        webhook_url=args.webhook,
        industry=args.industry,
        use_text_card=args.text_card,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
