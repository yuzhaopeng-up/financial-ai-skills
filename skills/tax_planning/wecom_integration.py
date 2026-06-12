"""
WeCom Integration - 企微卡片输出
用于将税务筹划结果以企微消息卡片形式发送
"""

import json
from typing import Dict, Any, Optional


def build_wecom_card(tax_result: Dict[str, Any], title: str = "企业税务筹划分析报告") -> Dict[str, Any]:
    """
    将税务筹划结果构建为企微卡片格式

    Args:
        tax_result: TaxPlanningEngine.generate() 返回的结果
        title: 卡片标题

    Returns:
        企微卡片 JSON 结构
    """
    company_info = tax_result.get("company_info", {})
    et = tax_result.get("tax_types", {}).get("enterprise_tax", {})
    savings = tax_result.get("savings_space", {})
    risks = tax_result.get("risk_points", [])
    suggestions = tax_result.get("suggestions", [])

    # 卡片元素
    elements = []

    # 1. 企业信息区
    elements.append({
        "tag": "markdown",
        "content": (
            f"**🏢 企业基本信息**\n"
            f"• 企业名称：{company_info.get('name', '未提供')}\n"
            f"• 所属行业：{company_info.get('industry', '一般')}\n"
            f"• 年营业收入：{company_info.get('annual_revenue_str', '-')}\n"
            f"• 研发投入：{company_info.get('rd_expense_str', '-')}\n"
            f"• 员工人数：{company_info.get('employee_count', 0)}人\n"
            f"• 高新企业：{'✅ 是' if company_info.get('is_high_tech') else '❌ 否'}\n"
            f"• 小微资格：{'✅ 符合' if company_info.get('is_small_micro_eligible') else '❌ 不符合'}"
        )
    })

    elements.append({"tag": "hr"})

    # 2. 税负分析
    elements.append({
        "tag": "markdown",
        "content": (
            f"**📊 主要税种分析**\n"
            f"• 适用方案：{et.get('applicable_scheme', '-')}\n"
            f"• 优惠税率：{et.get('tax_rate_display', '-')}\n"
            f"• 研发加计扣除节省：{et.get('rd_deduction_benefit', 0) / 10000:.2f}万元\n"
            f"• 预估企业所得税：{et.get('estimated_tax_str', '-')}\n"
            f"• vs一般企业节省：{et.get('savings_vs_base_str', '-')}"
        )
    })

    elements.append({"tag": "hr"})

    # 3. 节税空间（高亮）
    elements.append({
        "tag": "markdown",
        "content": (
            f"**💰 综合节税空间**\n"
            f"• 企业所得税节省：{savings.get('enterprise_tax_savings_str', '0元')}\n"
            f"• 研发加计扣除：{savings.get('rd_deduction_savings_str', '0元')}\n"
            f"• 增值税节省：{savings.get('vat_savings_str', '0元')}\n"
            f"• **合计节税：{savings.get('total_savings_str', '0元')}**"
        )
    })

    # 4. 风险提示（挑2个最重要的）
    if risks:
        top_risks = risks[:2]
        risk_content = "**⚠️ 风险提示**\n"
        for r in top_risks:
            risk_content += f"• [{r.get('level', '')}级] {r.get('category', '')}：{r.get('description', '')}\n"
        elements.append({"tag": "hr"})
        elements.append({"tag": "markdown", "content": risk_content})

    # 5. 核心建议（挑1个最高优先级的）
    if suggestions:
        top_suggestion = suggestions[0]
        elements.append({
            "tag": "markdown",
            "content": (
                f"**📋 核心筹划建议**\n"
                f"【{top_suggestion.get('priority', '')}优先级】{top_suggestion.get('title', '')}\n"
                f"{top_suggestion.get('detail', '')}\n"
                f"▶ 行动：{top_suggestion.get('action', '')}"
            )
        })

    # 6. 底部摘要
    elements.append({"tag": "hr"})
    elements.append({
        "tag": "markdown",
        "content": tax_result.get("summary", "")
    })

    # 构建完整卡片
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "text": title
                },
                "template": "blue"  # 蓝色主题
            },
            "elements": elements
        }
    }

    return card


def build_simple_card(tax_result: Dict[str, Any]) -> str:
    """构建简化版卡片（用于文字卡片）"""
    company_info = tax_result.get("company_info", {})
    savings = tax_result.get("savings_space", {})
    summary = tax_result.get("summary", "")

    return (
        f"🏢 {company_info.get('name', '企业')}\n"
        f"📊 年营收：{company_info.get('annual_revenue_str', '-')} | "
        f"研发：{company_info.get('rd_expense_str', '-')}\n"
        f"💰 节税空间：{savings.get('total_savings_str', '0元')}\n"
        f"─────────────────\n"
        f"{summary}"
    )


def send_wecom_message(card: Dict[str, Any], webhook_url: str = None) -> Dict[str, Any]:
    """
    发送企微卡片消息

    Args:
        card: build_wecom_card() 构建的卡片
        webhook_url: 企微群机器人的 Webhook URL

    Returns:
        API 响应
    """
    import urllib.request
    import urllib.error

    if not webhook_url:
        # 如果没有提供 webhook_url，返回卡片结构用于调试
        return {"status": "debug", "card": card}

    data = json.dumps(card).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result
    except urllib.error.URLError as e:
        return {"status": "error", "message": str(e)}


# CLI 入口
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    from tax_engine import TaxPlanningEngine, parse_input_text

    # 测试
    test_text = "税务筹划 某科技公司 年营收5000万 研发投入300万"
    params = parse_input_text(test_text)
    engine = TaxPlanningEngine()
    result = engine.generate(**params)

    card = build_wecom_card(result)
    print("企微卡片结构:")
    print(json.dumps(card, ensure_ascii=False, indent=2))
