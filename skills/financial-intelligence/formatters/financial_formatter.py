# -*- coding: utf-8 -*-
"""
财务场景格式化器 v1.0

继承BaseFormatter，提供6大财务场景的企微Markdown格式化
"""

import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

# 添加路径以导入BaseFormatter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "wecom", "formatters"))

from .base_formatter import BaseFormatter


class FinancialFormatter(BaseFormatter):
    """
    财务场景格式化器
    
    将6大财务引擎的结果格式化为企微Markdown消息
    """
    
    @staticmethod
    def format_invoice(result: Dict[str, Any]) -> str:
        """格式化发票查验结果"""
        if not result.get("success"):
            return f"⚠️ **发票查验失败**\n\n{result.get('message', '未知错误')}"
        
        status = result.get("status", "")
        lines = [f"## 🧾 发票查验结果", ""]
        
        if status == "valid":
            lines.extend([
                f"✅ **查验结果: 真票**",
                f"",
                f"| 项目 | 内容 |",
                f"|------|------|",
                f"| 发票代码 | {result.get('invoice_code', '-')} |",
                f"| 发票号码 | {result.get('invoice_no', '-')} |",
                f"| 发票类型 | {result.get('invoice_type', '-')} |",
                f"| 开票单位 | {result.get('seller_name', '-')} |",
                f"| 纳税人识别号 | {result.get('seller_tax_no', '-')} |",
                f"| 金额 | ¥{result.get('amount', 0):,.2f} |",
                f"| 税额 | ¥{result.get('tax_amount', 0):,.2f} |",
                f"| 价税合计 | **¥{result.get('total_amount', 0):,.2f}** |",
                f"| 开票日期 | {result.get('date', '-')} |",
                f"",
            ])
            
            # 明细
            items = result.get("items", [])
            if items:
                lines.extend(["**明细:**", ""])
                for item in items:
                    lines.append(f"• {item.get('name', '')}: ¥{item.get('amount', 0):,.2f} (税: ¥{item.get('tax', 0):,.2f})")
                lines.append("")
            
            # 合规
            compliance = result.get("compliance", {})
            comp_status = compliance.get("status", "未知")
            comp_emoji = "🟢" if comp_status == "合规" else "🟡" if comp_status == "需关注" else "🔴"
            lines.extend([
                f"### 📋 合规检查",
                f"",
                f"{comp_emoji} **合规状态**: {comp_status} (评分: {compliance.get('score', 0)}/100)",
                f"",
            ])
            
            flags = compliance.get("flags", [])
            for flag in flags:
                emoji = "🔴" if flag.get("level") == "error" else "🟡" if flag.get("level") == "warning" else "ℹ️"
                lines.append(f"{emoji} {flag.get('msg', '')}")
            
            if not flags:
                lines.append("✅ 无合规风险")
            
        else:
            lines.extend([
                f"❌ **查验结果: {result.get('reason', '异常')}**",
                f"",
                f"发票代码: {result.get('invoice_code', '-')}",
                f"发票号码: {result.get('invoice_no', '-')}",
                f"",
                f"⚠️ 该发票无法通过国家税务总局查验，请核实:",
                f"1. 发票代码和号码是否输入正确",
                f"2. 发票是否已作废或红冲",
                f"3. 开票日期是否超过5年",
            ])
        
        lines.extend(["", f"📡 查验来源: {result.get('verify_source', '-')}", ""])
        lines.append("---")
        lines.append("🦞 *龙马金融AI | 财务智能体*")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_budget(result: Dict[str, Any]) -> str:
        """格式化预算管控结果"""
        if not result.get("success"):
            return f"⚠️ **预算分析失败**\n\n{result.get('message', '未知错误')}"
        
        summary = result.get("summary", {})
        dept = result.get("dept", "全公司")
        
        lines = [
            f"## 📊 {dept} 预算执行报告",
            f"",
            f"**期间**: {result.get('period', '2026-Q2')}",
            f"",
            "---",
            f"",
            f"### 💰 总体情况",
            f"",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 预算总额 | ¥{summary.get('total_budget', 0):,.0f} |",
            f"| 已使用 | ¥{summary.get('total_spent', 0):,.0f} |",
            f"| 预计使用 | ¥{summary.get('total_forecast', 0):,.0f} |",
            f"| 当前执行率 | {summary.get('utilization', 0)}% |",
            f"| 预计执行率 | {summary.get('forecast_utilization', 0)}% |",
            f"",
        ]
        
        # 各科目
        categories = result.get("categories", [])
        if categories:
            lines.extend(["### 📋 科目明细", ""])
            lines.append("| 科目 | 预算 | 已用 | 预计 | 状态 |")
            lines.append("|------|------|------|------|------|")
            
            for cat in categories:
                status_emoji = "🟢" if cat.get("status") == "正常" else "🟡" if cat.get("status") == "接近上限" else "🔴"
                lines.append(
                    f"| {cat.get('name', '-')} | "
                    f"¥{cat.get('budget', 0):,.0f} | "
                    f"¥{cat.get('spent', 0):,.0f} | "
                    f"¥{cat.get('forecast', 0):,.0f} | "
                    f"{status_emoji} {cat.get('status', '-')} |"
                )
            lines.append("")
        
        # 预警
        warnings = result.get("warnings", [])
        if warnings:
            lines.extend(["### ⚠️ 预警信息", ""])
            for w in warnings:
                emoji = "🔴" if w.get("level") == "high" else "🟡"
                lines.append(f"{emoji} **{w.get('category', '')}**: {w.get('message', '')}")
            lines.append("")
        
        # 建议
        recommendations = result.get("recommendations", [])
        if recommendations:
            lines.extend(["### 💡 管控建议", ""])
            for rec in recommendations:
                lines.append(f"{rec}")
            lines.append("")
        
        lines.extend(["---", "🦞 *龙马金融AI | 财务智能体*"])
        return "\n".join(lines)
    
    @staticmethod
    def format_report(result: Dict[str, Any]) -> str:
        """格式化财报速读结果"""
        if not result.get("success"):
            return f"⚠️ **财报分析失败**\n\n{result.get('message', '未知错误')}"
        
        summary = result.get("summary", {})
        company = result.get("company_name", "未知公司")
        year = result.get("year", 2025)
        
        lines = [
            f"## 📊 {company} {year}年报速读",
            f"",
            "---",
            f"",
            f"### 🎯 速读结论",
            f"",
            f"> **{result.get('conclusion', '分析完成')}**",
            f"",
            f"### 💰 核心指标",
            f"",
            f"| 指标 | 数值 | 同比 |",
            f"|------|------|------|",
        ]
        
        revenue = summary.get("revenue", 0)
        revenue_yoy = summary.get("revenue_yoy", 0)
        profit = summary.get("net_profit", 0)
        profit_yoy = summary.get("net_profit_yoy", 0)
        
        lines.append(f"| 营业收入 | ¥{revenue:,.0f}亿 | {revenue_yoy:+.1f}% |")
        lines.append(f"| 净利润 | ¥{profit:,.0f}亿 | {profit_yoy:+.1f}% |")
        
        if summary.get("gross_margin"):
            lines.append(f"| 毛利率 | {summary['gross_margin']}% | - |")
        if summary.get("roe"):
            lines.append(f"| ROE | {summary['roe']}% | - |")
        if summary.get("debt_ratio"):
            lines.append(f"| 资产负债率 | {summary['debt_ratio']}% | - |")
        if summary.get("eps"):
            lines.append(f"| 每股收益 | ¥{summary['eps']} | - |")
        
        lines.append("")
        
        # 亮点
        highlights = result.get("highlights", [])
        if highlights:
            lines.extend(["### ✨ 亮点", ""])
            for h in highlights:
                lines.append(f"• {h}")
            lines.append("")
        
        # 风险
        risks = result.get("risks", [])
        if risks:
            lines.extend(["### ⚠️ 风险关注", ""])
            for r in risks:
                lines.append(f"• {r}")
            lines.append("")
        
        # 行业排名
        rank = result.get("industry_rank", {})
        if rank:
            lines.extend(["### 🏆 行业排名", ""])
            for k, v in rank.items():
                lines.append(f"• {k}: 第{v}位")
            lines.append("")
        
        lines.extend(["---", "🦞 *龙马金融AI | 财务智能体*"])
        return "\n".join(lines)
    
    @staticmethod
    def format_tax(result: Dict[str, Any]) -> str:
        """格式化税务筹划结果"""
        if not result.get("success"):
            return f"⚠️ **税务分析失败**\n\n{result.get('message', '未知错误')}"
        
        summary = result.get("summary", {})
        company = result.get("company_name", "未知公司")
        
        lines = [
            f"## 🏛️ {company} 税务筹划分析",
            f"",
            f"**税务年度**: {result.get('tax_year', 2025)}",
            f"",
            "---",
            f"",
            f"### 💰 税负概况",
            f"",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 营业收入 | ¥{summary.get('total_revenue', 0):,.0f} |",
            f"| 税费合计 | ¥{summary.get('total_tax', 0):,.0f} |",
            f"| 实际税负率 | {summary.get('effective_rate', 0)}% |",
            f"| 行业平均 | {summary.get('industry_avg_rate', 0)}% |",
            f"| 税负水平 | {summary.get('tax_burden_level', '-')} |",
            f"",
        ]
        
        # 税费明细
        tax_breakdown = result.get("tax_breakdown", {})
        if tax_breakdown:
            lines.extend(["### 📋 税费明细", ""])
            for tax_name, amount in tax_breakdown.items():
                lines.append(f"• {tax_name}: ¥{amount:,.0f}")
            lines.append("")
        
        # 优惠政策
        policies = result.get("policies", [])
        if policies:
            lines.extend(["### 🎁 适用优惠政策", ""])
            for p in policies:
                status = "✅ 已享受" if p.get("applicable") else "📋 可适用"
                lines.append(
                    f"• **{p.get('name', '-')}** ({p.get('type', '-')})\n"
                    f"  {status} | 优惠税率: {p.get('rate', 0)}% | 有效期至: {p.get('valid_until', '-')}\n"
                    f"  条件: {p.get('condition', '-')}"
                )
            lines.append("")
        
        # 节税空间
        savings = result.get("savings_opportunities", [])
        if savings:
            lines.extend(["### 💡 节税空间", ""])
            for s in savings:
                priority_emoji = "🔴" if s.get("priority") == "高" else "🟡"
                lines.append(
                    f"{priority_emoji} **{s.get('policy', '-')}**: "
                    f"预计可节税 ¥{s.get('potential_saving', 0):,.0f} "
                    f"(税率 {s.get('current_rate', 0)}% → {s.get('new_rate', 0)}%)"
                )
            lines.append("")
        
        # 合规
        compliance = result.get("compliance", {})
        comp_status = compliance.get("status", "未知")
        comp_emoji = "🟢" if comp_status == "合规" else "🟡" if comp_status == "需关注" else "🔴"
        lines.extend([
            f"### 📊 合规评分",
            f"",
            f"{comp_emoji} **{comp_status}** (评分: {compliance.get('score', 0)}/100)",
            f"",
        ])
        
        # 建议
        recommendations = result.get("recommendations", [])
        if recommendations:
            lines.extend(["### 📝 筹划建议", ""])
            for rec in recommendations:
                lines.append(f"{rec}")
            lines.append("")
        
        lines.extend(["---", "🦞 *龙马金融AI | 财务智能体*"])
        return "\n".join(lines)
    
    @staticmethod
    def format_expense(result: Dict[str, Any]) -> str:
        """格式化费用报销结果"""
        if not result.get("success"):
            return f"⚠️ **报销处理失败**\n\n{result.get('message', '未知错误')}"
        
        expense = result.get("expense", {})
        compliance = result.get("compliance", {})
        approval = result.get("approval", {})
        duplicate = result.get("duplicate_check", {})
        
        status_emoji = "🟢" if approval.get("status") == "通过" else "🟡" if approval.get("status") == "需核实" else "🔴"
        
        lines = [
            f"## 📝 费用报销审核",
            f"",
            f"### 📄 报销信息",
            f"",
            f"| 项目 | 内容 |",
            f"|------|------|",
            f"| 费用描述 | {expense.get('description', '-')} |",
            f"| 金额 | ¥{expense.get('amount', 0):,.2f} |",
            f"| 日期 | {expense.get('date', '-')} |",
            f"| 智能分类 | {expense.get('category', '-')} |",
            f"",
            f"### 📋 审核结果",
            f"",
            f"{status_emoji} **审批状态**: {approval.get('status', '待处理')}",
            f"📊 **审批级别**: {approval.get('level', '-')}",
            f"👥 **审批人**: {', '.join(approval.get('approvers', []))}",
            f"⏱️ **预计耗时**: {approval.get('estimated_time', '-')}",
            f"",
        ]
        
        # 合规
        lines.extend(["### ✅ 合规检查", ""])
        if compliance.get("passed"):
            lines.append(f"🟢 合规通过 (评分: {compliance.get('score', 0)}/100)")
        else:
            lines.append(f"🔴 合规未通过 (评分: {compliance.get('score', 0)}/100)")
        
        flags = compliance.get("flags", [])
        for flag in flags:
            emoji = "🔴" if flag.get("level") == "error" else "🟡"
            lines.append(f"{emoji} {flag.get('msg', '')}")
        lines.append("")
        
        # 重复检测
        lines.extend(["### 🔍 重复检测", ""])
        if duplicate.get("is_duplicate"):
            lines.append(f"⚠️ {duplicate.get('message', '疑似重复')}")
        else:
            lines.append(f"✅ {duplicate.get('message', '未检测到重复')}")
        lines.append("")
        
        # 建议
        recommendations = result.get("recommendations", [])
        if recommendations:
            lines.extend(["### 💡 处理建议", ""])
            for rec in recommendations:
                lines.append(f"{rec}")
            lines.append("")
        
        lines.extend(["---", "🦞 *龙马金融AI | 财务智能体*"])
        return "\n".join(lines)
    
    @staticmethod
    def format_cashflow(result: Dict[str, Any]) -> str:
        """格式化资金预测结果"""
        if not result.get("success"):
            return f"⚠️ **资金预测失败**\n\n{result.get('message', '未知错误')}"
        
        summary = result.get("summary", {})
        company = result.get("company", "未知公司")
        dates = result.get("forecast_dates", {})
        
        lines = [
            f"## 💰 {company} 资金预测",
            f"",
            f"**预测期间**: {dates.get('start', '-')} ~ {dates.get('end', '-')}",
            f"",
            "---",
            f"",
            f"### 📊 预测概要",
            f"",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 期初余额 | ¥{summary.get('starting_balance', 0):,.0f} |",
            f"| 预测最低 | ¥{summary.get('projected_lowest', 0):,.0f} |",
            f"| 预测最高 | ¥{summary.get('projected_highest', 0):,.0f} |",
            f"| 日均流入 | ¥{summary.get('avg_daily_inflow', 0):,.0f} |",
            f"| 日均流出 | ¥{summary.get('avg_daily_outflow', 0):,.0f} |",
            f"| 日均净流 | {'+' if summary.get('net_daily_flow', 0) >= 0 else ''}¥{summary.get('net_daily_flow', 0):,.0f} |",
            f"",
        ]
        
        # 日明细（前7天）
        forecast = result.get("daily_forecast", [])
        if forecast:
            lines.extend(["### 📅 近7日资金预测", ""])
            lines.append("| 日期 | 流入 | 流出 | 净额 | 余额 | 状态 |")
            lines.append("|------|------|------|------|------|------|")
            
            for day in forecast[:7]:
                alert_emoji = "🔴" if day.get("alert") else "🟢"
                lines.append(
                    f"| {day.get('date', '-')} | "
                    f"¥{day.get('inflow', 0):,.0f} | "
                    f"¥{day.get('outflow', 0):,.0f} | "
                    f"{'+' if day.get('net', 0) >= 0 else ''}¥{day.get('net', 0):,.0f} | "
                    f"¥{day.get('balance', 0):,.0f} | "
                    f"{alert_emoji} |"
                )
            lines.append("")
        
        # 缺口
        gaps = result.get("gaps", [])
        if gaps:
            lines.extend(["### 🚨 资金缺口预警", ""])
            for gap in gaps[:5]:  # 最多显示5个
                severity_emoji = "🔴" if gap.get("severity") == "严重" else "🟡" if gap.get("severity") == "中等" else "🟠"
                lines.append(
                    f"{severity_emoji} **{gap.get('date', '-')}**: "
                    f"余额¥{gap.get('balance', 0):,.0f}，"
                    f"缺口¥{gap.get('shortfall', 0):,.0f} "
                    f"({gap.get('severity', '-')})"
                )
            lines.append("")
        
        # 建议
        recommendations = result.get("recommendations", [])
        if recommendations:
            lines.extend(["### 💡 调度建议", ""])
            for rec in recommendations:
                lines.append(f"{rec}")
            lines.append("")
        
        lines.extend(["---", "🦞 *龙马金融AI | 财务智能体*"])
        return "\n".join(lines)
    
    @staticmethod
    def format_welcome() -> str:
        """财务智能体欢迎消息"""
        return """🦞 **龙马金融AI — 财务智能体**

我是您的AI财务助手，提供6大财务场景智能服务：

🧾 **发票查验** — 发票识别、真伪校验、合规审查
📊 **预算管控** — 预算跟踪、偏差分析、超支预警  
📈 **财报速读** — 关键指标提取、趋势分析、风险扫描
🏛️ **税务筹划** — 税负分析、优惠匹配、节税建议
📝 **费用报销** — 智能分类、合规检查、审批建议
💰 **资金预测** — 现金流建模、缺口预警、调度建议

**使用示例：**
```
查验发票 011001900111 12345678
市场部Q2预算情况
速读示例制造集团2025年报
分析银联商务税务状况
报销 差旅费 580元
预测未来30天现金流
```

输入"帮助"查看详细指南"""
    
    @staticmethod
    def format_help() -> str:
        """财务智能体帮助消息"""
        return """🦞 **财务智能体 — 使用指南**

**快捷指令：**
• `/发票` — 发票查验
• `/预算` — 预算管控
• `/财报` — 财报速读
• `/税务` — 税务筹划
• `/报销` — 费用报销
• `/资金` — 资金预测

**详细用法：**

🧾 **发票查验**
```
查验发票 [代码] [号码]
例如: 查验发票 011001900111 12345678
```

📊 **预算管控**
```
[部门]预算[期间]
例如: 市场部Q2预算
技术部预算执行情况
```

📈 **财报速读**
```
速读[公司][年份]年报
例如: 速读示例制造集团2025年报
对比 示例制造集团 vs 示例制造集团B
```

🏛️ **税务筹划**
```
分析[公司]税务
例如: 分析银联商务税务状况
```

📝 **费用报销**
```
报销 [描述] [金额]
例如: 报销 北京出差机票 1580
```

💰 **资金预测**
```
预测[天数]天现金流
例如: 预测30天现金流
```

---
🦞 *龙马金融AI v1.0 | 财务智能体*"""
