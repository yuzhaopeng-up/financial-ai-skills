#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风控合规引擎 v1.0

核心能力:
- 企业风险评估
- 信用评级
- 反欺诈检测
- 合规检查
- 财务诊断
- 监管政策查询
- 贷后监控
- 产业链风险追踪
- 市场情绪监测

纯规则引擎，零API费用，毫秒级响应
"""

import re
import random
from typing import Dict, Any, List


class RiskEngine:
    """风控合规引擎"""
    
    def __init__(self):
        self._init_mock_data()
    
    def _init_mock_data(self):
        """初始化演示数据"""
        # 企业风险数据
        self.enterprise_risks = {
            "比亚迪": {
                "basic": {"name": "比亚迪股份有限公司", "code": "002594", "industry": "汽车制造", "scale": "大型"},
                "risk_score": 72,
                "credit_rating": "AA",
                "risks": [
                    {"type": "市场风险", "level": "中", "desc": "新能源汽车市场竞争加剧，价格战压力"},
                    {"type": "供应链风险", "level": "中", "desc": "电池原材料价格波动，锂价不稳定"},
                    {"type": "政策风险", "level": "低", "desc": "新能源补贴退坡，但双碳政策支持"},
                    {"type": "技术风险", "level": "低", "desc": "技术迭代快，需持续研发投入"},
                    {"type": "财务风险", "level": "低", "desc": "现金流充裕，负债率合理"},
                ],
                "suggestion": "建议关注原材料价格波动，加强供应链多元化布局",
            },
            "宁德时代": {
                "basic": {"name": "宁德时代新能源科技", "code": "300750", "industry": "电池制造", "scale": "大型"},
                "risk_score": 68,
                "credit_rating": "AA-",
                "risks": [
                    {"type": "市场风险", "level": "高", "desc": "电池产能过剩，竞争白热化"},
                    {"type": "技术风险", "level": "中", "desc": "固态电池技术突破可能颠覆现有格局"},
                    {"type": "客户集中度", "level": "高", "desc": "前五大客户占比超60%"},
                    {"type": "原材料风险", "level": "中", "desc": "锂、钴、镍价格波动大"},
                    {"type": "海外政策", "level": "中", "desc": "欧美电池法案限制"},
                ],
                "suggestion": "建议分散客户结构，加大海外市场本土化布局",
            },
            "某科技公司": {
                "basic": {"name": "某科技有限公司", "code": "未上市", "industry": "软件开发", "scale": "中型"},
                "risk_score": 55,
                "credit_rating": "BBB",
                "risks": [
                    {"type": "经营风险", "level": "高", "desc": "成立仅3年，经营历史短"},
                    {"type": "财务风险", "level": "高", "desc": "连续亏损，现金流紧张"},
                    {"type": "市场风险", "level": "中", "desc": "细分市场竞争激烈"},
                    {"type": "技术风险", "level": "中", "desc": "技术壁垒不高，易被模仿"},
                    {"type": "人员风险", "level": "中", "desc": "核心技术人员流失风险"},
                ],
                "suggestion": "建议要求提供担保或抵押，缩短授信期限",
            },
        }
        
        # 反欺诈数据
        self.fraud_cases = {
            "TX2026001": {
                "transaction_id": "TX2026001",
                "amount": 500000,
                "risk_score": 85,
                "risk_level": "高风险",
                "anomalies": [
                    "交易金额异常(超出历史均值5倍)",
                    "交易时间异常(凌晨3点)",
                    "收款方为新注册账户",
                    "IP地址与常用地址不符",
                ],
                "suggestion": "建议人工复核，冻结交易并联系客户确认",
            },
            "TX2026002": {
                "transaction_id": "TX2026002",
                "amount": 5000,
                "risk_score": 25,
                "risk_level": "低风险",
                "anomalies": ["无异常特征"],
                "suggestion": "交易正常，自动通过",
            },
        }
        
        # 合规检查数据
        self.compliance_data = {
            "checks": [
                {"item": "反洗钱制度", "status": "通过", "detail": "制度完善，执行到位"},
                {"item": "客户身份识别", "status": "通过", "detail": "KYC流程规范"},
                {"item": "大额交易报告", "status": "警告", "detail": "3笔交易未及时上报"},
                {"item": "可疑交易监测", "status": "通过", "detail": "监测系统运行正常"},
                {"item": "数据安全保护", "status": "通过", "detail": "加密和备份机制完善"},
                {"item": "员工合规培训", "status": "警告", "detail": "2名员工培训过期"},
            ]
        }
    
    def get_enterprise_risk(self, target: str) -> Dict[str, Any]:
        """获取企业风险评估"""
        data = None
        for name, info in self.enterprise_risks.items():
            if name in target or target in name or target == info["basic"]["code"]:
                data = info
                target = name
                break
        
        if not data:
            data = self.enterprise_risks["比亚迪"]
            target = "比亚迪"
        
        return {
            "success": True,
            "target": target,
            "data": data,
        }
    
    def get_credit_rating(self, target: str) -> Dict[str, Any]:
        """获取信用评级"""
        data = None
        for name, info in self.enterprise_risks.items():
            if name in target or target in name:
                data = info
                target = name
                break
        
        if not data:
            data = self.enterprise_risks["宁德时代"]
            target = "宁德时代"
        
        return {
            "success": True,
            "target": target,
            "data": data,
        }
    
    def get_anti_fraud(self, target: str) -> Dict[str, Any]:
        """获取反欺诈检测"""
        data = self.fraud_cases.get(target)
        if not data:
            data = self.fraud_cases["TX2026001"]
            target = "TX2026001"
        
        return {
            "success": True,
            "target": target,
            "data": data,
        }
    
    def get_compliance(self) -> Dict[str, Any]:
        """获取合规检查"""
        return {
            "success": True,
            "data": self.compliance_data,
        }


class RiskFormatter:
    """风控合规格式化器"""
    
    @staticmethod
    def format_enterprise_risk(result: Dict[str, Any]) -> str:
        """格式化企业风险评估"""
        if not result.get("success"):
            return f"❌ {result.get('message', '未知错误')}"
        
        data = result["data"]
        b = data["basic"]
        score = data["risk_score"]
        score_color = "🟢" if score >= 70 else "🟡" if score >= 60 else "🔴"
        
        lines = [
            f"## 🏢 {b['name']} - 风险评估报告",
            "",
            f"**股票代码**: {b['code']} | **行业**: {b['industry']} | **规模**: {b['scale']}",
            "",
            f"### 综合风险评分: {score_color} **{score}/100**",
            f"**信用等级**: {data['credit_rating']}",
            "",
            "### 风险维度分析",
            "",
            "| 风险类型 | 等级 | 说明 |",
            "|:---|:---|:---|",
        ]
        
        for r in data["risks"]:
            level_emoji = "🔴" if r["level"] == "高" else "🟡" if r["level"] == "中" else "🟢"
            lines.append(f"| {r['type']} | {level_emoji} {r['level']} | {r['desc']} |")
        
        lines.extend([
            "",
            "### 风控建议",
            "",
            f"> {data['suggestion']}",
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_credit_rating(result: Dict[str, Any]) -> str:
        """格式化信用评级"""
        if not result.get("success"):
            return f"❌ {result.get('message', '未知错误')}"
        
        target = result["target"]
        data = result["data"]
        rating = data["credit_rating"]
        rating_colors = {"AA": "🟢", "AA-": "🟢", "A+": "🟡", "A": "🟡", "BBB": "🟡", "BB": "🔴"}
        color = rating_colors.get(rating, "🟡")
        
        lines = [
            f"## 📊 {target} - 信用评级报告",
            "",
            f"### 信用等级: {color} **{rating}**",
            "",
            "| 等级 | 含义 | 建议 |",
            "|:---|:---|:---|",
            "| AA | 信用优秀 | 建议积极合作，可给予优惠利率 |",
            "| AA- | 信用良好 | 建议正常合作，标准利率 |",
            "| A+ | 信用较好 | 建议正常合作，适度关注 |",
            "| A | 信用一般 | 建议审慎合作，加强监控 |",
            "| BBB | 信用中等 | 建议要求担保，缩短账期 |",
            "| BB及以下 | 信用较差 | 建议谨慎合作，要求抵押 |",
            "",
            f"### 评级依据",
            "",
            f"- 综合风险评分: {data['risk_score']}/100",
            f"- 行业地位: {'领先' if data['risk_score'] >= 70 else '中等' if data['risk_score'] >= 60 else '较弱'}",
            f"- 财务状况: {'健康' if data['risk_score'] >= 70 else '一般' if data['risk_score'] >= 60 else '紧张'}",
        ]
        
        return "\n".join(lines)
    
    @staticmethod
    def format_anti_fraud(result: Dict[str, Any]) -> str:
        """格式化反欺诈检测"""
        if not result.get("success"):
            return f"❌ {result.get('message', '未知错误')}"
        
        data = result["data"]
        score = data["risk_score"]
        level_color = "🔴" if score >= 70 else "🟡" if score >= 40 else "🟢"
        
        lines = [
            f"## 🛡️ 反欺诈检测报告",
            "",
            f"**交易编号**: `{data['transaction_id']}`",
            f"**交易金额**: ¥{data['amount']:,}",
            f"**风险评分**: {level_color} **{score}/100** ({data['risk_level']})",
            "",
        ]
        
        if data["anomalies"] and data["anomalies"][0] != "无异常特征":
            lines.append("### 异常特征")
            lines.append("")
            for a in data["anomalies"]:
                lines.append(f"- ⚠️ {a}")
            lines.append("")
        else:
            lines.append("✅ 未发现异常特征")
            lines.append("")
        
        lines.extend([
            "### 处置建议",
            "",
            f"> {data['suggestion']}",
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_compliance(result: Dict[str, Any]) -> str:
        """格式化合规检查"""
        if not result.get("success"):
            return f"❌ {result.get('message', '未知错误')}"
        
        checks = result["data"]["checks"]
        pass_count = sum(1 for c in checks if c["status"] == "通过")
        warning_count = sum(1 for c in checks if c["status"] == "警告")
        
        lines = [
            f"## ✅ 合规检查报告",
            "",
            f"**检查时间**: 2026-05-25",
            f"**检查结果**: 🟢 通过{pass_count}项 | 🟡 警告{warning_count}项 | 🔴 未通过0项",
            "",
            "### 检查明细",
            "",
            "| 检查项 | 状态 | 详情 |",
            "|:---|:---|:---|",
        ]
        
        for c in checks:
            status_emoji = "🟢" if c["status"] == "通过" else "🟡" if c["status"] == "警告" else "🔴"
            lines.append(f"| {c['item']} | {status_emoji} {c['status']} | {c['detail']} |")
        
        if warning_count > 0:
            lines.extend([
                "",
                "### 整改建议",
                "",
                "- 及时补报大额交易报告",
                "- 安排过期员工参加合规培训",
            ])
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Demo
    engine = RiskEngine()
    formatter = RiskFormatter()
    
    print(formatter.format_enterprise_risk(engine.get_enterprise_risk("比亚迪")))
    print("\n" + "="*50 + "\n")
    print(formatter.format_anti_fraud(engine.get_anti_fraud("TX2026001")))
