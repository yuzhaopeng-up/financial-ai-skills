"""
quant_fund - 企微卡片集成
生成飞书/企微格式的分析报告卡片
"""

import json
from typing import Optional, Dict, Any
from .quant_engine import QuantFundAnalysis, QuantFundEngine


class WecomCardFormatter:
    """企微/飞书消息卡片格式化器"""

    @staticmethod
    def format_fund_analysis_card(analysis: QuantFundAnalysis) -> Dict[str, Any]:
        """
        生成基金分析报告的企微卡片格式
        
        返回适合企微 webhook 或 飞书 card 的数据结构
        """
        fe = analysis.factor_exposure
        sd = analysis.style_drift
        ba = analysis.brinson_attribution
        pa = analysis.performance_attribution
        
        # 预警颜色
        alert_color = {
            "LOW": "#36b37e",      # 绿色
            "MEDIUM": "#ffab00",   # 黄色
            "HIGH": "#ff5630"      # 红色
        }.get(sd.alert, "#cccccc")
        
        # 风险等级
        risk_level = {
            "LOW": "低风险",
            "MEDIUM": "中等风险",
            "HIGH": "高风险"
        }.get(sd.alert, "未知")
        
        card = {
            "msgtype": "interactive",
            "interactive": {
                "tag": "card",
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"📊 {analysis.fund_name} - 量化分析报告"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": f"**基金代码**: {analysis.fund_code}  |  **分析日期**: {analysis.analysis_date}"
                    },
                    {"tag": "hr"},
                    {
                        "tag": "markdown",
                        "content": "### 🎯 因子暴露"
                    },
                    {
                        "tag": "column_set",
                        "flex_mode": "between",
                        "elements": [
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**Alpha**\n`{fe.alpha:+.2%}`"},
                                ]
                            },
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**Beta**\n`{fe.beta:.2f}`"},
                                ]
                            },
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**SMB**\n`{fe.smb:+.2f}`"},
                                ]
                            },
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**HML**\n`{fe.hml:+.2f}`"},
                                ]
                            },
                        ]
                    },
                    {
                        "tag": "column_set",
                        "flex_mode": "between",
                        "elements": [
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**RMW**\n`{fe.rmw:+.2f}`"},
                                ]
                            },
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**CMA**\n`{fe.cma:+.2f}`"},
                                ]
                            },
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**MOM**\n`{fe.mom:+.2f}`"},
                                ]
                            },
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": "**动量**"},
                                ]
                            },
                        ]
                    },
                    {"tag": "hr"},
                    {
                        "tag": "markdown",
                        "content": "### 🔄 风格漂移检测"
                    },
                    {
                        "tag": "column_set",
                        "flex_mode": "between",
                        "elements": [
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**漂移得分**\n`{sd.drift_score:.2f}`"},
                                ]
                            },
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**预警级别**\n🟢 {risk_level}"},
                                ]
                            },
                        ]
                    },
                    {
                        "tag": "markdown",
                        "content": f"当前: 规模{sd.current_style.get('size',0):.0%} / 价值{sd.current_style.get('value',0):.0%} / 成长{sd.current_style.get('growth',0):.0%}\n"
                                   f"契约: 规模{sd.contract_style.get('size',0):.0%} / 价值{sd.contract_style.get('value',0):.0%} / 成长{sd.contract_style.get('growth',0):.0%}"
                    },
                    {"tag": "hr"},
                    {
                        "tag": "markdown",
                        "content": "### 📈 Brinson归因"
                    },
                    {
                        "tag": "column_set",
                        "flex_mode": "between",
                        "elements": [
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**选股效应**\n`{ba.selection_effect:+.2%}`"},
                                ]
                            },
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**配置效应**\n`{ba.allocation_effect:+.2%}`"},
                                ]
                            },
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**交互效应**\n`{ba.interaction_effect:+.2%}`"},
                                ]
                            },
                        ]
                    },
                    {"tag": "hr"},
                    {
                        "tag": "markdown",
                        "content": "### 💰 业绩归因"
                    },
                    {
                        "tag": "column_set",
                        "flex_mode": "between",
                        "elements": [
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**基准收益**\n`{pa.benchmark_return:+.2%}`"},
                                ]
                            },
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**因子贡献**\n`{pa.factor_contribution:+.2%}`"},
                                ]
                            },
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**选股贡献**\n`{pa.selection_contribution:+.2%}`"},
                                ]
                            },
                        ]
                    },
                    {
                        "tag": "column_set",
                        "flex_mode": "between",
                        "elements": [
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**配置贡献**\n`{pa.allocation_contribution:+.2%}`"},
                                ]
                            },
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**择时贡献**\n`{pa.timing_contribution:+.2%}`"},
                                ]
                            },
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": f"**基金净收益**\n`{pa.net_return:+.2%}`"},
                                ]
                            },
                            {
                                "tag": "column",
                                "width": "stretch",
                                "elements": [
                                    {"tag": "markdown", "content": "**---**"},
                                ]
                            },
                        ]
                    },
                ]
            }
        }
        
        return card

    @staticmethod
    def format_fund_summary_card(analysis: QuantFundAnalysis) -> Dict[str, Any]:
        """
        生成精简版基金摘要卡片
        适合企微群消息推送
        """
        fe = analysis.factor_exposure
        sd = analysis.style_drift
        pa = analysis.performance_attribution
        
        # 预警emoji
        alert_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}.get(sd.alert, "⚪")
        
        card = {
            "msgtype": "markdown",
            "markdown": {
                "content": (
                    f"## 📊 {analysis.fund_name}\n"
                    f"**{analysis.fund_code}** | {analysis.analysis_date}\n\n"
                    f"### 业绩表现\n"
                    f"- 基准收益: {pa.benchmark_return:+.2%}\n"
                    f"- 基金净收益: **{pa.net_return:+.2%}**\n"
                    f"- Alpha: {fe.alpha:+.2%}\n\n"
                    f"### 风格漂移 {alert_emoji} {sd.alert}\n"
                    f"漂移得分: `{sd.drift_score:.2f}` | "
                    f"规模: {sd.current_style.get('size',0):.0%} "
                    f"价值: {sd.current_style.get('value',0):.0%} "
                    f"成长: {sd.current_style.get('growth',0):.0%}"
                )
            }
        }
        
        return card

    def generate_and_format(
        self,
        fund_code: str,
        fund_name: Optional[str] = None,
        card_type: str = "full"
    ) -> Dict[str, Any]:
        """
        生成并格式化基金分析卡片
        
        Args:
            fund_code: 基金代码
            fund_name: 基金名称
            card_type: 卡片类型 full/summary
        """
        engine = QuantFundEngine()
        analysis = engine.analyze(fund_code, fund_name)
        
        if card_type == "summary":
            return self.format_fund_summary_card(analysis)
        else:
            return self.format_fund_analysis_card(analysis)


def generate_wecom_card(
    fund_code: str,
    fund_name: Optional[str] = None,
    card_type: str = "full"
) -> str:
    """
    生成企微卡片的便捷函数
    
    Args:
        fund_code: 基金代码（F000001格式）
        fund_name: 基金名称
        card_type: full/summary
        
    Returns:
        JSON字符串，可直接用于企微webhook
    """
    formatter = WecomCardFormatter()
    card = formatter.generate_and_format(fund_code, fund_name, card_type)
    return json.dumps(card, ensure_ascii=False)


# 导出
__all__ = [
    "WecomCardFormatter",
    "generate_wecom_card",
]
