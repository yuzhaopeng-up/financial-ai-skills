#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并购方案生成 - 企微集成
"""

import json
import re
from ma_scheme_engine import MaSchemeEngine


class MaSchemeWecom:
    """并购方案生成企微集成"""
    
    def __init__(self):
        self.engine = MaSchemeEngine(api_mode=True)
    
    def handle_message(self, text: str, user_id: str = None) -> dict:
        text = text.strip()
        
        # 解析命令
        if text.startswith("并购方案") or text.startswith("生成方案"):
            return self._handle_generate(text)
        elif text.startswith("估值") or text.startswith("方案分析"):
            return self._handle_analysis(text)
        elif text in ["并购帮助", "帮助", "ma帮助"]:
            return self._build_help()
        else:
            return self._handle_generate(text)
    
    def _handle_generate(self, text: str) -> dict:
        """处理方案生成"""
        # 解析参数
        params = self._parse_ma_command(text)
        
        if not params.get("target"):
            return {
                "type": "text",
                "content": "请提供标的名称，例如：`并购方案 标的=A公司 营收=10000万 净利润=1000万`"
            }
        
        result = self.engine.generate_scheme(
            acquirer=params.get("acquirer"),
            target=params.get("target"),
            purpose=params.get("purpose"),
            target_revenue=params.get("revenue"),
            target_net_income=params.get("profit"),
            target_net_assets=params.get("assets"),
            target_industry=params.get("industry"),
            deal_size=params.get("deal_size"),
            synergy_revenue=params.get("synergy_rev"),
            synergy_cost=params.get("synergy_cost")
        )
        
        return self._build_result_card(result)
    
    def _handle_analysis(self, text: str) -> dict:
        """处理方案分析"""
        params = self._parse_ma_command(text)
        
        if not params.get("target"):
            return {
                "type": "text",
                "content": "请提供标的名称，例如：`估值 A公司 revenue=5000 profit=500`"
            }
        
        result = self.engine.generate_scheme(
            target=params.get("target"),
            target_revenue=params.get("revenue"),
            target_net_income=params.get("profit"),
            target_net_assets=params.get("assets"),
            target_industry=params.get("industry")
        )
        
        return self._build_valuation_card(result)
    
    def _parse_ma_command(self, text: str) -> dict:
        """解析并购命令参数"""
        params = {}
        
        # 移除命令前缀
        text = re.sub(r"^(并购方案|生成方案|估值|方案分析)\s*", "", text)
        
        # 解析 key=value 格式
        patterns = [
            (r"收购方[=＝]\s*([^&\s]+)", "acquirer"),
            (r"acquirer[=＝]\s*([^&\s]+)", "acquirer"),
            (r"甲方[=＝]\s*([^&\s]+)", "acquirer"),
            (r"标的[=＝]\s*([^&\s]+)", "target"),
            (r"target[=＝]\s*([^&\s]+)", "target"),
            (r"乙方[=＝]\s*([^&\s]+)", "target"),
            (r"目的[=＝]\s*([^&\s]+)", "purpose"),
            (r"purpose[=＝]\s*([^&\s]+)", "purpose"),
            (r"营收[=＝]\s*([\d.]+)", "revenue"),
            (r"revenue[=＝]\s*([\d.]+)", "revenue"),
            (r"r[=＝]\s*([\d.]+)", "revenue"),
            (r"利润[=＝]\s*([\d.]+)", "profit"),
            (r"profit[=＝]\s*([\d.]+)", "profit"),
            (r"e[=＝]\s*([\d.]+)", "profit"),
            (r"净利润[=＝]\s*([\d.]+)", "profit"),
            (r"净资产[=＝]\s*([\d.]+)", "assets"),
            (r"assets[=＝]\s*([\d.]+)", "assets"),
            (r"n[=＝]\s*([\d.]+)", "assets"),
            (r"行业[=＝]\s*([^&\s]+)", "industry"),
            (r"industry[=＝]\s*([^&\s]+)", "industry"),
            (r"i[=＝]\s*([^&\s]+)", "industry"),
            (r"交易规模[=＝]\s*([\d.]+)", "deal_size"),
            (r"deal[=＝]\s*([\d.]+)", "deal_size"),
            (r"d[=＝]\s*([\d.]+)", "deal_size"),
            (r"协同收入[=＝]\s*([\d.]+)", "synergy_rev"),
            (r"synergy_rev[=＝]\s*([\d.]+)", "synergy_rev"),
            (r"协同成本[=＝]\s*([\d.]+)", "synergy_cost"),
            (r"synergy_cost[=＝]\s*([\d.]+)", "synergy_cost"),
        ]
        
        for pattern, key in patterns:
            match = re.search(pattern, text)
            if match:
                value = match.group(1)
                if key in ["revenue", "profit", "assets", "deal_size", "synergy_rev", "synergy_cost"]:
                    try:
                        params[key] = float(value)
                    except:
                        params[key] = value
                else:
                    params[key] = value
        
        return params
    
    def _build_help(self) -> dict:
        """构建帮助信息"""
        return {
            "type": "text",
            "content": """🦞 **并购方案生成引擎**

