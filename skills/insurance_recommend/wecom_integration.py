"""
企微机器人卡片 - 保险产品推荐
用于在企业微信发送格式化的保险推荐卡片
"""

from typing import Optional


def build_insurance_recommend_card(
    customer_profile: dict,
    recommendations: list,
    protection_gap: dict,
    family_overview: dict,
    premium_budget: dict,
    mention_user_id: Optional[str] = None
) -> dict:
    """
    构建保险推荐消息卡片（适用于企微机器人）

    Args:
        customer_profile: 客户画像
        recommendations: 推荐方案列表
        protection_gap: 保障缺口
        family_overview: 家庭保障全景
        premium_budget: 保费预算
        mention_user_id: 要@的用户ID（可选）

    Returns:
        dict: 企微卡片格式的JSON
    """
    # 卡片头部
    header = {
        "title": {
            "tag": "plain_text",
            "text": "🛡️ 保险产品智能推荐方案"
        },
        "template": "blue"
    }

    # 客户画像模块
    profile_fields = []
    if isinstance(customer_profile, dict):
        for k, v in customer_profile.items():
            profile_fields.append({
                "type": "hr"
            })
            profile_fields.append({
                "type": "markdown",
                "text": f"**{k}**: {v}"
            })

    profile_section = {
        "type": "section",
        "fields": profile_fields[1:] if profile_fields else []
    }

    # 推荐方案模块
    recommendation_elements = []

    if recommendations:
        for rec in recommendations[:5]:  # 最多显示5个
            coverage = rec.get("coverage", "N/A")
            premium = rec.get("annual_premium", "N/A")
            term = rec.get("policy_term", "N/A")
            priority = rec.get("priority", "?")
            ins_type = rec.get("insurance_type", "")
            product = rec.get("product_matching", "")
            reason = rec.get("reason", "")[:50] + "..." if len(rec.get("reason", "")) > 50 else rec.get("reason", "")

            recommendation_elements.append({
                "type": "div",
                "fields": [
                    {
                        "type": "markdown",
                        "text": f"**{priority}. {ins_type}** | {product}"
                    }
                ]
            })
            recommendation_elements.append({
                "type": "markdown",
                "text": f"📊 保额: `{coverage}` | 💰 年保费: `{premium}` | ⏰ 期间: `{term}`"
            })
            recommendation_elements.append({
                "type": "markdown",
                "text": f"📝 {reason}"
            })
            recommendation_elements.append({
                "type": "hr"
            })
    else:
        recommendation_elements.append({
            "type": "markdown",
            "text": "✅ 您的基础保障已较完善，建议定期检视保单"
        })

    # 保障缺口模块
    gap_text = ""
    if isinstance(protection_gap, dict):
        gap_items = [f"{k}: {v}" for k, v in protection_gap.items()]
        gap_text = " | ".join(gap_items[:4])

    gap_section = {
        "type": "section",
        "text": {
            "type": "markdown",
            "text": f"**📊 保障缺口**\n{gap_text}"
        }
    }

    # 保费预算模块
    budget_text = ""
    if isinstance(premium_budget, dict):
        total = premium_budget.get("total_annual", "N/A")
        budget_text = f"年度总保费: **{total}**"
        if "note" in premium_budget:
            budget_text += f"\n_{premium_budget['note']}_"

    budget_section = {
        "type": "section",
        "text": {
            "type": "markdown",
            "text": budget_text
        }
    }

    # 优先级模块
    priority_order_text = ""
    if isinstance(family_overview, dict) and "priority_order" in family_overview:
        priority_order_text = " → ".join(family_overview["priority_order"])

    priority_section = {
        "type": "section",
        "text": {
            "type": "markdown",
            "text": f"**🏆 投保优先级**\n{priority_order_text}"
        }
    }

    # 底部提示
    footer_note = {
        "type": "note",
        "elements": [
            {
                "type": "plain_text",
                "text": "⚠️ 仅供参考，具体方案请咨询专业保险顾问"
            }
        ]
    }

    # 组装卡片
    elements = [
        profile_section,
        {"type": "hr"},
        gap_section,
        {"type": "hr"},
        *recommendation_elements,
        {"type": "hr"},
        priority_section,
        {"type": "hr"},
        budget_section,
        {"type": "hr"},
        footer_note
    ]

    card = {
        "msgtype": "interactive",
        "interactive": {
            "header": header,
            "elements": elements
        }
    }

    # 添加@mention
    if mention_user_id:
        # 企微@人的格式是在消息外层包装
        card["at"] = {
            "atMobiles": [],
            "atUserIds": [mention_user_id]
        }

    return card


