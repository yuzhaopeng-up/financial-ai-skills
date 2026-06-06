#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户分层运营模块
RFM模型、AUM分层、生命周期分层
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime, timedelta


class SegmentLevel(Enum):
    """客户分层等级"""
    DIAMOND = ("钻石客户", "💎", 1)
    PLATINUM = ("白金客户", "🥈", 2)
    GOLD = ("黄金客户", "🥉", 3)
    SILVER = ("白银客户", "⭐", 4)
    BRONZE = ("青铜客户", "🔹", 5)
    
    def __init__(self, label, emoji, priority):
        self.label = label
        self.emoji = emoji
        self.priority = priority


@dataclass
class RFMSegment:
    """RFM分层结果"""
    recency_score: int      # 最近交易时间 (1-5)
    frequency_score: int    # 交易频率 (1-5)
    monetary_score: int     # 交易金额 (1-5)
    rfm_score: int          # RFM总分
    segment: str            # 分层标签


@dataclass
class CustomerSegment:
    """客户分层结果"""
    customer_id: str
    aum_level: SegmentLevel
    rfm_segment: RFMSegment
    life_cycle_stage: str
    value_potential: str    # 高/中/低
    marketing_strategy: List[str] = field(default_factory=list)


class CustomerSegmentation:
    """客户分层运营器"""

    def __init__(self):
        self.segments = {}

    def segment_by_aum(self, aum: float) -> SegmentLevel:
        """基于AUM分层"""
        if aum >= 5000000:
            return SegmentLevel.DIAMOND
        elif aum >= 1000000:
            return SegmentLevel.PLATINUM
        elif aum >= 500000:
            return SegmentLevel.GOLD
        elif aum >= 100000:
            return SegmentLevel.SILVER
        else:
            return SegmentLevel.BRONZE

    def calculate_rfm(self, last_transaction_days: int,
                      transaction_count_12m: int,
                      total_amount_12m: float) -> RFMSegment:
        """计算RFM评分"""
        
        # Recency评分 (最近交易天数越少越好)
        if last_transaction_days <= 7:
            r_score = 5
        elif last_transaction_days <= 30:
            r_score = 4
        elif last_transaction_days <= 90:
            r_score = 3
        elif last_transaction_days <= 180:
            r_score = 2
        else:
            r_score = 1
        
        # Frequency评分 (12个月交易次数)
        if transaction_count_12m >= 24:
            f_score = 5
        elif transaction_count_12m >= 12:
            f_score = 4
        elif transaction_count_12m >= 6:
            f_score = 3
        elif transaction_count_12m >= 3:
            f_score = 2
        else:
            f_score = 1
        
        # Monetary评分 (12个月交易金额)
        if total_amount_12m >= 1000000:
            m_score = 5
        elif total_amount_12m >= 500000:
            m_score = 4
        elif total_amount_12m >= 100000:
            m_score = 3
        elif total_amount_12m >= 50000:
            m_score = 2
        else:
            m_score = 1
        
        rfm_score = r_score + f_score + m_score
        
        # RFM分层标签
        if rfm_score >= 13:
            segment = "重要价值客户"
        elif rfm_score >= 10:
            segment = "重要发展客户"
        elif rfm_score >= 7:
            segment = "一般价值客户"
        elif rfm_score >= 5:
            segment = "一般维持客户"
        else:
            segment = "流失风险客户"
        
        return RFMSegment(
            recency_score=r_score,
            frequency_score=f_score,
            monetary_score=m_score,
            rfm_score=rfm_score,
            segment=segment
        )

    def determine_life_cycle(self, customer_age_months: int,
                             last_transaction_days: int,
                             aum_trend: str) -> str:
        """确定客户生命周期阶段"""
        if last_transaction_days > 180:
            return "沉睡期"
        elif customer_age_months <= 3:
            return "获客期"
        elif aum_trend == "上升":
            return "成长期"
        elif aum_trend == "稳定":
            return "成熟期"
        elif aum_trend == "下降":
            return "衰退期"
        else:
            return "成熟期"

    def assess_value_potential(self, age: int, aum: float,
                                income_level: str,
                                occupation: str) -> str:
        """评估客户价值潜力"""
        potential_score = 0
        
        # 年龄潜力
        if 30 <= age <= 45:
            potential_score += 3
        elif 25 <= age < 30:
            potential_score += 2
        else:
            potential_score += 1
        
        # 收入潜力
        if income_level == "高":
            potential_score += 3
        elif income_level == "中":
            potential_score += 2
        else:
            potential_score += 1
        
        # 职业潜力
        high_potential_jobs = ["企业高管", "医生", "律师", "IT工程师", "金融从业者"]
        if occupation in high_potential_jobs:
            potential_score += 2
        
        # AUM增长空间
        if aum < 100000:
            potential_score += 2  # 增长空间大
        elif aum < 500000:
            potential_score += 1
        
        if potential_score >= 7:
            return "高"
        elif potential_score >= 5:
            return "中"
        else:
            return "低"

    def generate_strategy(self, aum_level: SegmentLevel,
                          rfm_segment: RFMSegment,
                          life_cycle: str,
                          potential: str) -> List[str]:
        """生成营销策略"""
        strategies = []
        
        # 基于AUM等级的策略
        if aum_level == SegmentLevel.DIAMOND:
            strategies.extend([
                "专属客户经理一对一服务",
                "定制化资产配置方案",
                "优先参与稀缺产品认购",
                "高端客户沙龙活动邀请"
            ])
        elif aum_level == SegmentLevel.PLATINUM:
            strategies.extend([
                "定期资产配置回顾",
                "专属理财产品推荐",
                "增值服务权益推送"
            ])
        elif aum_level == SegmentLevel.GOLD:
            strategies.extend([
                "AUM提升激励活动",
                "交叉销售产品推荐",
                "理财知识科普内容"
            ])
        else:
            strategies.extend([
                "入门级理财产品推荐",
                "线上活动参与邀请",
                "基础理财知识普及"
            ])
        
        # 基于RFM的策略
        if rfm_segment.segment == "流失风险客户":
            strategies.append("🚨 流失预警：立即安排客户回访")
            strategies.append("提供专属优惠激活交易")
        elif rfm_segment.segment == "重要价值客户":
            strategies.append("VIP专属活动邀请")
        
        # 基于生命周期的策略
        if life_cycle == "获客期":
            strategies.append("新客专属福利包推送")
        elif life_cycle == "沉睡期":
            strategies.append("沉睡客户唤醒活动")
            strategies.append("个性化关怀短信/电话")
        
        # 基于潜力的策略
        if potential == "高":
            strategies.append("重点关注，制定AUM提升计划")
        
        return list(set(strategies))  # 去重

    def full_segmentation(self, customer_id: str, aum: float,
                          last_transaction_days: int,
                          transaction_count_12m: int,
                          total_amount_12m: float,
                          customer_age_months: int,
                          aum_trend: str,
                          age: int,
                          income_level: str,
                          occupation: str) -> CustomerSegment:
        """执行完整分层"""
        
        aum_level = self.segment_by_aum(aum)
        rfm = self.calculate_rfm(last_transaction_days, transaction_count_12m, total_amount_12m)
        life_cycle = self.determine_life_cycle(customer_age_months, last_transaction_days, aum_trend)
        potential = self.assess_value_potential(age, aum, income_level, occupation)
        strategies = self.generate_strategy(aum_level, rfm, life_cycle, potential)
        
        segment = CustomerSegment(
            customer_id=customer_id,
            aum_level=aum_level,
            rfm_segment=rfm,
            life_cycle_stage=life_cycle,
            value_potential=potential,
            marketing_strategy=strategies
        )
        
        self.segments[customer_id] = segment
        return segment

    def get_segment_summary(self, customer_id: str) -> Dict:
        """获取分层摘要"""
        segment = self.segments.get(customer_id)
        if not segment:
            return {}
        
        rfm = segment.rfm_segment
        
        return {
            "客户ID": segment.customer_id,
            "AUM等级": f"{segment.aum_level.emoji} {segment.aum_level.label}",
            "RFM分层": rfm.segment,
            "RFM评分": f"R{rfm.recency_score} F{rfm.frequency_score} M{rfm.monetary_score} = {rfm.rfm_score}",
            "生命周期": segment.life_cycle_stage,
            "价值潜力": segment.value_potential,
            "营销策略": segment.marketing_strategy
        }
