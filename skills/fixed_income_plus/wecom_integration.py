"""
企微卡片集成模块
生成固收+分析报告的企微消息卡片
"""

import json
import os
from typing import Dict, Any


def _safe(v, decimals=2):
    """安全转换数值"""
    try:
        return round(float(v), decimals)
    except (TypeError, ValueError):
        return v


def generate_wecom_card(report) -> Dict[str, Any]:
    """
    将固收+分析报告转换为企微卡片格式

    Args:
        report: FIPlusReport 对象

    Returns:
        企微卡片 JSON 结构
    """
    rd = report.return_decomposition
    ds = report.duration_strategy
    cr = report.credit_risk
    al = report.allocation
    pc = report.pure_bond_comparison

    # 主标题
    title = f"📊 固收+分析报告 | {report.portfolio_amount/10000:.1f}亿 | 久期{report.duration:.1f}Y"

    # 收益分解行
    return_summary = (
        f"总收益 {rd.total_return:.2f}% | "
        f"票息 {rd.carry_return:.2f}% | "
        f"资本利得 {rd.capital_gain:.2f}%"
    )

    # 预警信息（如果有）
    warning_lines = []
    if cr and cr.warning_flag:
        warning_lines.append(f"⚠️ {cr.warning_message}")

    # 期限分布文本
    tenor_text = ""
    if ds:
        tenor_items = [f"{k}:{v}%" for k, v in ds.allocation_by_tenor.items() if v > 0]
        tenor_text = " | ".join(tenor_items[:4])

    # 配置比例文本
    alloc_text = ""
    if al:
        top_assets = sorted(al.optimal_allocation.items(), key=lambda x: x[1], reverse=True)[:3]
        alloc_text = " | ".join([f"{k}:{v}%" for k, v in top_assets])

    # 企微卡片结构
    card = {
        "msgtype": "interactive",
        "interactive": {
            "card_type": "template_card",
            "source": {
                "icon_url": "https://example.com/bond.png",
                "desc": "固收+策略分析"
            },
            "card_header": {
                "title": title,
                "palette": "palette_blue"
            },
            "card_elements": [
                # 收益分解
                {
                    "tag": "div",
                    "text": {
                        "content": f"**收益分解** {return_summary}",
                        "tag": "lark_md"
                    }
                },
                {"tag": "hr"},
                # 期限分布
                {
                    "tag": "div",
                    "text": {
                        "content": f"**期限分布** {tenor_text}",
                        "tag": "lark_md"
                    }
                },
                # 类属配置
                {
                    "tag": "div",
                    "text": {
                        "content": f"**类属配置** {alloc_text}",
                        "tag": "lark_md"
                    }
                },
                # VS纯债
                {
                    "tag": "div",
                    "text": {
                        "content": (
                            f"**VS纯债对比**\n"
                            f"固收+ {pc.fi_plus_return:.2f}% vs 纯债 {pc.pure_bond_return:.2f}% "
                            f"(超额 {pc.excess_return:.2f}%)\n"
                            f"回撤: 固收+ {pc.max_drawdown_fi_plus:.2f}% vs 纯债 {pc.max_drawdown_pure:.2f}%"
                        ),
                        "tag": "lark_md"
                    }
                },
                # 推荐策略
                {
                    "tag": "div",
                    "text": {
                        "content": f"**推荐策略**: {ds.strategy_name} | {ds.recommendation[:30]}...",
                        "tag": "lark_md"
                    }
                },
            ]
        }
    }

    # 如果有预警，添加到一个 note
    if warning_lines:
        card["interactive"]["card_elements"].append(
            {
                "tag": "note",
                "elements": [
                    {"content": warning, "tag": "plain_text"}
                    for warning in warning_lines
                ]
            }
        )

    # 添加底部
    card["interactive"]["card_elements"].append({
        "tag": "hr"
    })
    card["interactive"]["card_elements"].append({
        "tag": "div",
        "text": {
            "content": f"🕐 {report.analysis_timestamp} | 模型 v{report.model_version}",
            "tag": "lark_md"
        }
    })

    return card


def send_wecom_card(card: Dict[str, Any], webhook_url: str = None) -> Dict[str, Any]:
    """
    通过企微 webhook 发送卡片

    Args:
        card: 企微卡片 JSON
        webhook_url: Webhook 地址（可选）

    Returns:
        发送结果
    """
    import urllib.request

    if webhook_url is None:
        return {"errcode": 0, "errmsg": "webhook_url not provided, card generated but not sent"}

    data = json.dumps(card).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}


if __name__ == "__main__":
    # 测试代码
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from fi_plus_engine import FixedIncomePlusEngine

    engine = FixedIncomePlusEngine()
    report = engine.analyze(
        portfolio_amount=10000,
        duration=3.5,
        rating="AA",
        target_return=4.5
    )

    card = generate_wecom_card(report)
    print(json.dumps(card, ensure_ascii=False, indent=2))
