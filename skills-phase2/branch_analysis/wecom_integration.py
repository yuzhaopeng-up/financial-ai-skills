"""
企微卡片集成 (WeChat Work Card Integration)

将网点分析结果转换为企微消息卡片格式
"""

import json
from typing import Dict, Any, List, Optional


def _safe(v) -> str:
    """安全转换为字符串"""
    if v is None:
        return "N/A"
    if isinstance(v, (int, float)):
        return str(v)
    return str(v)


def swot_to_richtext(swot) -> Dict[str, Any]:
    """SWOT转换为企微富文本格式"""
    def bullet_items(items: List[str]) -> List[Dict]:
        return [{"tag": "text", "text": "• " + item} for item in items[:3]]
    
    sections = []
    
    sections.append({
        "tag": "text",
        "text": "✅ 优势\n",
    })
    for s in swot.strengths[:2]:
        sections.append({"tag": "text", "text": f"• {s}\n"})
    
    sections.append({"tag": "text", "text": "\n❌ 劣势\n"})
    for w in swot.weaknesses[:2]:
        sections.append({"tag": "text", "text": f"• {w}\n"})
    
    sections.append({"tag": "text", "text": "\n🌟 机会\n"})
    for o in swot.opportunities[:2]:
        sections.append({"tag": "text", "text": f"• {o}\n"})
    
    sections.append({"tag": "text", "text": "\n⚠️ 威胁\n"})
    for t in swot.threats[:2]:
        sections.append({"tag": "text", "text": f"• {t}\n"})
    
    return {"tag": "text", "text": ""}


def generate_wecom_card(analysis_result, title: Optional[str] = None) -> Dict[str, Any]:
    """
    将BranchAnalysisResult转换为企微交互卡片格式
    
    Args:
        analysis_result: BranchAnalysisEngine.analyze() 的返回值
        title: 卡片标题，不提供则自动生成
    
    Returns:
        企微卡片 JSON 对象
    """
    r = analysis_result
    card_title = title or f"网点分析报告 [{r.branch_id}]"
    
    # 头部基本信息
    header_elements = [
        {"tag": "markdown", "content": f"**{card_title}**\n{r.zone_type} | {r.area}㎡ | {r.staff_count}人 | {r.competitor_count}个竞争网点"},
    ]
    
    # KPI 区域
    kpi_fields = [
        {
            "type": "列",
            "fields": [
                {"type": "markdown", "text": f"**日均来访**\n{r.traffic_estimate.daily_visitors} 人"},
                {"type": "markdown", "text": f"**产能指数**\n{r.production_capacity_index} 万元/人/年"},
                {"type": "markdown", "text": f"**服务半径**\n{r.service_radius_km} km"},
            ]
        },
        {
            "type": "列",
            "fields": [
                {"type": "markdown", "text": f"**初始投资**\n{r.input_output_recommendation.initial_investment} 万元"},
                {"type": "markdown", "text": f"**预期ROI**\n{r.input_output_recommendation.expected_roi}%"},
                {"type": "markdown", "text": f"**回收周期**\n{r.input_output_recommendation.payback_period} 个月"},
            ]
        },
    ]
    
    # SWOT 区域
    swot_content = []
    swot_content.append({"tag": "text", "text": "**✅ 优势**\n"})
    for s in r.swot.strengths[:2]:
        swot_content.append({"tag": "text", "text": f"• {s}\n"})
    swot_content.append({"tag": "text", "text": "\n**❌ 劣势**\n"})
    for w in r.swot.weaknesses[:2]:
        swot_content.append({"tag": "text", "text": f"• {w}\n"})
    swot_content.append({"tag": "text", "text": "\n**🌟 机会**\n"})
    for o in r.swot.opportunities[:2]:
        swot_content.append({"tag": "text", "text": f"• {o}\n"})
    swot_content.append({"tag": "text", "text": "\n**⚠️ 威胁**\n"})
    for t in r.swot.threats[:2]:
        swot_content.append({"tag": "text", "text": f"• {t}\n"})
    
    # 客群画像
    customer_text = (
        f"**主要客群**: {r.customer_profile.primary}\n"
        f"**次要客群**: {r.customer_profile.secondary}\n"
        f"**潜力客群**: {r.customer_profile.potential}\n"
        f"**收入水平**: {r.customer_profile.income_level}"
    )
    
    # 三年预测表格
    forecast_lines = []
    for f in r.three_year_forecast:
        forecast_lines.append(
            f"• **{f.year}年**: 营收 {_safe(f.revenue)} 万元 | "
            f"客户 {_safe(f.customers)} 户 | 份额 {f.market_share*100:.1f}%"
        )
    
    # 业务重点
    bf_lines = "\n".join([f"{i+1}. {bf}" for i, bf in enumerate(r.business_focus[:4])])
    
    # 资源配置
    res = r.resource_allocation
    resource_text = (
        f"前台 {res.staff_front_desk}人 | 营销 {res.staff_sales}人 | "
        f"后台 {res.staff_back_office}人\n"
        f"营销预算: {res.marketing_budget} 万元/年"
    )
    
    # 组装卡片
    card = {
        "msgtype": "interactive",
        "interactive": {
            "card_type": "template_card",
            "source": {
                "icon_url": "https://example.com/icon.png",
                "desc": "龙马集群 AI"
            },
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": card_title,
                        "lang": "zh_cn"
                    },
                    "description": {
                        "tag": "markdown",
                        "content": f"**{r.zone_type}** | 员工 {r.staff_count}人 | 竞争 {r.competitor_count}个 | 企业 {r.local_enterprise_count}家"
                    }
                },
                "main_title": {
                    "tag": "markdown",
                    "content": (
                        f"📊 日均 {r.traffic_estimate.daily_visitors} 人次 | "
                        f"转化 {r.traffic_estimate.conversion_rate*100:.0f}% | "
                        f"产能 {r.production_capacity_index} 万"
                    )
                },
                "horizontal_contents": [
                    {
                        "type": "cols",
                        "cols": [
                            {"type": "markdown", "text": f"**💰 初始投资**\n{res.marketing_budget * 10:.0f} 万元"},
                            {"type": "markdown", "text": f"**📈 预期ROI**\n{r.input_output_recommendation.expected_roi}%"},
                            {"type": "markdown", "text": f"**⏱️ 回收周期**\n{r.input_output_recommendation.payback_period}月"},
                        ]
                    }
                ],
                "note": {
                    "tag": "markdown",
                    "content": f"⚠️ 风险等级: **{r.input_output_recommendation.risk_level}**"
                },
                "sections": [
                    {
                        "header": {"title": {"tag": "plain_text", "content": "🔍 SWOT 分析"}},
                        "fields": [
                            {"type": "markdown", "text": "\n".join([
                                "✅ " + " | ".join(r.swot.strengths[:2]),
                                "❌ " + " | ".join(r.swot.weaknesses[:2]),
                                "🌟 " + " | ".join(r.swot.opportunities[:2]),
                                "⚠️ " + " | ".join(r.swot.threats[:2]),
                            ])}
                        ]
                    },
                    {
                        "header": {"title": {"tag": "plain_text", "content": "👥 客群画像"}},
                        "fields": [
                            {"type": "markdown", "text": customer_text}
                        ]
                    },
                    {
                        "header": {"title": {"tag": "plain_text", "content": "📈 三年经营预测"}},
                        "fields": [
                            {"type": "markdown", "text": "\n".join(forecast_lines)}
                        ]
                    },
                    {
                        "header": {"title": {"tag": "plain_text", "content": "🎯 重点发展业务"}},
                        "fields": [
                            {"type": "markdown", "text": bf_lines}
                        ]
                    },
                    {
                        "header": {"title": {"tag": "plain_text", "content": "⚙️ 资源配置建议"}},
                        "fields": [
                            {"type": "markdown", "text": resource_text}
                        ]
                    },
                ],
                "extra": {
                    "tag": "markdown",
                    "content": f"🏧 设备: {', '.join(r.resource_allocation.equipment[:3])}"
                },
                "button_selection": {
                    "name": "操作选项",
                    "action_name": "查看详情",
                    "options": [
                        {"id": "swot", "name": "SWOT详情"},
                        {"id": "forecast", "name": "三年预测"},
                        {"id": "resource", "name": "资源方案"},
                    ]
                },
                "buttons": [
                    {
                        "name": "导出报告",
                        "action_type": 1,
                        "value": {"branch_id": r.branch_id}
                    },
                    {
                        "name": "分享结果",
                        "action_type": 2,
                        "value": {"branch_id": r.branch_id}
                    }
                ]
            }
        }
    }
    
    return card


