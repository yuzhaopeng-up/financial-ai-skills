#!/usr/bin/env python3
"""
审计智能抽样 - 企微卡片集成

将审计抽样结果格式化为企业微信消息卡片，
支持通过企微API或wecom-mcp工具发送。
"""

import json
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path

# 尝试导入可选依赖
try:
    from企微 import WeComClient
    HAS_WECOM_SDK = True
except ImportError:
    HAS_WECOM_SDK = False


def format_wecom_card(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    将审计抽样结果格式化为企微消息卡片
    
    Args:
        result: audit_sampling_engine.generate() 返回的结果
        
    Returns:
        企微消息卡片JSON
    """
    plan = result["sampling_plan"]
    res = result["sampling_results"]
    findings = result["audit_findings"]
    conclusion = result["population_conclusion"]
    pop = result["population_summary"]
    
    # 判断审计意见颜色
    if "无保留" in conclusion["opinion_impact"]:
        opinion_color = "green"
        opinion_emoji = "✅"
    elif "保留" in conclusion["opinion_impact"]:
        opinion_color = "yellow"
        opinion_emoji = "⚠️"
    else:
        opinion_color = "red"
        opinion_emoji = "❌"
    
    # 格式化金额
    def fmt_amount(a: float) -> str:
        if abs(a) >= 100000000:
            return f"{a/100000000:.2f}亿"
        elif abs(a) >= 10000:
            return f"{a/10000:.2f}万"
        else:
            return f"{a:,.2f}"
    
    card = {
        "msgtype": "interactive",
        "card": {
            "header": {
                "title": f"📊 审计智能抽样报告 - {result['scenario']}",
                "banner": "",
                "color": opinion_color
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": (
                        "**【总体概况】**\n"
                        f"- 总体数量: **{pop['total_count']:,}** 件\n"
                        f"- 总体金额: **{fmt_amount(pop['total_amount'])}** 元\n"
                        f"- 风险等级: {pop['risk_level']}\n\n"
                        "**【抽样方案】**\n"
                        f"- 方法: **{plan['method']}**\n"
                        f"- 样本量: **{plan['sample_size']}** 件\n"
                        f"- 置信水平: **{plan['confidence_level']*100:.0f}%**\n"
                        f"- 可容忍误差: **{plan['tolerable_error_rate']*100:.1f}%**"
                    )
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "markdown",
                    "content": (
                        "**【抽样结果】**\n"
                        f"- 实际抽样: **{res['sample_size']}** 件\n"
                        f"- 发现问题: **{res['findings_count']}** 件 ({res['findings_rate']:.2f}%)\n"
                        f"- 问题金额: **{fmt_amount(res['findings_amount'])}** 元\n\n"
                        "**【误差推断】**\n"
                        f"- 估计误差率: **{findings['estimated_error_rate']:.2f}%**\n"
                        f"- 误差范围: {findings['error_rate_lower']:.2f}% ~ {findings['error_rate_upper']:.2f}%\n"
                        f"- 推断总体误差: **{fmt_amount(findings['projected_total_amount'])}** 元"
                    )
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "markdown",
                    "content": (
                        f"**{opinion_emoji} 【总体结论】**\n"
                        f"审计意见: **{conclusion['opinion_impact']}**\n"
                        f"{conclusion['recommendation']}\n\n"
                        f"📌 {pop['risk_level']} | {plan['method']} | "
                        f"置信{plan['confidence_level']*100:.0f}%"
                    )
                }
            ],
            "actions": [
                {
                    "tag": "button",
                    "text": "查看抽样明细",
                    "type": "view_more",
                    "expand": True
                }
            ],
            "extra": {
                "scene": "audit_sampling",
                "scenario": result["scenario"],
                "confidence": plan["confidence_level"]
            }
        }
    }
    
    return card


def format_wecom_text(result: Dict[str, Any]) -> str:
    """格式化文本消息（适用于企微文本消息）"""
    plan = result["sampling_plan"]
    res = result["sampling_results"]
    findings = result["audit_findings"]
    conclusion = result["population_conclusion"]
    pop = result["population_summary"]
    
    def fmt_amount(a: float) -> str:
        if abs(a) >= 100000000:
            return f"{a/100000000:.2f}亿"
        elif abs(a) >= 10000:
            return f"{a/10000:.2f}万"
        else:
            return f"{a:,.2f}"
    
    lines = [
        f"📊审计抽样报告 | {result['scenario']}",
        f"总体: {pop['total_count']:,}件 {fmt_amount(pop['total_amount'])}元 [{pop['risk_level']}]",
        f"抽样: {plan['method']} | 样本{plan['sample_size']}件 | 置信{plan['confidence_level']*100:.0f}%",
        f"结果: 发现{res['findings_count']}个问题 ({res['findings_rate']:.2f}%)",
        f"推断: 误差率{findings['estimated_error_rate']:.2f}% | 总体误差{fmt_amount(findings['projected_total_amount'])}元",
        f"结论: {conclusion['opinion_impact']}",
    ]
    
    return "\n".join(lines)


def send_wecom_card(
    card: Dict[str, Any],
    chat_id: Optional[str] = None,
    webhook_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    发送企微消息卡片
    
    Args:
        card: format_wecom_card() 返回的卡片JSON
        chat_id: 企微群聊ID（使用应用消息API时）
        webhook_url: 企微群机器人Webhook地址
        
    Returns:
        API响应结果
    """
    import urllib.request
    import urllib.error
    
    if webhook_url:
        # 使用Webhook发送
        data = json.dumps(card).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            return {"success": False, "error": str(e)}
    elif chat_id:
        # 使用应用API发送（需要access_token）
        # 此处返回占位，实际使用时需接入wecom-mcp
        return {
            "success": False,
            "error": "需要提供webhook_url或配置企微应用access_token",
            "note": "建议使用企微群机器人Webhook方式发送"
        }
    else:
        return {
            "success": False,
            "error": "请提供chat_id或webhook_url"
        }


class AuditSamplingWeCom:
    """审计抽样企微集成类"""
    
    def __init__(
        self,
        webhook_url: Optional[str] = None,
        chat_id: Optional[str] = None
    ):
        self.webhook_url = webhook_url
        self.chat_id = chat_id
    
    def send_result(
        self,
        result: Dict[str, Any],
        as_text: bool = False
    ) -> Dict[str, Any]:
        """发送审计抽样结果到企微"""
        if as_text:
            content = format_wecom_text(result)
            msg = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            return send_wecom_card(msg, webhook_url=self.webhook_url)
        else:
            card = format_wecom_card(result)
            return send_wecom_card(card, webhook_url=self.webhook_url)
    
    def preview(self, result: Dict[str, Any]) -> str:
        """预览企微卡片内容"""
        card = format_wecom_card(result)
        return json.dumps(card, ensure_ascii=False, indent=2)


def main():
    """CLI入口 - 测试发送"""
    import argparse
    import sys
    
    sys.path.insert(0, str(Path(__file__).parent))
    from audit_sampling_engine import AuditSamplingEngine
    
    parser = argparse.ArgumentParser(description="审计抽样企微集成")
    parser.add_argument("--webhook", "-w", help="企微Webhook地址")
    parser.add_argument("--query", "-q", default="审计抽样 发票总量10000张 总金额5000万 高风险业务", help="场景描述")
    parser.add_argument("--text", "-t", action="store_true", help="发送纯文本")
    args = parser.parse_args()
    
    # 生成抽样结果
    engine = AuditSamplingEngine(seed=42)
    result = engine.generate(
        scenario="发票审计",
        total_count=10000,
        total_amount=50000000,
        risk_level="高风险"
    )
    
    if args.webhook:
        # 发送到企微
        integration = AuditSamplingWeCom(webhook_url=args.webhook)
        resp = integration.send_result(result, as_text=args.text)
        print(json.dumps(resp, ensure_ascii=False, indent=2))
    else:
        # 仅预览卡片
        integration = AuditSamplingWeCom()
        print(integration.preview(result))


if __name__ == "__main__":
    main()
