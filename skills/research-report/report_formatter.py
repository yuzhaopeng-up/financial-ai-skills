"""ReportFormatter - 研报多格式渲染。"""
from __future__ import annotations
import json
from typing import Dict, Any


class ReportFormatter:

    @staticmethod
    def to_text(report) -> str:
        r = report
        L = []
        L.append("=" * 72)
        L.append(f"📈 {r.title}")
        L.append("=" * 72)
        L.append(f"📅 生成时间: {r.generated_at}   |   置信度: {r.confidence:.0%}")
        L.append("")
        L.append("【一、报告摘要】")
        L.append(f"   {r.summary}")
        L.append("")
        L.append("【二、行业趋势分析】")
        L.append(f"   核心趋势: {' · '.join(r.industry_section['core_trends'][:5])}")
        L.append(f"   增长驱动:")
        for d in r.industry_section["growth_drivers"][:5]:
            L.append(f"      • {d}")
        L.append(f"   行业风险:")
        for w in r.industry_section["industry_risks"][:4]:
            L.append(f"      ⚠ {w}")
        L.append(f"   龙头公司: {', '.join(r.industry_section['key_companies'][:6])}")
        L.append("")
        L.append("【三、公司基本面分析】")
        cs = r.company_section
        L.append(f"   股票代码: {cs['code']}")
        L.append(f"   主营业务:")
        for s in cs["business_segments"]:
            L.append(f"      • {s}")
        L.append(f"   护城河:")
        for m in cs["moat"]:
            L.append(f"      ✓ {m}")
        L.append(f"   近期亮点:")
        for h in cs["highlights"]:
            L.append(f"      ★ {h}")
        L.append("")
        L.append("【四、财务亮点与估值】")
        fs = r.financial_section
        L.append(f"   关键指标:")
        for k in fs["core_metrics"]:
            L.append(f"      • {k}")
        L.append(f"   估值参考:")
        for k, v in fs["valuation_reference"].items():
            L.append(f"      • {k}: {v}")
        L.append(f"   可比公司: {', '.join(fs['comparable_companies'])}")
        L.append("")
        L.append("【五、风险提示】")
        for risk in r.risks:
            L.append(f"   ⚠️  {risk}")
        L.append("")
        L.append("【六、投资建议】")
        v = r.investment_view
        L.append(f"   🎯 评级: {v['rating']}")
        L.append(f"   📝 评级说明: {v['rating_explanation']}")
        L.append(f"   💡 核心逻辑: {v['core_logic']}")
        L.append(f"   📅 时间维度: {v['timeframe']}")
        L.append(f"   🚀 关键催化剂:")
        for c in v["key_catalysts"]:
            L.append(f"      • {c}")
        L.append(f"   📌 目标价说明: {v['target_price_note']}")
        L.append("")
        L.append("=" * 72)
        L.append("⚠️  本报告由 ArkClaw 研报生成器自动产出，仅供参考，不构成投资建议。")
        L.append("=" * 72)
        return "\n".join(L)

    @staticmethod
    def to_markdown(report) -> str:
        r = report
        L = []
        L.append(f"# 📈 {r.title}")
        L.append("")
        L.append(f"> 生成时间: `{r.generated_at}` · 置信度 `{r.confidence:.0%}`")
        L.append("")
        L.append("## 一、报告摘要")
        L.append(r.summary)
        L.append("")
        L.append("## 二、行业趋势分析")
        L.append("### 核心趋势")
        L.append(" · ".join(f"`{x}`" for x in r.industry_section["core_trends"]))
        L.append("")
        L.append("### 增长驱动")
        for d in r.industry_section["growth_drivers"]:
            L.append(f"- {d}")
        L.append("")
        L.append("### 行业风险")
        for w in r.industry_section["industry_risks"]:
            L.append(f"- ⚠ {w}")
        L.append("")
        L.append(f"### 龙头公司")
        L.append(", ".join(f"**{c}**" for c in r.industry_section["key_companies"]))
        L.append("")
        L.append("## 三、公司基本面分析")
        cs = r.company_section
        L.append(f"**股票代码**：`{cs['code']}`")
        L.append("")
        L.append("### 主营业务")
        for s in cs["business_segments"]:
            L.append(f"- {s}")
        L.append("")
        L.append("### 护城河")
        for m in cs["moat"]:
            L.append(f"- ✓ {m}")
        L.append("")
        L.append("### 近期亮点")
        for h in cs["highlights"]:
            L.append(f"- ★ {h}")
        L.append("")
        L.append("## 四、财务亮点与估值")
        fs = r.financial_section
        L.append("### 关键指标")
        for k in fs["core_metrics"]:
            L.append(f"- {k}")
        L.append("")
        L.append("### 估值方法参考")
        L.append("| 方法 | 说明 |")
        L.append("|------|------|")
        for k, v in fs["valuation_reference"].items():
            L.append(f"| {k} | {v} |")
        L.append("")
        L.append(f"**可比公司**：{', '.join(fs['comparable_companies'])}")
        L.append("")
        L.append("## 五、风险提示")
        for risk in r.risks:
            L.append(f"- ⚠️ {risk}")
        L.append("")
        L.append("## 六、投资建议")
        v = r.investment_view
        L.append(f"### 🎯 评级：**{v['rating']}**")
        L.append(f"> {v['rating_explanation']}")
        L.append("")
        L.append(f"**核心逻辑**：{v['core_logic']}")
        L.append("")
        L.append(f"**时间维度**：{v['timeframe']}")
        L.append("")
        L.append("**关键催化剂**：")
        for c in v["key_catalysts"]:
            L.append(f"- 🚀 {c}")
        L.append("")
        L.append(f"_目标价说明：{v['target_price_note']}_")
        L.append("")
        L.append("---")
        L.append("> ⚠️ 本报告由 ArkClaw 研报生成器自动产出，仅供参考，不构成投资建议。")
        return "\n".join(L)

    @staticmethod
    def to_json(report, indent: int = 2) -> str:
        return json.dumps(report.to_dict(), ensure_ascii=False, indent=indent)

    @staticmethod
    def to_wecom_card(report) -> Dict[str, Any]:
        r = report
        v = r.investment_view
        rating_color = {"买入": "🟢", "增持": "🟡", "中性": "⚪", "减持": "🔴"}.get(v["rating"], "⚪")
        return {
            "card_type": "text_notice",
            "main_title": {"title": f"📈 {r.title}", "desc": r.generated_at},
            "emphasis_content": {
                "title": f"{rating_color} {v['rating']}",
                "desc": f"置信度 {r.confidence:.0%}",
            },
            "horizontal_content_list": [
                {"keyname": "标的", "value": r.request.company or "-"},
                {"keyname": "行业", "value": r.request.industry},
                {"keyname": "年度", "value": str(r.request.year)},
                {"keyname": "时间维度", "value": v["timeframe"]},
                {"keyname": "可比公司", "value": ", ".join(r.financial_section["comparable_companies"][:3])},
            ],
            "quote_area": {
                "title": "💡 核心逻辑",
                "quote_text": v["core_logic"],
            },
            "button_list": [
                {"text": "📄 查看完整报告", "action_url": "/research/report"},
                {"text": "📊 行业趋势", "action_url": "/research/industry"},
                {"text": "⚠️ 风险提示", "action_url": "/research/risks"},
                {"text": "💼 加入自选", "action_url": "/research/watch"},
            ],
        }


if __name__ == "__main__":
    from report_engine import ReportEngine
    e = ReportEngine()
    r = e.generate("研报生成 新能源 宁德时代 2025")
    print(ReportFormatter.to_text(r))
