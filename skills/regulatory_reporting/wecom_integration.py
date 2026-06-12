"""
企业微信卡片集成 - wecom_integration.py

将监管报送要求清单渲染为企微消息卡片格式，便于通过企微机器人/应用推送。
"""

import json
from typing import Any


def build_regreport_card(
    report_type: str = "1104",
    period: str = "2024Q1",
    engine_result: dict | None = None,
) -> dict[str, Any]:
    """
    构建监管报送企微卡片消息体。

    Args:
        report_type: 报送类型代码，如 "1104", "GRS", "EAST", "RPBC"
        period: 报送期间，如 "2024Q1"
        engine_result: RegReportingEngine.generate() 的返回结果，若为 None 则调用引擎

    Returns:
        企微消息卡片 JSON（符合企微 webhook / 应用消息格式）
    """

    if engine_result is None:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from reg_report_engine import RegReportingEngine
        engine = RegReportingEngine()
        engine_result = engine.generate(report_type, period, api_mode=True)

    r = engine_result
    meta = r.get("meta", {})
    reports = r.get("reports", [])
    indicators = r.get("key_indicators", [])
    data_sources = r.get("data_sources", [])
    errors = r.get("common_errors", [])

    # ── 卡片头部 ──────────────────────────────────────
    header_color = _authority_color(meta.get("authority", ""))

    # ── 报表清单段落 ───────────────────────────────────
    report_lines = []
    if reports:
        for rep in reports[:8]:  # 最多显示8条
            due_info = f"截止+{rep.get('due_days', '?')}天" if isinstance(rep.get('due_days'), int) else rep.get('period', '')
            report_lines.append(
                f"• [{rep['code']}] {rep['name']}（{due_info}）"
            )
        if len(reports) > 8:
            report_lines.append(f"…等共 {len(reports)} 张报表")
    else:
        report_lines.append("暂无报表数据")

    # ── 指标段落 ───────────────────────────────────────
    indicator_lines = []
    if indicators:
        for ind in indicators[:6]:
            indicator_lines.append(
                f"• {ind['name']}：{ind['threshold']} {ind['unit']}"
            )
    else:
        indicator_lines.append("暂无指标数据")

    # ── 数据源段落 ─────────────────────────────────────
    source_lines = []
    if data_sources:
        for ds in data_sources[:4]:
            source_lines.append(f"• {ds['system']}：{ds['tables']}")
    else:
        source_lines.append("暂无数据源信息")

    # ── 常见错误段落 ───────────────────────────────────
    error_lines = []
    if errors:
        for err in errors[:3]:
            error_lines.append(f"⚠ [{err['code']}] {err['description']}")
    else:
        error_lines.append("暂无常见错误记录")

    card = {
        "msgtype": "markdown",
        "markdown": {
            "content": _build_markdown(
                meta_name=meta.get("name", report_type),
                authority=meta.get("authority", ""),
                period=r.get("period", period),
                deadline=r.get("deadline", "待定"),
                report_lines=report_lines,
                indicator_lines=indicator_lines,
                source_lines=source_lines,
                error_lines=error_lines,
                header_color=header_color,
            )
        },
    }

    return card


def _authority_color(authority: str) -> str:
    """根据监管机构返回企微卡片标题颜色。"""
    color_map = {
        "银保监会": "red",
        "人民银行": "blue",
        "金融稳定局": "orange",
        "银保监/人民银行": "purple",
    }
    return color_map.get(authority, "gray")


def _build_markdown(
    meta_name: str,
    authority: str,
    period: str,
    deadline: str,
    report_lines: list[str],
    indicator_lines: list[str],
    source_lines: list[str],
    error_lines: list[str],
    header_color: str,
) -> str:
    """构建企微 Markdown 卡片内容。"""

    # 企微 markdown 支持的颜色标签
    color_tag_map = {
        "red": "<font color=\"red\">",
        "blue": "<font color=\"blue\">",
        "orange": "<font color=\"orange\">",
        "purple": "<font color=\"purple\">",
        "gray": "<font color=\"gray\">",
    }
    color_tag = color_tag_map.get(header_color, "<font color=\"gray\">")
    color_close = "</font>"

    md = (
        f"## {color_tag}📋 {meta_name}{color_close}\n"
        f"**监管机构：** {authority}  \n"
        f"**报送期间：** {period}  \n"
        f"**截止日期：** {color_tag}**{deadline}**{color_close}\n\n"
        "---\n\n"
        "### 📑 报表清单\n"
        + "\n".join(report_lines)
        + "\n\n---\n\n"
        "### 📊 关键监管指标\n"
        + "\n".join(indicator_lines)
        + "\n\n---\n\n"
        "### 💾 数据来源系统\n"
        + "\n".join(source_lines)
        + "\n\n---\n\n"
        "### ⚠️ 常见错误提示\n"
        + "\n".join(error_lines)
        + "\n\n"
        "---\n\n"
        f"<font color=\"gray\">由 ArkClaw 监管报送引擎生成 · {period}</font>"
    )
    return md


def card_to_wecom_json(card: dict, webhook_url: str | None = None) -> dict:
    """
    将卡片消息体封装为可发送的完整企微 webhook 请求体。

    Args:
        card: build_regreport_card() 返回的消息体
        webhook_url: 企微 webhook 地址（可选，不填则只返回消息体）

    Returns:
        完整的 webhook POST 请求体
    """
    payload = {
        "msgtype": card["msgtype"],
        card["msgtype"]: card["markdown"]["content"],
    }
    return payload


# ─────────────────────────────────────────────
#  直接运行测试
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    # 测试生成 1104 报送卡片
    print("=== 测试：1104 2024年Q1 ===")
    card = build_regreport_card(report_type="1104", period="2024Q1")
    print(json.dumps(card, ensure_ascii=False, indent=2))
