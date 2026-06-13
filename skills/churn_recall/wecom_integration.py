#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流失客户召回引擎 - 企微集成

Author: ArkClaw
Version: 1.0.0
"""

import json
from typing import Dict, Any, Optional

from churn_recall_engine import ChurnRecallEngine, generate_mock_customer


class ChurnRecallWecom:
    """流失客户召回企微集成"""
    
    def __init__(self, api_mode: bool = True):
        self.engine = ChurnRecallEngine(api_mode=api_mode)
    
    def handle_message(self, text: str, user_id: str = None) -> Dict[str, Any]:
        """
        处理企微消息
        
        Args:
            text: 用户输入文本
            user_id: 用户ID
        
        Returns:
            响应数据
        """
        text = text.strip()
        
        # 解析命令
        if text.startswith("流失召回"):
            return self._handle_recall(text, user_id)
        elif text.startswith("流失分析"):
            return self._handle_analyze(text, user_id)
        elif text.startswith("召回话术"):
            return self._handle_script(text, user_id)
        elif text in ["流失帮助", "帮助"]:
            return self._build_help()
        elif text.startswith("流失批量"):
            return self._handle_batch(text)
        else:
            return self._build_help()
    
    def _handle_recall(self, text: str, user_id: str = None) -> Dict[str, Any]:
        """处理流失召回命令"""
        # 解析参数
        parts = text.replace("流失召回", "").strip()
        
        if not parts:
            return self._build_help_recall()
        
        # 简单参数解析
        params = self._parse_params(parts)
        customer_id = params.get("id", f"C{user_id or '00000'}")
        name = params.get("name", "客户")
        
        # 生成模拟数据
        customer = generate_mock_customer(customer_id, name)
        customer.update(params)
        
        # 分析并生成召回
        risk_result = self.engine.analyze_churn_risk(customer)
        recall_result = self.engine.generate_recall_script(customer, risk_result)
        
        return self._build_recall_card(recall_result)
    
    def _handle_analyze(self, text: str, user_id: str = None) -> Dict[str, Any]:
        """处理流失分析命令"""
        parts = text.replace("流失分析", "").strip()
        
        if not parts:
            return self._build_help_analyze()
        
        params = self._parse_params(parts)
        customer_id = params.get("id", f"C{user_id or '00000'}")
        name = params.get("name", "客户")
        
        customer = generate_mock_customer(customer_id, name)
        customer.update(params)
        
        risk_result = self.engine.analyze_churn_risk(customer)
        
        return self._build_analysis_card(risk_result)
    
    def _handle_script(self, text: str, user_id: str = None) -> Dict[str, Any]:
        """处理召回话术命令"""
        parts = text.replace("召回话术", "").strip()
        
        if not parts:
            return self._build_help_script()
        
        params = self._parse_params(parts)
        customer_id = params.get("id", f"C{user_id or '00000'}")
        name = params.get("name", "客户")
        
        customer = generate_mock_customer(customer_id, name)
        customer.update(params)
        
        risk_result = self.engine.analyze_churn_risk(customer)
        recall_result = self.engine.generate_recall_script(customer, risk_result)
        
        return self._build_script_card(recall_result)
    
    def _handle_batch(self, text: str) -> Dict[str, Any]:
        """处理批量分析命令"""
        parts = text.replace("流失批量", "").strip()
        
        # 解析数量
        count = 5
        if parts:
            try:
                count = int(parts.split()[0])
            except:
                count = 5
        
        customers = [generate_mock_customer() for _ in range(count)]
        results = self.engine.batch_analyze(customers)
        
        high = len([r for r in results if r["risk_level"] == "high"])
        medium = len([r for r in results if r["risk_level"] == "medium"])
        low = len([r for r in results if r["risk_level"] == "low"])
        
        content = f"""📊 **批量流失风险分析完成**

分析了 **{len(results)}** 位客户：

🔴 高风险：{high}人
🟡 中风险：{medium}人
🟢 低风险：{low}人

---
💡 发送 `流失批量 10 高风险` 获取详细召回方案"""
        
        return {"type": "text", "content": content}
    
    def _parse_params(self, text: str) -> Dict[str, Any]:
        """简单参数解析"""
        params = {}
        
        # 处理常见格式
        # 格式1: 张三 30天 2次 500元
        # 格式2: id=C88888 name=张三 recency=30
        
        parts = text.split()
        for part in parts:
            if "=" in part:
                key, value = part.split("=", 1)
                params[key.strip()] = self._convert_value(value.strip())
            elif "天" in part:
                try:
                    params["recency"] = int(part.replace("天", ""))
                except:
                    pass
            elif "次" in part:
                try:
                    params["frequency"] = float(part.replace("次", ""))
                except:
                    pass
            elif "元" in part:
                try:
                    params["amount"] = float(part.replace("元", ""))
                except:
                    pass
            elif part.isdigit():
                if "recency" not in params:
                    params["recency"] = int(part)
                elif "frequency" not in params:
                    params["frequency"] = float(part)
                elif "amount" not in params:
                    params["amount"] = float(part)
            elif "id=" in part:
                params["customer_id"] = part.split("=")[1].strip()
            elif "name=" in part:
                params["name"] = part.split("=")[1].strip()
        
        return params
    
    def _convert_value(self, value: str) -> Any:
        """转换参数值类型"""
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except:
            pass
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        return value
    
    def _build_help(self) -> Dict[str, Any]:
        """构建帮助信息"""
        content = """🦞 **流失客户召回引擎**

