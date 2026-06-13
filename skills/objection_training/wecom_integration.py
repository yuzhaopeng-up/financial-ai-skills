#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户异议训练引擎 - 企微集成

Author: ArkClaw
Version: 1.0.0
"""

import json
from typing import Dict, Any, Optional

from objection_training_engine import ObjectionTrainingEngine


class ObjectionTrainingWecom:
    """客户异议训练企微集成"""
    
    def __init__(self, api_mode: bool = True):
        self.engine = ObjectionTrainingEngine(api_mode=api_mode)
        self.current_scenario = None  # 存储当前场景用于多轮对话
    
    def handle_message(self, text: str, user_id: str = None) -> Dict[str, Any]:
        """
        处理企微消息
        """
        text = text.strip()
        
        if text.startswith("异议训练"):
            return self._handle_training(text)
        elif text.startswith("训练"):
            return self._handle_training(text)
        elif text.startswith("模拟训练"):
            return self._handle_training(text)
        elif text.startswith("评估"):
            return self._handle_evaluation(text)
        elif text in ["异议类型", "异议帮助", "帮助"]:
            return self._build_help()
        elif text == "下一轮" and self.current_scenario:
            return self._handle_next_round()
        elif text == "跳过" and self.current_scenario:
            # 跳过当前，进入下一场景
            return self._handle_training("异议训练")
        else:
            return self._build_help()
    
    def _handle_training(self, text: str) -> Dict[str, Any]:
        """处理训练请求"""
        parts = text.replace("异议训练", "").replace("训练", "").replace("模拟训练", "").strip()
        
        # 解析参数
        obj_type = None
        difficulty = "medium"
        
        if parts:
            # 检查是否是有效的异议类型
            available_types = [t["type"] for t in self.engine.get_available_types()]
            if parts.lower() in available_types:
                obj_type = parts.lower()
            elif parts.lower() in ["价格", "贵"]:
                obj_type = "price"
            elif parts.lower() in ["竞品", "比较", "别家"]:
                obj_type = "competition"
            elif parts.lower() in ["需求", "需要"]:
                obj_type = "need"
            elif parts.lower() in ["拖延", "考虑"]:
                obj_type = "time"
            elif parts.lower() in ["信任", "靠谱"]:
                obj_type = "trust"
            elif parts.lower() in ["风险", "担心"]:
                obj_type = "risk"
            elif parts.lower() in ["服务", "投诉"]:
                obj_type = "service"
            
            # 检查难度
            if "简单" in parts or "容易" in parts:
                difficulty = "easy"
            elif "困难" in parts or "难" in parts:
                difficulty = "hard"
        
        # 生成场景
        scenario = self.engine.generate_scenario(obj_type, difficulty)
        self.current_scenario = scenario
        
        return self._build_scenario_card(scenario)
    
    def _handle_evaluation(self, text: str) -> Dict[str, Any]:
        """处理评估请求"""
        if not self.current_scenario:
            return {
                "type": "text",
                "content": "请先发送 `异议训练` 开始训练，再发送您的回复进行评估"
            }
        
        # 提取用户回复
        user_response = text.replace("评估", "").strip()
        
        if not user_response:
            return {
                "type": "text",
                "content": "请在 `评估` 后输入您的回复，例如：`评估 您的回复内容`"
            }
        
        evaluation = self.engine.evaluate_response(self.current_scenario, user_response)
        
        return self._build_evaluation_card(evaluation)
    
    def _handle_next_round(self) -> Dict[str, Any]:
        """处理下一轮训练"""
        if not self.current_scenario:
            return self._handle_training("异议训练")
        
        scenario = self.engine.generate_continue_scenario(
            self.current_scenario,
            ""  # 上一轮回复
        )
        self.current_scenario = scenario
        
        return self._build_scenario_card(scenario)
    
    def _build_help(self) -> Dict[str, Any]:
        """构建帮助信息"""
        types_text = "\n".join([
            f"• **{t['icon']} {t['name']}**: {t['description']}"
            for t in self.engine.get_available_types()
        ])
        
        content = f"""🦞 **客户异议训练引擎**

📋 **功能说明**
模拟客户各种异议场景，为您提供实战训练

📝 **命令列表**

