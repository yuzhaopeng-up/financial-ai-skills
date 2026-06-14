# -*- coding: utf-8 -*-
"""
税务筹划引擎 v1.0

核心能力:
- 税负分析
- 优惠政策匹配
- 合规性检查
- 节税建议

协同: RemoteAgentA (策略分析) / RemoteAgentB (法规查询)
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class TaxEngine:
    """税务筹划引擎"""
    
    # 模拟税务数据
    MOCK_TAX_DATA = {
        "银联商务": {
            "tax_year": 2025,
            "total_revenue": 5000000000,  # 50亿
            "taxable_income": 450000000,
            "tax_paid": {
                "增值税": 85000000,
                "企业所得税": 112500000,
                "附加税": 10200000,
                "印花税": 500000,
            },
            "effective_rate": 25.3,
            "industry_avg_rate": 22.5,
            "applicable_policies": [
                {"name": "高新技术企业优惠", "rate": 15, "saving": 45000000, "status": "已享受"},
                {"name": "研发费用加计扣除", "rate": 100, "saving": 28000000, "status": "已享受"},
                {"name": "西部大开发优惠", "rate": 15, "saving": 0, "status": "未适用"},
            ]
        }
    }
    
    # 税收优惠政策库
    TAX_POLICIES = [
        {
            "name": "高新技术企业优惠",
            "type": "企业所得税",
            "rate": 15,
            "condition": "通过高新技术企业认定",
            "valid_until": "2027-12-31",
            "applicable_industries": ["科技", "软件", "生物医药"],
        },
        {
            "name": "研发费用加计扣除",
            "type": "企业所得税",
            "rate": 100,
            "condition": "开展研发活动",
            "valid_until": "2027-12-31",
            "applicable_industries": ["全部"],
        },
        {
            "name": "小型微利企业优惠",
            "type": "企业所得税",
            "rate": 5,
            "condition": "应纳税所得额≤300万，从业人数≤300人，资产总额≤5000万",
            "valid_until": "2027-12-31",
            "applicable_industries": ["全部"],
        },
        {
            "name": "增值税留抵退税",
            "type": "增值税",
            "rate": 100,
            "condition": "符合条件的企业可申请退还增量留抵税额",
            "valid_until": "长期",
            "applicable_industries": ["制造业", "科技", "软件"],
        },
        {
            "name": "技术转让所得减免",
            "type": "企业所得税",
            "rate": 0,
            "condition": "技术转让所得不超过500万元的部分免征",
            "valid_until": "长期",
            "applicable_industries": ["科技", "软件"],
        },
    ]
    
    def __init__(self):
        self.engine_name = "TaxEngine"
        self.version = "1.0.0"
    
    def analyze(
        self,
        company_name: Optional[str] = None,
        revenue: Optional[float] = None,
        tax_paid: Optional[Dict[str, float]] = None,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        税务分析主入口
        
        Args:
            company_name: 公司名称
            revenue: 年营收
            tax_paid: 已缴纳税费
            industry: 所属行业
            
        Returns:
            税务分析结果
        """
        start_time = datetime.now()
        
        # 1. 获取或生成数据
        if company_name and company_name in self.MOCK_TAX_DATA:
            data = self.MOCK_TAX_DATA[company_name]
        else:
            data = self._generate_demo_data(company_name or "演示企业", revenue, tax_paid)
        
        # 2. 计算税负指标
        total_tax = sum(data["tax_paid"].values())
        effective_rate = (total_tax / data["total_revenue"] * 100) if data["total_revenue"] > 0 else 0
        
        # 3. 匹配优惠政策
        matched_policies = self._match_policies(industry or "科技")
        
        # 4. 计算节税空间
        savings = self._calculate_savings(data, matched_policies)
        
        # 5. 合规检查
        compliance = self._check_compliance(data)
        
        result = {
            "success": True,
            "scenario": "tax_planning",
            "company_name": company_name or "演示企业",
            "tax_year": data["tax_year"],
            "summary": {
                "total_revenue": data["total_revenue"],
                "total_tax": total_tax,
                "effective_rate": round(effective_rate, 2),
                "industry_avg_rate": data.get("industry_avg_rate", 22.5),
                "tax_burden_level": "偏高" if effective_rate > 25 else "正常" if effective_rate > 18 else "偏低",
            },
            "tax_breakdown": data["tax_paid"],
            "policies": matched_policies,
            "savings_opportunities": savings,
            "compliance": compliance,
            "recommendations": self._generate_recommendations(data, savings, compliance),
            "timestamp": datetime.now().isoformat(),
            "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000)
        }
        
        return result
    
    def _generate_demo_data(
        self,
        company_name: str,
        revenue: Optional[float] = None,
        tax_paid: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """生成演示用税务数据"""
        rev = revenue or 1000000000  # 默认10亿
        
        if tax_paid:
            tp = tax_paid
        else:
            tp = {
                "增值税": rev * 0.017,
                "企业所得税": rev * 0.0225,
                "附加税": rev * 0.002,
                "印花税": rev * 0.0001,
            }
        
        return {
            "tax_year": 2025,
            "total_revenue": rev,
            "taxable_income": rev * 0.09,
            "tax_paid": tp,
            "effective_rate": 25.0,
            "industry_avg_rate": 22.5,
            "applicable_policies": []
        }
    
    def _match_policies(self, industry: str) -> List[Dict[str, Any]]:
        """匹配适用的税收优惠政策"""
        matched = []
        
        for policy in self.TAX_POLICIES:
            applicable = policy["applicable_industries"]
            if "全部" in applicable or industry in applicable:
                matched.append({
                    "name": policy["name"],
                    "type": policy["type"],
                    "rate": policy["rate"],
                    "condition": policy["condition"],
                    "valid_until": policy["valid_until"],
                    "applicable": True
                })
        
        return matched
    
    def _calculate_savings(
        self,
        data: Dict[str, Any],
        policies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """计算节税空间"""
        savings = []
        taxable_income = data.get("taxable_income", 0)
        
        for policy in policies:
            if policy["type"] == "企业所得税" and policy["rate"] < 25:
                current_tax = taxable_income * 0.25
                new_tax = taxable_income * (policy["rate"] / 100)
                saving = current_tax - new_tax
                
                savings.append({
                    "policy": policy["name"],
                    "potential_saving": round(saving, 2),
                    "current_rate": 25,
                    "new_rate": policy["rate"],
                    "priority": "高" if saving > 10000000 else "中"
                })
        
        # 按节税金额排序
        savings.sort(key=lambda x: x["potential_saving"], reverse=True)
        return savings
    
    def _check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """合规性检查"""
        flags = []
        score = 100
        
        # 检查税负率异常
        effective_rate = data.get("effective_rate", 0)
        if effective_rate < 10:
            flags.append({"level": "warning", "msg": "实际税负率偏低，可能存在税务风险"})
            score -= 15
        elif effective_rate > 35:
            flags.append({"level": "warning", "msg": "实际税负率偏高，建议检查优惠政策适用情况"})
            score -= 5
        
        # 检查增值税税负
        vat = data["tax_paid"].get("增值税", 0)
        revenue = data["total_revenue"]
        vat_rate = (vat / revenue * 100) if revenue > 0 else 0
        if vat_rate < 1.0:
            flags.append({"level": "info", "msg": "增值税税负率低于行业预警值，建议关注进项抵扣"})
            score -= 5
        
        status = "合规" if score >= 90 else "需关注" if score >= 70 else "风险"
        
        return {"score": score, "flags": flags, "status": status}
    
    def _generate_recommendations(
        self,
        data: Dict[str, Any],
        savings: List[Dict[str, Any]],
        compliance: Dict[str, Any]
    ) -> List[str]:
        """生成筹划建议"""
        recommendations = []
        
        # 节税建议
        if savings:
            top = savings[0]
            recommendations.append(
                f"💰 优先申请「{top['policy']}」，预计可节税 ¥{top['potential_saving']:,.0f}"
            )
        
        # 合规建议
        if compliance["status"] != "合规":
            recommendations.append(
                f"⚠️ 当前合规评分{compliance['score']}分，建议关注: "
                f"{compliance['flags'][0]['msg']}"
            )
        
        # 通用建议
        effective_rate = data.get("effective_rate", 0)
        if effective_rate > data.get("industry_avg_rate", 22.5):
            recommendations.append(
                f"📊 当前实际税负率{effective_rate}%高于行业平均，"
                f"建议全面梳理可适用优惠政策"
            )
        
        if not recommendations:
            recommendations.append("✅ 当前税务状况良好，建议持续关注政策变化")
        
        return recommendations
