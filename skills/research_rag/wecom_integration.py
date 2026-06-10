"""
research_rag WeCom 集成 —— 企微卡片入口。
==========================================
将 RAG 答案以企微消息卡片格式输出，支持交互按钮。
"""
from __future__ import annotations
import os
import sys
import json
from typing import Any, Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from rag_engine import ResearchRAGEngine, Citation, RAGAnswer


# ---------------------------------------------------------------------------
# 企微卡片构建工具
# ---------------------------------------------------------------------------

def _truncate(text: str, max_chars: int = 150) -> str:
    """截断文本，超长部分用省略号。"""
    text = text.replace("\n", " ").replace("  ", " ")
    if len(text) <= max_chars:
        return text
    return text[:max_chars - 3] + "..."


def _citation_to_article(c: Citation, idx: int) -> Dict[str, Any]:
    """将 Citation 转换为企微文章格式。"""
    return {
        "title": f"[{idx}] {c.label()}",
        "desc": _truncate(c.snippet, 120),
        "url": "",   # 企微卡片中 url 可填产品详情页
    }


def _build_source_buttons(sources: List[str]) -> List[Dict[str, str]]:
    """从来源列表构建跳转按钮。"""
    btns = []
    for src in sources[:3]:
        if "宁德" in src:
            btns.append({"text": "🔋 某新能源公司详情", "action_url": "/research/company/catl"})
        elif "某汽车公司" in src:
            btns.append({"text": "🚗 某汽车公司详情", "action_url": "/research/company/byd"})
        elif "某银行A" in src:
            btns.append({"text": "🏦 某银行A详情", "action_url": "/research/company/cmb"})
        elif "某白酒公司" in src:
            btns.append({"text": "🍶 某白酒公司详情", "action_url": "/research/company/moutai"})
        else:
            btns.append({"text": f"📊 查看{src}", "action_url": "/research/list"})
    return btns


def rag_to_wecom_card(answer: RAGAnswer) -> Dict[str, Any]:
    """
    将 RAGAnswer 转换为企微消息卡片格式。

    卡片结构：
    - main_title：RAG答案摘要（截断）
    - horizontal_content_list：查询信息
    - citation_list：引用来源列表
    - quote_area：Top 引用内容预览
    - button_list：操作按钮
    """
    main_title = answer.answer.split("\n")[0][:50]
    main_desc = _truncate(answer.answer, 200)

    # 引用来源摘要
    citation_items = []
    for i, c in enumerate(answer.citations[:3], 1):
        citation_items.append({
            "title": f"[{i}] {c.label()}",
            "desc": _truncate(c.snippet, 100),
        })

    # 引用全文预览（quote_area）
    quote_parts = []
    for c in answer.citations[:2]:
        quote_parts.append(f"▎{c.source_name}·{c.section}\n{_truncate(c.snippet, 200)}")
    quote_text = "\n\n".join(quote_parts)

    card = {
        "card_type": "news",
        "main_title": {
            "title": main_title,
            "desc": main_desc,
        },
        "horizontal_content_list": [
            {"keyname": "📖 涉及来源", "value": str(len(answer.sources_used)) + " 个"},
            {"keyname": "🔗 引用数量", "value": str(len(answer.citations)) + " 条"},
            {"keyname": "🕐 生成时间", "value": answer.generated_at},
        ],
        "citation_count": str(len(answer.citations)),
        "citation_list": citation_items,
        "quote_area": {
            "title": "📌 核心引用",
            "quote_text": quote_text,
        },
    }

    # 操作按钮
    buttons = [
        {"text": "🔍 展开全部引用", "action_url": "/research/rag/full"},
        {"text": "📊 生成完整研报", "action_url": "/research/report/generxy"},
        {"text": "💬 继续追问", "action_url": "/research/rag/continue"},
    ]
    # 来源快速跳转
    src_btns = _build_source_buttons(answer.sources_used)
    buttons.extend(src_btns[:2])

    card["button_list"] = buttons[:4]  # 企微限制 button_list 长度

    return card


