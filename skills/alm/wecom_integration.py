# -*- coding: utf-8 -*-
"""
ALM 企微机器人卡片集成
WeChat Work (企微) Card Integration for ALM Analysis

提供多种格式的企微消息卡片输出：
- 分析摘要卡片
- 预警详情卡片
- 优化建议卡片
- 完整报告卡片

依赖：
    已配置的企微机器人 webhook（通过飞书机器人间接支持）
    或直接使用企微机器人 API
"""

import json
import re
from typing import Dict, Any, List, Optional

# 尝试导入可选依赖
try:
    from ..alm_engine import ALMEngine, Warning
    _ENGINE_AVAILABLE = True
except ImportError:
    _ENGINE_AVAILABLE = False


# ─────────────────────────────────────────────
# 企微卡片构建工具
# ─────────────────────────────────────────────

class WeComCardBuilder:
    """企微消息卡片构建器"""
    
    # 企微卡片配色
    COLORS = {
        "green": "#36B759",    # 正常
        "yellow": "#FFA500",   # 预警
        "red": "#F53F3F",      # 风险
        "blue": "#4080FF",     # 信息
        "gray": "#646A73",     # 次要
    }
    
    @classmethod
    def status_color(cls, status: str) -> str:
        return cls.COLORS.get(status, cls.COLORS["blue"])
    
    @classmethod
    def _format_yuan(cls, amount: float) -> str:
        """格式化金额"""
        if abs(amount) >= 1e8:
            return f"{amount/1e8:.2f}亿"
        elif abs(amount) >= 1e4:
            return f"{amount/1e4:.2f}万"
        else:
            return f"{amount:.0f}"
    
    @classmethod
    def _status_tag(cls, status: str) -> str:
        emoji = {"green": "✅ 正常", "yellow": "🟡 预警", "red": "🔴 超标"}.get(status, "⚪ 未知")
        return emoji
    
    # ─── 摘要卡片 ─────────────────────────────
    
    @classmethod
    def build_summary_card(cls, text: str, engine=None) -> Dict[str, Any]:
        """
        构建 ALM 摘要卡片（适合飞书/企微机器人推送）
        
        返回企微 interactive 消息卡片格式
        """
        if engine is None and _ENGINE_AVAILABLE:
            engine = ALMEngine()
            engine.parse(text)
        
        lcr = engine.calculate_lcr()
        nsfr = engine.calculate_nsfr()
        dg = engine.calculate_duration_gap()
        warnings = engine.generate_warnings()
        
        ta = engine.total_assets
        
        # 风险元素
        elements = [
            {
                "tag": "markdown",
                "content": f"**🏦 资产负债管理分析**\n总资产：**{cls._format_yuan(ta)}**"
            },
            {"tag": "hr"},
            {
                "tag": "column_set",
                "flex_mode": "border",
                "background_style": "tertiary",
                "columns": [
                    {
                        "tag": "column",
                        "width": "auto",
                        "vertical_align": "top",
                        "elements": [
                            {"tag": "markdown", "content": f"**LCR**\n{lcr.lcr_ratio:.1%}\n{cls._status_tag(lcr.status)}"},
                        ]
                    },
                    {
                        "tag": "column",
                        "width": "auto",
                        "vertical_align": "top",
                        "elements": [
                            {"tag": "markdown", "content": f"**NSFR**\n{nsfr.nsfr_ratio:.1%}\n{cls._status_tag(nsfr.status)}"},
                        ]
                    },
                    {
                        "tag": "column",
                        "width": "auto",
                        "vertical_align": "top",
                        "elements": [
                            {"tag": "markdown", "content": f"**久期缺口**\n{dg.duration_gap_adjusted:+.2f}年\n{cls._status_tag(dg.status)}"},
                        ]
                    },
                ]
            },
        ]
        
        # 预警信息
        if warnings:
            warning_lines = []
            for w in warnings[:3]:  # 最多3条
                emoji = "🔴" if w.level == "red" else "🟡"
                warning_lines.append(f"{emoji} **{w.indicator}**：{w.message}")
            
            elements.append({
                "tag": "markdown",
                "content": "\n".join(warning_lines)
            })
        
        # 页脚
        elements.append({
            "tag": "note",
            "elements": [
                {"tag": "plain_text", "content": "龙马集群AI团队 · ArkClaw · ALM分析"}
            ]
        })
        
        card = {
            "msgtype": "interactive",
            "interactive": {
                "header": {
                    "title": {"tag": "plain_text", "content": "📊 ALM 资产负债管理分析报告"},
                    "template": "orange" if any(w.level == "red" for w in warnings) else "blue"
                },
                "elements": elements
            }
        }
        
        return card
    
    # ─── 详细报告卡片 ─────────────────────────
    
    @classmethod
    def build_full_report_card(cls, text: str, engine=None) -> Dict[str, Any]:
        """
        构建完整的 ALM 分析报告卡片（多卡片组合）
        """
        if engine is None and _ENGINE_AVAILABLE:
            engine = ALMEngine()
            engine.parse(text)
        
        result = engine.analyze()
        ta = engine.total_assets
        
        # 主卡片
        main_elements = [
            {
                "tag": "markdown",
                "content": f"🏦 **总资产：{cls._format_yuan(ta)}**"
            },
            {"tag": "hr"},
            {
                "tag": "markdown",
                "content": (
                    f"**流动性指标**\n"
                    f"• LCR：{result['lcr']['lcr_ratio']:.1%} {cls._status_tag(result['lcr']['status'])}\n"
                    f"• HQLA：{cls._format_yuan(result['lcr']['hqla']['total'])} | "
                    f"净流出：{cls._format_yuan(result['lcr']['net_cash_outflow'])}\n"
                    f"• NSFR：{result['nsfr']['nsfr_ratio']:.1%} {cls._status_tag(result['nsfr']['status'])}"
                )
            },
            {"tag": "hr"},
            {
                "tag": "markdown",
                "content": (
                    f"**久期分析**\n"
                    f"• 资产久期：{result['duration_gap']['asset_duration']:.2f}年\n"
                    f"• 负债久期：{result['duration_gap']['liability_duration']:.2f}年\n"
                    f"• 调整久期缺口：{result['duration_gap']['duration_gap_adjusted']:+.2f}年 "
                    f"{cls._status_tag(result['duration_gap']['status'])}"
                )
            },
        ]
        
        # 期限缺口表格
        gap_lines = ["**期限缺口（累计）**", "| 档位 | 资产 | 负债 | 缺口 | 状态 |"]
        gap_lines.append("|---|---|---|---|---|")
        for bucket, g in result["gap_analysis"].items():
            bucket_label = {"1m": "1月", "3m": "3月", "6m": "6月", "1y": "1年", "3y": "3年", "5y": "5年"}.get(bucket, bucket)
            gap_lines.append(
                f"| {bucket_label} | {cls._format_yuan(g['asset'])} | "
                f"{cls._format_yuan(g['liability'])} | {g['gap']:+.0f} | "
                f"{cls._status_tag(g['status'])} |"
            )
        
        main_elements.append({"tag": "markdown", "content": "\n".join(gap_lines)})
        
        # 预警
        if result["warnings"]:
            warning_section = ["**⚠️ 风险预警**"]
            for w in result["warnings"][:5]:
                emoji = "🔴" if w["level"] == "red" else "🟡"
                warning_section.append(f"{emoji} {w['message']}")
            main_elements.append({"tag": "markdown", "content": "\n".join(warning_section)})
        
        main_elements.append({
            "tag": "note",
            "elements": [{"tag": "plain_text", "content": "龙马集群AI团队 · ArkClaw · ALM分析"}]
        })
        
        return {
            "msgtype": "interactive",
            "interactive": {
                "header": {
                    "title": {"tag": "plain_text", "content": "📊 ALM 资产负债管理报告"},
                    "template": "red" if any(w["level"] == "red" for w in result["warnings"]) else "blue"
                },
                "elements": main_elements
            }
        }
    
    # ─── 预警卡片 ─────────────────────────────
    
    @classmethod
    def build_warning_card(cls, warnings: List[Dict]) -> Dict[str, Any]:
        """
        构建风险预警专用卡片
        """
        if not warnings:
            return {
                "msgtype": "text",
                "text": "✅ 暂无风险预警，各项指标均在正常范围内"
            }
        
        elements = []
        
        for w in warnings:
            emoji = "🔴" if w["level"] == "red" else "🟡"
            elements.append({
                "tag": "markdown",
                "content": f"{emoji} **{w['indicator']}**\n{w['message']}\n💡 **{w['suggestion']}**"
            })
            elements.append({"tag": "hr"})
        
        elements.append({
            "tag": "note",
            "elements": [{"tag": "plain_text", "content": f"共 {len(warnings)} 条预警 · 龙马集群AI团队"}]
        })
        
        return {
            "msgtype": "interactive",
            "interactive": {
                "header": {
                    "title": {"tag": "plain_text", "content": "⚠️ ALM 风险预警报告"},
                    "template": "red"
                },
                "elements": elements
            }
        }
    
    # ─── 优化建议卡片 ─────────────────────────
    
    @classmethod
    def build_optimization_card(cls, optimization: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        构建优化建议卡片
        """
        elements = [
            {"tag": "markdown", "content": "**📋 资产负债管理优化建议**"}
        ]
        
        sections = [
            ("💰 负债结构调整", "liability_adjustment"),
            ("📈 资产配置优化", "asset_optimization"),
            ("🔄 衍生品对冲", "derivatives_hedge"),
        ]
        
        for title, key in sections:
            items = optimization.get(key, [])
            if items:
                lines = [f"**{title}**"]
                for item in items[:3]:  # 每类最多3条
                    lines.append(f"• {item}")
                elements.append({"tag": "markdown", "content": "\n".join(lines)})
        
        elements.append({
            "tag": "note",
            "elements": [{"tag": "plain_text", "content": "龙马集群AI团队 · ArkClaw · ALM分析"}]
        })
        
        return {
            "msgtype": "interactive",
            "interactive": {
                "header": {
                    "title": {"tag": "plain_text", "content": "📋 ALM 优化建议报告"},
                    "template": "green"
                },
                "elements": elements
            }
        }


# ─────────────────────────────────────────────
# 企微卡片发送函数（示例）
# ─────────────────────────────────────────────

def send_wecom_card(webhook_url: str, card: Dict[str, Any]) -> bool:
    """
    向企微机器人 webhook 发送卡片消息
    
    Args:
        webhook_url: 企微机器人的 webhook 地址
        card: 卡片内容（由 WeComCardBuilder 构建）
    
    Returns:
        是否发送成功
    """
    import urllib.request
    
    try:
        data = json.dumps(card, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("errcode", 1) == 0
    except Exception as e:
        print(f"企微卡片发送失败：{e}", file=sys.stderr)
        return False


def alm_to_wecom_card(text: str, card_type: str = "summary", webhook_url: str = None) -> Dict[str, Any]:
    """
    快捷函数：将 ALM 分析结果转换为企微卡片格式
    
    Args:
        text: 分析文本
        card_type: 卡片类型（summary/full/warning/optimization）
        webhook_url: 可选的企微 webhook，用于发送
    
    Returns:
        卡片内容字典
    """
    if not _ENGINE_AVAILABLE:
        raise RuntimeError("ALM Engine 未安装，请先安装 alm_engine")
    
    engine = ALMEngine()
    engine.parse(text)
    
    if card_type == "summary":
        card = WeComCardBuilder.build_summary_card(text, engine)
    elif card_type == "full":
        card = WeComCardBuilder.build_full_report_card(text, engine)
    elif card_type == "warning":
        warnings = engine.generate_warnings()
        card = WeComCardBuilder.build_warning_card([
            {"level": w.level, "indicator": w.indicator, "message": w.message, "suggestion": w.suggestion}
            for w in warnings
        ])
    elif card_type == "optimization":
        opt = engine.generate_optimization()
        card = WeComCardBuilder.build_optimization_card(opt)
    else:
        raise ValueError(f"未知的卡片类型：{card_type}")
    
    if webhook_url:
        send_wecom_card(webhook_url, card)
    
    return card


# ─────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python3 wecom_integration.py <分析文本> [卡片类型]")
        print("  示例：python3 wecom_integration.py 'ALM 资产500亿 定期存款60% 活期30%'")
        sys.exit(1)
    
    text = sys.argv[1]
    card_type = sys.argv[2] if len(sys.argv) > 2 else "summary"
    
    card = alm_to_wecom_card(text, card_type)
    print(json.dumps(card, ensure_ascii=False, indent=2))
