"""
wecom_integration.py - 企微机器人卡片集成
将信用审批报告以飞书/企业微信卡片消息格式输出
"""

import json
from typing import Dict, Any, List, Optional


def build_credit_card(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    将信用审批结果转换为飞书/企微卡片消息格式

    Args:
        result: CreditApprovalEngine.evaluate() 返回的结果

    Returns:
        飞书 interactive 卡片消息体（dict）
    """
    r = result

    # 审批结论颜色
    conclusion_colors = {
        "通过": "#00C853",
        "有条件通过": "#FFB300",
        "拒绝": "#F44336",
    }
    conclusion_color = conclusion_colors.get(r["approval_conclusion"], "#9E9E9E")

    # 信用等级颜色
    grade_colors = {
        "AAA": "#00C853",
        "AA": "#64DD17",
        "A": "#AEEA00",
        "BBB": "#FFEB3B",
        "BB": "#FFC107",
        "B": "#FF9800",
        "CCC": "#FF5722",
        "CC": "#F44336",
        "C": "#E91E63",
        "D": "#9C27B0",
    }
    grade_color = grade_colors.get(r["grade"], "#9E9E9E")

    # Z-score 区域颜色
    z_colors = {
        "安全区": "#00C853",
        "灰色区": "#FFB300",
        "破产区": "#F44336",
    }
    z_color = z_colors.get(r["z_score"]["zone"], "#9E9E9E")

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "text": f"📋 信用审批报告 | {r['company_name']}",
                    "emoji": True,
                },
                "template": "blue",
            },
            "elements": [
                # 综合评估
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**信用评分**\n{r['credit_score']} / 100",
                            },
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**信用等级**\n`{r['grade']}`",
                            },
                        },
                    ],
                },
                {
                    "tag": "hr",
                },
                # 审批结论
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": (
                            f"### 🚨 审批结论：{r['approval_conclusion']}\n"
                            f"信用评分：{r['credit_score']} | "
                            f"等级：{r['grade']} | "
                            f"Z-score：{r['z_score']['value']}（{r['z_score']['zone']}）"
                        ),
                    },
                },
                {
                    "tag": "hr",
                },
                # 杜邦分析
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": (
                            f"### 📊 杜邦分析（ROE 拆解）\n"
                            f"• **ROE** = {r['dupont_analysis']['ROE']:.4f}\n"
                            f"• 净利率 = {r['dupont_analysis']['net_margin']:.4f}\n"
                            f"• 资产周转率 = {r['dupont_analysis']['asset_turnover']:.4f}\n"
                            f"• 权益乘数 = {r['dupont_analysis']['equity_multiplier']:.4f}"
                        ),
                    },
                },
                {
                    "tag": "hr",
                },
                # Z-score
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": (
                            f"### ⚠️ Altman Z-score 预警\n"
                            f"• **Z值** = {r['z_score']['value']:.4f}（{r['z_score']['zone']}）\n"
                            f"• {r['z_score']['warning']}\n"
                            f"• X1={r['z_score']['x1']} X2={r['z_score']['x2']} "
                            f"X3={r['z_score']['x3']} X4={r['z_score']['x4']} X5={r['z_score']['x5']}"
                        ),
                    },
                },
                {
                    "tag": "hr",
                },
                # 贷款与利率
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": (
                                    f"**💰 贷款额度建议**\n"
                                    f"{r['loan_suggestion']['max_amount']:.2f} 万元\n"
                                    f"期限：{r['loan_suggestion']['tenor']}"
                                ),
                            },
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": (
                                    f"**📈 利率建议**\n"
                                    f"{r['interest_rate_suggestion']['final_rate']:.2f}%\n"
                                    f"{r['interest_rate_suggestion']['description']}"
                                ),
                            },
                        },
                    ],
                },
                {
                    "tag": "hr",
                },
                # 信用评分维度
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": (
                            f"### 🔍 信用评分维度（满分100）\n"
                            f"• 资产负债率(20分)：{r['scoring_details']['debt_ratio_score']}\n"
                            f"• 流动比率(20分)：{r['scoring_details']['current_ratio_score']}\n"
                            f"• 利润率(20分)：{r['scoring_details']['profit_margin_score']}\n"
                            f"• 经营年限(20分)：{r['scoring_details']['operating_years_score']}\n"
                            f"• 行业风险(20分)：{r['scoring_details']['industry_risk_score']}"
                        ),
                    },
                },
                {
                    "tag": "hr",
                },
                # 原始数据
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": (
                            f"### 📄 原始数据\n"
                            f"• 年营收：{r['raw_inputs']['annual_revenue']} 万元\n"
                            f"• 负债率：{r['raw_inputs']['debt_ratio']}%\n"
                            f"• 利润率：{r['raw_inputs']['profit_margin']}%\n"
                            f"• 经营年限：{r['raw_inputs']['operating_years']} 年\n"
                            f"• 行业：{r['raw_inputs']['industry']}\n"
                            f"• 资产总额：{r['raw_inputs']['total_assets']} 万元\n"
                            f"• 净资产：{r['raw_inputs']['equity']} 万元"
                        ),
                    },
                },
                # 底部
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "text": "本报告由 CreditApprovalEngine v1.0.0 自动生成，仅供参考，实际审批需结合人工复核",
                            "emoji": True,
                        },
                    ],
                },
            ],
        },
    }

    return card


def build_simple_card(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    简化版卡片（适用于机器人消息限制场景）
    仅包含核心指标，无明细数据
    """
    r = result

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "text": f"📋 信用审批 | {r['company_name']}",
                    "emoji": True,
                },
                "template": "blue",
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {"is_short": True, "text": {"tag": "lark_md", "content": f"**信用评分**\n{r['credit_score']} / 100"}},
                        {"is_short": True, "text": {"tag": "lark_md", "content": f"**信用等级**\n`{r['grade']}`"}},
                        {"is_short": True, "text": {"tag": "lark_md", "content": f"**审批结论**\n{r['approval_conclusion']}"}},
                        {"is_short": True, "text": {"tag": "lark_md", "content": f"**Z-score**\n{r['z_score']['value']}（{r['z_score']['zone']}）"}},
                    ],
                },
                {
                    "tag": "hr",
                },
                {
                    "tag": "div",
                    "fields": [
                        {"is_short": True, "text": {"tag": "lark_md", "content": f"**贷款额度**\n{r['loan_suggestion']['max_amount']:.2f} 万元"}},
                        {"is_short": True, "text": {"tag": "lark_md", "content": f"**建议利率**\n{r['interest_rate_suggestion']['final_rate']:.2f}%"}},
                        {"is_short": True, "text": {"tag": "lark_md", "content": f"**ROE**\n{r['dupont_analysis']['ROE']:.4f}"}},
                        {"is_short": True, "text": {"tag": "lark_md", "content": f"**期限**\n{r['loan_suggestion']['tenor']}"}},
                    ],
                },
            ],
        },
    }

    return card


