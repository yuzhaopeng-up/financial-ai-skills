#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户异议训练引擎 v1.0
模拟客户各种异议场景，为客户经理提供实战训练

Author: ArkClaw
Version: 1.0.0
"""

import json
import random
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


class ObjectionTrainingEngine:
    """客户异议训练引擎"""
    
    VERSION = "1.0.0"
    
    # 异议类型定义
    OBJECTION_TYPES = {
        "price": {
            "name": "价格异议",
            "icon": "💰",
            "description": "客户认为产品价格过高",
            "examples": [
                "太贵了，能便宜点吗？",
                "别家的比你们便宜多了",
                "这个价格我能买别的好几样了",
                "打个折吧，不打折我就不要了",
            ],
            "keywords": ["贵", "便宜", "打折", "价格", "钱", "太贵", "划算"],
        },
        "competition": {
            "name": "竞品比较",
            "icon": "🏃",
            "description": "客户更倾向竞品或进行比较",
            "examples": [
                "XX银行的产品比你们的好",
                "我朋友推荐我用那家的",
                "别家的收益率更高",
                "我看XX产品也不错",
            ],
            "keywords": ["XX", "别家", "其他", "竞争", "对比", "比较好"],
        },
        "need": {
            "name": "需求质疑",
            "icon": "🤔",
            "description": "客户质疑是否真正需要",
            "examples": [
                "我好像不需要这个",
                "买了也没多大用",
                "我再想想有没有必要",
                "有这个必要吗？",
            ],
            "keywords": ["不需要", "没用", "考虑", "必要", "想"],
        },
        "time": {
            "name": "拖延推辞",
            "icon": "⏰",
            "description": "客户找借口拖延决策",
            "examples": [
                "我再考虑考虑",
                "等我有时间再说",
                "等我跟家人商量商量",
                "下次再说吧",
            ],
            "keywords": ["考虑", "商量", "下次", "等等", "拖延", "忙"],
        },
        "trust": {
            "name": "信任问题",
            "icon": "🤨",
            "description": "客户对产品或服务不信任",
            "examples": [
                "你们靠谱吗？",
                "不会骗人吧？",
                "没听说过这个产品",
                "能相信你们吗？",
            ],
            "keywords": ["骗", "靠谱", "相信", "信任", "可靠", "安全"],
        },
        "risk": {
            "name": "风险担忧",
            "icon": "😰",
            "description": "客户担心潜在风险",
            "examples": [
                "会不会有风险？",
                "万一亏了怎么办？",
                "这个产品安全吗？",
                "会不会跑路？",
            ],
            "keywords": ["风险", "亏", "安全", "损失", "万一", "担心"],
        },
        "service": {
            "name": "服务投诉",
            "icon": "😤",
            "description": "客户对过去服务不满",
            "examples": [
                "上次服务不好，我不想再买了",
                "你们的态度太差了",
                "上次办理等了很久",
                "之前的问题都没解决",
            ],
            "keywords": ["服务", "态度", "不好", "投诉", "等", "慢"],
        },
    }
    
    # 回应策略模板
    RESPONSE_STRATEGIES = {
        "price": {
            "principle": "先认同后转化 - 将价格问题转化为价值问题",
            "steps": [
                "认同客户的顾虑",
                "询问价格背后的真正原因",
                "强调产品价值和差异化",
                "提供解决方案（如分期、优惠）",
                "促成行动"
            ],
            "example": "李先生，我完全理解您对价格的关注。其实很多客户一开始都有同样的顾虑。但您知道吗？这款产品的综合回报率比同类产品高出15%，而且我们还提供专属的增值服务..."
        },
        "competition": {
            "principle": "不贬低竞品 - 突出自身差异化优势",
            "steps": [
                "肯定竞品的优势",
                "了解客户选择竞品的原因",
                "强调自身差异化价值",
                "提供对比数据或案例",
                "引导客户重新评估"
            ],
            "example": "XX确实是个不错的品牌，我也很尊重它。不过每个产品都有自己的特点，您更看重哪方面呢？让我来给您介绍一下我们产品的独特优势..."
        },
        "need": {
            "principle": "启发需求认知 - 帮助客户发现潜在需求",
            "steps": [
                "询问当前状况",
                "挖掘潜在需求和痛点",
                "举例说明产品如何解决问题",
                "展示相似客户的成功案例",
                "引导客户自我评估"
            ],
            "example": "我理解您的顾虑。张先生，我想请教您一下，您目前有没有遇到过...（挖掘需求）其实很多客户一开始也觉得自己不需要，但后来发现..."
        },
        "time": {
            "principle": "制造紧迫感 - 给出决策的理由",
            "steps": [
                "理解客户的犹豫",
                "询问拖延的真正原因",
                "强调时间成本或机会成本",
                "提供限时优惠或特别方案",
                "约定具体的跟进时间"
            ],
            "example": "我理解您需要时间考虑。其实我想提醒您的是，这个优惠活动本周五就要结束了，而且按照您刚才说的情况，每拖延一天可能会有..."
        },
        "trust": {
            "principle": "建立信任 - 用证据说话",
            "steps": [
                "理解客户的不安全感",
                "介绍公司背景和资质",
                "展示客户评价和案例",
                "提供保障承诺",
                "降低决策门槛"
            ],
            "example": "您的顾虑完全合理，毕竟金额不小。其实我们是国企背景，拥有XX年的行业经验，已经服务了XX万客户。这是我们的资质证书和客户评价..."
        },
        "risk": {
            "principle": "理性分析 - 用数据消除担忧",
            "steps": [
                "承认风险的存在",
                "分析风险的实际程度",
                "介绍风险控制措施",
                "提供历史数据支持",
                "建议从小额开始尝试"
            ],
            "example": "您问的这个问题非常专业。确实，任何投资都有风险，但我们有完善的风险控制体系。过去5年我们产品的最大回撤只有2.3%，而且..."
        },
        "service": {
            "principle": "真诚道歉 - 用行动证明改变",
            "steps": [
                "真诚道歉",
                "认真倾听客户的不满",
                "承诺改进措施",
                "提供补偿方案",
                "邀请客户监督"
            ],
            "example": "非常抱歉给您带来了不好的体验，这是我绝对不想看到的。您说的问题我已经记录下来了，我们会立即改进。这是我们针对您情况的补偿方案..."
        },
    }
    
    # 评分维度
    SCORING_DIMENSIONS = {
        "first_impression": {
            "name": "第一印象",
            "weight": 0.2,
            "criteria": ["问候是否热情", "是否建立信任", "是否专业"]
        },
        "value_communication": {
            "name": "价值传递",
            "weight": 0.3,
            "criteria": ["是否清晰介绍产品", "是否突出差异化", "是否匹配客户需求"]
        },
        "objection_handling": {
            "name": "异议化解",
            "weight": 0.3,
            "criteria": ["是否先认同", "是否给出解决方案", "是否转化话题"]
        },
        "action_closing": {
            "name": "行动促成",
            "weight": 0.2,
            "criteria": ["是否给客户台阶下", "是否约定下一步", "是否制造紧迫感"]
        }
    }
    
    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode
        self._log("初始化客户异议训练引擎 v%s" % self.VERSION)
    
    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)
    
    def get_available_types(self) -> List[Dict[str, str]]:
        """获取所有可用的异议类型"""
        return [
            {"type": key, **val}
            for key, val in self.OBJECTION_TYPES.items()
        ]
    
    def generate_scenario(self, objection_type: str = None, difficulty: str = "medium") -> Dict[str, Any]:
        """
        生成训练场景
        
        Args:
            objection_type: 异议类型 (如不指定则随机)
            difficulty: 难度 (easy/medium/hard)
        
        Returns:
            训练场景
        """
        if objection_type and objection_type not in self.OBJECTION_TYPES:
            raise ValueError(f"不支持的异议类型: {objection_type}")
        
        if not objection_type:
            objection_type = random.choice(list(self.OBJECTION_TYPES.keys()))
        
        obj_info = self.OBJECTION_TYPES[objection_type]
        strategy = self.RESPONSE_STRATEGIES[objection_type]
        
        # 根据难度调整客户态度
        difficulty_multiplier = {
            "easy": 0.7,      # 较容易说服
            "medium": 1.0,    # 中等难度
            "hard": 1.5       # 难以说服
        }.get(difficulty, 1.0)
        
        scenario = {
            "scenario_id": self._generate_id(),
            "objection_type": objection_type,
            "objection_name": obj_info["name"],
            "objection_icon": obj_info["icon"],
            "difficulty": difficulty,
            "customer_statement": random.choice(obj_info["examples"]),
            "customer_mood": self._generate_customer_mood(difficulty),
            "principle": strategy["principle"],
            "suggested_steps": strategy["steps"],
            "example_response": strategy["example"],
            "hints": self._generate_hints(objection_type),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return scenario
    
    def _generate_id(self) -> str:
        return f"SC{int(datetime.now().timestamp())}{random.randint(100, 999)}"
    
    def _generate_customer_mood(self, difficulty: str) -> str:
        moods = {
            "easy": ["比较友好", "愿意倾听", "有些犹豫"],
            "medium": ["态度一般", "有所保留", "需要说服"],
            "hard": ["态度强硬", "不太友好", "非常抵触"]
        }
        return random.choice(moods.get(difficulty, moods["medium"]))
    
    def _generate_hints(self, objection_type: str) -> List[str]:
        """生成提示"""
        hints_map = {
            "price": [
                "不要直接拒绝客户的价格诉求",
                "尝试了解'贵'背后的真正原因",
                "可以将价格问题转化为价值问题"
            ],
            "competition": [
                "不要贬低竞品",
                "了解客户选择竞品的原因",
                "强调自身差异化优势"
            ],
            "need": [
                "不要急于否定客户",
                "通过提问挖掘潜在需求",
                "用案例引导客户思考"
            ],
            "time": [
                "不要给客户太大压力",
                "了解拖延的真正原因",
                "可以制造适度的紧迫感"
            ],
            "trust": [
                "展示资质和案例",
                "用数据说话",
                "降低决策门槛"
            ],
            "risk": [
                "理性分析风险",
                "介绍风控措施",
                "建议从小额开始"
            ],
            "service": [
                "真诚道歉",
                "倾听客户不满",
                "承诺改进"
            ]
        }
        return hints_map.get(objection_type, [])
    
    def evaluate_response(self, scenario: Dict, user_response: str) -> Dict[str, Any]:
        """
        评估用户回复
        
        Args:
            scenario: 训练场景
            user_response: 用户的回复
        
        Returns:
            评估结果
        """
        scores = {}
        feedbacks = {}
        total_score = 0
        
        response_lower = user_response.lower()
        obj_type = scenario["objection_type"]
        
        # 第一印象评分
        first_impression = self._score_first_impression(response_lower, obj_type)
        scores["first_impression"] = first_impression
        feedbacks["first_impression"] = self._get_first_impression_feedback(first_impression, response_lower, obj_type)
        
        # 价值传递评分
        value_score = self._score_value_communication(response_lower, obj_type)
        scores["value_communication"] = value_score
        feedbacks["value_communication"] = self._get_value_feedback(value_score, response_lower)
        
        # 异议化解评分
        objection_score = self._score_objection_handling(response_lower, obj_type)
        scores["objection_handling"] = objection_score
        feedbacks["objection_handling"] = self._get_objection_feedback(objection_score, response_lower, obj_type)
        
        # 行动促成评分
        action_score = self._score_action_closing(response_lower, obj_type)
        scores["action_closing"] = action_score
        feedbacks["action_closing"] = self._get_action_feedback(action_score, response_lower)
        
        # 计算加权总分
        weighted_scores = {
            key: scores[key] * self.SCORING_DIMENSIONS[key]["weight"]
            for key in scores
        }
        total_score = sum(weighted_scores.values())
        
        # 评级
        if total_score >= 85:
            grade = "A"
            grade_label = "🌟 优秀"
        elif total_score >= 70:
            grade = "B"
            grade_label = "👍 良好"
        elif total_score >= 60:
            grade = "C"
            grade_label = "⚠️ 及格"
        else:
            grade = "D"
            grade_label = "❌ 不及格"
        
        return {
            "scenario_id": scenario["scenario_id"],
            "objection_type": scenario["objection_type"],
            "objection_name": scenario["objection_name"],
            "user_response": user_response,
            "scores": scores,
            "weighted_scores": weighted_scores,
            "total_score": round(total_score, 1),
            "grade": grade,
            "grade_label": grade_label,
            "feedbacks": feedbacks,
            "suggestions": self._generate_suggestions(scenario, scores),
            "evaluated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _score_first_impression(self, response: str, obj_type: str) -> float:
        """评分第一印象"""
        score = 60  # 基础分
        
        # 正面指标
        positive_words = ["理解", "了解", "明白", "您说得对", "确实", "完全", "理解您"]
        for word in positive_words:
            if word in response:
                score += 8
        
        # 专业性
        professional_words = ["产品", "服务", "方案", "帮助", "解决"]
        for word in professional_words:
            if word in response:
                score += 3
        
        return min(100, score)
    
    def _score_value_communication(self, response: str, obj_type: str) -> float:
        """评分价值传递"""
        score = 50
        
        # 提到产品价值
        value_words = ["价值", "收益", "回报", "优势", "特点", "好处", "帮助"]
        for word in value_words:
            if word in response:
                score += 7
        
        # 具体数据
        if any(c in response for c in ["%", "倍", "万", "千"]):
            score += 10
        
        # 差异化
        diff_words = ["不同", "区别", "相比", "独特", "特别"]
        for word in diff_words:
            if word in response:
                score += 5
        
        return min(100, score)
    
    def _score_objection_handling(self, response: str, obj_type: str) -> float:
        """评分异议化解"""
        score = 40
        
        # 认同策略
        if any(word in response for word in ["理解", "明白", "确实", "您说得对"]):
            score += 15
        
        # 提供解决方案
        solution_words = ["可以", "建议", "方案", "帮助", "提供", "这样"]
        for word in solution_words:
            if word in response:
                score += 5
        
        # 类型特定
        type_scores = {
            "price": (["打折", "优惠", "便宜"], 15),
            "competition": (["优势", "区别", "不同"], 10),
            "need": (["需要", "其实", "帮助"], 10),
            "time": (["考虑", "理解"], 5),
            "trust": (["保证", "承诺", "见证"], 15),
            "risk": (["风险", "控制", "安全"], 10),
            "service": (["道歉", "改进", "解决"], 20),
        }
        
        if obj_type in type_scores:
            words, bonus = type_scores[obj_type]
            for word in words:
                if word in response:
                    score += bonus
                    break
        
        return min(100, score)
    
    def _score_action_closing(self, response: str, obj_type: str) -> float:
        """评分行动促成"""
        score = 40
        
        # 促进行动
        action_words = ["试试", "体验", "了解", "看看", "考虑", "先", "可以先"]
        for word in action_words:
            if word in response:
                score += 12
        
        # 约定下一步
        next_words = ["明天", "后天", "周一", "本周", "稍后", "到时候"]
        for word in next_words:
            if word in response:
                score += 15
        
        # 紧迫感
        urgency_words = ["今天", "现在", "优惠", "活动", "限时"]
        for word in urgency_words:
            if word in response:
                score += 8
        
        return min(100, score)
    
    def _get_first_impression_feedback(self, score: float, response: str, obj_type: str) -> str:
        if score >= 80:
            return "👍 开场很好，建立了良好的沟通氛围"
        elif score >= 60:
            return "⚠️ 开场一般，可以更热情一些"
        else:
            return "❌ 开场需要改进，注意先认同客户"
    
    def _get_value_feedback(self, score: float, response: str) -> str:
        if score >= 80:
            return "👍 价值传递清晰有效"
        elif score >= 60:
            return "⚠️ 价值传递有所欠缺，建议多举例"
        else:
            return "❌ 价值传递不足，需要更具体地说明产品优势"
    
    def _get_objection_feedback(self, score: float, response: str, obj_type: str) -> str:
        if score >= 80:
            return "👍 异议化解得当，客户会感到被理解"
        elif score >= 60:
            return "⚠️ 异议化解一般，注意先认同再引导"
        else:
            return "❌ 异议化解不够，建议先理解客户立场"
    
    def _get_action_feedback(self, score: float, response: str) -> str:
        if score >= 80:
            return "👍 促进行动自然，给了客户台阶"
        elif score >= 60:
            return "⚠️ 促进行动可以更明确"
        else:
            return "❌ 没有有效地促进行动"
    
    def _generate_suggestions(self, scenario: Dict, scores: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        lowest_key = min(scores, key=scores.get)
        lowest_score = scores[lowest_key]
        
        dim_info = self.SCORING_DIMENSIONS[lowest_key]
        
        if lowest_score < 70:
            suggestions.append(f"💡 {dim_info['name']}需要加强（当前{lowest_score}分）")
            suggestions.append(f"   {', '.join(dim_info['criteria'])}")
        
        if scores.get("first_impression", 0) < 70:
            suggestions.append("💡 建议：开始对话时先表达对客户的理解和认同")
        
        if scores.get("value_communication", 0) < 70:
            suggestions.append("💡 建议：用具体数据和案例来说明产品价值")
        
        if scores.get("objection_handling", 0) < 70:
            suggestions.append("💡 建议：先认同客户顾虑，再提供解决方案")
        
        if scores.get("action_closing", 0) < 70:
            suggestions.append("💡 建议：给客户一个容易接受的行动建议")
        
        return suggestions[:5]  # 最多5条建议
    
    def generate_continue_scenario(self, scenario: Dict, user_response: str) -> Dict[str, Any]:
        """生成多轮对话的下一轮场景"""
        return {
            "scenario_id": self._generate_id(),
            "objection_type": scenario["objection_type"],
            "objection_name": scenario["objection_name"],
            "previous_response": user_response,
            "customer_counter": "我还是有顾虑，能不能给我更多保障？",
            "difficulty": "hard",
            "principle": scenario["principle"],
            "hints": scenario["hints"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def format_text(self, result: Dict, format_type: str = "scenario") -> str:
        """格式化输出"""
        if format_type == "scenario":
            return self._format_scenario_text(result)
        elif format_type == "evaluation":
            return self._format_evaluation_text(result)
        else:
            return self._format_scenario_text(result)
    
    def _format_scenario_text(self, scenario: Dict) -> str:
        """格式化场景"""
        lines = [
            f"🎭 **客户异议训练场景**",
            f"",
            f"📌 **场景ID**: {scenario['scenario_id']}",
            f"🏷️ **异议类型**: {scenario['objection_icon']} {scenario['objection_name']}",
            f"📊 **难度**: {scenario['difficulty']}",
            f"😀 **客户态度**: {scenario['customer_mood']}",
            f"",
            f"{'='*30}",
            f"",
            f"💬 **客户说**:",
            f"",
            f"{scenario['customer_statement']}",
            f"",
            f"{'='*30}",
            f"",
            f"💡 **回应原则**:",
            f"",
            f"{scenario['principle']}",
            f"",
            f"📝 **建议步骤**:",
        ]
        
        for i, step in enumerate(scenario["suggested_steps"], 1):
            lines.append(f"   {i}. {step}")
        
        if scenario.get("hints"):
            lines.extend([
                f"",
                f"🔖 **提示**:"
            ])
            for hint in scenario["hints"][:2]:
                lines.append(f"   • {hint}")
        
        lines.extend([
            f"",
            f"{'='*30}",
            f"⏰ 生成时间：{scenario['created_at']}",
        ])
        
        return '\n'.join(lines)
    
    def _format_evaluation_text(self, result: Dict) -> str:
        """格式化评估结果"""
        lines = [
            f"📊 **训练评估报告**",
            f"",
            f"🏷️ **场景**: {result['objection_name']}",
            f"📌 **场景ID**: {result['scenario_id']}",
            f"",
            f"{'='*30}",
            f"",
            f"🎯 **总分**: {result['total_score']:.1f}/100",
            f"📋 **评级**: {result['grade_label']} ({result['grade']})",
            f"",
            f"📉 **分项得分**:",
        ]
        
        for key, score in result["scores"].items():
            dim_info = self.SCORING_DIMENSIONS[key]
            bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
            lines.append(f"   {dim_info['name']}: {score:.0f}/100 {bar}")
        
        lines.extend([
            f"",
            f"{'='*30}",
            f"",
            f"💬 **您的回复**:",
            f"",
            f"{result['user_response']}",
            f"",
            f"{'='*30}",
            f"",
            f"📝 **分项反馈**:",
        ])
        
        for key, feedback in result["feedbacks"].items():
            dim_info = self.SCORING_DIMENSIONS[key]
            lines.append(f"   **{dim_info['name']}**: {feedback}")
        
        if result.get("suggestions"):
            lines.extend([
                f"",
                f"{'='*30}",
                f"",
                f"💡 **改进建议**:"
            ])
            for suggestion in result["suggestions"]:
                lines.append(f"   {suggestion}")
        
        lines.extend([
            f"",
            f"{'='*30}",
            f"⏰ 评估时间：{result['evaluated_at']}",
        ])
        
        return '\n'.join(lines)


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("🦞 客户异议训练引擎 v1.0")
    print("=" * 50)
    print()
    
    engine = ObjectionTrainingEngine()
    
    # 显示可用类型
    print("📋 支持的异议类型:")
    for obj in engine.get_available_types():
        print(f"  {obj['icon']} {obj['type']}: {obj['name']}")
    print()
    
    # 生成场景
    print("🎭 生成训练场景")
    print("-" * 40)
    scenario = engine.generate_scenario("price", "medium")
    print(engine.format_text(scenario))
    print()
    
    # 模拟用户回复
    user_response = input("请输入您的回复（直接回车使用示例回复）:\n") or (
        "我理解您的顾虑，确实价格是我们选择产品时非常重要的因素。"
        "其实您知道吗？这款产品虽然价格看起来稍高，但它的综合回报率比同类产品高出20%以上。"
        "而且我们还提供专属的VIP服务和一年期的免费维护。"
        "您可以先体验一下，现在开户还有优惠活动。"
    )
    print()
    
    # 评估回复
    print("📊 评估您的回复")
    print("-" * 40)
    evaluation = engine.evaluate_response(scenario, user_response)
    print(engine.format_text(evaluation, "evaluation"))


if __name__ == "__main__":
    main()
