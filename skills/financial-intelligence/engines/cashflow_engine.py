# -*- coding: utf-8 -*-
"""
资金预测引擎 v1.0

核心能力:
- 现金流建模
- 短期资金预测
- 缺口预警
- 资金调度建议

协同: RemoteAgentA (分析建模) / RemoteAgentB (数据对接)
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta


class CashflowEngine:
    """资金预测引擎"""
    
    # 模拟现金流数据
    MOCK_CASHFLOW = {
        "company": "银联商务",
        "base_balance": 250000000,  # 2.5亿
        "daily_inflow_avg": 8500000,   # 日均流入850万
        "daily_outflow_avg": 7200000,  # 日均流出720万
        "seasonal_factor": {
            "Q1": 0.85,
            "Q2": 1.05,
            "Q3": 1.10,
            "Q4": 1.20,
        },
        "upcoming_payments": [
            {"date": "2026-05-25", "desc": "供应商货款", "amount": 15000000},
            {"date": "2026-05-28", "desc": "工资发放", "amount": 8500000},
            {"date": "2026-06-01", "desc": "房租", "amount": 3200000},
            {"date": "2026-06-05", "desc": "税费", "amount": 22000000},
            {"date": "2026-06-10", "desc": "贷款还款", "amount": 5000000},
        ],
        "upcoming_receipts": [
            {"date": "2026-05-26", "desc": "客户回款", "amount": 12000000},
            {"date": "2026-05-30", "desc": "客户回款", "amount": 18000000},
            {"date": "2026-06-03", "desc": "政府补贴", "amount": 5000000},
        ]
    }
    
    def __init__(self):
        self.engine_name = "CashflowEngine"
        self.version = "1.0.0"
    
    def forecast(
        self,
        days: int = 30,
        company: Optional[str] = None,
        scenario: str = "base"
    ) -> Dict[str, Any]:
        """
        资金预测主入口
        
        Args:
            days: 预测天数
            company: 公司名称
            scenario: 情景（base/optimistic/pessimistic）
            
        Returns:
            预测结果
        """
        start_time = datetime.now()
        
        # 1. 获取数据
        data = self.MOCK_CASHFLOW if not company or company in self.MOCK_CASHFLOW["company"] else self._generate_demo_data(company)
        
        # 2. 情景调整
        scenario_factor = {"base": 1.0, "optimistic": 1.15, "pessimistic": 0.85}.get(scenario, 1.0)
        
        # 3. 构建日现金流预测
        daily_forecast = self._build_daily_forecast(data, days, scenario_factor)
        
        # 4. 识别缺口
        gaps = self._identify_gaps(daily_forecast)
        
        # 5. 生成建议
        recommendations = self._generate_recommendations(gaps, data)
        
        result = {
            "success": True,
            "scenario": "cashflow_forecast",
            "company": data["company"],
            "forecast_period": f"{days}天",
            "forecast_dates": {
                "start": datetime.now().strftime("%Y-%m-%d"),
                "end": (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            },
            "summary": {
                "starting_balance": data["base_balance"],
                "projected_lowest": min(d["balance"] for d in daily_forecast),
                "projected_highest": max(d["balance"] for d in daily_forecast),
                "avg_daily_inflow": data["daily_inflow_avg"] * scenario_factor,
                "avg_daily_outflow": data["daily_outflow_avg"],
                "net_daily_flow": (data["daily_inflow_avg"] * scenario_factor) - data["daily_outflow_avg"],
            },
            "daily_forecast": daily_forecast[:14],  # 只返回前14天详细数据
            "gaps": gaps,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
            "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000)
        }
        
        return result
    
    def _build_daily_forecast(
        self,
        data: Dict[str, Any],
        days: int,
        scenario_factor: float
    ) -> List[Dict[str, Any]]:
        """构建日现金流预测"""
        forecast = []
        balance = data["base_balance"]
        
        # 构建付款/收款查找表
        payments = {p["date"]: p for p in data.get("upcoming_payments", [])}
        receipts = {r["date"]: r for r in data.get("upcoming_receipts", [])}
        
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            
            # 基础流入流出
            inflow = data["daily_inflow_avg"] * scenario_factor
            outflow = data["daily_outflow_avg"]
            
            # 特殊收支
            special_in = 0
            special_out = 0
            special_items = []
            
            if date in receipts:
                r = receipts[date]
                special_in += r["amount"]
                special_items.append(f"+{r['desc']} ¥{r['amount']:,.0f}")
            
            if date in payments:
                p = payments[date]
                special_out += p["amount"]
                special_items.append(f"-{p['desc']} ¥{p['amount']:,.0f}")
            
            total_in = inflow + special_in
            total_out = outflow + special_out
            net = total_in - total_out
            balance += net
            
            forecast.append({
                "date": date,
                "day_of_week": (datetime.now() + timedelta(days=i)).strftime("%a"),
                "inflow": total_in,
                "outflow": total_out,
                "net": net,
                "balance": balance,
                "special_items": special_items,
                "alert": balance < 50000000  # 低于5000万预警
            })
        
        return forecast
    
    def _identify_gaps(self, forecast: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别资金缺口"""
        gaps = []
        
        # 安全线：5000万
        safety_line = 50000000
        
        for day in forecast:
            if day["balance"] < safety_line:
                gaps.append({
                    "date": day["date"],
                    "balance": day["balance"],
                    "shortfall": safety_line - day["balance"],
                    "severity": "严重" if day["balance"] < 10000000 else "中等" if day["balance"] < 30000000 else "轻微"
                })
        
        return gaps
    
    def _generate_recommendations(
        self,
        gaps: List[Dict[str, Any]],
        data: Dict[str, Any]
    ) -> List[str]:
        """生成资金调度建议"""
        recommendations = []
        
        if not gaps:
            recommendations.append("✅ 预测期内无资金缺口，现金流健康")
            return recommendations
        
        # 按严重程度分组
        severe = [g for g in gaps if g["severity"] == "严重"]
        medium = [g for g in gaps if g["severity"] == "中等"]
        
        if severe:
            total_shortfall = sum(g["shortfall"] for g in severe)
            recommendations.append(
                f"🚨 紧急: 预测期内出现{len(severe)}天严重缺口，"
                f"最大缺口¥{max(g['shortfall'] for g in severe):,.0f}，"
                f"建议立即安排短期融资¥{total_shortfall:,.0f}"
            )
        
        if medium:
            recommendations.append(
                f"⚠️ 关注: {len(medium)}天出现中等缺口，"
                f"建议提前与银行沟通授信额度"
            )
        
        # 通用建议
        upcoming_payments = data.get("upcoming_payments", [])
        if upcoming_payments:
            total_payments = sum(p["amount"] for p in upcoming_payments)
            recommendations.append(
                f"📋 未来有大额支出{len(upcoming_payments)}笔，"
                f"合计¥{total_payments:,.0f}，建议做好资金安排"
            )
        
        return recommendations
    
    def _generate_demo_data(self, company: str) -> Dict[str, Any]:
        """生成演示用现金流数据"""
        hash_val = sum(ord(c) for c in company)
        base = 100000000 + (hash_val % 400000000)  # 1-5亿
        
        return {
            "company": company,
            "base_balance": base,
            "daily_inflow_avg": base * 0.035,
            "daily_outflow_avg": base * 0.03,
            "seasonal_factor": {"Q1": 0.9, "Q2": 1.0, "Q3": 1.1, "Q4": 1.15},
            "upcoming_payments": [
                {"date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"), "desc": "供应商货款", "amount": base * 0.06},
                {"date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"), "desc": "工资发放", "amount": base * 0.035},
            ],
            "upcoming_receipts": [
                {"date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"), "desc": "客户回款", "amount": base * 0.05},
            ]
        }
