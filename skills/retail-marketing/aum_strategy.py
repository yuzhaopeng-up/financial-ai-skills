#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUM提升策略模块
资产提升路径、交叉销售、向上销售
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class StrategyType(Enum):
    """策略类型"""
    CROSS_SELL = "交叉销售"
    UP_SELL = "向上销售"
    ACTIVATION = "客户激活"
    RETENTION = "客户留存"
    REFERRAL = "客户转介"


@dataclass
class AUMStrategy:
    """AUM提升策略"""
    strategy_type: StrategyType
    strategy_name: str
    description: str
    target_aum_increase: float  # 目标AUM提升金额
    expected_conversion_rate: float  # 预期转化率
    actions: List[str]
    timeline: str  # 执行周期
    success_metrics: List[str]


@dataclass
class AUMPath:
    """AUM提升路径"""
    current_level: str
    target_level: str
    gap_amount: float
    strategies: List[AUMStrategy]
    estimated_time: str
    success_probability: float


class AUMGrowthStrategy:
    """AUM提升策略引擎"""

    def __init__(self):
        self.level_thresholds = {
            "基础客户": 0,
            "普通客户": 100000,
            "潜力客户": 500000,
            "白金客户": 1000000,
            "钻石客户": 5000000
        }

    def determine_next_level(self, current_aum: float) -> str:
        """确定下一等级"""
        levels = list(self.level_thresholds.items())
        for i, (level, threshold) in enumerate(levels):
            if current_aum < threshold:
                return level
            if i + 1 < len(levels):
                next_level, next_threshold = levels[i + 1]
                if current_aum < next_threshold:
                    return next_level
        return "钻石客户"

    def calculate_gap(self, current_aum: float, target_level: str) -> float:
        """计算AUM缺口"""
        target_threshold = self.level_thresholds.get(target_level, 0)
        return max(0, target_threshold - current_aum)

    def generate_cross_sell_strategy(self, current_products: List[str],
                                      risk_preference: str,
                                      aum: float) -> AUMStrategy:
        """生成交叉销售策略"""
        
        # 分析产品缺口
        all_product_types = ["存款", "理财", "基金", "保险", "信托"]
        held_types = set()
        for product in current_products:
            for ptype in all_product_types:
                if ptype in product:
                    held_types.add(ptype)
        
        missing_types = set(all_product_types) - held_types
        
        actions = []
        if "理财" in missing_types:
            actions.append("推荐稳健型理财产品")
        if "基金" in missing_types:
            actions.append("推荐债券基金或指数基金")
        if "保险" in missing_types:
            actions.append("推荐养老保险或重疾险")
        if "信托" in missing_types and aum >= 1000000:
            actions.append("推荐信托计划（高净值专属）")
        
        if not actions:
            actions.append("推荐产品组合优化方案")
        
        return AUMStrategy(
            strategy_type=StrategyType.CROSS_SELL,
            strategy_name="产品组合完善",
            description=f"补充缺失产品类型：{', '.join(missing_types) if missing_types else '优化现有组合'}",
            target_aum_increase=aum * 0.2,
            expected_conversion_rate=0.3,
            actions=actions,
            timeline="3个月",
            success_metrics=["新产品开户数", "新增AUM", "产品覆盖率"]
        )

    def generate_up_sell_strategy(self, current_aum: float,
                                   risk_preference: str,
                                   age: int) -> AUMStrategy:
        """生成向上销售策略"""
        
        actions = []
        
        if current_aum >= 1000000:
            actions.extend([
                "推荐大额存单（利率上浮）",
                "推荐专属理财产品",
                "推荐家族信托服务"
            ])
        elif current_aum >= 500000:
            actions.extend([
                "推荐结构性存款",
                "推荐混合型基金",
                "推荐养老规划方案"
            ])
        elif current_aum >= 100000:
            actions.extend([
                "推荐定期理财",
                "推荐债券基金",
                "推荐基金定投计划"
            ])
        else:
            actions.extend([
                "推荐零钱理财",
                "推荐基金定投（低门槛）",
                "推荐储蓄计划"
            ])
        
        # 根据年龄调整
        if age >= 55:
            actions.append("推荐养老型保险产品")
        elif age <= 35:
            actions.append("推荐成长型基金组合")
        
        return AUMStrategy(
            strategy_type=StrategyType.UP_SELL,
            strategy_name="产品升级",
            description="引导客户升级至更高收益/更高门槛产品",
            target_aum_increase=current_aum * 0.3,
            expected_conversion_rate=0.25,
            actions=actions,
            timeline="6个月",
            success_metrics=["产品升级率", "AUM增长率", "客户满意度"]
        )

    def generate_activation_strategy(self, last_transaction_days: int,
                                      current_aum: float) -> Optional[AUMStrategy]:
        """生成客户激活策略"""
        
        if last_transaction_days <= 30:
            return None  # 客户活跃，不需要激活
        
        actions = []
        
        if last_transaction_days > 180:
            actions.extend([
                "🚨 紧急：安排客户经理电话回访",
                "发送专属关怀短信",
                "提供限时优惠活动"
            ])
        elif last_transaction_days > 90:
            actions.extend([
                "发送产品更新资讯",
                "邀请参加线上活动",
                "推送个性化产品推荐"
            ])
        else:
            actions.extend([
                "发送市场分析报告",
                "推送热门产品信息"
            ])
        
        return AUMStrategy(
            strategy_type=StrategyType.ACTIVATION,
            strategy_name="客户激活",
            description=f"客户已{last_transaction_days}天未交易，需激活",
            target_aum_increase=current_aum * 0.1,
            expected_conversion_rate=0.2,
            actions=actions,
            timeline="1个月",
            success_metrics=["交易激活率", "回访成功率", "AUM回流"]
        )

    def generate_retention_strategy(self, aum_trend: str,
                                     complaint_history: int) -> Optional[AUMStrategy]:
        """生成客户留存策略"""
        
        if aum_trend == "上升" and complaint_history == 0:
            return None  # 客户健康，不需要特别留存
        
        actions = []
        
        if aum_trend == "下降":
            actions.extend([
                "🔴 紧急：了解资金流出原因",
                "提供资产保全方案",
                "安排高级客户经理对接"
            ])
        
        if complaint_history > 0:
            actions.extend([
                f"处理历史投诉（{complaint_history}次）",
                "提供补偿方案",
                "建立专属服务通道"
            ])
        
        if not actions:
            actions.append("定期客户满意度调研")
        
        return AUMStrategy(
            strategy_type=StrategyType.RETENTION,
            strategy_name="客户留存",
            description="防止客户流失，提升满意度",
            target_aum_increase=0,
            expected_conversion_rate=0.5,
            actions=actions,
            timeline="持续",
            success_metrics=["客户满意度", "流失率", "投诉解决率"]
        )

    def generate_aum_path(self, customer_id: str, current_aum: float,
                          current_products: List[str],
                          risk_preference: str,
                          age: int,
                          last_transaction_days: int,
                          aum_trend: str = "稳定",
                          complaint_history: int = 0) -> AUMPath:
        """生成AUM提升路径"""
        
        next_level = self.determine_next_level(current_aum)
        gap = self.calculate_gap(current_aum, next_level)
        
        strategies = []
        
        # 1. 交叉销售
        cross_sell = self.generate_cross_sell_strategy(
            current_products, risk_preference, current_aum
        )
        strategies.append(cross_sell)
        
        # 2. 向上销售
        up_sell = self.generate_up_sell_strategy(
            current_aum, risk_preference, age
        )
        strategies.append(up_sell)
        
        # 3. 客户激活
        activation = self.generate_activation_strategy(
            last_transaction_days, current_aum
        )
        if activation:
            strategies.append(activation)
        
        # 4. 客户留存
        retention = self.generate_retention_strategy(
            aum_trend, complaint_history
        )
        if retention:
            strategies.append(retention)
        
        # 计算成功概率
        total_target = sum(s.target_aum_increase for s in strategies)
        if gap > 0 and total_target > 0:
            probability = min(0.95, total_target / gap * 0.5)
        else:
            probability = 0.8
        
        return AUMPath(
            current_level=self._get_current_level(current_aum),
            target_level=next_level,
            gap_amount=gap,
            strategies=strategies,
            estimated_time="6-12个月",
            success_probability=round(probability, 2)
        )

    def _get_current_level(self, aum: float) -> str:
        """获取当前等级"""
        levels = list(self.level_thresholds.items())
        current_level = "基础客户"
        for level, threshold in levels:
            if aum >= threshold:
                current_level = level
        return current_level