📋 功能：输入收购方、被收购方、交易目的，输出交易结构设计、估值分析、财务预测及风险提示

📝 命令：`并购方案 标的=xxx 营收=xxx 利润=xxx`

**参数说明：**
• `收购方` / `acquirer` - 收购方名称
• `标的` / `target` - 被收购方名称
• `目的` / `purpose` - 交易目的
• `营收` / `revenue` / `r` - 营业收入（万元）
• `利润` / `profit` / `e` - 净利润（万元）
• `净资产` / `assets` / `n` - 净资产（万元）
• `行业` / `industry` / `i` - 所属行业
• `交易规模` / `deal` / `d` - 交易规模（万元）
• `协同收入` - 预期收入协同效应（万元/年）
• `协同成本` - 预期成本协同效应（万元/年）

**示例：**
`并购方案 标的=B科技公司 营收=50000 利润=5000 行业=互联网`

`估值 标的=A公司 营收=10000 利润=1000`"""
        }
    
    def _build_result_card(self, result: dict) -> dict:
        """构建结果卡片"""
        rec = result.get("recommendation", {})
        vals = result.get("valuations", {}).get("summary", {})
        risks = result.get("risks", {}).get("risk_stats", {})
        
        template_map = {
            "high": "red",
            "medium": "orange", 
            "low": "green"
        }
        
        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"📊 并购方案 - {result['target']}",
                    "template": template_map.get(rec.get("overall_risk", "medium"), "gray")
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {"tag": "lark_md", "content": f"**收购方**: {result['acquirer']}\n**标的**: {result['target']}\n**目的**: {result['purpose']}"}
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {"tag": "lark_md", "content": f"**推荐结构**: {rec.get('recommended_structure', '-')}\n**推荐估值**: {rec.get('recommended_value', 0):.0f}万\n**交易区间**: {rec.get('deal_size_range', {}).get('min', 0):.0f}万 ~ {rec.get('deal_size_range', {}).get('max', 0):.0f}万"}
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {"tag": "lark_md", "content": f"**风险统计**: 🔴{risks.get('high', 0)} 🟡{risks.get('medium', 0)} 🟢{risks.get('low', 0)}\n**风险等级**: {rec.get('overall_risk', 'medium').upper()}"}
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {"tag": "lark_md", "content": f"💡 {rec.get('risk_opinion', '')}"}
                    }
                ]
            }
        }
    
    def _build_valuation_card(self, result: dict) -> dict:
        """构建估值卡片"""
        vals = result.get("valuations", {})
        summary = vals.get("summary", {})
        
        elements = [
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"**标的**: {result['target']}\n**行业**: {result.get('target_industry', '-')}"}
            },
            {"tag": "hr"},
        ]
        
        for key in ["pe", "ps", "pb", "dcf"]:
            if key in vals:
                v = vals[key]
                elements.append({
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": f"**{v['name']}**: {v['value']:.0f}万 × {v.get('multiple', '-')}"}
                })
        
        if "synergy" in vals:
            syn = vals["synergy"]
            elements.append({
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"**协同效应**: {syn['value']:.0f}万"}
            })
        
        elements.extend([
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"**估值区间**: {summary.get('min', 0):.0f}万 ~ {summary.get('max', 0):.0f}万\n**推荐估值**: {summary.get('median', 0):.0f}万"}
            }
        ])
        
        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"💰 估值分析 - {result['target']}",
                    "template": "blue"
                },
                "elements": elements
            }
        }


def handle(text: str, user_id: str = None) -> dict:
    """入口函数"""
    return MaSchemeWecom().handle_message(text, user_id)


if __name__ == "__main__":
    # 测试
    result = handle("并购方案 标的=B科技公司 营收=50000 利润=5000 行业=互联网")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:1000])
