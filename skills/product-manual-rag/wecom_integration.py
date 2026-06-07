"""
WeCom (企微) 集成：把 product-manual-rag 接入企微"产品手册问答"入口。

提供：
1. 主页入口（template_card）
2. 提问输入框（接受语音/文字）
3. 答案卡片（含出处）
4. 满意度反馈按钮
"""
from __future__ import annotations
import os
import sys
from typing import Dict, Any, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from product_manual_rag import ProductManualRAG, RAGFormatter


# ---------- 单例：避免每次问答重建索引 ----------

_rag_singleton: Optional[ProductManualRAG] = None


def get_rag(kb_dir: Optional[str] = None) -> ProductManualRAG:
    global _rag_singleton
    if _rag_singleton is None:
        kb_dir = kb_dir or os.path.join(HERE, "knowledge_base")
        rag = ProductManualRAG()
        rag.load_knowledge_base(kb_dir)
        rag.build_index()
        _rag_singleton = rag
    return _rag_singleton


# ---------- 企微卡片渲染 ----------

def build_home_card(user_role: str = "客户经理") -> Dict[str, Any]:
    """主页：选择产品类别 → 进入问答。"""
    rag = get_rag()
    products = sorted({c.product for c in rag.chunks})
    return {
        "card_type": "button_interaction",
        "main_title": {"title": "📖 产品手册智能问答", "desc": f"你好，{user_role}"},
        "task_id": "product_manual_home",
        "horizontal_content_list": [
            {"keyname": "可查询产品", "value": f"{len(products)} 个"},
            {"keyname": "今日问答", "value": "—"},
            {"keyname": "平均响应", "value": "< 3 ms"},
        ],
        "button_list": [
            {"text": "🔍 直接提问", "action_url": "/rag/ask"},
            {"text": "🎤 语音提问", "action_url": "/rag/voice"},
            {"text": "📚 浏览产品", "action_url": "/rag/products"},
            {"text": "📊 我的提问历史", "action_url": "/rag/history"},
        ],
        "quote_area": {
            "title": "💡 示例问题",
            "quote_text": (
                "• 金葵花理财起购金额是多少？\n"
                "• 平安白金卡逾期违约金怎么算？\n"
                "• 建行惠懂你最高额度多少？\n"
                "• 招行金葵花税务处理规则？"
            ),
        },
    }


def build_answer_card(question: str, kb_dir: Optional[str] = None) -> Dict[str, Any]:
    """提问 → 答案卡片。"""
    rag = get_rag(kb_dir)
    result = rag.query(question, top_k=3)
    answer = result["answer"]
    citations = result["citations"]
    confidence = "高" if not result.get("no_answer") else "低"

    sources_text = "\n".join(
        f"[{i}] 《{c['product']}》 · {c['section']}"
        for i, c in enumerate(citations[:3], 1)
    ) or "（无）"

    snippet_text = "\n\n".join(
        f"[{i}] {c['snippet']}" for i, c in enumerate(citations[:2], 1)
    )

    return {
        "card_type": "text_notice",
        "main_title": {"title": "📖 产品手册问答", "desc": question[:30]},
        "emphasis_content": {
            "title": (answer[:80] + "...") if len(answer) > 80 else answer,
            "desc": "AI 抽取答案",
        },
        "quote_area": {"title": "完整答案", "quote_text": answer},
        "horizontal_content_list": [
            {"keyname": "📚 出处", "value": sources_text},
            {"keyname": "🎯 置信度", "value": confidence},
            {"keyname": "📊 命中数", "value": str(len(citations))},
        ],
        "sub_title_text": snippet_text[:400],
        "button_list": [
            {"text": "👍 答案有用", "action_url": f"/rag/feedback?q={question}&v=up"},
            {"text": "👎 不准确", "action_url": f"/rag/feedback?q={question}&v=down"},
            {"text": "📋 复制到聊天", "action_url": "/rag/copy"},
            {"text": "🔍 重新提问", "action_url": "/rag/ask"},
        ],
    }


def build_product_list_card() -> Dict[str, Any]:
    rag = get_rag()
    products = {}
    for c in rag.chunks:
        products.setdefault(c.product, set()).add(c.section)
    items = []
    for p, secs in sorted(products.items()):
        items.append({
            "keyname": f"📕 {p}",
            "value": f"{len(secs)} 章 · 包含 {len(secs)} 个主题",
        })
    return {
        "card_type": "text_notice",
        "main_title": {"title": "📚 已加载产品手册", "desc": f"共 {len(products)} 个"},
        "horizontal_content_list": items,
        "button_list": [
            {"text": "➕ 上传新手册", "action_url": "/rag/upload"},
            {"text": "🔙 返回主页", "action_url": "/rag/home"},
        ],
    }


def build_voice_ask_card() -> Dict[str, Any]:
    """语音入口：触发企微语音录入。"""
    return {
        "card_type": "text_notice",
        "main_title": {"title": "🎤 语音提问", "desc": "长按下方按钮说出问题"},
        "emphasis_content": {"title": "示例", "desc": "金葵花理财起购金额是多少"},
        "quote_area": {
            "title": "提示",
            "quote_text": (
                "• 系统将自动转写为文字\n"
                "• 建议提问时包含产品名称\n"
                "• 平均响应时间 < 3 ms"
            ),
        },
        "button_list": [
            {"text": "🎤 开始录音", "action_url": "/rag/voice/start"},
            {"text": "📝 改用文字", "action_url": "/rag/ask"},
        ],
    }


# ---------- 示例 / 演示 ----------

if __name__ == "__main__":
    import json
    print("=== 主页 ===")
    print(json.dumps(build_home_card(), ensure_ascii=False, indent=2))
    print("\n=== 问答 ===")
    print(json.dumps(build_answer_card("金葵花理财起购金额是多少"), ensure_ascii=False, indent=2))
    print("\n=== 产品列表 ===")
    print(json.dumps(build_product_list_card(), ensure_ascii=False, indent=2))
