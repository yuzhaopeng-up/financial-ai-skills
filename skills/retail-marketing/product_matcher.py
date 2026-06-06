#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品匹配引擎
风险适配、需求匹配、收益预期匹配
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class ProductType(Enum):
    """产品类型"""
    DEPOSIT = "存款"
    WEALTH = "理财"
    FUND = "基金"
    INSURANCE = "保险"
    TRUST = "信托"
    BOND = "债券"
    STOCK = "股票"
    STRUCTURED = "结构性存款"


class RiskLevel(Enum):
    """产品风险等级"""
    R1 = ("低风险", 1)
    R2 = ("中低风险", 2)
    R3 = ("中风险", 3)
    R4 = ("中高风险", 4)
    R5 = ("高风险", 5)
    
    def __init__(self, label, level):
        self.label = label
        self.level = level


@dataclass
class FinancialProduct:
    """金融产品"""
    product_id: str
    name: str
    product_type: ProductType
    risk_level: RiskLevel
    min_investment: float
    expected_return: float  # 预期收益率
    duration: str  # 期限
    liquidity: str  # 流动性：高/中/低
    features: List[str] = field(default_factory=list)
    target_customers: List[str] = field(default_factory=list)


@dataclass
class ProductRecommendation:
    """产品推荐结果"""
    product: FinancialProduct
    match_score: float  # 匹配度 0-100
    match_reasons: List[str]
    risk_warning: str
    suggested_allocation: float  # 建议配置比例


