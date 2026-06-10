"""
企微卡片集成 - 保单管理
用法：python3 wecom_integration.py generate "保单检视 寿险50万 重疾30万 年缴保费2万 已缴5年"
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from policy_management import PolicyManagementEngine, review_policy_from_text


def build_card(result: dict) -> dict:
    """构建企微消息卡片。"""
    gap = result.get("coverage_gap", {})
    premium = result.get("premium_analysis", {})
    cv = result.get("cash_value", {})
    suggestions = result.get("policy_suggestions", [])
    renewal = result.get("renewal_reminder", {})
    overview = result.get("family_overview", {})

    # 保障缺口摘要
    life_gap = gap.get("life_gap", 0)
    critical_gap = gap.get("critical_gap", 0)
    gap_summary = []
    if life_gap > 0:
        gap_summary.append(f"寿险缺口 {life_gap/10000:.1f}万元")
    if critical_gap > 0:
        gap_summary.append(f"重疾缺口 {critical_gap/10000:.1f}万元")
    if not gap_summary:
        gap_summary.append("基础保障基本覆盖")

    # 保全建议摘要
    sug_text = ""
    if suggestions:
        top3 = suggestions[:3]
        sug_text = "\n".join(
            f"• [{s.get('priority','')}] {s.get('action','')} {s.get('target','')}：{s.get('reason','')[:40]}"
            for s in top3
        )
    else:
        sug_text = "暂无保全建议"

    # 现金价值
    current_cv = cv.get("current_cv", 0)
    break_even = cv.get("break_even_year", "N/A")
    cv_assessment = cv.get("assessment", "")

    # 热力图
    heat = overview.get("heat_map", {})
    death_pct = heat.get("身故保障", 0)
    critical_pct = heat.get("重疾保障", 0)
    medical_pct = heat.get("医疗保障", 0)

    return {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": "📋 保单检视报告"},
                "color": "blue",
            },
            "elements": [
                {"tag": "markdown", "content": f"**【保障缺口】**\n• " + "\n• ".join(gap_summary)},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【保费合理性】**\n年缴保费 {premium.get('total_premium',0)/10000:.2f}万元 | 占比 {premium.get('premium_ratio',0)*100:.1f}% | {premium.get('assessment','N/A')}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【现金价值】**\n当前 {current_cv/10000:.2f}万元 | 回本 第{break_even}年 | {cv_assessment}"},
                {"tag": "markdown", "content": f"**【保障热力图】**\n身故 {death_pct:.0f}% | 重疾 {critical_pct:.0f}% | 医疗 {medical_pct:.0f}%"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【保全建议】**\n{sug_text}"},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"**【续期提醒】**\n{renewal.get('next_due_date','--')} | 金额 {renewal.get('next_due_amount',0)/10000:.2f}万元 | {renewal.get('lapse_risk','--')}"},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": f"家庭保障充足率：{overview.get('sufficiency_rate',0)*100:.1f}%"}]},
            ],
        },
    }


if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "保单检视 寿险50万 重疾30万 年缴保费2万 已缴5年"
    if len(sys.argv) < 2:
        text = "保单检视 寿险50万 重疾30万 年缴保费2万 已缴5年"
    else:
        text = " ".join(sys.argv[1:])

    eng = PolicyManagementEngine()
    result = review_policy_from_text(text)
    card = build_card(result)
    print(card)
