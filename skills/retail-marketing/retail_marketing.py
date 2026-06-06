#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
零售营销主引擎
整合所有模块，提供一站式零售营销服务
"""

from customer_profiler import CustomerProfiler, RiskPreference, LifeStage
from customer_segment import CustomerSegmentation, SegmentLevel
from product_matcher import ProductMatcher
from aum_strategy import AUMGrowthStrategy
from campaign_evaluator import CampaignEvaluator


class RetailMarketingEngine:
    """零售营销引擎"""

    def __init__(self):
        self.profiler = CustomerProfiler()
        self.segmentation = CustomerSegmentation()
        self.product_matcher = ProductMatcher()
        self.aum_strategy = AUMGrowthStrategy()
        self.evaluator = CampaignEvaluator()

    def build_customer_profile(self, customer_id: str, name: str, age: int,
                               gender: str, occupation: str, income_level: str,
                               aum: float, risk_preference: str,
                               investment_experience: str = "一般",
                               transaction_frequency: str = "中",
                               channel_preference: list = None,
                               product_holdings: list = None) -> dict:
        """构建客户画像"""
        print(f"🔍 为客户 [{name}] 构建画像...")
        
        profile = self.profiler.build_profile(
            customer_id=customer_id,
            name=name,
            age=age,
            gender=gender,
            occupation=occupation,
            income_level=income_level,
            aum=aum,
            risk_preference=risk_preference,
            investment_experience=investment_experience,
            transaction_frequency=transaction_frequency,
            channel_preference=channel_preference,
            product_holdings=product_holdings
        )
        
        return self.profiler.get_profile_summary(customer_id)

    def segment_customer(self, customer_id: str, aum: float,
                         last_transaction_days: int,
                         transaction_count_12m: int,
                         total_amount_12m: float,
                         customer_age_months: int,
                         aum_trend: str,
                         age: int,
                         income_level: str,
                         occupation: str) -> dict:
        """客户分层"""
        print(f"📊 为客户 [{customer_id}] 进行分层...")
        
        segment = self.segmentation.full_segmentation(
            customer_id=customer_id,
            aum=aum,
            last_transaction_days=last_transaction_days,
            transaction_count_12m=transaction_count_12m,
            total_amount_12m=total_amount_12m,
            customer_age_months=customer_age_months,
            aum_trend=aum_trend,
            age=age,
            income_level=income_level,
            occupation=occupation
        )
        
        return self.segmentation.get_segment_summary(customer_id)

    def generate_recommendations(self, risk_preference: str, aum: float,
                                  age: int, investment_horizon: str = "中期",
                                  liquidity_need: str = "中",
                                  existing_products: list = None) -> list:
        """生成产品推荐"""
        print(f"🎯 生成产品推荐...")
        
        recommendations = self.product_matcher.match_products(
            risk_preference=risk_preference,
            aum=aum,
            age=age,
            investment_horizon=investment_horizon,
            liquidity_need=liquidity_need,
            existing_products=existing_products
        )
        
        result = []
        for i, rec in enumerate(recommendations, 1):
            result.append({
                "排名": i,
                "产品名称": rec.product.name,
                "产品类型": rec.product.product_type.value,
                "风险等级": rec.product.risk_level.label,
                "预期收益": f"{rec.product.expected_return}%",
                "起投金额": f"{rec.product.min_investment:,.0f} 元",
                "匹配度": f"{rec.match_score:.1f} 分",
                "匹配原因": rec.match_reasons,
                "风险警示": rec.risk_warning,
                "建议配置": f"{rec.suggested_allocation * 100:.0f}%"
            })
        
        return result

    def generate_aum_strategy(self, customer_id: str, current_aum: float,
                               current_products: list,
                               risk_preference: str,
                               age: int,
                               last_transaction_days: int,
                               aum_trend: str = "稳定",
                               complaint_history: int = 0) -> dict:
        """生成AUM提升策略"""
        print(f"📈 生成AUM提升策略...")
        
        path = self.aum_strategy.generate_aum_path(
            customer_id=customer_id,
            current_aum=current_aum,
            current_products=current_products,
            risk_preference=risk_preference,
            age=age,
            last_transaction_days=last_transaction_days,
            aum_trend=aum_trend,
            complaint_history=complaint_history
        )
        
        strategies = []
        for s in path.strategies:
            strategies.append({
                "策略类型": s.strategy_type.value,
                "策略名称": s.strategy_name,
                "描述": s.description,
                "目标提升": f"{s.target_aum_increase:,.0f} 元",
                "预期转化率": f"{s.expected_conversion_rate * 100:.0f}%",
                "执行动作": s.actions,
                "时间周期": s.timeline,
                "成功指标": s.success_metrics
            })
        
        return {
            "当前等级": path.current_level,
            "目标等级": path.target_level,
            "AUM缺口": f"{path.gap_amount:,.0f} 元",
            "预计时间": path.estimated_time,
            "成功概率": f"{path.success_probability * 100:.0f}%",
            "策略清单": strategies
        }

    def evaluate_campaign(self, campaign_id: str, campaign_name: str,
                          start_date: str, end_date: str,
                          total_targeted: int, total_cost: float,
                          total_reached: int, opens: int, clicks: int,
                          responses: int, conversions: int,
                          new_aum: float, new_customers: int,
                          product_sales: int) -> dict:
        """评估营销活动"""
        print(f"📊 评估营销活动 [{campaign_name}]...")
        
        campaign = self.evaluator.create_campaign(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            start_date=start_date,
            end_date=end_date,
            total_targeted=total_targeted,
            total_cost=total_cost
        )
        
        self.evaluator.update_campaign_metrics(
            campaign_id=campaign_id,
            total_reached=total_reached,
            opens=opens,
            clicks=clicks,
            responses=responses,
            conversions=conversions,
            new_aum=new_aum,
            new_customers=new_customers,
            product_sales=product_sales
        )
        
        return self.evaluator.get_campaign_report(campaign_id)

    def full_marketing_analysis(self, customer_id: str, name: str,
                                 age: int, gender: str, occupation: str,
                                 income_level: str, aum: float,
                                 risk_preference: str,
                                 last_transaction_days: int,
                                 transaction_count_12m: int,
                                 total_amount_12m: float,
                                 customer_age_months: int,
                                 aum_trend: str,
                                 current_products: list = None,
                                 investment_experience: str = "一般",
                                 transaction_frequency: str = "中") -> dict:
        """执行完整营销分析"""
        print(f"\n{'='*60}")
        print(f"🚀 开始零售营销全流程分析")
        print(f"{'='*60}\n")
        
        # 1. 客户画像
        print("步骤 1/5: 构建客户画像...")
        profile = self.build_customer_profile(
            customer_id=customer_id,
            name=name,
            age=age,
            gender=gender,
            occupation=occupation,
            income_level=income_level,
            aum=aum,
            risk_preference=risk_preference,
            investment_experience=investment_experience,
            transaction_frequency=transaction_frequency,
            product_holdings=current_products
        )
        
        # 2. 客户分层
        print("步骤 2/5: 客户分层运营...")
        segment = self.segment_customer(
            customer_id=customer_id,
            aum=aum,
            last_transaction_days=last_transaction_days,
            transaction_count_12m=transaction_count_12m,
            total_amount_12m=total_amount_12m,
            customer_age_months=customer_age_months,
            aum_trend=aum_trend,
            age=age,
            income_level=income_level,
            occupation=occupation
        )
        
        # 3. 产品推荐
        print("步骤 3/5: 精准产品推荐...")
        recommendations = self.generate_recommendations(
            risk_preference=risk_preference,
            aum=aum,
            age=age,
            existing_products=current_products
        )
        
        # 4. AUM策略
        print("步骤 4/5: AUM提升策略...")
        aum_path = self.generate_aum_strategy(
            customer_id=customer_id,
            current_aum=aum,
            current_products=current_products or [],
            risk_preference=risk_preference,
            age=age,
            last_transaction_days=last_transaction_days,
            aum_trend=aum_trend
        )
        
        # 5. 生成报告
        print("步骤 5/5: 生成营销报告...")
        report = self._generate_markdown_report(
            profile, segment, recommendations, aum_path
        )
        
        print("\n✅ 零售营销分析完成！")
        
        return {
            "profile": profile,
            "segment": segment,
            "recommendations": recommendations,
            "aum_strategy": aum_path,
            "report_markdown": report
        }

    def _generate_markdown_report(self, profile: dict, segment: dict,
                                   recommendations: list, aum_path: dict) -> str:
        """生成Markdown报告"""
        lines = []
        lines.append("# 📊 零售客户营销分析报告")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 客户画像
        lines.append("## 一、客户画像")
        lines.append("")
        for key, value in profile.items():
            lines.append(f"- **{key}**：{value}")
        lines.append("")
        
        # 客户分层
        lines.append("## 二、客户分层")
        lines.append("")
        for key, value in segment.items():
            if key == "营销策略":
                lines.append(f"- **{key}**：")
                for strategy in value:
                    lines.append(f"  - {strategy}")
            else:
                lines.append(f"- **{key}**：{value}")
        lines.append("")
        
        # 产品推荐
        lines.append("## 三、精准产品推荐")
        lines.append("")
        for rec in recommendations[:3]:
            lines.append(f"### {rec['排名']}. {rec['产品名称']} ({rec['匹配度']})")
            lines.append(f"- **类型**：{rec['产品类型']} | **风险**：{rec['风险等级']}")
            lines.append(f"- **预期收益**：{rec['预期收益']} | **起投**：{rec['起投金额']}")
            lines.append(f"- **建议配置**：{rec['建议配置']}")
            lines.append(f"- **匹配原因**：{', '.join(rec['匹配原因'])}")
            lines.append(f"- **{rec['风险警示']}**")
            lines.append("")
        
        # AUM策略
        lines.append("## 四、AUM提升路径")
        lines.append("")
        lines.append(f"- **当前等级**：{aum_path['当前等级']}")
        lines.append(f"- **目标等级**：{aum_path['目标等级']}")
        lines.append(f"- **AUM缺口**：{aum_path['AUM缺口']}")
        lines.append(f"- **预计时间**：{aum_path['预计时间']}")
        lines.append(f"- **成功概率**：{aum_path['成功概率']}")
        lines.append("")
        lines.append("### 执行策略")
        lines.append("")
        for i, strategy in enumerate(aum_path['策略清单'], 1):
            lines.append(f"**{i}. {strategy['策略名称']}** ({strategy['策略类型']})")
            lines.append(f"- {strategy['描述']}")
            lines.append(f"- 目标提升：{strategy['目标提升']} | 转化率：{strategy['预期转化率']}")
            lines.append(f"- 时间周期：{strategy['时间周期']}")
            lines.append("- 执行动作：")
            for action in strategy['执行动作']:
                lines.append(f"  - {action}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append("*本报告由零售营销 Skill 自动生成*")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # 演示
    engine = RetailMarketingEngine()
    
    result = engine.full_marketing_analysis(
        customer_id="C001",
        name="李明",
        age=35,
        gender="男",
        occupation="IT工程师",
        income_level="高",
        aum=500000,
        risk_preference="稳健型",
        last_transaction_days=15,
        transaction_count_12m=12,
        total_amount_12m=200000,
        customer_age_months=24,
        aum_trend="上升",
        current_products=["活期存款", "稳健理财"],
        investment_experience="一般",
        transaction_frequency="中"
    )
    
    print("\n" + "="*60)
    print("📋 营销报告预览")
    print("="*60)
    print(result["report_markdown"][:2500])
    print("\n... [报告已截断] ...")