def card_to_json_string(card: Dict[str, Any], indent: bool = True) -> str:
    """将企微卡片转换为JSON字符串"""
    return json.dumps(card, ensure_ascii=False, indent=2 if indent else None)


# 兼容旧接口：直接生成文本摘要
def generate_summary(analysis_result) -> str:
    """生成简短文本摘要（用于无法使用交互卡片的场景）"""
    r = analysis_result
    lines = [
        f"🏦 网点分析 [{r.branch_id}]",
        f"📍 {r.zone_type} | {r.area}㎡ | {r.staff_count}人 | 竞争{r.competitor_count}家",
        f"📊 日均来访 {r.traffic_estimate.daily_visitors} 人 | 转化 {r.traffic_estimate.conversion_rate*100:.0f}%",
        f"💰 产能 {r.production_capacity_index} 万/人/年",
        f"🌟 重点业务: {r.business_focus[0] if r.business_focus else 'N/A'}",
        f"💵 初始投资 {r.input_output_recommendation.initial_investment} 万 | ROI {r.input_output_recommendation.expected_roi}%",
        f"⏱️ 回收周期 {r.input_output_recommendation.payback_period} 个月 | 风险 {r.input_output_recommendation.risk_level}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    sys_path_fix = __import__("os").path.dirname(__file__)
    import os
    sys_path_fix = os.path.join(os.path.dirname(__file__), "..")
    import sys
    sys.path.insert(0, sys_path_fix)
    
    from branch_analysis import BranchAnalysisEngine
    
    engine = BranchAnalysisEngine()
    result = engine.analyze(
        zone_type="商业区",
        area=300.0,
        staff_count=10,
        competitor_count=3,
        local_enterprise_count=50,
    )
    
    print("=== 文本摘要 ===")
    print(generate_summary(result))
    print()
    print("=== 企微卡片 JSON ===")
    card = generate_wecom_card(result)
    print(card_to_json_string(card))
