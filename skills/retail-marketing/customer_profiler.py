#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户画像构建模块
多维度标签体系，360°客户视图
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class RiskPreference(Enum):
    """风险偏好"""
    CONSERVATIVE = "保守型"
    STEADY = "稳健型"
    BALANCED = "平衡型"
    AGGRESSIVE = "进取型"
    RADICAL = "激进型"


class LifeStage(Enum):
    """人生阶段"""
    SINGLE = "单身期"
    NEWLYWED = "新婚期"
    PARENTING = "育儿期"
    MATURE = "成熟期"
    RETIREMENT = "退休期"


@dataclass
class CustomerProfile:
    """客户画像"""
    customer_id: str
    name: str
    age: int
    gender: str
    occupation: str
    income_level: str  # 高/中/低
    aum: float  # 资产管理规模
    risk_preference: RiskPreference
    life_stage: LifeStage
    investment_experience: str  # 丰富/一般/ novice
    
    # 行为标签
    transaction_frequency: str  # 高/中/低
    channel_preference: List[str] = field(default_factory=list)  # APP/网银/柜台/电话
    product_holdings: List[str] = field(default_factory=list)
    
    # 计算标签
    tags: List[str] = field(default_factory=list)
    score: float = 0.0  # 客户价值评分


class CustomerProfiler:
    """客户画像构建器"""

    def __init__(self):
        self.profiles = {}

    def build_profile(self, customer_id: str, name: str, age: int,
                      gender: str, occupation: str, income_level: str,
                      aum: float, risk_preference: str,
                      investment_experience: str = "一般",
                      transaction_frequency: str = "中",
                      channel_preference: Optional[List[str]] = None,
                      product_holdings: Optional[List[str]] = None) -> CustomerProfile:
        """构建客户画像"""
        
        # 确定人生阶段
        life_stage = self._determine_life_stage(age)
        
        # 解析风险偏好
        risk = self._parse_risk_preference(risk_preference)
        
        # 生成标签
        tags = self._generate_tags(
            age, aum, risk, life_stage, 
            investment_experience, transaction_frequency
        )
        
        # 计算客户价值评分
        score = self._calculate_customer_value(aum, transaction_frequency, age)
        
        profile = CustomerProfile(
            customer_id=customer_id,
            name=name,
            age=age,
            gender=gender,
            occupation=occupation,
            income_level=income_level,
            aum=aum,
            risk_preference=risk,
            life_stage=life_stage,
            investment_experience=investment_experience,
            transaction_frequency=transaction_frequency,
            channel_preference=channel_preference or ["APP"],
            product_holdings=product_holdings or [],
            tags=tags,
            score=score
        )
        
        self.profiles[customer_id] = profile
        return profile

    def _determine_life_stage(self, age: int) -> LifeStage:
        """根据年龄确定人生阶段"""
        if age < 25:
            return LifeStage.SINGLE
        elif age < 35:
            return LifeStage.NEWLYWED
        elif age < 50:
            return LifeStage.PARENTING
        elif age < 60:
            return LifeStage.MATURE
        else:
            return LifeStage.RETIREMENT

    def _parse_risk_preference(self, preference: str) -> RiskPreference:
        """解析风险偏好"""
        mapping = {
            "保守": RiskPreference.CONSERVATIVE,
            "稳健": RiskPreference.STEADY,
            "平衡": RiskPreference.BALANCED,
            "进取": RiskPreference.AGGRESSIVE,
            "激进": RiskPreference.RADICAL
        }
        return mapping.get(preference, RiskPreference.STEADY)

    def _generate_tags(self, age: int, aum: float, risk: RiskPreference,
                       life_stage: LifeStage, experience: str,
                       frequency: str) -> List[str]:
        """生成客户标签"""
        tags = []
        
        # AUM标签
        if aum >= 1000000:
            tags.append("高净值客户")
        elif aum >= 500000:
            tags.append("潜力客户")
        elif aum >= 100000:
            tags.append("普通客户")
        else:
            tags.append("基础客户")
        
        # 年龄标签
        if age < 30:
            tags.append("年轻客户")
        elif age > 55:
            tags.append("年长客户")
        
        # 风险偏好标签
        if risk in [RiskPreference.AGGRESSIVE, RiskPreference.RADICAL]:
            tags.append("高风险承受")
        elif risk == RiskPreference.CONSERVATIVE:
            tags.append("低风险偏好")
        
        # 活跃度标签
        if frequency == "高":
            tags.append("活跃客户")
        elif frequency == "低":
            tags.append("沉睡客户")
        
        # 人生阶段标签
        tags.append(life_stage.value)
        
        # 经验标签
        if experience == "丰富":
            tags.append("资深投资者")
        elif experience == " novice":
            tags.append("投资新手")
        
        return tags

    def _calculate_customer_value(self, aum: float, frequency: str, age: int) -> float:
        """计算客户价值评分 (0-100)"""
        score = 0.0
        
        # AUM得分 (最高60分)
        if aum >= 5000000:
            score += 60
        elif aum >= 1000000:
            score += 50
        elif aum >= 500000:
            score += 40
        elif aum >= 100000:
            score += 25
        else:
            score += 10
        
        # 活跃度得分 (最高20分)
        freq_scores = {"高": 20, "中": 12, "低": 5}
        score += freq_scores.get(frequency, 10)
        
        # 年龄得分 (潜力评估，最高20分)
        if 30 <= age <= 45:
            score += 20  # 黄金年龄段
        elif 25 <= age < 30 or 45 < age <= 55:
            score += 15
        else:
            score += 10
        
        return min(100, score)

    def get_profile_summary(self, customer_id: str) -> Dict:
        """获取画像摘要"""
        profile = self.profiles.get(customer_id)
        if not profile:
            return {}
        
        return {
            "客户ID": profile.customer_id,
            "姓名": profile.name,
            "年龄": profile.age,
            "性别": profile.gender,
            "职业": profile.occupation,
            "收入水平": profile.income_level,
            "AUM": f"{profile.aum:,.0f} 元",
            "风险偏好": profile.risk_preference.value,
            "人生阶段": profile.life_stage.value,
            "投资经验": profile.investment_experience,
            "交易频率": profile.transaction_frequency,
            "偏好渠道": ", ".join(profile.channel_preference),
            "持有产品": ", ".join(profile.product_holdings) if profile.product_holdings else "无",
            "客户标签": ", ".join(profile.tags),
            "价值评分": f"{profile.score:.1f} 分"
        }
