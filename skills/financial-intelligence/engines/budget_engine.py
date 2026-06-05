# -*- coding: utf-8 -*-
"""
预算管控引擎 v1.0

核心能力:
- 预算执行跟踪
- 偏差分析
- 超支预警
- 趋势预测

协同: ArkClaw (分析决策) / KimiClaw (数据抓取)
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime


class BudgetEngine:
    """预算管控引擎"""
    
    # 模拟预算数据（演示用）
    MOCK_BUDGETS = {
        "市场部": {
            "period": "2026-Q2",
            "total_budget": 500000,
            "categories": {
                "差旅费": {"budget": 150000, "spent": 168000, "forecast": 185000},
                "招待费": {"budget": 80000, "spent": 62000, "forecast": 75000},
                "广告费": {"budget": 200000, "spent": 145000, "forecast": 195000},
                "办公费": {"budget": 70000, "spent": 50000, "forecast": 68000},
            }
        },
        "技术部": {
            "period": "2026-Q2",
            "total_budget": 800000,
            "categories": {
                "研发费": {"budget": 500000, "spent": 420000, "forecast": 510000},
                "设备费": {"budget": 200000, "spent": 85000, "forecast": 180000},
                "培训费": {"budget": 100000, "spent": 45000, "forecast": 92000},
            }
        },
        "财务部": {
            "period": "2026-Q2",
            "total_budget": 300000,
            "categories": {
                "审计费": {"budget": 120000, "spent": 80000, "forecast": 115000},
                "软件费": {"budget": 100000, "spent": 95000, "forecast": 105000},
                "咨询费": {"budget": 80000, "spent": 30000, "forecast": 75000},
            }
        }
    }
    
    def __init__(self):
        self.engine_name = "BudgetEngine"
        self.version = "1.0.0"
    
    def analyze(
        self,
        dept: Optional[str] = None,
        period: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        预算分析主入口
        
        Args:
            dept: 部门名称（如"市场部"）
            period: 期间（如"2026-Q2"）
            category: 费用类别（可选）
            
        Returns:
            预算分析结果
        """
        start_time = datetime.now()
        
        # 1. 查找部门预算
        if dept and dept in self.MOCK_BUDGETS:
            budget_data = self.MOCK_BUDGETS[dept]
        else:
            # 返回全公司概览
            return self._build_overview()
        
        # 2. 计算指标
        total_budget = budget_data["total_budget"]
        total_spent = sum(c["spent"] for c in budget_data["categories"].values())
        total_forecast = sum(c["forecast"] for c in budget_data["categories"].values())
        
        utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0
        forecast_utilization = (total_forecast / total_budget * 100) if total_budget > 0 else 0
        
        # 3. 分析各科目
        category_analysis = []
        warnings = []
        
        for cat_name, cat_data in budget_data["categories"].items():
            cat_budget = cat_data["budget"]
            cat_spent = cat_data["spent"]
            cat_forecast = cat_data["forecast"]
            
            cat_util = (cat_spent / cat_budget * 100) if cat_budget > 0 else 0
            cat_forecast_util = (cat_forecast / cat_budget * 100) if cat_budget > 0 else 0
            
            # 偏差
            variance = cat_spent - cat_budget
            variance_pct = (variance / cat_budget * 100) if cat_budget > 0 else 0
            
            status = "正常"
            if cat_forecast_util > 100:
                status = "超支预警"
                warnings.append({
                    "category": cat_name,
                    "level": "high",
                    "message": f"{cat_name}预计超支 {cat_forecast_util - 100:.1f}%"
                })
            elif cat_forecast_util > 90:
                status = "接近上限"
                warnings.append({
                    "category": cat_name,
                    "level": "medium",
                    "message": f"{cat_name}已使用 {cat_util:.1f}%，预计使用 {cat_forecast_util:.1f}%"
                })
            
            category_analysis.append({
                "name": cat_name,
                "budget": cat_budget,
                "spent": cat_spent,
                "forecast": cat_forecast,
                "utilization": round(cat_util, 1),
                "forecast_utilization": round(cat_forecast_util, 1),
                "variance": round(variance, 2),
                "variance_pct": round(variance_pct, 1),
                "status": status
            })
        
        # 4. 排序：按超支风险排序
        category_analysis.sort(key=lambda x: x["forecast_utilization"], reverse=True)
        
        result = {
            "success": True,
            "scenario": "budget",
            "dept": dept,
            "period": budget_data["period"],
            "summary": {
                "total_budget": total_budget,
                "total_spent": total_spent,
                "total_forecast": total_forecast,
                "utilization": round(utilization, 1),
                "forecast_utilization": round(forecast_utilization, 1),
                "remaining": total_budget - total_spent,
                "forecast_remaining": total_budget - total_forecast,
            },
            "categories": category_analysis,
            "warnings": warnings,
            "recommendations": self._generate_recommendations(warnings, category_analysis),
            "timestamp": datetime.now().isoformat(),
            "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000)
        }
        
        # 如果指定了具体类别，过滤结果
        if category:
            result["categories"] = [c for c in category_analysis if category in c["name"]]
        
        return result
    
    def _build_overview(self) -> Dict[str, Any]:
        """构建全公司预算概览"""
        depts = []
        total_budget = 0
        total_spent = 0
        total_warnings = 0
        
        for dept_name, dept_data in self.MOCK_BUDGETS.items():
            dept_budget = dept_data["total_budget"]
            dept_spent = sum(c["spent"] for c in dept_data["categories"].values())
            dept_forecast = sum(c["forecast"] for c in dept_data["categories"].values())
            
            total_budget += dept_budget
            total_spent += dept_spent
            
            # 统计预警
            warnings = 0
            for cat_data in dept_data["categories"].values():
                if cat_data["forecast"] > cat_data["budget"]:
                    warnings += 1
            total_warnings += warnings
            
            depts.append({
                "name": dept_name,
                "budget": dept_budget,
                "spent": dept_spent,
                "forecast": dept_forecast,
                "utilization": round(dept_spent / dept_budget * 100, 1),
                "warnings": warnings
            })
        
        return {
            "success": True,
            "scenario": "budget_overview",
            "summary": {
                "total_budget": total_budget,
                "total_spent": total_spent,
                "utilization": round(total_spent / total_budget * 100, 1),
                "dept_count": len(self.MOCK_BUDGETS),
                "total_warnings": total_warnings
            },
            "departments": depts,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_recommendations(
        self,
        warnings: List[Dict],
        categories: List[Dict]
    ) -> List[str]:
        """生成管控建议"""
        recommendations = []
        
        if not warnings:
            recommendations.append("✅ 当前预算执行情况良好，无超支风险")
            return recommendations
        
        # 按风险等级分组
        high_risk = [w for w in warnings if w["level"] == "high"]
        medium_risk = [w for w in warnings if w["level"] == "medium"]
        
        if high_risk:
            cat_names = ", ".join([w["category"] for w in high_risk])
            recommendations.append(f"🚨 紧急: {cat_names} 已触发超支预警，建议立即冻结新增支出")
        
        if medium_risk:
            cat_names = ", ".join([w["category"] for w in medium_risk])
            recommendations.append(f"⚠️ 关注: {cat_names} 接近预算上限，建议加强审批管控")
        
        # 找出节余科目
        surplus = [c for c in categories if c["forecast_utilization"] < 70]
        if surplus:
            cat_names = ", ".join([c["name"] for c in surplus[:2]])
            recommendations.append(f"💡 建议: {cat_names} 有预算节余，可考虑调剂至紧缺科目")
        
        return recommendations