def build_simple_text_recommendation(result: dict) -> str:
    """
    构建简单的文本推荐（适用于企微文本消息）

    Args:
        result: 推荐引擎返回的完整结果

    Returns:
        str: 格式化的文本
    """
    lines = []

    lines.append("🛡️ 保险产品推荐方案")
    lines.append("─" * 40)

    # 客户画像
    profile = result.get("customer_profile", {})
    if profile:
        age = profile.get("age", "?")
        gender = profile.get("gender", "?")
        income = profile.get("annual_income", "?")
        lines.append(f"👤 {age}岁{gender} 年收入{income}")
        lines.append(f"   家庭状况: {profile.get('family_status', 'N/A')}")

    # 保障缺口
    gap = result.get("protection_gap", {})
    if gap:
        gap_short = {k.replace("缺口", ""): v for k, v in gap.items()}
        gap_str = " | ".join([f"{k}:{v}" for k, v in gap_short.items()])
        lines.append(f"\n📊 保障缺口: {gap_str}")

    # 推荐方案
    recs = result.get("recommendations", [])
    if recs:
        lines.append(f"\n💡 推荐方案 (共{len(recs)}项):")
        for rec in recs[:4]:
            priority = rec.get("priority", "?")
            ins_type = rec.get("insurance_type", "")
            coverage = rec.get("coverage", "?")
            premium = rec.get("annual_premium", "?")
            product = rec.get("product_matching", "")
            short_product = product[:15] + "..." if len(product) > 15 else product
            lines.append(f"  {priority}. {ins_type} | {short_product}")
            lines.append(f"     保额:{coverage} 年保费:{premium}")

    # 保费预算
    budget = result.get("premium_budget", {})
    if budget:
        total = budget.get("total_annual", "?")
        lines.append(f"\n💰 保费预算: {total}/年")

    # 优先级
    overview = result.get("family_protection_overview", {})
    if overview and "priority_order" in overview:
        order = "→".join(overview["priority_order"][:5])
        lines.append(f"🏆 投保顺序: {order}")

    lines.append("\n" + "─" * 40)
    lines.append("⚠️ 仅供参考，请咨询专业保险顾问")

    return "\n".join(lines)


def send_wecom_card(
    webhook_url: str,
    card: dict,
    mentioned_user_ids: list = None
) -> dict:
    """
    发送企微卡片消息

    Args:
        webhook_url: 企微机器人Webhook URL
        card: build_insurance_recommend_card() 返回的卡片
        mentioned_user_ids: 要@的用户ID列表

    Returns:
        dict: 发送结果
    """
    import json
    import urllib.request

    # 如果指定了@用户，在卡片外层包装
    payload = card.copy()
    if mentioned_user_ids:
        payload["atMobiles"] = []
        payload["atUserIds"] = mentioned_user_ids

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}


# 导出便捷函数
def quick_recommend(
    age: int,
    gender: str,
    annual_income: float,
    family: dict = None,
    existing_policies: list = None,
    liabilities: dict = None,
    **kwargs
) -> dict:
    """
    快速生成推荐并返回企微卡片payload

    使用示例:
        from insurance_recommend.wecom_integration import quick_recommend

        card = quick_recommend(
            age=30,
            gender="male",
            annual_income=300000,
            family={"married": True, "children": [{"age": 1}]}
        )
    """
    from insurance_recommend import InsuranceRecommendEngine

    engine = InsuranceRecommendEngine()

    result = engine.generate_recommendation(
        age=age,
        gender=gender,
        annual_income=annual_income,
        family=family,
        existing_policies=existing_policies,
        liabilities=liabilities,
        **kwargs
    )

    card = build_insurance_recommend_card(
        customer_profile=result.get("customer_profile", {}),
        recommendations=result.get("recommendations", []),
        protection_gap=result.get("protection_gap", {}),
        family_overview=result.get("family_protection_overview", {}),
        premium_budget=result.get("premium_budget", {})
    )

    text = build_simple_text_recommendation(result)

    return {
        "card": card,
        "text": text,
        "full_result": result
    }


if __name__ == "__main__":
    # 测试代码
    from insurance_recommend import InsuranceRecommendEngine

    engine = InsuranceRecommendEngine()

    # 模拟客户
    params = engine.parse_natural_language(
        "保险推荐 30岁男性 已婚 孩子1岁 年收入30万 已有医保"
    )

    result = engine.generate_recommendation(**params)

    # 生成卡片
    card = build_insurance_recommend_card(
        customer_profile=result["customer_profile"],
        recommendations=result["recommendations"],
        protection_gap=result["protection_gap"],
        family_overview=result["family_protection_overview"],
        premium_budget=result["premium_budget"]
    )

    print("卡片结构:")
    import json
    print(json.dumps(card, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)

    # 生成文本
    text = build_simple_text_recommendation(result)
    print("文本格式:")
    print(text)