`异议训练 [类型] [难度]`
  - 生成训练场景
  - 示例: 异议训练 价格
  - 示例: 异议训练 价格 困难
  - 示例: 异议训练 竞品 简单

`评估 [您的回复]`
  - 评估您的回复质量
  - 示例: 评估 我理解您的顾虑...

`下一轮`
  - 继续下一轮对话训练

📋 **支持的异议类型**

{types_text}

💡 **评分维度**
• 第一印象 (20%)
• 价值传递 (30%)
• 异议化解 (30%)
• 行动促成 (20%)"""
        
        return {"type": "text", "content": content}
    
    def _build_scenario_card(self, scenario: Dict) -> Dict[str, Any]:
        """构建场景卡片"""
        steps_text = "\n".join([
            f"{i+1}. {step}"
            for i, step in enumerate(scenario["suggested_steps"])
        ])
        
        hints_text = ""
        if scenario.get("hints"):
            hints_text = "\n".join([
                f"• {hint}"
                for hint in scenario["hints"][:2]
            ])
        
        card = {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"🎭 异议训练 - {scenario['objection_name']}",
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"""**难度**: {scenario['difficulty']}
**客户态度**: {scenario['customer_mood']}"""
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**💬 客户说:**\n\n> {scenario['customer_statement']}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**💡 回应原则:**\n\n{scenario['principle']}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**📝 建议步骤:**\n{steps_text}"
                        }
                    }
                ]
            }
        }
        
        if hints_text:
            card["card"]["elements"].append({"tag": "hr"})
            card["card"]["elements"].append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**🔖 提示:**\n{hints_text}"
                }
            })
        
        card["card"]["elements"].extend([
            {"tag": "hr"},
            {
                "tag": "note",
                "elements": [
                    {"tag": "plain_text", "content": "请输入您的回复，我将为您评分"}
                ]
            }
        ])
        
        return card
    
    def _build_evaluation_card(self, evaluation: Dict) -> Dict[str, Any]:
        """构建评估结果卡片"""
        grade_colors = {
            "A": "green",
            "B": "blue", 
            "C": "orange",
            "D": "red"
        }
        
        grade_colors_map = {
            "A": "green",
            "B": "blue",
            "C": "orange",
            "D": "red"
        }
        
        scores_text = "\n".join([
            f"• {evaluation['scores'][key]:.0f}/100"
            for key in ["first_impression", "value_communication", "objection_handling", "action_closing"]
        ])
        
        feedbacks_text = "\n".join([
            f"• {evaluation['feedbacks'][key]}"
            for key in ["first_impression", "value_communication", "objection_handling", "action_closing"]
        ])
        
        suggestions_text = ""
        if evaluation.get("suggestions"):
            suggestions_text = "\n".join([
                f"• {s}"
                for s in evaluation["suggestions"][:3]
            ])
        
        card = {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"📊 训练评估 - {evaluation['objection_name']}",
                    "template": grade_colors_map.get(evaluation["grade"], "gray")
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"""**总分**: {evaluation['total_score']:.1f}/100
**评级**: {evaluation['grade_label']}"""
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**💬 您的回复:**\n\n{evaluation['user_response']}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**📉 分项得分:**\n{scores_text}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**📝 分项反馈:**\n{feedbacks_text}"
                        }
                    }
                ]
            }
        }
        
        if suggestions_text:
            card["card"]["elements"].extend([
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**💡 改进建议:**\n{suggestions_text}"
                    }
                }
            ])
        
        card["card"]["elements"].extend([
            {"tag": "hr"},
            {
                "tag": "note",
                "elements": [
                    {"tag": "plain_text", "content": f"发送 `下一轮` 继续训练"}
                ]
            }
        ])
        
        return card


# 便捷函数
_wecom_instance = None

def handle(text: str, user_id: str = None) -> Dict[str, Any]:
    """处理企微消息的便捷函数"""
    global _wecom_instance
    if _wecom_instance is None:
        _wecom_instance = ObjectionTrainingWecom()
    return _wecom_instance.handle_message(text, user_id)


if __name__ == "__main__":
    # 测试
    handler = ObjectionTrainingWecom()
    
    print("测试异议训练:")
    result = handler.handle_message("异议训练 价格")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:500])
