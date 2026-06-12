"""
寿险理赔审核 V2 - 企业微信卡片集成

将 ClaimReviewV2Engine 的审核结果渲染为企微消息卡片（Interactive 消息），
支持直接发送到企业微信群或应用。
"""

from typing import Any
import json


def build_review_card(result: dict) -> dict:
    """
    将理赔审核结果构建为企业微信 Interactive 卡片消息体。

    参数：
        result: ClaimReviewV2Engine.review() 返回的字典

    返回：
        企业微信卡片元素字典，可直接作为 card.message 到 Webhook 或 API。
    """

    decision = result.get("review_decision", {})
    audit = result.get("audit_points", {})
    calc = result.get("claim_calculation", {})
    fraud = result.get("fraud_check", {})
    proc = result.get("processing_time", {})

    # 决策颜色映射
    code = decision.get("code", "")
    if code == "APPROVED":
        decision_color = "2E8B57"    # green
        decision_icon = "✅"
    elif code == "PROPORTIONAL":
        decision_color = "FFA500"    # orange
        decision_icon = "⚠️"
    elif code == "PENDING_MATERIALS":
        decision_color = "1E90FF"    # blue
        decision_icon = "📋"
    else:
        decision_color = "FF4500"    # red
        decision_icon = "❌"

    # 风险颜色映射
    risk_color_map = {
        "低风险": "2E8B57",
        "中风险": "FFA500",
        "高风险": "FF6600",
        "极高风险": "FF0000",
    }
    risk = fraud.get("risk_level", "低风险")
    risk_color = risk_color_map.get(risk, "2E8B57")

    # 审核要点
    history = audit.get("history_relevance", {})
    excl = audit.get("exclusion_clauses", {})
    policy = audit.get("policy_validity", {})

    # 构建卡片元素
    elements = []

    # 标题区
    elements.append({
        "tag": "markdown",
        "text": f"**案件编号**：{result.get('claim_id', 'N/A')}　　**时间**：{result.get('timestamp', '')[:10]}"
    })
    elements.append({"tag": "hr"})

    # 审核结果 + 风险 + 时效 三列
    elements.append({
        "tag": "column_set",
        "flex_mode": "segment",
        "elements": [
            {
                "tag": "column",
                "width": "weighted",
                "weight": 1,
                "vertical_align": "top",
                "elements": [
                    {"tag": "plain_text", "text": "审核结果", "color": "#999999", "size": "lg"},
                    {"tag": "plain_text", "text": f"{decision_icon}{decision.get('result', '未知')}",
                     "color": decision_color, "weight": "bold", "size": "lg"}
                ]
            },
            {
                "tag": "column",
                "width": "weighted",
                "weight": 1,
                "vertical_align": "top",
                "elements": [
                    {"tag": "plain_text", "text": "反欺诈风险", "color": "#999999", "size": "lg"},
                    {"tag": "plain_text", "text": f"{fraud.get('score', 0)}分 / {risk}",
                     "color": f"#{risk_color}", "weight": "bold", "size": "lg"}
                ]
            },
            {
                "tag": "column",
                "width": "weighted",
                "weight": 1,
                "vertical_align": "top",
                "elements": [
                    {"tag": "plain_text", "text": "处理时效", "color": "#999999", "size": "lg"},
                    {"tag": "plain_text", "text": f"{proc.get('days', 7)}个工作日",
                     "weight": "bold", "size": "lg"}
                ]
            }
        ]
    })
    elements.append({"tag": "hr"})

    # 决策依据
    if decision.get("reason"):
        elements.append({
            "tag": "markdown",
            "text": f"**📌 决策依据**：{decision.get('reason', '')}"
        })
        elements.append({"tag": "hr"})

    # 理赔金额明细
    elements.append({
        "tag": "markdown",
        "text": "**💰 理赔金额明细**"
    })
    elements.append({
        "tag": "column_set",
        "flex_mode": "segment",
        "elements": [
            {
                "tag": "column",
                "width": "weighted",
                "weight": 1,
                "elements": [
                    {"tag": "plain_text", "text": "申请理赔额", "color": "#999999"},
                    {"tag": "plain_text", "text": f"¥{calc.get('claim_amount', 0):,.2f}", "weight": "bold"}
                ]
            },
            {
                "tag": "column",
                "width": "weighted",
                "weight": 1,
                "elements": [
                    {"tag": "plain_text", "text": "审核赔付额", "color": "#999999"},
                    {"tag": "plain_text", "text": f"¥{calc.get('final_payment', 0):,.2f}", "weight": "bold",
                     "color": decision_color}
                ]
            },
            {
                "tag": "column",
                "width": "weighted",
                "weight": 1,
                "elements": [
                    {"tag": "plain_text", "text": "免赔额", "color": "#999999"},
                    {"tag": "plain_text", "text": f"¥{calc.get('deductible', 0):,.2f}", "weight": "bold"}
                ]
            },
            {
                "tag": "column",
                "width": "weighted",
                "weight": 1,
                "elements": [
                    {"tag": "plain_text", "text": "赔付比例", "color": "#999999"},
                    {"tag": "plain_text", "text": f"{calc.get('co_insurance_rate', 1.0)*100:.0f}%", "weight": "bold"}
                ]
            }
        ]
    })

    # 审核要点
    audit_sections = []

    # 既往症
    hist_text = ""
    if history.get("has_pre_existing"):
        if history.get("related"):
            hist_text = "📌 既往症：**有关联**（触发免责）"
        else:
            hist_text = "📌 既往症：无关联"
        for d in history.get("details", []):
            hist_text += f"\n• {d}"
    else:
        hist_text = "✅ 既往症：无既往症或已如实告知"
    audit_sections.append(hist_text)

    # 责任免除
    excl_text = ""
    if excl.get("triggered"):
        excl_text = "⚠️ 责任免除：**触发**"
        for e in excl.get("triggered", []):
            excl_text += f"\n• {e}"
    else:
        excl_text = "✅ 责任免除：未触发"
    audit_sections.append(excl_text)

    # 保单有效性
    policy_text = ""
    if policy.get("valid"):
        policy_text = "✅ 保单有效性：有效"
    else:
        policy_text = "❌ 保单有效性：**无效**"
        for issue in policy.get("issues", []):
            policy_text += f"\n• {issue}"
    audit_sections.append(policy_text)

    elements.append({"tag": "hr"})
    elements.append({"tag": "markdown", "text": "**🔍 审核要点**"})
    for section in audit_sections:
        elements.append({"tag": "markdown", "text": section})

    # 反欺诈红旗
    if fraud.get("flags"):
        elements.append({"tag": "hr"})
        flags_md = "\n".join([f"⚠️ {f}" for f in fraud.get("flags", [])])
        elements.append({
            "tag": "markdown",
            "text": f"**🚨 反欺诈红旗**\n{flags_md}"
        })

    # 后续步骤
    if result.get("next_steps"):
        elements.append({"tag": "hr"})
        steps_md = "\n".join([f"▶ {s}" for s in result.get("next_steps", [])])
        elements.append({
            "tag": "markdown",
            "text": f"**📋 后续步骤**\n{steps_md}"
        })

    # 底部免责
    elements.extend([
        {"tag": "hr"},
        {
            "tag": "note",
            "elements": [
                {"tag": "plain_text",
                 "text": "⚠️ 本报告仅供参考，最终理赔决定需人工审核确认",
                 "color": "#999999"}
            ]
        }
    ])

    card = {
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "text": "🏥 寿险理赔审核报告 V2"
                },
                "color": "#2060C0"
            },
            "elements": elements
        },
        "action_policy": "1"
    }

    return card


def send_to_wecom_webhook(webhook_url: str, result: dict) -> dict:
    """
    通过企业微信 Webhook 将理赔审核卡片发送到群。

    参数：
        webhook_url: 企微群机器人的 Webhook URL
        result: ClaimReviewV2Engine.review() 返回的字典

    返回：
        企微 API 响应的 JSON（成功则 {"errcode": 0, "errmsg": "ok"}）
    """
    import urllib.request

    card = build_review_card(result)
    payload = json.dumps(card).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


# 示例用法
if __name__ == "__main__":
    from claim_review_engine import ClaimReviewV2Engine

    engine = ClaimReviewV2Engine()
    sample_result = engine.review(
        insurance_type="终身寿险",
        accident_type="身故",
        accident_reason="疾病身故",
        claim_amount=500000,
        policy_years=3,
        premium_paid=True,
        beneficiary="张三",
        beneficiary_relation="配偶",
        death_certificate=True,
    )

    card = build_review_card(sample_result)
    print("=== 企业微信卡片结构（预览）===")
    print(json.dumps(card, ensure_ascii=False, indent=2))
