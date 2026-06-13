#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流失客户召回引擎 v1.0
识别高流失风险客户，生成个性化召回话术

Author: ArkClaw
Version: 1.0.0
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple


class ChurnRecallEngine:
    """流失客户召回引擎"""
    
    VERSION = "1.0.0"
    
    # 流失原因映射
    CHURN_REASONS = {
        "price": {"name": "价格敏感", "icon": "💰"},
        "service": {"name": "服务质量", "icon": "😤"},
        "competitor": {"name": "竞品吸引", "icon": "🏃"},
        "product": {"name": "产品不满", "icon": "😞"},
        "inactive": {"name": "长期不活跃", "icon": "😴"},
        "lifestyle": {"name": "生活变化", "icon": "🔄"},
    }
    
    # 召回策略模板
    RECALL_STRATEGIES = {
        "price": {
            "strategy": "专属优惠+价格保护",
            "tactics": ["提供限时折扣", "发送专属优惠券", "承诺价格保护"],
            "priority": "high"
        },
        "service": {
            "strategy": "服务升级+专属客服",
            "tactics": ["安排专属客服", "赠送增值服务", "优先处理投诉"],
            "priority": "high"
        },
        "competitor": {
            "strategy": "差异化价值强调",
            "tactics": ["强调产品差异化", "展示用户好评", "提供试用体验"],
            "priority": "medium"
        },
        "product": {
            "strategy": "产品优化+功能引导",
            "tactics": ["介绍新功能", "提供使用培训", "收集改进建议"],
            "priority": "medium"
        },
        "inactive": {
            "strategy": "激活营销+权益唤醒",
            "tactics": ["发送激活短信", "限时权益提醒", "个性化内容推荐"],
            "priority": "low"
        },
        "lifestyle": {
            "strategy": "场景适配+产品推荐",
            "tactics": ["了解新需求", "推荐适配产品", "提供上门服务"],
            "priority": "medium"
        },
    }
    
    def __init__(self, api_mode: bool = False):
        """
        初始化流失召回引擎
        
        Args:
            api_mode: 是否为API模式（减少日志输出）
        """
        self.api_mode = api_mode
        self._log("初始化流失客户召回引擎 v%s" % self.VERSION)
    
    def _log(self, msg: str):
        """日志输出"""
        if not self.api_mode:
            print(msg)
    
    def analyze_churn_risk(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析客户流失风险
        
        Args:
            customer_data: 客户数据 {
                "customer_id": str,
                "name": str,
                "last_purchase_days": int,  # 最近购买距今天数
                "purchase_frequency": int,   # 月均购买次数
                "avg_order_amount": float,   # 平均订单金额
                "login_interval_days": int,  # 平均登录间隔
                "product_active_days": int,   # 产品活跃天数
                "service_complaints": int,    # 投诉次数
                "total_orders": int,          # 总订单数
                "member_level": str,          # 会员等级
            }
        
        Returns:
            流失风险分析结果
        """
        # 计算RFM得分
        r_score = self._calculate_r_score(customer_data.get("last_purchase_days", 0))
        f_score = self._calculate_f_score(customer_data.get("purchase_frequency", 0))
        m_score = self._calculate_m_score(customer_data.get("avg_order_amount", 0))
        
        # 综合流失风险评分 (0-100, 越高流失风险越大)
        risk_score = self._calculate_risk_score(
            r_score, f_score, m_score,
            customer_data.get("login_interval_days", 0),
            customer_data.get("product_active_days", 0),
            customer_data.get("service_complaints", 0)
        )
        
        # 风险等级
        if risk_score >= 70:
            risk_level = "high"
            risk_label = "🔴 高风险"
        elif risk_score >= 40:
            risk_level = "medium"
            risk_label = "🟡 中风险"
        else:
            risk_level = "low"
            risk_label = "🟢 低风险"
        
        # 推测流失原因
        churn_reasons = self._infer_churn_reasons(customer_data, r_score, f_score, m_score)
        
        return {
            "customer_id": customer_data.get("customer_id"),
            "name": customer_data.get("name", "客户"),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_label": risk_label,
            "rfm_scores": {"R": r_score, "F": f_score, "M": m_score},
            "churn_reasons": churn_reasons,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _calculate_r_score(self, last_purchase_days: int) -> int:
        """计算R得分 (最近购买, 越高风险越大)"""
        if last_purchase_days > 90:
            return 5
        elif last_purchase_days > 60:
            return 4
        elif last_purchase_days > 30:
            return 3
        elif last_purchase_days > 14:
            return 2
        elif last_purchase_days > 7:
            return 1
        return 0
    
    def _calculate_f_score(self, purchase_frequency: int) -> int:
        """计算F得分 (购买频率, 越低风险越大)"""
        if purchase_frequency == 0:
            return 5
        elif purchase_frequency <= 1:
            return 4
        elif purchase_frequency <= 3:
            return 3
        elif purchase_frequency <= 6:
            return 2
        return 1
    
    def _calculate_m_score(self, avg_order_amount: float) -> int:
        """计算M得分 (消费金额, 越低风险越大)"""
        if avg_order_amount < 100:
            return 5
        elif avg_order_amount < 500:
            return 4
        elif avg_order_amount < 1000:
            return 3
        elif avg_order_amount < 5000:
            return 2
        return 1
    
    def _calculate_risk_score(self, r: int, f: int, m: int, 
                              login_interval: int, active_days: int,
                              complaints: int) -> float:
        """计算综合流失风险评分"""
        # RFM权重
        rfm_score = (r * 0.4 + f * 0.3 + m * 0.3) * 10
        
        # 登录间隔惩罚
        login_penalty = min(20, login_interval * 0.5) if login_interval > 7 else 0
        
        # 活跃度奖励
        active_bonus = max(0, (30 - active_days) * 0.3) if active_days < 30 else 0
        
        # 投诉惩罚
        complaint_penalty = complaints * 8
        
        risk_score = rfm_score + login_penalty + active_bonus + complaint_penalty
        return min(100, max(0, risk_score))
    
    def _infer_churn_reasons(self, customer_data: Dict, r: int, f: int, m: int) -> List[Dict]:
        """推测流失原因"""
        reasons = []
        
        if r >= 4:
            reasons.append({
                "type": "inactive",
                "reason": "长期未购买",
                "confidence": min(1.0, 0.5 + (r - 3) * 0.15)
            })
        
        if f >= 4:
            reasons.append({
                "type": "lifestyle",
                "reason": "购买频率大幅下降",
                "confidence": min(1.0, 0.4 + (f - 3) * 0.15)
            })
        
        if m >= 4:
            reasons.append({
                "type": "price",
                "reason": "消费能力下降或转移",
                "confidence": min(1.0, 0.4 + (m - 3) * 0.15)
            })
        
        if customer_data.get("service_complaints", 0) >= 2:
            reasons.append({
                "type": "service",
                "reason": "多次投诉未满意解决",
                "confidence": 0.8
            })
        
        # 默认添加inactive作为兜底
        if not reasons:
            reasons.append({
                "type": "inactive",
                "reason": "活跃度下降",
                "confidence": 0.5
            })
        
        # 按置信度排序
        reasons.sort(key=lambda x: x["confidence"], reverse=True)
        return reasons[:3]  # 最多返回3个原因
    
    def generate_recall_script(self, customer_data: Dict, risk_result: Dict,
                              preferred_channel: str = "企微") -> Dict[str, Any]:
        """
        生成召回话术
        
        Args:
            customer_data: 客户基本信息
            risk_result: 流失风险分析结果
            preferred_channel: 偏好触达渠道
        
        Returns:
            个性化召回话术和策略
        """
        name = customer_data.get("name", "客户")
        member_level = customer_data.get("member_level", "普通会员")
        top_reason = risk_result["churn_reasons"][0] if risk_result["churn_reasons"] else {}
        reason_type = top_reason.get("type", "inactive")
        
        # 获取对应策略
        strategy = self.RECALL_STRATEGIES.get(reason_type, self.RECALL_STRATEGIES["inactive"])
        
        # 生成话术
        scripts = self._generate_scripts(name, reason_type, member_level)
        
        # 触达建议
        outreach = self._generate_outreach_suggestion(reason_type, preferred_channel)
        
        return {
            "customer_id": customer_data.get("customer_id"),
            "name": name,
            "risk_level": risk_result["risk_label"],
            "primary_reason": top_reason.get("reason", "活跃度下降"),
            "strategy": strategy["strategy"],
            "tactics": strategy["tactics"],
            "scripts": scripts,
            "outreach": outreach,
            "priority": strategy["priority"],
            "generate_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _generate_scripts(self, name: str, reason_type: str, 
                          member_level: str) -> Dict[str, str]:
        """生成各类召回话术"""
        templates = {
            "price": {
                "title": "💰 专属优惠唤醒",
                "opening": f"亲爱的{name}，感谢您一直以来的支持！",
                "body": "我们为您准备了专属限时优惠，可以享受X%的额外折扣。",
                "cta": "点击领取专属优惠，有效期仅限本周！",
                "closing": "期待您的回归，有任何问题可随时联系我~"
            },
            "service": {
                "title": "🌟 服务升级通知",
                "opening": f"亲爱的{name}，您的反馈我们一直记在心里。",
                "body": "为了给您更好的体验，我们已全面升级服务，并为您安排了专属客服。",
                "cta": "回复1即可享受VIP专属服务通道。",
                "closing": "您的满意是我们最大的追求！"
            },
            "competitor": {
                "title": "🏆 感谢您一路相伴",
                "opening": f"亲爱的{name}，您的支持对我们至关重要。",
                "body": "我们的产品又有新升级，新增了多项独家功能，正是您需要的！",
                "cta": "现在回访即送精美礼品一份。",
                "closing": "期待与您继续同行~"
            },
            "product": {
                "title": "✨ 产品新体验",
                "opening": f"亲爱的{name}，我们的产品又有新功能啦！",
                "body": "根据您的使用习惯，我们为您推荐这些新功能，一定会让您惊喜。",
                "cta": "现在体验可获得专属新手礼包。",
                "closing": "期待您的反馈！"
            },
            "inactive": {
                "title": "👋 我们想您了",
                "opening": f"亲爱的{name}，好久不见！",
                "body": "您有一笔待享权益即将过期，我们特意为您保留。",
                "cta": "点击查看您的专属权益，回复本消息即可激活。",
                "closing": "期待您的回归~"
            },
            "lifestyle": {
                "title": "🔄 为您准备了新方案",
                "opening": f"亲爱的{name}，您的需求我们一直关注。",
                "body": "根据您的情况，我们特别调整了产品方案，更适合您现在的生活。",
                "cta": "回复'新方案'即可查看详情。",
                "closing": "祝您生活愉快！"
            },
        }
        
        template = templates.get(reason_type, templates["inactive"])
        
        return {
            "title": template["title"],
            "opening": template["opening"],
            "body": template["body"],
            "cta": template["cta"],
            "closing": template["closing"],
            "full_script": f"""{template['opening']}

{template['body']}

{template['cta']}

{template['closing']}

— 您专属的客户经理"""
        }
    
    def _generate_outreach_suggestion(self, reason_type: str, 
                                       channel: str) -> Dict[str, Any]:
        """生成触达建议"""
        suggestions = {
            "price": {
                "channel": "短信+企微",
                "timing": "工作日10:00-11:30, 14:30-16:00",
                "frequency": "连续3天，每天1次",
                "script_tone": "温暖实惠型"
            },
            "service": {
                "channel": "电话+企微",
                "timing": "工作日14:00-17:00",
                "frequency": "1次/天，连续5天",
                "script_tone": "真诚道歉+服务承诺型"
            },
            "competitor": {
                "channel": "电话+线下活动",
                "timing": "周末10:00-12:00",
                "frequency": "1次，邀约线下体验",
                "script_tone": "价值强调型"
            },
            "product": {
                "channel": "企微+APP推送",
                "timing": "任意时间",
                "frequency": "3次，每次间隔2天",
                "script_tone": "功能介绍型"
            },
            "inactive": {
                "channel": "短信+APP推送",
                "timing": "周末9:00-10:00",
                "frequency": "1次/周，连续2周",
                "script_tone": "权益唤醒型"
            },
            "lifestyle": {
                "channel": "电话+上门拜访",
                "timing": "工作日15:00-18:00",
                "frequency": "1次/周",
                "script_tone": "关怀询问型"
            }
        }
        
        return suggestions.get(reason_type, suggestions["inactive"])
    
    def batch_analyze(self, customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量分析客户流失风险
        
        Args:
            customers: 客户数据列表
        
        Returns:
            批量分析结果
        """
        results = []
        for customer in customers:
            risk_result = self.analyze_churn_risk(customer)
            results.append(risk_result)
        
        # 按风险评分排序
        results.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return results
    
    def generate_batch_recall(self, customers: List[Dict[str, Any]],
                             high_priority_only: bool = True) -> List[Dict[str, Any]]:
        """
        批量生成召回方案
        
        Args:
            customers: 客户数据列表
            high_priority_only: 是否仅返回高优先级客户
        
        Returns:
            批量召回方案
        """
        # 先批量分析
        analyses = self.batch_analyze(customers)
        
        recalls = []
        for analysis in analyses:
            if high_priority_only and analysis["risk_level"] != "high":
                continue
            
            # 找到对应的客户数据
            customer_data = next(
                (c for c in customers if c.get("customer_id") == analysis.get("customer_id")),
                {"customer_id": analysis.get("customer_id"), "name": analysis.get("name")}
            )
            
            recall = self.generate_recall_script(customer_data, analysis)
            recalls.append(recall)
        
        return recalls
    
    def format_text(self, result: Dict[str, Any], format_type: str = "recall") -> str:
        """格式化输出为文本"""
        if format_type == "analysis":
            return self._format_analysis_text(result)
        elif format_type == "recall":
            return self._format_recall_text(result)
        else:
            return self._format_recall_text(result)
    
    def _format_analysis_text(self, result: Dict) -> str:
        """格式化分析结果"""
        lines = [
            f"📊 **客户流失风险分析报告**",
            f"",
            f"👤 客户：{result['name']} ({result['customer_id']})",
            f"⏰ 分析时间：{result['analysis_time']}",
            f"",
            f"{'='*30}",
            f"",
            f"🎯 **风险等级：{result['risk_label']}**",
            f"📈 风险评分：{result['risk_score']:.1f}/100",
            f"",
            f"📉 **RFM得分**",
            f"   R（最近购买）：{result['rfm_scores']['R']}/5 {'⚠️' if result['rfm_scores']['R'] >= 3 else '✅'}",
            f"   F（购买频率）：{result['rfm_scores']['F']}/5 {'⚠️' if result['rfm_scores']['F'] >= 3 else '✅'}",
            f"   M（消费金额）：{result['rfm_scores']['M']}/5 {'⚠️' if result['rfm_scores']['M'] >= 3 else '✅'}",
            f"",
            f"🔍 **流失原因分析**",
        ]
        
        for i, reason in enumerate(result['churn_reasons'], 1):
            reason_info = self.CHURN_REASONS.get(reason['type'], {"name": reason['type'], "icon": "❓"})
            lines.append(f"   {i}. {reason_info['icon']} {reason_info['name']}")
            lines.append(f"      - {reason['reason']}")
            lines.append(f"      - 置信度：{reason['confidence']*100:.0f}%")
        
        return '\n'.join(lines)
    
    def _format_recall_text(self, result: Dict) -> str:
        """格式化召回方案"""
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(result['priority'], "⚪")
        
        lines = [
            f"📞 **客户召回方案**",
            f"",
            f"👤 客户：{result['name']} ({result['customer_id']})",
            f"⚠️ 风险等级：{result['risk_level']}",
            f"🔍 主要原因：{result['primary_reason']}",
            f"🎯 召回策略：{result['strategy']}",
            f"",
            f"{'='*30}",
            f"",
            f"📝 **个性化话术**",
            f"",
            f"{result['scripts']['full_script']}",
            f"",
            f"{'='*30}",
            f"",
            f"📱 **触达建议**",
            f"   渠道：{result['outreach']['channel']}",
            f"   时间：{result['outreach']['timing']}",
            f"   频次：{result['outreach']['frequency']}",
            f"   风格：{result['outreach']['script_tone']}",
            f"",
            f"💡 **具体措施**",
        ]
        
        for i, tactic in enumerate(result['tactics'], 1):
            lines.append(f"   {i}. {tactic}")
        
        lines.extend([
            f"",
            f"{'='*30}",
            f"⏰ 生成时间：{result['generate_time']}",
            f"🎯 优先级：{priority_emoji} {result['priority'].upper()}",
        ])
        
        return '\n'.join(lines)
    
    def format_json(self, result: Dict) -> str:
        """格式化输出为JSON"""
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    def format_markdown(self, result: Dict, format_type: str = "recall") -> str:
        """格式化输出为Markdown"""
        return self.format_text(result, format_type)


# 模拟客户数据生成器（用于测试）
def generate_mock_customer(customer_id: str = None, name: str = None) -> Dict[str, Any]:
    """生成模拟客户数据"""
    names = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十"]
    member_levels = ["普通会员", "银卡会员", "金卡会员", "白金会员", "钻石会员"]
    
    return {
        "customer_id": customer_id or f"C{ random.randint(10000, 99999)}",
        "name": name or random.choice(names),
        "last_purchase_days": random.choice([3, 7, 15, 30, 45, 60, 90, 120]),
        "purchase_frequency": random.choice([0, 0.5, 1, 2, 3, 5, 8, 12]),
        "avg_order_amount": random.choice([50, 100, 200, 500, 1000, 2000, 5000]),
        "login_interval_days": random.choice([1, 2, 3, 5, 7, 14, 30, 60]),
        "product_active_days": random.choice([0, 3, 7, 14, 30, 60]),
        "service_complaints": random.choice([0, 0, 0, 1, 1, 2, 3]),
        "total_orders": random.randint(0, 200),
        "member_level": random.choice(member_levels)
    }


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("🦞 流失客户召回引擎 v1.0")
    print("=" * 50)
    print()
    
    engine = ChurnRecallEngine()
    
    # 演示单个客户分析
    print("📊 客户流失风险分析演示")
    print("-" * 40)
    
    customer = generate_mock_customer("C88888", "张伟")
    print(f"客户：{customer['name']} (ID: {customer['customer_id']})")
    print(f"会员等级：{customer['member_level']}")
    print(f"最近购买：{customer['last_purchase_days']}天前")
    print(f"月均购买：{customer['purchase_frequency']}次")
    print(f"平均金额：¥{customer['avg_order_amount']:.2f}")
    print()
    
    # 风险分析
    risk_result = engine.analyze_churn_risk(customer)
    print(engine.format_text(risk_result, "analysis"))
    print()
    
    # 召回话术
    recall_result = engine.generate_recall_script(customer, risk_result)
    print(engine.format_text(recall_result, "recall"))
    print()
    
    # 批量分析演示
    print("=" * 50)
    print("📊 批量客户流失风险分析")
    print("-" * 40)
    
    customers = [generate_mock_customer() for _ in range(5)]
    batch_results = engine.batch_analyze(customers)
    
    print(f"分析了 {len(batch_results)} 位客户")
    print()
    
    high_risk = [r for r in batch_results if r["risk_level"] == "high"]
    medium_risk = [r for r in batch_results if r["risk_level"] == "medium"]
    low_risk = [r for r in batch_results if r["risk_level"] == "low"]
    
    print(f"🔴 高风险：{len(high_risk)}人")
    print(f"🟡 中风险：{len(medium_risk)}人")
    print(f"🟢 低风险：{len(low_risk)}人")
    print()
    
    # 批量召回
    recalls = engine.generate_batch_recall(customers, high_priority_only=True)
    if recalls:
        print(f"生成了 {len(recalls)} 份高优先级召回方案")


if __name__ == "__main__":
    main()
