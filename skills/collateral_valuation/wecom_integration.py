#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抵押物估值 - 企微集成
"""

import json
from collateral_valuation_engine import CollateralValuationEngine


class CollateralValuationWecom:
    def __init__(self):
        self.engine = CollateralValuationEngine(api_mode=True)
    
    def handle_message(self, text: str, user_id: str = None) -> dict:
        text = text.strip()
        
        # 解析抵押物估值命令
        # 格式: 抵押物估值 [类型] [地址/规格] [面积] [描述]
        if text.startswith("抵押物估值") or text.startswith("估值"):
            parts = text.replace("抵押物估值", "").replace("估值", "").strip().split()
            
            if len(parts) >= 1:
                collateral_type = parts[0]
            else:
                return {"type": "text", "content": "请输入抵押物信息，例如：`抵押物估值 房产 北京朝阳 100平`"}
            
            location_or_spec = parts[1] if len(parts) >= 2 else ""
            area_or_quantity = parts[2] if len(parts) >= 3 else ""
            description = " ".join(parts[3:]) if len(parts) >= 4 else ""
            
            result = self.engine.valuate(collateral_type, location_or_spec, area_or_quantity, description)
            return self._build_card(result)
        
        elif text in ["估值帮助", "帮助", "抵押物帮助"]:
            return self._build_help()
        
        return self._build_help()
    
    def _build_help(self) -> dict:
        return {
            "type": "text",
            "content": """🦞 **抵押物智能估值引擎**

📋 功能：输入抵押物类型、地址/规格、面积，输出估值报告+风险建议

📝 命令：`抵押物估值 [类型] [地址/规格] [面积] [描述]`

🏠 支持类型：房产/设备/车辆/土地/应收账款/股权

📊 验收标准：
  房产≤10% | 设备≤15% | 车辆≤12%
  土地≤15% | 应收账款≤10% | 股权≤15%

⚠️ 风险等级：🔴高 🟡中 🟢低

示例：
`抵押物估值 房产 北京朝阳 100平 房龄5年`
`抵押物估值 设备 医疗设备 2台 使用约3年`
`抵押物估值 车辆 宝马530Li 1辆 使用约1年`"""
        }
    
    def _build_card(self, result: dict) -> dict:
        val = result["valuation"]
        
        def fmt(v):
            if v >= 100000000:
                return f"{v/100000000:.2f}亿"
            elif v >= 10000:
                return f"{v/10000:.2f}万"
            else:
                return f"{v:.2f}"
        
        # 根据风险等级选择颜色
        color_map = {"high": "red", "medium": "orange", "low": "green"}
        template = color_map.get(result["risk_level"], "gray")
        
        # 估算价值显示
        estimated_str = fmt(val["estimated_value"])
        
        elements = [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**抵押物类型**: {result['collateral_type']}"}},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**位置/规格**: {result['location_or_spec']}"}},
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**💰 估算价值**: **{estimated_str}**"}},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"估值区间: {fmt(val['lower_bound'])} ~ {fmt(val['upper_bound'])}\n偏差率: ±{val['deviation_rate']*100:.0f}%"}},
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**风险等级**: {result['risk_label']}\n**风险评分**: {result['risk_score']:.0f}/100"}},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**流动性**: {result['liquidity_assessment']}"}},
        ]
        
        # 风险因素
        if result["risk_reasons"]:
            elements.append({"tag": "hr"})
            elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"**风险因素**: {'; '.join(result['risk_reasons'])}"}})
        
        # 验收标准
        collateral_dev = val.get("deviation_rate", 0.15)
        acceptance_std = {"房产": 0.10, "设备": 0.15, "车辆": 0.12, "土地": 0.15, "应收账款": 0.10, "股权": 0.15}
        std = acceptance_std.get(result["collateral_type"], 0.15)
        check_emoji = "✅" if collateral_dev <= std else "⚠️"
        elements.append({"tag": "hr"})
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": f"{check_emoji} **验收标准**: 偏差率 {collateral_dev*100:.0f}% vs 目标 {std*100:.0f}%"}})
        
        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"🏠 抵押物估值 - {result['risk_label']}",
                    "template": template
                },
                "elements": elements
            }
        }


def handle(text: str, user_id: str = None) -> dict:
    return CollateralValuationWecom().handle_message(text, user_id)


if __name__ == "__main__":
    test_cases = [
        "抵押物估值 房产 北京朝阳 100平 房龄5年",
        "抵押物估值 设备 医疗设备 2台 使用约3年",
        "抵押物估值 车辆 宝马530Li 1辆 使用约1年",
    ]
    
    for tc in test_cases:
        print(f"测试: {tc}")
        result = handle(tc)
        print(json.dumps(result, ensure_ascii=False, indent=2)[:500])
        print()
