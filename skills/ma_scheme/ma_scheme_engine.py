#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并购方案生成引擎 v1.0
输入收购方、被收购方、交易目的，输出交易结构设计、估值分析、财务预测及风险提示

Author: ArkClaw
Version: 1.0.0
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


class MaSchemeEngine:
    """并购方案生成引擎"""
    
    VERSION = "1.0.0"
    
    # 交易结构类型
    TRANSACTION_TYPES = {
        "cash_acquisition": {
            "name": "现金收购",
            "description": "收购方以现金支付对价",
            "sub_types": ["100%收购", "控股收购", "参股收购"]
        },
        "stock_swap": {
            "name": "股票对价",
            "description": "收购方以定向增发股票作为对价",
            "sub_types": ["换股合并", "定向增发购买资产"]
        },
        "mixed_payment": {
            "name": "混合支付",
            "description": "现金+股票组合支付",
            "sub_types": ["现金为主", "股票为主", "现金股票对半"]
        },
        "asset_swap": {
            "name": "资产置换",
            "description": "资产互换+现金补差",
            "sub_types": ["完整置换", "部分置换"]
        },
        "debt_assumption": {
            "name": "承债式收购",
            "description": "承担目标公司债务",
            "sub_types": ["全额承债", "部分承债"]
        },
        "lbo": {
            "name": "杠杆收购",
            "description": "高杠杆融资收购",
            "sub_types": ["MBO管理层收购", "IBO投资者收购"]
        }
    }
    
    # 估值方法
    VALUATION_METHODS = {
        "dcf": {
            "name": "DCF现金流折现",
            "description": "预测未来自由现金流并折现",
            "applicable": "成熟稳定盈利企业"
        },
        "pe": {
            "name": "PE市盈率法",
            "description": "基于净利润的相对估值",
            "applicable": "上市公司、盈利稳定企业"
        },
        "pb": {
            "name": "PB市净率法",
            "description": "基于净资产的相对估值",
            "applicable": "金融机构、重资产企业"
        },
        "ps": {
            "name": "PS市销率法",
            "description": "基于营业收入的相对估值",
            "applicable": "成长期企业、互联网企业"
        },
        "asset": {
            "name": "资产基础法",
            "description": "基于资产负债表的评估",
            "applicable": "重资产企业、困境企业"
        },
        "comparable": {
            "name": "可比交易法",
            "description": "参考同类并购案例",
            "applicable": "所有类型企业"
        }
    }
    
    # 监管审查要点
    REGULATORY_RISKS = {
        "antitrust": {
            "name": "反垄断审查",
            "level": "high",
            "description": "经营者集中反垄断审查",
            "thresholds": {
                "china": "经营者营业额>40亿或全球营业额>100亿",
                "import": "境外并购涉及安全审查"
            }
        },
        "national_security": {
            "name": "国家安全审查",
            "level": "high",
            "description": "涉及关键领域的外资并购",
            "sensitive_sectors": ["国防、军工", "网络安全", "关键基础设施", "稀有资源"]
        },
        ".Cross_listing": {
            "name": "跨境审批",
            "level": "medium",
            "description": "境外并购需发改委/商务部审批",
            "requirements": ["ODI备案", "外汇登记", "国家安全审查"]
        },
        "minority_protection": {
            "name": "中小股东保护",
            "level": "medium",
            "description": "关联交易的公允性",
            "requirements": ["独立董事意见", "股东大会批准", "信息披露"]
        },
        "information_disclosure": {
            "name": "信息披露合规",
            "level": "low",
            "description": "重大资产重组信息披露",
            "requirements": ["预案披露", "进程公告", "最终报告"]
        }
    }
    
    # 交易风险库
    TRANSACTION_RISKS = {
        "high": [
            {
                "id": "TR001",
                "name": "估值泡沫风险",
                "description": "高溢价收购形成商誉泡沫",
                "suggestion": "充分尽职调查，合理确定估值"
            },
            {
                "id": "TR002",
                "name": "业绩对赌失败风险",
                "description": "业绩承诺无法实现导致商誉减值",
                "suggestion": "设置合理的业绩对赌条款"
            },
            {
                "id": "TR003",
                "name": "融资失败风险",
                "description": "并购融资不到位导致交易失败",
                "suggestion": "制定备选融资方案"
            }
        ],
        "medium": [
            {
                "id": "TR004",
                "name": "审批风险",
                "description": "监管审批存在不确定性",
                "suggestion": "提前与监管沟通，做好时间规划"
            },
            {
                "id": "TR005",
                "name": "整合风险",
                "description": "收购后业务整合不及预期",
                "suggestion": "制定详细的整合计划"
            },
            {
                "id": "TR006",
                "name": "核心人员流失",
                "description": "标的公司核心团队离职",
                "suggestion": "设计人员保留计划"
            }
        ],
        "low": [
            {
                "id": "TR007",
                "name": "税务风险",
                "description": "并购重组涉及税务成本",
                "suggestion": "提前进行税务筹划"
            },
            {
                "id": "TR008",
                "name": "交割风险",
                "description": "交割条件无法按期满足",
                "suggestion": "合理设置交割条件和时间表"
            }
        ]
    }
    
    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode
        self._log("初始化并购方案生成引擎 v%s" % self.VERSION)
    
    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)
    
    def parse_input(self, text: str) -> Dict[str, Any]:
        """
        解析用户输入，提取收购方、被收购方、交易目的
        
        Args:
            text: 用户输入文本
        
        Returns:
            解析结果
        """
        text = text.strip()
        
        # 尝试从文本中提取关键信息
        result = {
            "acquirer": None,
            "target": None,
            "purpose": None,
            "transaction_type": None,
            "raw_text": text
        }
        
        # 简单模式匹配
        patterns = [
            r"收购方[：:]\s*([^\s，,]+)",
            r"收购[方]?\s*([^\s，,]+)",
            r"甲方[：:]\s*([^\s，,]+)",
            r"被收购方[：:]\s*([^\s，,]+)",
            r"被收购[方]?\s*([^\s，,]+)",
            r"乙方[：:]\s*([^\s，,]+)",
            r"标的[：:]\s*([^\s，,]+)",
            r"目的[：:]\s*([^\s]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                result["target"] = match.group(1)
        
        # 识别交易结构
        for stype, info in self.TRANSACTION_TYPES.items():
            for keyword in [info["name"]] + info.get("sub_types", []):
                if keyword in text:
                    result["transaction_type"] = stype
                    break
        
        return result
    
    def generate_scheme(
        self,
        acquirer: str = None,
        target: str = None,
        purpose: str = None,
        transaction_type: str = None,
        target_revenue: float = None,
        target_net_income: float = None,
        target_net_assets: float = None,
        target_industry: str = None,
        deal_size: float = None,
        synergy_revenue: float = None,
        synergy_cost: float = None
    ) -> Dict[str, Any]:
        """
        生成并购方案
        
        Args:
            acquirer: 收购方
            target: 被收购方/标的
            purpose: 交易目的
            transaction_type: 交易结构类型
            target_revenue: 标的营业收入（万元）
            target_net_income: 标的净利润（万元）
            target_net_assets: 标的净资产（万元）
            target_industry: 标的所属行业
            deal_size: 交易规模（万元）
            synergy_revenue: 协同效应-收入（万元/年）
            synergy_cost: 协同效应-成本节约（万元/年）
        
        Returns:
            并购方案结果
        """
        # 默认值
        target = target or "标的公司"
        acquirer = acquirer or "收购方"
        purpose = purpose or "战略整合"
        target_industry = target_industry or "一般制造业"
        target_revenue = target_revenue or 10000  # 默认1亿营收
        target_net_income = target_net_income or 1000  # 默认1000万净利润
        target_net_assets = target_net_assets or 5000  # 默认5000万净资产
        
        # 生成交易结构方案
        structures = self._generate_structures(
            acquirer, target, transaction_type, deal_size, target_revenue
        )
        
        # 估值分析
        valuations = self._generate_valuations(
            target_revenue, target_net_income, target_net_assets, 
            target_industry, deal_size, synergy_revenue, synergy_cost
        )
        
        # 财务预测
        forecast = self._generate_forecast(
            target_revenue, target_net_income, 
            synergy_revenue, synergy_cost
        )
        
        # 风险识别
        risks = self._identify_risks(
            acquirer, target, target_industry, 
            structures, valuations
        )
        
        # 综合推荐
        recommendation = self._generate_recommendation(
            structures, valuations, risks
        )
        
        return {
            "acquirer": acquirer,
            "target": target,
            "purpose": purpose,
            "target_industry": target_industry,
            "structures": structures,
            "valuations": valuations,
            "forecast": forecast,
            "risks": risks,
            "recommendation": recommendation,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _generate_structures(
        self,
        acquirer: str,
        target: str,
        transaction_type: str,
        deal_size: float,
        target_revenue: float
    ) -> List[Dict[str, Any]]:
        """生成多种交易结构方案"""
        structures = []
        deal_size = deal_size or target_revenue * 2  # 默认2倍PS
        
        # 方案1：现金收购
        structures.append({
            "id": "S1",
            "type": "cash_acquisition",
            "name": "现金收购方案",
            "description": "收购方以现金支付全部对价",
            "payment": {
                "cash_ratio": 1.0,
                "stock_ratio": 0.0,
                "deal_size": deal_size,
                "currency": "人民币"
            },
            "lock_period": "无锁定期（现金）",
            "pros": ["交易简单快捷", "原股东快速退出", "无稀释效应"],
            "cons": ["收购方资金压力较大", "无法享受税务递延优惠", "无法绑定原股东"],
            "applicable": "收购方资金充裕、标的原股东急于套现"
        })
        
        # 方案2：股票对价
        structures.append({
            "id": "S2",
            "type": "stock_swap",
            "name": "股票对价方案",
            "description": "收购方定向增发股票作为对价",
            "payment": {
                "cash_ratio": 0.0,
                "stock_ratio": 1.0,
                "deal_size": deal_size,
                "currency": "人民币",
                "exchange_ratio": "按定价基准日收盘价确定"
            },
            "lock_period": "原股东12个月/认购方36个月",
            "pros": ["无资金压力", "绑定原股东利益", "享受税务递延"],
            "cons": ["股权稀释", "审批复杂", "交易周期长"],
            "applicable": "收购方股价较高、双方希望长期绑定"
        })
        
        # 方案3：混合支付
        structures.append({
            "id": "S3",
            "type": "mixed_payment",
            "name": "混合支付方案",
            "description": "现金+股票组合支付",
            "payment": {
                "cash_ratio": 0.5,
                "stock_ratio": 0.5,
                "cash_amount": deal_size * 0.5,
                "stock_amount": deal_size * 0.5,
                "currency": "人民币"
            },
            "lock_period": "现金部分无锁定期/股票部分12个月",
            "pros": ["资金压力分散", "利益绑定与税务优惠兼顾"],
            "cons": ["结构相对复杂", "两种方式缺点均沾"],
            "applicable": "平衡资金压力与股东绑定"
        })
        
        # 方案4：承债式收购
        if target_revenue > 5000:  # 中大型企业适用
            structures.append({
                "id": "S4",
                "type": "debt_assumption",
                "name": "承债式收购方案",
                "description": "承担目标公司债务，降低实际支付对价",
                "payment": {
                    "cash_ratio": 0.3,
                    "debt_assumption": 0.7,
                    "deal_size": deal_size,
                    "debt_amount": deal_size * 0.7
                },
                "lock_period": "视情况而定",
                "pros": ["降低现金支付压力", "债权人关系稳定"],
                "cons": ["接手债务风险", "谈判复杂"],
                "applicable": "负债率较高但有重组价值的标的"
            })
        
        return structures
    
    def _generate_valuations(
        self,
        revenue: float,
        net_income: float,
        net_assets: float,
        industry: str,
        deal_size: float,
        synergy_rev: float = None,
        synergy_cost: float = None
    ) -> Dict[str, Any]:
        """生成估值分析"""
        deal_size = deal_size or revenue * 2
        
        # 行业PE/PB/PS参考
        industry_multiples = {
            "互联网": {"pe": 30, "ps": 8, "pb": 5},
            "科技": {"pe": 25, "ps": 6, "pb": 4},
            "制造业": {"pe": 15, "ps": 2, "pb": 2},
            "金融": {"pe": 10, "ps": 3, "pb": 1},
            "医药": {"pe": 20, "ps": 4, "pb": 3},
            "消费": {"pe": 18, "ps": 3, "pb": 3},
            "房地产": {"pe": 8, "ps": 1, "pb": 1},
            "一般制造业": {"pe": 12, "ps": 2, "pb": 2}
        }
        
        multiples = industry_multiples.get(industry, {"pe": 15, "ps": 3, "pb": 2})
        
        # DCF参数
        wacc = 0.10  # 加权平均资本成本
        growth_rate = 0.05  # 永续增长率
        fcf = net_income * 0.8  # 假设FCF为净利润的80%
        
        # 估值计算
        pe_value = net_income * multiples["pe"]
        ps_value = revenue * multiples["ps"]
        pb_value = net_assets * multiples["pb"]
        dcf_value = fcf * (1 + growth_rate) / (wacc - growth_rate)
        
        # 可比交易折扣
        comparable_discount = 0.85  # 私营公司打折
        
        results = {
            "pe": {
                "method": "pe",
                "name": "市盈率法",
                "value": round(pe_value, 0),
                "multiple": multiples["pe"],
                "formula": f"{net_income:.0f}万 × {multiples['pe']} = {pe_value:.0f}万"
            },
            "ps": {
                "method": "ps",
                "name": "市销率法",
                "value": round(ps_value, 0),
                "multiple": multiples["ps"],
                "formula": f"{revenue:.0f}万 × {multiples['ps']} = {ps_value:.0f}万"
            },
            "pb": {
                "method": "pb",
                "name": "市净率法",
                "value": round(pb_value, 0),
                "multiple": multiples["pb"],
                "formula": f"{net_assets:.0f}万 × {multiples['pb']} = {pb_value:.0f}万"
            },
            "dcf": {
                "method": "dcf",
                "name": "DCF现金流折现",
                "value": round(dcf_value * comparable_discount, 0),
                "wacc": wacc,
                "growth_rate": growth_rate,
                "formula": f"FCF({fcf:.0f}万) × (1+{growth_rate}) / ({wacc}-{growth_rate}) × {comparable_discount}"
            }
        }
        
        # 综合估值
        values = [r["value"] for r in results.values()]
        results["summary"] = {
            "min": round(min(values) * 0.9, 0),
            "median": round(sum(values) / len(values), 0),
            "max": round(max(values) * 1.1, 0),
            "recommended": round(sum(values) / len(values), 0),
            "deal_size_proposed": deal_size
        }
        
        # 协同效应估值
        if synergy_rev or synergy_cost:
            syn_fcf = (synergy_rev or 0) * 0.7 + (synergy_cost or 0) * 0.8
            syn_value = syn_fcf * (1 + growth_rate) / (wacc - growth_rate)
            results["synergy"] = {
                "name": "协同效应估值",
                "value": round(syn_value * comparable_discount, 0),
                "revenue_synergy": synergy_rev or 0,
                "cost_synergy": synergy_cost or 0,
                "formula": f"收入协同({synergy_rev or 0}万)×0.7 + 成本协同({synergy_cost or 0}万)×0.8"
            }
        
        return results
    
    def _generate_forecast(
        self,
        base_revenue: float,
        base_profit: float,
        synergy_rev: float = None,
        synergy_cost: float = None
    ) -> Dict[str, Any]:
        """生成财务预测"""
        forecast_years = [1, 2, 3, 4, 5]
        base_profit_ratio = base_profit / base_revenue if base_revenue > 0 else 0.1
        
        rows = []
        cumulative_profit = 0
        
        for i, year in enumerate(forecast_years):
            # 假设收入增长15%，利润率逐步提升
            rev_growth = 1.15 if i == 0 else 1.10
            base_revenue *= rev_growth
            profit_margin = min(base_profit_ratio * (1 + i * 0.02), 0.20)  # 利润率逐步提升至20%
            
            revenue = base_revenue
            profit = revenue * profit_margin
            
            # 协同效应从第2年开始
            if year >= 2:
                syn_rev = (synergy_rev or 0) * 0.5
                syn_cost = (synergy_cost or 0) * 0.5
                revenue += syn_rev
                profit += syn_rev * 0.5 + syn_cost * 0.7
            
            cumulative_profit += profit
            
            rows.append({
                "year": year,
                "revenue": round(revenue, 0),
                "profit": round(profit, 0),
                "margin": round(profit_margin * 100, 1),
                "cumulative": round(cumulative_profit, 0)
            })
        
        return {
            "base_year_revenue": round(base_revenue / (1.15 ** 5), 0),
            "base_year_profit": round(base_revenue / (1.15 ** 5) * base_profit_ratio, 0),
            "forecast": rows,
            "assumptions": [
                "收入增长假设：第1年15%，第2-5年10%",
                "净利润率：逐年提升至20%",
                "协同效应：第2年起逐步释放"
            ]
        }
    
    def _identify_risks(
        self,
        acquirer: str,
        target: str,
        industry: str,
        structures: List[Dict],
        valuations: Dict
    ) -> Dict[str, Any]:
        """识别交易风险"""
        risks = []
        
        # 通用高风险
        for r in self.TRANSACTION_RISKS["high"]:
            risks.append({
                **r,
                "level": "high",
                "level_label": "🔴 高风险"
            })
        
        # 通用中风险
        for r in self.TRANSACTION_RISKS["medium"]:
            risks.append({
                **r,
                "level": "medium",
                "level_label": "🟡 中风险"
            })
        
        # 通用低风险
        for r in self.TRANSACTION_RISKS["low"]:
            risks.append({
                **r,
                "level": "low",
                "level_label": "🟢 低风险"
            })
        
        # 行业特定风险
        industry_specific = {
            "互联网": {
                "name": "用户数据合规风险",
                "level": "high",
                "description": "用户数据跨境或安全审查",
                "suggestion": "进行数据安全评估"
            },
            "金融": {
                "name": "金融牌照审查",
                "level": "high",
                "description": "牌照变更需监管审批",
                "suggestion": "提前与监管沟通"
            },
            "医药": {
                "name": "医药审批风险",
                "level": "medium",
                "description": "药品/器械审批不确定性",
                "suggestion": "评估产品管线进展"
            }
        }
        
        if industry in industry_specific:
            r = industry_specific[industry]
            risks.append({
                "id": f"IR_{industry}",
                **r,
                "level_label": "🔴 高风险" if r["level"] == "high" else "🟡 中风险"
            })
        
        # 估值风险
        summary = valuations.get("summary", {})
        deal_size = summary.get("deal_size_proposed", 0)
        median_val = summary.get("median", 0)
        
        if deal_size > median_val * 1.3:
            risks.append({
                "id": "VR001",
                "name": "估值偏高风险",
                "level": "high",
                "level_label": "🔴 高风险",
                "description": f"拟交易对价({deal_size:.0f}万)高于估值中位数({median_val:.0f}万)30%以上",
                "suggestion": "重新评估估值合理性或调整交易对价"
            })
        
        # 按等级分组
        risk_stats = {
            "high": len([r for r in risks if r["level"] == "high"]),
            "medium": len([r for r in risks if r["level"] == "medium"]),
            "low": len([r for r in risks if r["level"] == "low"])
        }
        
        return {
            "risks": risks,
            "risk_stats": risk_stats
        }
    
    def _generate_recommendation(
        self,
        structures: List[Dict],
        valuations: Dict,
        risks: Dict
    ) -> Dict[str, Any]:
        """生成方案推荐"""
        summary = valuations.get("summary", {})
        risk_stats = risks["risk_stats"]
        
        # 推荐方案
        recommended_structure = structures[2] if len(structures) > 2 else structures[0]  # 默认推荐混合方案
        
        # 推荐估值
        recommended_value = summary.get("recommended", 0)
        deal_size = summary.get("deal_size_proposed", recommended_value)
        
        # 风险评估
        if risk_stats["high"] >= 3:
            overall_risk = "high"
            risk_opinion = "本交易风险较高，建议充分尽职调查后再推进"
        elif risk_stats["high"] >= 1:
            overall_risk = "medium"
            risk_opinion = "本交易存在一定风险，需要重点关注高风险事项"
        else:
            overall_risk = "low"
            risk_opinion = "本交易整体风险可控"
        
        return {
            "recommended_structure": recommended_structure["name"],
            "structure_id": recommended_structure["id"],
            "recommended_value": recommended_value,
            "deal_size_range": {
                "min": summary.get("min", 0),
                "median": recommended_value,
                "max": summary.get("max", 0)
            },
            "proposed_deal_size": deal_size,
            "overall_risk": overall_risk,
            "risk_opinion": risk_opinion,
            "key_points": [
                "建议采用混合支付方案，平衡资金压力与股东利益绑定",
                f"交易对价建议控制在{summary.get('median', 0):.0f}万-{summary.get('max', 0):.0f}万区间",
                "需重点关注业绩对赌条款设计与商誉减值风险",
                "建议提前与监管机构沟通审批事宜"
            ]
        }
    
    def format_text(self, result: Dict) -> str:
        """格式化输出为文本"""
        lines = [
            f"📊 **并购方案生成报告**",
            f"",
            f"🏢 收购方: {result['acquirer']}",
            f"🎯 被收购方: {result['target']}",
            f"📋 交易目的: {result['purpose']}",
            f"🏭 所属行业: {result['target_industry']}",
            f"⏰ 生成时间: {result['generated_at']}",
            f"",
            f"{'='*40}",
            f"",
            f"📐 **一、交易结构方案**",
            f"",
        ]
        
        for s in result["structures"]:
            stock_info = ""
            if "stock_ratio" in s["payment"]:
                stock_info = f"  股票比例: {s['payment']['stock_ratio']*100:.0f}%\n"
            elif "debt_assumption" in s["payment"]:
                stock_info = f"  承债比例: {s['payment']['debt_assumption']*100:.0f}%\n"
            
            lines.extend([
                f"**方案{s['id']}：{s['name']}**",
                f"  描述: {s['description']}",
                f"  现金比例: {s['payment']['cash_ratio']*100:.0f}%",
                stock_info,
                f"  锁定期: {s['lock_period']}",
                f"  ✅ 优点: {', '.join(s['pros'][:2])}",
                f"  ❌ 缺点: {', '.join(s['cons'][:2])}",
                f"  适用: {s['applicable']}",
                f""
            ])
        
        # 估值分析
        vals = result["valuations"]
        v_sum = vals.get("summary", {})
        
        lines.extend([
            f"{'='*40}",
            f"",
            f"💰 **二、估值分析**",
            f"",
            f"| 方法 | 估值结果 | 倍数 | 公式 |",
            f"|------|---------|------|------|",
        ])
        
        for key in ["pe", "ps", "pb", "dcf"]:
            if key in vals:
                v = vals[key]
                lines.append(f"| {v['name']} | {v['value']:.0f}万 | {v.get('multiple', '-')} | {v.get('formula', '-')[:30]}... |")
        
        if "synergy" in vals:
            syn = vals["synergy"]
            lines.append(f"| 协同效应 | {syn['value']:.0f}万 | - | 收入+成本协同 |")
        
        lines.extend([
            f"",
            f"估值区间: **{v_sum.get('min', 0):.0f}万 ~ {v_sum.get('max', 0):.0f}万**",
            f"推荐估值: **{v_sum.get('median', 0):.0f}万**",
            f"拟交易对价: **{v_sum.get('deal_size_proposed', 0):.0f}万**",
        ])
        
        # 财务预测
        forecast = result["forecast"]
        lines.extend([
            f"",
            f"{'='*40}",
            f"",
            f"📈 **三、财务预测（5年）**",
            f"",
            f"| 年度 | 营业收入(万) | 净利润(万) | 利润率 | 累计净利润 |",
            f"|------|-------------|-----------|--------|----------|",
        ])
        
        for row in forecast["forecast"]:
            lines.append(
                f"| 第{row['year']}年 | {row['revenue']:,.0f} | {row['profit']:,.0f} | "
                f"{row['margin']:.1f}% | {row['cumulative']:,.0f} |"
            )
        
        lines.extend([
            f"",
            f"*假设: {chr(10).join(forecast['assumptions'])}*"
        ])
        
        # 风险提示
        risks = result["risks"]
        r_stats = risks["risk_stats"]
        
        lines.extend([
            f"",
            f"{'='*40}",
            f"",
            f"⚠️ **四、风险提示**",
            f"",
            f"风险统计: 🔴{r_stats['high']}个 🟡{r_stats['medium']}个 🟢{r_stats['low']}个",
            f"",
        ])
        
        high_risks = [r for r in risks["risks"] if r["level"] == "high"][:3]
        for r in high_risks:
            lines.extend([
                f"**{r['name']}** ({r['level_label']})",
                f"  {r['description']}",
                f"  💡 建议: {r['suggestion']}",
                f""
            ])
        
        # 推荐
        rec = result["recommendation"]
        lines.extend([
            f"{'='*40}",
            f"",
            f"✅ **五、综合推荐**",
            f"",
            f"推荐结构: **{rec['recommended_structure']}**",
            f"推荐估值: **{rec['recommended_value']:.0f}万**",
            f"交易对价区间: **{rec['deal_size_range']['min']:.0f}万 ~ {rec['deal_size_range']['max']:.0f}万**",
            f"综合风险: **{rec['overall_risk'].upper()}**",
            f"",
            f"📝 风险意见: {rec['risk_opinion']}",
            f"",
            f"**关键要点:**",
        ])
        
        for point in rec["key_points"]:
            lines.append(f"  • {point}")
        
        return '\n'.join(lines)
    
    def format_json(self, result: Dict) -> str:
        """格式化输出为JSON"""
        return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("🦞 并购方案生成引擎 v1.0")
    print("=" * 50)
    print()
    
    engine = MaSchemeEngine()
    
    # 测试示例
    result = engine.generate_scheme(
        acquirer="A上市公司",
        target="B科技公司",
        purpose="横向整合，提升技术实力",
        target_revenue=50000,  # 5亿营收
        target_net_income=5000,  # 5000万净利润
        target_net_assets=20000,  # 2亿净资产
        target_industry="互联网",
        deal_size=150000,  # 15亿交易规模
        synergy_revenue=5000,  # 5000万收入协同
        synergy_cost=3000   # 3000万成本协同
    )
    
    print(engine.format_text(result))


if __name__ == "__main__":
    main()
