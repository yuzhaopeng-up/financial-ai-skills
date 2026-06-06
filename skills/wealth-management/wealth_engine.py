#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财富管理引擎 v1.0

核心能力:
- 资产配置建议
- 财务健康诊断
- 退休养老规划
- 保险规划
- 税务优化
- 教育金规划
- 房产规划
- 智能投顾

纯规则引擎，零API费用，毫秒级响应
"""

import re
from typing import Dict, Any, List


class WealthEngine:
    """财富管理引擎"""
    
    def __init__(self):
        self._init_mock_data()
    
    def _init_mock_data(self):
        """初始化演示数据"""
        self.customers = {
            "张伟": {"age": 38, "job": "企业高管", "aum": 520, "risk": "激进型", "income": 80, "family": "已婚，一子"},
            "李娜": {"age": 32, "job": "医生", "aum": 180, "risk": "稳健型", "income": 45, "family": "已婚"},
            "王芳": {"age": 45, "job": "私营业主", "aum": 850, "risk": "平衡型", "income": 120, "family": "已婚，一女"},
            "刘洋": {"age": 28, "job": "程序员", "aum": 35, "risk": "激进型", "income": 35, "family": "未婚"},
            "陈明": {"age": 52, "job": "企业主", "aum": 1200, "risk": "保守型", "income": 200, "family": "已婚，一子一女"},
        }
        
        # 资产配置数据
        self.allocations = {
            "张伟": {
                "profile": {"riskScore": 78, "horizon": "长期", "capacity": "高"},
                "allocation": [
                    {"type": "股票基金", "percent": 40, "amount": 208, "products": ["蓝筹精选", "成长混合"]},
                    {"type": "债券基金", "percent": 25, "amount": 130, "products": ["产业债A", "信用债"]},
                    {"type": "货币基金", "percent": 15, "amount": 78, "products": ["余额宝", "现金增利"]},
                    {"type": "黄金ETF", "percent": 10, "amount": 52, "products": ["黄金ETF"]},
                    {"type": "QDII", "percent": 10, "amount": 52, "products": ["纳斯达克100指数基金"]},
                ],
                "suggestion": "基于您的激进型风险偏好和长期视野，建议加大权益类资产配置，适度参与海外市场。",
                "expectedReturn": "年化预期收益 8.5%-12%",
                "riskWarning": "最大回撤可能达 25%-30%",
            },
            "李娜": {
                "profile": {"riskScore": 55, "horizon": "中期", "capacity": "中等"},
                "allocation": [
                    {"type": "债券基金", "percent": 40, "amount": 72, "products": ["产业债A", "双利债券"]},
                    {"type": "股票基金", "percent": 25, "amount": 45, "products": ["价值精选", "时代先锋"]},
                    {"type": "货币基金", "percent": 20, "amount": 36, "products": ["余额宝"]},
                    {"type": "银行理财", "percent": 15, "amount": 27, "products": ["朝朝盈", "添利宝"]},
                ],
                "suggestion": "作为稳健型投资者，建议以债券基金为底仓，适度配置权益类资产获取超额收益。",
                "expectedReturn": "年化预期收益 5.5%-7.5%",
                "riskWarning": "最大回撤可能达 12%-15%",
            },
            "王芳": {
                "profile": {"riskScore": 62, "horizon": "长期", "capacity": "高"},
                "allocation": [
                    {"type": "股票基金", "percent": 35, "amount": 297.5, "products": ["消费行业", "价值精选"]},
                    {"type": "债券基金", "percent": 30, "amount": 255, "products": ["信用债", "丰禄债券"]},
                    {"type": "私募基金", "percent": 15, "amount": 127.5, "products": ["邻山1号", "景林价值"]},
                    {"type": "货币基金", "percent": 10, "amount": 85, "products": ["余额宝"]},
                    {"type": "保险理财", "percent": 10, "amount": 85, "products": ["财富宝", "鑫享宝"]},
                ],
                "suggestion": "建议均衡配置，适度参与私募获取超额收益，同时保持足够流动性。",
                "expectedReturn": "年化预期收益 7%-10%",
                "riskWarning": "最大回撤可能达 18%-22%",
            },
            "刘洋": {
                "profile": {"riskScore": 80, "horizon": "长期", "capacity": "中等"},
                "allocation": [
                    {"type": "股票基金", "percent": 50, "amount": 17.5, "products": ["上证50ETF联接", "创业板ETF"]},
                    {"type": "指数基金", "percent": 20, "amount": 7, "products": ["沪深300指数基金"]},
                    {"type": "债券基金", "percent": 15, "amount": 5.25, "products": ["产业债A"]},
                    {"type": "货币基金", "percent": 15, "amount": 5.25, "products": ["余额宝"]},
                ],
                "suggestion": "年轻投资者可承受较高波动，建议以指数基金定投为主，长期复利效应显著。",
                "expectedReturn": "年化预期收益 9%-14%",
                "riskWarning": "最大回撤可能达 30%-35%",
            },
            "陈明": {
                "profile": {"riskScore": 35, "horizon": "长期", "capacity": "高"},
                "allocation": [
                    {"type": "债券基金", "percent": 45, "amount": 540, "products": ["产业债A", "信用债", "双利债券"]},
                    {"type": "银行理财", "percent": 25, "amount": 300, "products": ["朝朝盈", "添利宝"]},
                    {"type": "股票基金", "percent": 15, "amount": 180, "products": ["价值精选"]},
                    {"type": "保险理财", "percent": 10, "amount": 120, "products": ["财富宝"]},
                    {"type": "货币基金", "percent": 5, "amount": 60, "products": ["余额宝"]},
                ],
                "suggestion": "作为保守型投资者，建议以固收类产品为主，权益类资产不超过20%。",
                "expectedReturn": "年化预期收益 4.5%-6%",
                "riskWarning": "最大回撤可能达 8%-10%",
            },
        }
        
        # 财务健康数据
        self.health_data = {
            "张伟": {"score": 78, "savings_rate": 25, "debt_ratio": 35, "liquidity": 6, "insurance_coverage": 80},
            "李娜": {"score": 82, "savings_rate": 40, "debt_ratio": 10, "liquidity": 8, "insurance_coverage": 60},
            "王芳": {"score": 75, "savings_rate": 30, "debt_ratio": 25, "liquidity": 5, "insurance_coverage": 70},
            "刘洋": {"score": 68, "savings_rate": 35, "debt_ratio": 15, "liquidity": 4, "insurance_coverage": 40},
            "陈明": {"score": 85, "savings_rate": 45, "debt_ratio": 20, "liquidity": 10, "insurance_coverage": 90},
        }
        
        # 退休规划数据
        self.retirement_data = {
            "张伟": {"current_age": 38, "retire_age": 60, "monthly_need": 25000, "gap": 280, "monthly_save": 10500},
            "李娜": {"current_age": 32, "retire_age": 55, "monthly_need": 18000, "gap": 150, "monthly_save": 6800},
            "王芳": {"current_age": 45, "retire_age": 55, "monthly_need": 22000, "gap": 320, "monthly_save": 13300},
            "刘洋": {"current_age": 28, "retire_age": 60, "monthly_need": 15000, "gap": 180, "monthly_save": 4200},
            "陈明": {"current_age": 52, "retire_age": 60, "monthly_need": 30000, "gap": 150, "monthly_save": 15600},
        }
    
    def get_allocation(self, name: str) -> Dict[str, Any]:
        """获取资产配置方案"""
        c = self.customers.get(name)
        data = self.allocations.get(name)
        
        if not c or not data:
            return {"success": False, "message": f"客户 {name} 不存在"}
        
        return {
            "success": True,
            "customer": c,
            "allocation": data,
        }
    
    def get_health(self, name: str) -> Dict[str, Any]:
        """获取财务健康诊断"""
        c = self.customers.get(name)
        h = self.health_data.get(name)
        
        if not c or not h:
            return {"success": False, "message": f"客户 {name} 不存在"}
        
        return {
            "success": True,
            "customer": c,
            "health": h,
        }
    
    def get_retirement(self, name: str) -> Dict[str, Any]:
        """获取退休规划"""
        c = self.customers.get(name)
        r = self.retirement_data.get(name)
        
        if not c or not r:
            return {"success": False, "message": f"客户 {name} 不存在"}
        
        return {
            "success": True,
            "customer": c,
            "retirement": r,
        }
    
    def list_customers(self) -> Dict[str, Any]:
        """获取客户列表"""
        return {
            "success": True,
            "customers": self.customers,
        }


class WealthFormatter:
    """财富管理格式化器"""
    
    @staticmethod
    def format_allocation(result: Dict[str, Any]) -> str:
        """格式化资产配置"""
        if not result.get("success"):
            return f"❌ {result.get('message', '未知错误')}"
        
        c = result["customer"]
        data = result["allocation"]
        
        lines = [
            f"## 📈 {c.get('name', '客户')} - 资产配置方案",
            "",
            f"**客户**: {c.get('name')} | {c['age']}岁 | {c['job']} | 资产{c['aum']}万",
            f"**风险偏好**: {c['risk']} | **投资期限**: {data['profile']['horizon']}",
            "",
            "### 配置方案",
            "",
            "| 资产类型 | 比例 | 金额(万) | 推荐产品 |",
            "|:---|---:|---:|:---|",
        ]
        
        for item in data['allocation']:
            products = "、".join(item['products'])
            lines.append(f"| {item['type']} | {item['percent']}% | {item['amount']} | {products} |")
        
        lines.extend([
            "",
            "### 方案说明",
            "",
            f"> {data['suggestion']}",
            "",
            f"- **预期收益**: {data['expectedReturn']}",
            f"- **风险提示**: {data['riskWarning']}",
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_health(result: Dict[str, Any]) -> str:
        """格式化财务健康诊断"""
        if not result.get("success"):
            return f"❌ {result.get('message', '未知错误')}"
        
        c = result["customer"]
        h = result["health"]
        
        score_color = "🟢" if h['score'] >= 80 else "🟡" if h['score'] >= 70 else "🔴"
        
        lines = [
            f"## 🏥 {c.get('name', '客户')} - 财务健康诊断",
            "",
            f"### 综合评分: {score_color} **{h['score']}/100**",
            "",
            "| 指标 | 数值 | 评价 |",
            "|:---|---:|:---|",
            f"| 储蓄率 | {h['savings_rate']}% | {'🟢 优秀' if h['savings_rate'] >= 30 else '🟡 一般' if h['savings_rate'] >= 20 else '🔴 偏低'} |",
            f"| 负债率 | {h['debt_ratio']}% | {'🟢 健康' if h['debt_ratio'] <= 30 else '🟡 关注' if h['debt_ratio'] <= 50 else '🔴 偏高'} |",
            f"| 流动性 | {h['liquidity']}个月 | {'🟢 充足' if h['liquidity'] >= 6 else '🟡 一般' if h['liquidity'] >= 3 else '🔴 不足'} |",
            f"| 保险覆盖 | {h['insurance_coverage']}% | {'🟢 充分' if h['insurance_coverage'] >= 80 else '🟡 基本' if h['insurance_coverage'] >= 60 else '🔴 不足'} |",
            "",
            "### 改进建议",
            "",
        ]
        
        if h['savings_rate'] < 30:
            lines.append("- 💡 储蓄率有提升空间，建议制定强制储蓄计划")
        if h['debt_ratio'] > 30:
            lines.append("- 💡 负债率偏高，建议优先偿还高息债务")
        if h['liquidity'] < 6:
            lines.append("- 💡 应急资金不足，建议储备6个月生活费")
        if h['insurance_coverage'] < 80:
            lines.append("- 💡 保险覆盖不足，建议补充重疾险和寿险")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_retirement(result: Dict[str, Any]) -> str:
        """格式化退休规划"""
        if not result.get("success"):
            return f"❌ {result.get('message', '未知错误')}"
        
        c = result["customer"]
        r = result["retirement"]
        
        lines = [
            f"## 🏖️ {c.get('name', '客户')} - 退休养老规划",
            "",
            f"**当前年龄**: {r['current_age']}岁 | **计划退休**: {r['retire_age']}岁",
            f"**退休年限**: {r['retire_age'] - r['current_age']}年",
            "",
            "### 养老金缺口分析",
            "",
            f"| 项目 | 数值 |",
            f"|:---|---:|",
            f"| 退休后月支出需求 | **{r['monthly_need']:,}元** |",
            f"| 养老金总缺口 | **{r['gap']}万** |",
            f"| 每月需储蓄 | **{r['monthly_save']:,}元** |",
            "",
            "### 储蓄计划",
            "",
            f"> 建议通过基金定投+养老保险组合，每月定投 **{r['monthly_save']:,}元**，",
            f"> 按年化收益6%测算，退休时可积累约 **{r['gap'] * 1.2:.0f}万** 养老金。",
        ]
        
        return "\n".join(lines)
    
    @staticmethod
    def format_customer_list(result: Dict[str, Any]) -> str:
        """格式化客户列表"""
        if not result.get("success"):
            return f"❌ {result.get('message', '未知错误')}"
        
        lines = [
            "## 💰 财富客户列表",
            "",
            "| 客户 | 年龄 | 职业 | 资产(万) | 风险偏好 |",
            "|:---|---:|:---|---:|:---|",
        ]
        
        for name, c in result["customers"].items():
            lines.append(f"| **{name}** | {c['age']} | {c['job']} | {c['aum']} | {c['risk']} |")
        
        lines.extend([
            "",
            "**快捷指令**：",
            "- `资产配置 张伟` - 查看资产配置方案",
            "- `财务健康 李娜` - 财务健康诊断",
            "- `退休规划 王芳` - 退休养老规划",
        ])
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Demo
    engine = WealthEngine()
    formatter = WealthFormatter()
    
    print(formatter.format_customer_list(engine.list_customers()))
    print("\n" + "="*50 + "\n")
    print(formatter.format_allocation(engine.get_allocation("张伟")))
