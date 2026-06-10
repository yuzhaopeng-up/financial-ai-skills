"""
理赔分析 - 企业微信卡片集成

将 ClaimAnalysisEngine 的分析结果渲染为企微消息卡片（Interactive 消息），
支持直接发送到企业微信群或应用。

依赖：requests（HTTP 发送）或直接配合 feishu_im_user_message 使用企微 Webhook。
"""

from typing import Any


def build_claim_card(result: dict) -> dict:
    """
    将理赔分析结果构建为企业微信 Interactive 卡片消息体。

    参数：
        result: ClaimAnalysisEngine.analyze() 返回的字典

    返回：
        企业微信卡片元素字典，可直接作为 card.message 到 Webhook 或 API。
    """

    liability = result.get("liability_assessment", {})
    fraud = result.get("fraud_check", {})
    calc = result.get("claim_calculation", {})
    proc = result.get("processing_time", {})

    # 风险颜色映射
    risk_color_map = {
        "低风险": ("<=500", "2E8B57"),   # green
        "中风险": ("2E8B57", "FFA500"),  # orange
        "高风险": ("FFA500", "FF4500"),  # red-orange
        "极高风险": ("FF4500", "FF0000"), # red
    }
    risk = fraud.get("risk_level", "低风险")
    risk_color = risk_color_map.get(risk, ("2E8B57", "2E8B57"))[1]

    # 赔付结论颜色
    decision = liability.get("decision", "待定")
    if "属于" in decision and "部分" not in decision:
        decision_color = "2E8B57"
    elif "部分属于" in decision:
        decision_color = "FFA500"
    else:
        decision_color = "FF4500"

    # 构建审核要点字段
    audit_fields = []
    for point in result.get("audit_points", []):
        audit_fields.append(
            {
                "type": "markdown",
                "text": f"📋 {point}"
            }
        )

    # 构建后续步骤字段
    steps_md = ""
    for step in result.get("next_steps", []):
        steps_md += f"\n▶ {step}"

    card = {
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "text": "🏥 理赔分析报告"
                },
                "color": "#2060C0"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "text": f"**案件编号**：{result.get('claim_id', 'N/A')}　　**时间**：{result.get('timestamp', '')[:10]}"
                },
                {"tag": "hr"},
                {
                    "tag": "column_set",
                    "flex_mode": "segment",
                    "elements": [
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "vertical_align": "top",
                            "elements": [
                                {
                                    "tag": "plain_text",
                                    "text": "责任认定",
                                    "color": "#999999",
                                    "size": "lg"
                                },
                                {
                                    "tag": "plain_text",
                                    "text": decision,
                                    "color": decision_color,
                                    "weight": "bold",
                                    "size": "lg"
                                }
                            ]
                        },
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "vertical_align": "top",
                            "elements": [
                                {
                                    "tag": "plain_text",
                                    "text": "反欺诈风险",
                                    "color": "#999999",
                                    "size": "lg"
                                },
                                {
                                    "tag": "plain_text",
                                    "text": f"{fraud.get('score', 0)}分 / {risk}",
                                    "color": f"#{risk_color}",
                                    "weight": "bold",
                                    "size": "lg"
                                }
                            ]
                        },
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "vertical_align": "top",
                            "elements": [
                                {
                                    "tag": "plain_text",
                                    "text": "处理时效",
                                    "color": "#999999",
                                    "size": "lg"
                                },
                                {
                                    "tag": "plain_text",
                                    "text": f"{proc.get('days', 7)}个工作日",
                                    "weight": "bold",
                                    "size": "lg"
                                }
                            ]
                        }
                    ]
                },
                {"tag": "hr"},
                {
                    "tag": "markdown",
                    "text": "**💰 理赔金额明细**"
                },
                {
                    "tag": "column_set",
                    "flex_mode": "segment",
                    "elements": [
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "elements": [
                                {"tag": "plain_text", "text": "住院总花费", "color": "#999999"},
                                {"tag": "plain_text", "text": f"¥{calc.get('total_expense', 0):,.2f}", "weight": "bold"}
                            ]
                        },
                        {
                            "tag": "column",
                            "width": "weighted",
                            "weight": 1,
                            "elements": [
                                {"tag": "plain_text", "text": "医保已报销", "color": "#999999"},
                                {"tag": "plain_text", "text": f"¥{calc.get('insurance_paid', 0):,.2f}", "weight": "bold"}
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
                                {"tag": "plain_text", "text": f"{calc.get('co_insurance_rate', 0)*100:.0f}%", "weight": "bold"}
                            ]
                        }
                    ]
                },
                {
                    "tag": "box",
                    "layout": "branch",
                    "conditions": [
                        {
                            "condition": decision != "不属于保险责任",
                            "text": {
                                "tag": "note",
                                "elements": [
                                    {
                                        "tag": "plain_text",
                                        "text": f"✨ 最终赔付额：¥{calc.get('final_reimbursement', 0):,.2f}"
                                    }
                                ]
                            }
                        }
                    ]
                },
                {"tag": "hr"},
            ]
        },
        "action_policy": "1"
    }

    # 动态添加审核要点
    if result.get("audit_points"):
        card["card"]["elements"].append({
            "tag": "markdown",
            "text": "**📋 审核要点**"
        })
        for point in result.get("audit_points", []):
            card["card"]["elements"].append({
                "tag": "markdown",
                "text": f"• {point}"
            })
        card["card"]["elements"].append({"tag": "hr"})

    # 动态添加反欺诈红旗
    if fraud.get("flags"):
        flags_md = "\n".join([f"⚠️ {f}" for f in fraud.get("flags", [])])
        card["card"]["elements"].append({
            "tag": "markdown",
            "text": f"**🚨 反欺诈红旗**\n{flags_md}"
        })
        card["card"]["elements"].append({"tag": "hr"})

    # 动态添加除外责任
    if liability.get("exclusions"):
        excl_md = "\n".join([f"❌ {e}" for e in liability.get("exclusions", [])])
        card["card"]["elements"].append({
            "tag": "markdown",
            "text": f"**❌ 除外责任**\n{excl_md}"
        })
        card["card"]["elements"].append({"tag": "hr"})

    # 后续步骤
    if result.get("next_steps"):
        steps_md = "\n".join([f"▶ {s}" for s in result.get("next_steps", [])])
        card["card"]["elements"].append({
            "tag": "markdown",
            "text": f"**📌 后续步骤**\n{steps_md}"
        })

    # 底部免责
    card["card"]["elements"].extend([
        {"tag": "hr"},
        {
            "tag": "note",
            "elements": [
                {"tag": "plain_text", "text": "⚠️ 本报告仅供参考，最终理赔决定需人工审核确认", "color": "#999999"}
            ]
        }
    ])

    return card


def send_to_wecom_webhook(webhook_url: str, result: dict) -> dict:
    """
    通过企业微信 Webhook 将理赔分析卡片发送到群。

    参数：
        webhook_url: 企微群机器人的 Webhook URL
        result: ClaimAnalysisEngine.analyze() 返回的字典

    返回：
        企微 API 响应的 JSON（成功则 {"errcode": 0, "errmsg": "ok"}）
    """
    import json
    import urllib.request

    card = build_claim_card(result)
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
    # 演示用
    from claim_engine import ClaimAnalysisEngine

    engine = ClaimAnalysisEngine()
    sample_result = engine.analyze(
        insurance_type="医疗险",
        accident_type="疾病",
        hospital_level="三甲医院",
        total_expense=80000.0,
        insurance_paid=30000.0,
    )

    card = build_claim_card(sample_result)
    print("=== 企业微信卡片结构（预览）===")
    print(json.dumps(card, ensure_ascii=False, indent=2))