📋 **功能说明**
识别高流失风险客户，生成个性化召回话术

📝 **命令列表**

`流失召回 [客户名] [参数]`
  - 流失风险分析 + 召回话术
  - 示例: 流失召回 张伟 30天 2次

`流失分析 [客户名] [参数]`
  - 仅分析流失风险
  - 示例: 流失分析 李四 60天

`召回话术 [客户名] [参数]`
  - 仅生成召回话术
  - 示例: 召回话术 王五 90天 1次 300元

`流失批量 [数量]`
  - 批量分析客户风险
  - 示例: 流失批量 10

💡 **参数说明**
- 天数: 最近购买距今天数
- 次数: 月均购买次数
- 元: 平均订单金额"""
        
        return {"type": "text", "content": content}
    
    def _build_help_recall(self) -> Dict[str, Any]:
        content = """📝 **流失召回命令**

格式: `流失召回 客户名 天数 次数 金额`

示例:
`流失召回 张伟` - 使用默认参数
`流失召回 张伟 30天` - 30天未购买
`流失召回 张伟 30天 2次` - 30天未购买，月均2次
`流失召回 张伟 30天 2次 500元` - 完整参数"""
        return {"type": "text", "content": content}
    
    def _build_help_analyze(self) -> Dict[str, Any]:
        content = """📝 **流失分析命令**

格式: `流失分析 客户名 天数`

示例:
`流失分析 张伟` - 使用默认参数
`流失分析 张伟 60天` - 60天未购买"""
        return {"type": "text", "content": content}
    
    def _build_help_script(self) -> Dict[str, Any]:
        content = """📝 **召回话术命令**

格式: `召回话术 客户名 天数 次数 金额`

示例:
`召回话术 张伟` - 使用默认参数
`召回话术 张伟 90天 1次 300元`"""
        return {"type": "text", "content": content}
    
    def _build_recall_card(self, result: Dict) -> Dict[str, Any]:
        """构建召回方案卡片"""
        priority_color = {
            "high": "red",
            "medium": "orange", 
            "low": "green"
        }.get(result["priority"], "gray")
        
        card = {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"📞 客户召回方案 - {result['name']}",
                    "template": priority_color
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"""**客户ID**: {result['customer_id']}
**风险等级**: {result['risk_level']}
**主要原因**: {result['primary_reason']}
**召回策略**: {result['strategy']}"""
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**📝 个性化话术**\n\n{result['scripts']['full_script']}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"""**📱 触达建议**
- 渠道: {result['outreach']['channel']}
- 时间: {result['outreach']['timing']}
- 频次: {result['outreach']['frequency']}
- 风格: {result['outreach']['script_tone']}"""
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "note",
                        "elements": [
                            {"tag": "plain_text", "content": f"⏰ 生成时间: {result['generate_time']}"}
                        ]
                    }
                ]
            }
        }
        
        return card
    
    def _build_analysis_card(self, result: Dict) -> Dict[str, Any]:
        """构建分析结果卡片"""
        r_color = "red" if result['rfm_scores']['R'] >= 3 else "green"
        f_color = "red" if result['rfm_scores']['F'] >= 3 else "green"
        m_color = "red" if result['rfm_scores']['M'] >= 3 else "green"
        
        reasons_text = "\n".join([
            f"- **{r['reason']}** (置信度: {r['confidence']*100:.0f}%)"
            for r in result['churn_reasons'][:3]
        ])
        
        card = {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"📊 流失风险分析 - {result['name']}",
                    "template": result['risk_level'] == "high" and "red" or result['risk_level'] == "medium" and "orange" or "green"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"""**客户ID**: {result['customer_id']}
**风险评分**: {result['risk_score']:.1f}/100
**风险等级**: {result['risk_label']}"""
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"""**📉 RFM得分**
- R(最近购买): {result['rfm_scores']['R']}/5
- F(购买频率): {result['rfm_scores']['F']}/5
- M(消费金额): {result['rfm_scores']['M']}/5"""
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"""**🔍 流失原因分析**
{reasons_text}"""
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "note",
                        "elements": [
                            {"tag": "plain_text", "content": f"⏰ 分析时间: {result['analysis_time']}"}
                        ]
                    }
                ]
            }
        }
        
        return card
    
    def _build_script_card(self, result: Dict) -> Dict[str, Any]:
        """构建话术卡片"""
        card = {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"📝 召回话术 - {result['name']}",
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**📌 话术主题**: {result['scripts']['title']}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**📖 话术内容**\n\n{result['scripts']['full_script']}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"""**💡 具体措施**
""" + "\n".join([f"{i+1}. {t}" for i, t in enumerate(result['tactics'])])
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "note",
                        "elements": [
                            {"tag": "plain_text", "content": f"⏰ 生成时间: {result['generate_time']} | 优先级: {result['priority'].upper()}"}
                        ]
                    }
                ]
            }
        }
        
        return card


# 便捷函数
_wecom_instance = None

def handle(text: str, user_id: str = None) -> Dict[str, Any]:
    """处理企微消息的便捷函数"""
    global _wecom_instance
    if _wecom_instance is None:
        _wecom_instance = ChurnRecallWecom()
    return _wecom_instance.handle_message(text, user_id)


if __name__ == "__main__":
    # 测试
    handler = ChurnRecallWecom()
    
    print("测试流失召回:")
    result = handler.handle_message("流失召回 张伟 30天 2次 500元")
    print(json.dumps(result, ensure_ascii=False, indent=2))