def rag_to_wecom_card_interactive(answer: RAGAnswer) -> Dict[str, Any]:
    """
    返回一个交互式按钮卡片，让用户选择下一步操作。
    适合首轮查询后用户想深入了解的场景。
    """
    # 判断查询类型
    q = answer.query
    is_company = any(k in q for k in ["公司", "宁德", "某汽车公司", "招商", "茅台"])
    is_industry = any(k in q for k in ["行业", "趋势", "赛道", "市场"])
    is_risk = any(k in q for k in ["风险", "危机", "隐患"])
    is_metric = any(k in q for k in ["指标", "估值", "财务", "ROE"])

    # 动态按钮
    buttons = []
    if is_company:
        buttons.append({"text": "🏢 公司深度分析", "action_url": "/research/deep/company"})
        buttons.append({"text": "📈 行业对比", "action_url": "/research/compare/industry"})
    if is_industry:
        buttons.append({"text": "📊 行业全景报告", "action_url": "/research/report/industry"})
        buttons.append({"text": "🏆 龙头公司", "action_url": "/research/report/topcompany"})
    if is_risk:
        buttons.append({"text": "⚠️ 风险详情", "action_url": "/research/risk/detail"})
        buttons.append({"text": "🛡️ 风险控制建议", "action_url": "/research/risk/mitigation"})
    if is_metric:
        buttons.append({"text": "📉 财务指标详情", "action_url": "/research/financial/detail"})
        buttons.append({"text": "📊 估值分析", "action_url": "/research/valuation"})

    buttons.append({"text": "💬 继续追问", "action_url": "/research/rag/continue"})
    buttons.append({"text": "📋 查看全部引用", "action_url": "/research/rag/citations"})

    # 限制按钮数量
    buttons = buttons[:4]

    main_title = answer.answer.split("\n")[0][:40]
    main_desc = _truncate(answer.answer, 150)

    return {
        "card_type": "button_interaction",
        "main_title": {
            "title": "🔍 " + main_title,
            "desc": main_desc,
        },
        "horizontal_content_list": [
            {"keyname": "引用", "value": f"{len(answer.citations)} 条"},
            {"keyname": "来源", "value": f"{len(answer.sources_used)} 个"},
        ],
        "button_list": buttons,
        "quote_area": {
            "title": "💡 Top 引用",
            "quote_text": "\n".join(
                f"[{i+1}] {c.label()}：{_truncate(c.snippet, 80)}"
                for i, c in enumerate(answer.citations[:2])
            ),
        },
    }


def build_home_card() -> Dict[str, Any]:
    """返回 RAG 首页引导卡片。"""
    return {
        "card_type": "button_interaction",
        "main_title": {
            "title": "🔍 研报RAG智能检索",
            "desc": "输入研究问题，秒级返回带引用的答案",
        },
        "horizontal_content_list": [
            {"keyname": "检索方式", "value": "BM25 + TF-IDF 双路"},
            {"keyname": "对话记忆", "value": "支持多轮上下文"},
        ],
        "button_list": [
            {"text": "💬 输入研究问题", "action_url": "/research/rag/input"},
            {"text": "📚 浏览知识库", "action_url": "/research/rag/knowledge"},
            {"text": "🔋 某新能源公司", "action_url": "/research/rag/search?query=某新能源公司"},
            {"text": "🏦 某银行A", "action_url": "/research/rag/search?query=某银行A"},
        ],
        "quote_area": {
            "title": "💡 示例问题",
            "quote_text": (
                "某新能源公司储能业务竞争力分析\n"
                "某银行A净息差走势与风险\n"
                "半导体行业国产替代进展\n"
                "某汽车公司和特斯拉对比"
            ),
        },
    }


# ---------------------------------------------------------------------------
# CLI 演示
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== 首页卡片 ===")
    print(json.dumps(build_home_card(), ensure_ascii=False, indent=2))

    print("\n=== 示例查询卡片 ===")
    from rag_engine import query
    ans = query("某新能源公司储能业务竞争力分析")
    print("\n--- 基础卡片 ---")
    print(json.dumps(rag_to_wecom_card(ans), ensure_ascii=False, indent=2))
    print("\n--- 交互卡片 ---")
    print(json.dumps(rag_to_wecom_card_interactive(ans), ensure_ascii=False, indent=2))
