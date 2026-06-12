# -*- coding: utf-8 -*-
"""
企业微信卡片集成 (WeChat Work Card Integration)
用于将发票查验结果以卡片形式推送至企业微信
"""

import json
from typing import Dict, Any, Optional


def build_invoice_card(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    将发票查验结果构建为企业微信卡片消息格式

    Args:
        result: InvoiceCheckEngine.check() 返回的查验结果

    Returns:
        企业微信消息卡片字典（可直接用于企微机器人推送）
    """

    status = result.get("status", "未知")
    confidence = result.get("confidence", 0.0)

    # 状态配色
    if status == "真票":
        status_color = "#36AF6B"   # 绿色
        status_emoji = "✅"
    elif status in ["假票", "失控发票"]:
        status_color = "#F53F3F"  # 红色
        status_emoji = "❌"
    elif status == "作废发票":
        status_color = "#F53F3F"
        status_emoji = "⚠️"
    elif status in ["红字发票", "超过认证期限"]:
        status_color = "#FF7A00"  # 橙色
        status_emoji = "🔔"
    else:
        status_color = "#888888"
        status_emoji = "❓"

    # 异常摘要
    anomalies = result.get("anomalies", [])
    high_count = sum(1 for a in anomalies if a.get("severity") == "high")
    med_count = sum(1 for a in anomalies if a.get("severity") == "medium")

    # 增值税抵扣
    vat = result.get("vat_deduction", {})
    can_deduct = vat.get("can_deduct", False)
    vat_text = f"✅ {vat.get('deduction_type', '正常抵扣')}" if can_deduct else f"❌ {vat.get('deduction_type', '不可抵扣')}"

    # 构建卡片elements
    elements = [
        {
            "tag": "markdown",
            "content": (
                f"**发票查验报告**\n"
                f"> 发票代码: `{result.get('invoice_code', '')}`\n"
                f"> 发票号码: `{result.get('invoice_number', '')}`"
            )
        },
        {
            "tag": "div",
            "text": {
                "tag": "plain_text",
                "content": " ",
                "css": {"color": "#dcdcdc"}
            }
        },
        {
            "tag": "markdown",
            "content": (
                f"**查验结果:** "
                f'<font color="{status_color}">{status_emoji} {status}</font>  "
                f"`置信度 {confidence*100:.1f}%`"
            )
        }
    ]

    # 异常详情
    if anomalies:
        anomaly_lines = []
        for a in anomalies[:5]:  # 最多显示5条
            sev = a.get("severity", "").upper()
            sev_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(sev, "⚪")
            anomaly_lines.append(f"{sev_icon}[{sev}] {a.get('type','')}: {a.get('description','')}")

        if anomaly_lines:
            elements.append({
                "tag": "markdown",
                "content": f"**🔍 异常提示({len(anomalies)}项)**\n" + "\n".join(anomaly_lines)
            })

    # 抵扣建议
    elements.append({
        "tag": "markdown",
        "content": (
            f"**💰 增值税抵扣建议**\n"
            f"> {vat_text}\n"
            f"> 原因: {vat.get('reason','')}"
        )
    })

    # 税务风险点
    risk_points = result.get("tax_risk_points", [])
    if risk_points:
        risk_lines = []
        for rp in risk_points[:3]:
            level = rp.get("risk_level", "low").upper()
            icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(level, "⚪")
            risk_lines.append(f"{icon} {rp.get('point','')}")

        if risk_lines:
            elements.append({
                "tag": "markdown",
                "content": f"**⚠️ 税务风险点**\n" + "\n".join(risk_lines)
            })

    # 底部提示
    elements.append({
        "tag": "markdown",
        "content": "⚠️ _本结果仅供参考，最终以主管税务机关认定为准_"
    })

    # 构建完整卡片
    card = {
        "msgtype": "interactive",
        "interactive": {
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"📄 发票查验 | {status_emoji} {status}",
                        "color": status_color
                    },
                    "emphasis": {
                        "title": {
                            "tag": "plain_text",
                            "content": f"📄 发票查验 | {status_emoji} {status}",
                            "color": status_color
                        }
                    }
                },
                "elements": elements
            }
        }
    }

    return card


def build_simple_text(result: Dict[str, Any]) -> str:
    """
    构建简化的文本消息格式（用于不支持卡片的场景）
    """
    status = result.get("status", "未知")
    confidence = result.get("confidence", 0.0)
    anomalies = result.get("anomalies", [])
    vat = result.get("vat_deduction", {})

    lines = [
        f"📄 发票查验报告",
        f"━━━━━━━━━━━━━━━",
        f"发票代码: {result.get('invoice_code','')}",
        f"发票号码: {result.get('invoice_number','')}",
        f"查验结果: {status} (置信度{confidence*100:.1f}%)",
    ]

    if anomalies:
        lines.append(f"⚠️ 异常提示({len(anomalies)}项):")
        for a in anomalies[:3]:
            lines.append(f"  [{a.get('severity','').upper()}] {a.get('type','')}")

    lines.extend([
        f"💰 抵扣建议: {'可以抵扣' if vat.get('can_deduct') else '不可抵扣'}",
        f"━━━━━━━━━━━━━━━",
        f"⚠️ 仅供参考，以税务机关认定为准"
    ])

    return "\n".join(lines)


def send_wecom_card(card: Dict[str, Any], webhook_url: Optional[str] = None) -> Dict[str, Any]:
    """
    发送企业微信卡片消息

    Args:
        card: build_invoice_card() 构建的卡片字典
        webhook_url: 企微机器人Webhook地址（可选，不提供则只返回卡片数据）

    Returns:
        发送结果字典
    """
    if not webhook_url:
        return {
            "success": True,
            "card": card,
            "message": "卡片已构建，未提供webhook_url"
        }

    import urllib.request
    import urllib.error

    data = json.dumps(card).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            response_data = json.loads(resp.read().decode("utf-8"))
            if response_data.get("errcode") == 0:
                return {"success": True, "message": "发送成功"}
            else:
                return {"success": False, "message": response_data.get("errmsg", "发送失败")}
    except urllib.error.URLError as e:
        return {"success": False, "message": f"网络错误: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"发送异常: {str(e)}"}


# CLI入口
if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from invoice_engine import InvoiceCheckEngine

    engine = InvoiceCheckEngine(api_mode=True)
    test_text = "发票查验 发票代码144031900360 号码44450123 开票日期2024-03-01 金额10万"
    result = engine.check_from_text(test_text)

    card = build_invoice_card(result)
    print(json.dumps(card, ensure_ascii=False, indent=2))
