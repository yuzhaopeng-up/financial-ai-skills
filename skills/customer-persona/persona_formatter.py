"""
PersonaFormatter —— 客户画像渲染器
支持 text / json / markdown / wecom_card 四种格式。
"""
from __future__ import annotations
import json
from typing import Dict, Any


class PersonaFormatter:
    """画像结果的多格式输出。"""

    @staticmethod
    def to_text(persona) -> str:
        """终端友好的纯文本格式。"""
        ci = persona.customer
        rfm = persona.rfm_score
        lines = []
        lines.append("=" * 60)
        lines.append(f"📊 客户 360° 画像报告 - {ci.name or '匿名客户'}")
        lines.append("=" * 60)
        # 基础信息
        lines.append("")
        lines.append("👤 基础信息:")
        lines.append(f"   姓名/年龄: {ci.name or '-'} / {ci.age or '-'} 岁")
        lines.append(f"   性别/婚姻: {ci.gender or '-'} / {ci.marital_status or '-'}")
        if ci.monthly_income:
            lines.append(f"   月收入: {ci.monthly_income:,.0f} 元 ({ci.income_level()})")
        if ci.aum:
            lines.append(f"   AUM: {ci.aum:,.0f} 元")
        lines.append(f"   家庭: {'有房贷 ' if ci.has_mortgage else ''}"
                     f"{'有车贷 ' if ci.has_car_loan else ''}"
                     f"{f'有{ci.children_count}个孩子' if ci.has_children else '无子女'}")
        lines.append(f"   风险偏好: {ci.risk_preference or '-'}")
        if ci.occupation:
            lines.append(f"   职业: {ci.occupation}")
        if ci.city:
            lines.append(f"   城市: {ci.city}")
        # RFM
        lines.append("")
        lines.append(f"🎯 客户分层: {persona.rfm_segment}")
        lines.append(f"   RFM 评分: R={rfm['R']}/5  F={rfm['F']}/5  M={rfm['M']}/5  "
                     f"(综合 {sum(rfm.values())}/15)")
        lines.append(f"   生命周期: {persona.life_cycle_stage}")
        # 标签
        lines.append("")
        lines.append(f"🏷️  价值标签: {' / '.join(persona.value_tags)}")
        # 产品推荐
        lines.append("")
        lines.append(f"💰 推荐产品 (Top {len(persona.recommended_products)}):")
        for i, p in enumerate(persona.recommended_products, 1):
            lines.append(f"   {i}. [{p['type']}/{p['risk']}] {p['name']}  (匹配度 {p['score']})")
        # 渠道
        lines.append("")
        lines.append(f"📞 触达渠道:")
        for ch in persona.contact_channels:
            best_time = ch.get("best_time", "全天")
            lines.append(f"   • {ch['channel']}  最佳时段: {best_time}")
            lines.append(f"     原因: {ch.get('reason', '-')}")
        # 营销话术
        lines.append("")
        lines.append(f"💬 营销话术钩子:")
        for i, h in enumerate(persona.marketing_hooks, 1):
            lines.append(f"   [{i}] ({h['scenario']})")
            lines.append(f"       \"{h['hook_text']}\"")
            lines.append(f"       💭 预期反应: {h['expected_response']}")
        # 风险提示
        if persona.risk_warnings:
            lines.append("")
            lines.append(f"⚠️  风险提示:")
            for w in persona.risk_warnings:
                lines.append(f"   • {w}")
        # NBA
        lines.append("")
        lines.append(f"🎬 下一步最佳动作:")
        lines.append(f"   👉 {persona.next_best_action}")
        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)

    @staticmethod
    def to_json(persona, indent: int = 2) -> str:
        return json.dumps(persona.to_dict(), ensure_ascii=False, indent=indent)

    @staticmethod
    def to_markdown(persona) -> str:
        ci = persona.customer
        rfm = persona.rfm_score
        lines = []
        lines.append(f"# 📊 客户 360° 画像 - {ci.name or '匿名客户'}")
        lines.append("")
        lines.append(f"**分层**：{persona.rfm_segment}  |  **生命周期**：{persona.life_cycle_stage}")
        lines.append("")
        lines.append("## 基础信息")
        lines.append("| 项目 | 内容 |")
        lines.append("|------|------|")
        lines.append(f"| 姓名 | {ci.name or '-'} |")
        lines.append(f"| 年龄 | {ci.age or '-'} |")
        lines.append(f"| 月收入 | {ci.monthly_income or '-'} |")
        lines.append(f"| AUM | {ci.aum or '-'} |")
        lines.append(f"| 婚姻 | {ci.marital_status or '-'} |")
        lines.append(f"| 房贷 | {'是' if ci.has_mortgage else '否'} |")
        lines.append(f"| 子女 | {ci.children_count if ci.has_children else 0} |")
        lines.append(f"| 风险偏好 | {ci.risk_preference or '-'} |")
        lines.append("")
        lines.append(f"## RFM 评分: R={rfm['R']} / F={rfm['F']} / M={rfm['M']}")
        lines.append("")
        lines.append("## 价值标签")
        lines.append(", ".join(f"`{t}`" for t in persona.value_tags))
        lines.append("")
        lines.append("## 推荐产品")
        lines.append("| 序号 | 产品 | 类型 | 风险 | 匹配度 |")
        lines.append("|------|------|------|------|--------|")
        for i, p in enumerate(persona.recommended_products, 1):
            lines.append(f"| {i} | {p['name']} | {p['type']} | {p['risk']} | {p['score']} |")
        lines.append("")
        lines.append("## 触达渠道")
        for ch in persona.contact_channels:
            lines.append(f"- **{ch['channel']}** ({ch.get('best_time', '-')})：{ch.get('reason', '-')}")
        lines.append("")
        lines.append("## 营销话术钩子")
        for h in persona.marketing_hooks:
            lines.append(f"### {h['scenario']}")
            lines.append(f"> {h['hook_text']}")
            lines.append(f"_预期反应: {h['expected_response']}_")
            lines.append("")
        if persona.risk_warnings:
            lines.append("## ⚠️ 风险提示")
            for w in persona.risk_warnings:
                lines.append(f"- {w}")
            lines.append("")
        lines.append(f"## 下一步动作")
        lines.append(f"> {persona.next_best_action}")
        return "\n".join(lines)

    @staticmethod
    def to_wecom_card(persona) -> Dict[str, Any]:
        """企微 template_card 格式。"""
        ci = persona.customer
        top_product = persona.recommended_products[0]["name"] if persona.recommended_products else "-"
        top_channel = persona.contact_channels[0]["channel"] if persona.contact_channels else "-"
        return {
            "card_type": "text_notice",
            "main_title": {
                "title": f"📊 {ci.name or '客户'} 360° 画像",
                "desc": f"{persona.rfm_segment} · {persona.life_cycle_stage}",
            },
            "emphasis_content": {
                "title": top_product,
                "desc": "首推产品",
            },
            "horizontal_content_list": [
                {"keyname": "RFM 评分",
                 "value": f"R{persona.rfm_score['R']} F{persona.rfm_score['F']} M{persona.rfm_score['M']}"},
                {"keyname": "推荐渠道", "value": top_channel},
                {"keyname": "推荐产品数", "value": f"{len(persona.recommended_products)} 个"},
                {"keyname": "营销话术", "value": f"{len(persona.marketing_hooks)} 套"},
                {"keyname": "标签", "value": " / ".join(persona.value_tags[:4])},
            ],
            "quote_area": {
                "title": "🎬 下一步动作",
                "quote_text": persona.next_best_action,
            },
            "card_action": {
                "type": 1,
                "url": "/persona/detail",
            },
            "button_list": [
                {"text": "📞 立即触达", "action_url": "/persona/contact"},
                {"text": "💰 查看产品", "action_url": "/persona/products"},
                {"text": "💬 话术详情", "action_url": "/persona/hooks"},
                {"text": "📋 完整报告", "action_url": "/persona/full"},
            ],
        }


if __name__ == "__main__":
    from persona_engine import PersonaEngine
    eng = PersonaEngine()
    p = eng.generate("客户画像 张伟 35岁 月收入2万 已婚 有房贷 风险偏好稳健")
    print(PersonaFormatter.to_text(p))