class ProductMatcher:
    """产品匹配引擎"""

    def __init__(self):
        self.products = self._init_product_database()

    def _init_product_database(self) -> List[FinancialProduct]:
        """初始化产品库"""
        return [
            FinancialProduct(
                product_id="P001",
                name="活期存款",
                product_type=ProductType.DEPOSIT,
                risk_level=RiskLevel.R1,
                min_investment=0,
                expected_return=0.25,
                duration="活期",
                liquidity="高",
                features=["随时存取", "本金保障"],
                target_customers=["保守型", "流动性需求高"]
            ),
            FinancialProduct(
                product_id="P002",
                name="大额存单",
                product_type=ProductType.DEPOSIT,
                risk_level=RiskLevel.R1,
                min_investment=200000,
                expected_return=2.5,
                duration="3年",
                liquidity="中",
                features=["保本保息", "利率较高"],
                target_customers=["稳健型", "大额资金"]
            ),
            FinancialProduct(
                product_id="P003",
                name="稳健理财",
                product_type=ProductType.WEALTH,
                risk_level=RiskLevel.R2,
                min_investment=10000,
                expected_return=3.5,
                duration="1年",
                liquidity="中",
                features=["低风险", "收益稳定"],
                target_customers=["稳健型", "平衡型"]
            ),
            FinancialProduct(
                product_id="P004",
                name="债券基金",
                product_type=ProductType.FUND,
                risk_level=RiskLevel.R2,
                min_investment=1000,
                expected_return=4.0,
                duration="灵活",
                liquidity="高",
                features=["分散投资", "专业管理"],
                target_customers=["稳健型", "中长期投资"]
            ),
            FinancialProduct(
                product_id="P005",
                name="混合基金",
                product_type=ProductType.FUND,
                risk_level=RiskLevel.R3,
                min_investment=1000,
                expected_return=6.0,
                duration="灵活",
                liquidity="高",
                features=["股债平衡", "收益潜力"],
                target_customers=["平衡型", "能承受波动"]
            ),
            FinancialProduct(
                product_id="P006",
                name="指数基金",
                product_type=ProductType.FUND,
                risk_level=RiskLevel.R3,
                min_investment=1000,
                expected_return=8.0,
                duration="长期",
                liquidity="高",
                features=["跟踪指数", "费用低廉"],
                target_customers=["平衡型", "长期投资者"]
            ),
            FinancialProduct(
                product_id="P007",
                name="股票基金",
                product_type=ProductType.FUND,
                risk_level=RiskLevel.R4,
                min_investment=1000,
                expected_return=12.0,
                duration="长期",
                liquidity="高",
                features=["高收益潜力", "波动较大"],
                target_customers=["进取型", "激进型"]
            ),
            FinancialProduct(
                product_id="P008",
                name="养老保险",
                product_type=ProductType.INSURANCE,
                risk_level=RiskLevel.R2,
                min_investment=5000,
                expected_return=3.8,
                duration="长期",
                liquidity="低",
                features=["养老保障", "税收优惠"],
                target_customers=["退休期", "长期规划"]
            ),
            FinancialProduct(
                product_id="P009",
                name="信托计划",
                product_type=ProductType.TRUST,
                risk_level=RiskLevel.R3,
                min_investment=1000000,
                expected_return=7.0,
                duration="2年",
                liquidity="低",
                features=["高收益", "门槛较高"],
                target_customers=["高净值", "合格投资者"]
            ),
            FinancialProduct(
                product_id="P010",
                name="结构性存款",
                product_type=ProductType.STRUCTURED,
                risk_level=RiskLevel.R2,
                min_investment=50000,
                expected_return=4.5,
                duration="1年",
                liquidity="中",
                features=["保本浮动", "挂钩标的"],
                target_customers=["稳健型", "追求收益"]
            )
        ]

    def match_products(self, risk_preference: str, aum: float,
                       age: int, investment_horizon: str,
                       liquidity_need: str,
                       existing_products: Optional[List[str]] = None) -> List[ProductRecommendation]:
        """匹配产品"""
        
        # 风险偏好映射到风险等级
        risk_mapping = {
            "保守型": 1,
            "稳健型": 2,
            "平衡型": 3,
            "进取型": 4,
            "激进型": 5
        }
        customer_risk_level = risk_mapping.get(risk_preference, 2)
        
        recommendations = []
        
        for product in self.products:
            score = 0.0
            reasons = []
            
            # 1. 风险适配 (最高40分)
            product_risk = product.risk_level.level
            risk_diff = abs(product_risk - customer_risk_level)
            if risk_diff == 0:
                score += 40
                reasons.append("风险等级完全匹配")
            elif risk_diff == 1:
                score += 25
                reasons.append("风险等级基本匹配")
            elif risk_diff == 2:
                score += 10
                reasons.append("风险等级略有偏差")
            else:
                score -= 20
                reasons.append("风险等级不匹配")
            
            # 2. 资金门槛 (最高20分)
            if aum >= product.min_investment * 2:
                score += 20
                reasons.append("资金充足")
            elif aum >= product.min_investment:
                score += 15
                reasons.append("满足起投金额")
            else:
                score -= 30
                reasons.append("资金不足")
            
            # 3. 年龄适配 (最高15分)
            if age >= 60 and product.product_type in [ProductType.INSURANCE, ProductType.DEPOSIT]:
                score += 15
                reasons.append("适合退休规划")
            elif 30 <= age < 50 and product.risk_level.level >= 3:
                score += 10
                reasons.append("适合成长期投资")
            elif age < 30 and product.liquidity == "高":
                score += 10
                reasons.append("流动性好，适合年轻客户")
            
            # 4. 期限匹配 (最高15分)
            horizon_map = {"短期": 1, "中期": 2, "长期": 3}
            horizon_score = horizon_map.get(investment_horizon, 2)
            
            if product.duration == "活期" and horizon_score == 1:
                score += 15
                reasons.append("期限匹配")
            elif product.duration in ["1年", "灵活"] and horizon_score == 2:
                score += 15
                reasons.append("期限匹配")
            elif product.duration in ["2年", "3年", "长期"] and horizon_score == 3:
                score += 15
                reasons.append("期限匹配")
            
            # 5. 流动性需求 (最高10分)
            if liquidity_need == "高" and product.liquidity == "高":
                score += 10
                reasons.append("流动性满足")
            elif liquidity_need == "中" and product.liquidity in ["中", "高"]:
                score += 10
                reasons.append("流动性满足")
            elif liquidity_need == "低":
                score += 10
                reasons.append("可接受较低流动性")
            
            # 排除已持有产品
            if existing_products and product.name in existing_products:
                score -= 50
                reasons.append("已持有该产品")
            
            # 确保分数在合理范围
            score = max(0, min(100, score))
            
            if score >= 30:  # 只返回匹配度较高的
                # 生成风险警示
                if product_risk > customer_risk_level:
                    risk_warning = f"⚠️ 产品风险({product.risk_level.label})高于您的偏好({risk_preference})"
                elif product_risk < customer_risk_level:
                    risk_warning = f"💡 产品风险({product.risk_level.label})低于您的偏好，可能收益有限"
                else:
                    risk_warning = "✅ 风险等级匹配"
                
                # 建议配置比例
                if score >= 80:
                    allocation = 0.3
                elif score >= 60:
                    allocation = 0.2
                elif score >= 40:
                    allocation = 0.1
                else:
                    allocation = 0.05
                
                recommendations.append(ProductRecommendation(
                    product=product,
                    match_score=score,
                    match_reasons=reasons,
                    risk_warning=risk_warning,
                    suggested_allocation=allocation
                ))
        
        # 按匹配度排序
        recommendations.sort(key=lambda x: x.match_score, reverse=True)
        
        return recommendations[:5]  # 返回前5个推荐

    def get_product_by_id(self, product_id: str) -> Optional[FinancialProduct]:
        """根据ID获取产品"""
        for product in self.products:
            if product.product_id == product_id:
                return product
        return None
