#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
估值核算辅助 - 企微集成
"""

import json
from valuation_helper_engine import ValuationHelperEngine


class ValuationHelperWecom:
    def __init__(self):
        self.engine = ValuationHelperEngine(api_mode=True)

    def handle_message(self, text: str, user_id: str = None) -> dict:
        text = text.strip()

        # 解析命令
        if text.startswith("估值核算") or text.startswith("估值"):
            content = text.replace("估值核算", "").replace("估值", "").strip()
            
            # 解析持仓和日期
            nav_date = None
            positions_text = content
            
            # 尝试提取日期
            import re
            date_match = re.search(r'日期[:：]?\s*(\d{4}-\d{2}-\d{2})', content)
            if date_match:
                nav_date = date_match.group(1)
                positions_text = content.replace(date_match.group(0), "").strip()
            
            if not nav_date:
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', content)
                if date_match:
                    nav_date = date_match.group(1)
                    positions_text = content.replace(date_match.group(0), "").strip()
            
            # 移除"持仓:"等前缀
            for prefix in ["持仓:", "持仓：", "positions:", "持仓"]:
                if positions_text.startswith(prefix):
                    positions_text = positions_text[len(prefix):].strip()
                    break
            
            if positions_text:
                positions = self.engine.parse_positions(positions_text)
                # TODO: 实际场景中应从行情API获取实时价格
                # 这里做简单的成本=现价处理
                result = self.engine.calculate_valuation(positions, nav_date=nav_date)
                return self.engine.format_wecom_card(result)
            
            return {"type": "text", "content": "请输入持仓信息，例如：`估值核算 持仓: 招商银行 1000股@35.5元 日期: 2024-01-15`"}

        elif text in ["估值帮助", "帮助", "help"]:
            return self._build_help()

        return self._build_help()

    def _build_help(self) -> dict:
        return {
            "type": "text",
            "content": """🦞 **估值核算辅助引擎**

📋 功能：持仓估值计算与异常预警

📝 命令：`估值核算 [持仓信息] [日期]`

📖 示例：
`估值核算 招商银行 1000股@35.5元, 基金A 5000份@2.3元 日期: 2024-01-15`

⚠️ 预警等级：🔴严重 🟠警告 🟡注意 🔵提示

💡 实际使用需接入行情API获取实时价格"""
        }

    def update_prices_from_api(self, positions: list, nav_date: str) -> list:
        """
        从行情API更新价格（实际场景中调用）
        这里仅做占位实现
        """
        # TODO: 接入实际行情API
        # 1. 股票: 实时行情接口
        # 2. 基金: 基金公司/托管行净值接口
        # 3. 债券: 中债估值接口
        return positions


def handle(text: str, user_id: str = None) -> dict:
    return ValuationHelperWecom().handle_message(text, user_id)


if __name__ == "__main__":
    result = handle("估值核算 招商银行 1000股@35.5元, 沪深300ETF 5000份@3.85元 日期: 2024-01-15")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:500])
