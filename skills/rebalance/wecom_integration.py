#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资产配置再平衡 - 企微集成
"""

import json
from rebalance_engine import RebalanceEngine


class RebalanceWecom:
    def __init__(self):
        self.engine = RebalanceEngine(api_mode=True)
    
    def handle_message(self, text: str, user_id: str = None) -> dict:
        """
        处理企微消息
        
        支持的命令格式：
        - 再平衡 [当前持仓] [目标配置]
        - 帮助
        
        示例：
        再平衡 股票:400000,债券:200000 股票:50,债券:50
        """
        text = text.strip()
        
        if not text or text in ["帮助", "help"]:
            return self._build_help()
        
        if text.startswith("再平衡") or text.startswith("rebalance"):
            return self._parse_and_rebalance(text)
        
        # 尝试解析简化格式
        return self._parse_and_rebalance("再平衡 " + text)
    
    def _parse_and_rebalance(self, text: str) -> dict:
        """解析并执行再平衡"""
        # 去掉命令前缀
        content = text.replace("再平衡", "").replace("rebalance", "").strip()
        
        if not content:
            return self._build_help()
        
        # 尝试两种格式：
        # 格式1: 持仓JSON 目标JSON（用 | 或 空格 分隔）
        # 格式2: key:value,key:value  key:value,key:value
        
        parts = content.replace("|", " ").split()
        
        if len(parts) >= 2:
            # 两段式
            holdings_str, target_str = parts[0], parts[1]
        elif len(parts) == 1 and "," in content:
            # 简化格式：持仓目标合并
            return self._build_help()
        else:
            return self._build_help()
        
        # 解析持仓
        holdings = self._parse_kv_string(holdings_str)
        target = self._parse_kv_string(target_str)
        
        if not holdings or not target:
            return {
                "type": "text",
                "content": "❌ 格式解析失败，请使用：`再平衡 股票:400000,债券:200000 股票:50,债券:50`"
            }
        
        total = sum(holdings.values())
        result = self.engine.rebalance(
            current_holdings=holdings,
            target_allocation=target,
            total_value=total,
        )
        
        return self.engine.format_wecom_card(result)
    
    def _parse_kv_string(self, s: str) -> dict:
        """解析 key:value,key:value 格式"""
        try:
            result = {}
            items = s.split(",")
            for item in items:
                if ":" in item:
                    key, val = item.split(":", 1)
                    result[key.strip()] = float(val.strip())
            return result
        except (ValueError, AttributeError):
            return None
    
    def _build_help(self) -> dict:
        return {
            "type": "text",
            "content": """🦞 **资产配置再平衡引擎**

📋 功能：输入当前持仓 + 目标配置，输出调仓方案 + 交易成本估算

📝 命令：`再平衡 [当前持仓] [目标配置]`

💡 格式：`再平衡 股票:400000,债券:200000 股票:50,债券:50`

📊 支持资产类型：
  · 股票(A股/港股/美股)
  · 债券(国债/企业债)
  · 基金(ETF/指数基金)
  · 货币基金/现金
  · 黄金
  · 外汇
  · 银行理财

⚙️ 参数说明：
  · tolerance: 容忍偏差（默认5%）
  · min-trade: 最小交易额（默认1000元）

示例：`再平衡 股票:400000,债券:200000,黄金:100000 股票:35,债券:25,黄金:10`"""
        }


def handle(text: str, user_id: str = None) -> dict:
    """企微消息处理入口"""
    return RebalanceWecom().handle_message(text, user_id)


if __name__ == "__main__":
    # 测试
    test_cases = [
        "帮助",
        "再平衡 股票:400000,债券:200000,货币基金:150000,黄金:100000,银行存款:150000 股票:35,债券:25,货币基金:20,黄金:10,银行存款:10",
        "股票:400000,债券:200000 股票:50,债券:50",
    ]
    
    for tc in test_cases:
        print(f"\n{'='*40}")
        print(f"输入: {tc[:60]}...")
        result = handle(tc)
        print(f"输出类型: {result['type']}")
        if result["type"] == "text":
            print(result["content"][:200])
        else:
            print(json.dumps(result, ensure_ascii=False)[:300])