def print_card_preview(card: Dict[str, Any]):
    """在终端打印卡片预览（ASCII 简化版）"""
    header = card["card"]["header"]["title"]["text"]
    elements = card["card"]["elements"]

    print("=" * 60)
    print(f"  {header}")
    print("=" * 60)

    for el in elements:
        if el["tag"] == "div" and "fields" in el:
            for field in el["fields"]:
                content = field["text"]["content"]
                # 移除 markdown 格式
                content = content.replace("**", "").replace("`", "")
                print(f"  {content}")
            print("-" * 60)
        elif el["tag"] == "div" and "text" in el:
            content = el["text"]["content"].replace("### ", "").replace("**", "").replace("• ", "  • ")
            for line in content.split("\n"):
                print(f"  {line}")
            print("-" * 60)
        elif el["tag"] == "hr":
            pass
        elif el["tag"] == "note":
            for elem in el.get("elements", []):
                print(f"  [{elem.get('text', '')}]")


# 单元测试
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    from credit_engine import CreditApprovalEngine

    engine = CreditApprovalEngine()
    result = engine.evaluate(
        company_name="某制造企业",
        annual_revenue=5000,
        debt_ratio=60,
        profit_margin=8,
        operating_years=5,
        industry="制造业",
        current_ratio=1.8,
    )

    print("=== 完整卡片 ===")
    card = build_credit_card(result)
    print(json.dumps(card, ensure_ascii=False, indent=2))

    print("\n=== 简化卡片 ===")
    simple = build_simple_card(result)
    print(json.dumps(simple, ensure_ascii=False, indent=2))

    print("\n=== 终端预览 ===")
    print_card_preview(card)
