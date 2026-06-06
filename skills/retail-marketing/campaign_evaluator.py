#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
营销效果评估模块
转化率、ROI、客户满意度追踪
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class CampaignMetrics:
    """营销活动指标"""
    campaign_id: str
    campaign_name: str
    start_date: str
    end_date: str
    
    # 触达指标
    total_targeted: int
    total_reached: int
    open_rate: float
    click_rate: float
    
    # 转化指标
    total_responses: int
    conversions: int
    conversion_rate: float
    
    # 业务指标
    new_aum: float
    new_customers: int
    product_sales: int
    
    # 成本指标
    total_cost: float
    cost_per_reach: float
    cost_per_conversion: float
    
    # ROI
    roi: float


@dataclass
class CustomerFeedback:
    """客户反馈"""
    customer_id: str
    satisfaction_score: int  # 1-10
    feedback_text: str
    would_recommend: bool
    timestamp: str


class CampaignEvaluator:
    """营销效果评估器"""

    def __init__(self):
        self.campaigns = {}
        self.feedbacks = []

    def create_campaign(self, campaign_id: str, campaign_name: str,
                        start_date: str, end_date: str,
                        total_targeted: int, total_cost: float) -> CampaignMetrics:
        """创建营销活动记录"""
        campaign = CampaignMetrics(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            start_date=start_date,
            end_date=end_date,
            total_targeted=total_targeted,
            total_reached=0,
            open_rate=0.0,
            click_rate=0.0,
            total_responses=0,
            conversions=0,
            conversion_rate=0.0,
            new_aum=0.0,
            new_customers=0,
            product_sales=0,
            total_cost=total_cost,
            cost_per_reach=0.0,
            cost_per_conversion=0.0,
            roi=0.0
        )
        self.campaigns[campaign_id] = campaign
        return campaign

    def update_campaign_metrics(self, campaign_id: str,
                                 total_reached: int,
                                 opens: int,
                                 clicks: int,
                                 responses: int,
                                 conversions: int,
                                 new_aum: float,
                                 new_customers: int,
                                 product_sales: int):
        """更新活动指标"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return
        
        campaign.total_reached = total_reached
        campaign.open_rate = (opens / total_reached * 100) if total_reached > 0 else 0
        campaign.click_rate = (clicks / total_reached * 100) if total_reached > 0 else 0
        campaign.total_responses = responses
        campaign.conversions = conversions
        campaign.conversion_rate = (conversions / total_reached * 100) if total_reached > 0 else 0
        campaign.new_aum = new_aum
        campaign.new_customers = new_customers
        campaign.product_sales = product_sales
        
        # 计算成本指标
        campaign.cost_per_reach = campaign.total_cost / total_reached if total_reached > 0 else 0
        campaign.cost_per_conversion = campaign.total_cost / conversions if conversions > 0 else 0
        
        # 计算ROI (假设AUM带来的年化收益为2%)
        annual_revenue = new_aum * 0.02
        campaign.roi = ((annual_revenue - campaign.total_cost) / campaign.total_cost * 100) if campaign.total_cost > 0 else 0

    def add_customer_feedback(self, customer_id: str,
                               satisfaction_score: int,
                               feedback_text: str,
                               would_recommend: bool):
        """添加客户反馈"""
        feedback = CustomerFeedback(
            customer_id=customer_id,
            satisfaction_score=satisfaction_score,
            feedback_text=feedback_text,
            would_recommend=would_recommend,
            timestamp=datetime.now().isoformat()
        )
        self.feedbacks.append(feedback)

    def get_campaign_report(self, campaign_id: str) -> Dict:
        """获取活动报告"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return {}
        
        # 计算NPS
        nps = self._calculate_nps()
        
        # 评级
        performance = self._rate_performance(campaign)
        
        return {
            "活动ID": campaign.campaign_id,
            "活动名称": campaign.campaign_name,
            "活动周期": f"{campaign.start_date} 至 {campaign.end_date}",
            "触达情况": {
                "目标人数": campaign.total_targeted,
                "实际触达": campaign.total_reached,
                "触达率": f"{(campaign.total_reached / campaign.total_targeted * 100):.1f}%",
                "打开率": f"{campaign.open_rate:.1f}%",
                "点击率": f"{campaign.click_rate:.1f}%"
            },
            "转化情况": {
                "响应数": campaign.total_responses,
                "转化数": campaign.conversions,
                "转化率": f"{campaign.conversion_rate:.2f}%"
            },
            "业务成果": {
                "新增AUM": f"{campaign.new_aum:,.0f} 元",
                "新增客户": campaign.new_customers,
                "产品销售": campaign.product_sales
            },
            "成本效益": {
                "总成本": f"{campaign.total_cost:,.0f} 元",
                "单客触达成本": f"{campaign.cost_per_reach:.2f} 元",
                "单客转化成本": f"{campaign.cost_per_conversion:.2f} 元",
                "ROI": f"{campaign.roi:.1f}%"
            },
            "客户满意度": {
                "NPS": nps,
                "评级": performance
            }
        }

    def _calculate_nps(self) -> int:
        """计算NPS (净推荐值)"""
        if not self.feedbacks:
            return 0
        
        promoters = sum(1 for f in self.feedbacks if f.satisfaction_score >= 9)
        detractors = sum(1 for f in self.feedbacks if f.satisfaction_score <= 6)
        total = len(self.feedbacks)
        
        if total == 0:
            return 0
        
        return int((promoters - detractors) / total * 100)

    def _rate_performance(self, campaign: CampaignMetrics) -> str:
        """评级活动表现"""
        score = 0
        
        # 转化率评分
        if campaign.conversion_rate >= 5:
            score += 3
        elif campaign.conversion_rate >= 2:
            score += 2
        elif campaign.conversion_rate >= 1:
            score += 1
        
        # ROI评分
        if campaign.roi >= 100:
            score += 3
        elif campaign.roi >= 50:
            score += 2
        elif campaign.roi >= 0:
            score += 1
        
        # 打开率评分
        if campaign.open_rate >= 30:
            score += 2
        elif campaign.open_rate >= 15:
            score += 1
        
        if score >= 7:
            return "🌟 优秀"
        elif score >= 5:
            return "✅ 良好"
        elif score >= 3:
            return "⚠️ 一般"
        else:
            return "❌ 需改进"

    def get_benchmark_comparison(self, campaign_id: str) -> Dict:
        """与行业基准对比"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return {}
        
        # 行业基准数据
        benchmarks = {
            "open_rate": 25.0,
            "click_rate": 3.5,
            "conversion_rate": 2.0,
            "cost_per_conversion": 150.0
        }
        
        return {
            "打开率": {
                "本活动": f"{campaign.open_rate:.1f}%",
                "行业基准": f"{benchmarks['open_rate']:.1f}%",
                "对比": "高于" if campaign.open_rate > benchmarks['open_rate'] else "低于"
            },
            "点击率": {
                "本活动": f"{campaign.click_rate:.1f}%",
                "行业基准": f"{benchmarks['click_rate']:.1f}%",
                "对比": "高于" if campaign.click_rate > benchmarks['click_rate'] else "低于"
            },
            "转化率": {
                "本活动": f"{campaign.conversion_rate:.2f}%",
                "行业基准": f"{benchmarks['conversion_rate']:.2f}%",
                "对比": "高于" if campaign.conversion_rate > benchmarks['conversion_rate'] else "低于"
            },
            "单客转化成本": {
                "本活动": f"{campaign.cost_per_conversion:.2f} 元",
                "行业基准": f"{benchmarks['cost_per_conversion']:.2f} 元",
                "对比": "更优" if campaign.cost_per_conversion < benchmarks['cost_per_conversion'] else "更高"
            }
        }
