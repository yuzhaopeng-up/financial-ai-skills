"""
WeCom (企微) 集成：把 regulatory-policy-rag 接入企微"监管政策解读"入口。

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

from regulatory_policy_rag import RegulatoryPolicyRAG, RAGFormatter


# ---------- 单例：避免每次问答重建索引 ----------

_rag_singleton: Optional[RegulatoryPolicyRAG] = None


def get_rag(kb_dir: Optional[str] = None) -> RegulatoryPolicyRAG:
    global _rag_singleton
    if _rag_singleton is None:
        kb_dir = kb_dir or os.path.join(HERE, "knowledge_base")
        rag = RegulatoryPolicyRAG()
        rag.load_knowledge_base(kb_dir)
        rag.build_index()
        _rag_singleton = rag
    return _rag_singleton


# ---------- 企微卡片渲染 ----------

def build_home_card(user_role: str = "合规专员") -> Dict[str, Any]:
    """主页：选择监管机构类别 → 进入问答。"""
    return {
        "card_type": "button_interaction",
        "main_title": {"title": "📋 监管政策智能解读", "desc": f"你好，{user_role}"},
        "task_id": "regulatory_policy_home",
        "horizontal_content_list": [
            {"keyname": "可查询机构", "value": "银保监 / 央行 / 证监会"},
            {"keyname": "今日查询", "value": "—"},
            {"keyname": "平均响应", "value": "< 5 ms"},
        ],
        "button_list": [
            {"text": "🔍 直接提问", "action_url": "/policy/ask"},
            {"text": "🏛️ 银保监政策", "action_url": "/policy/ask?agency=cbirc"},
            {"text": "💰 央行政策", "action_url": "/policy/ask?agency=pboc"},
            {"text": "📈 证监会政策", "action_url": "/policy/ask?agency=csrc"},
        ],
        "quote_area": {
            "title": "💡 示例问题",
            "quote_text": (
                "• 理财销售双录要求是什么？\n"
                "• 金融资产风险分类有几类？\n"
                "• 客户身份资料保存多久？\n"
                "• 年度报告披露时限？"
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
        f"[{i}] {c['doc_title']} · {c['section']}（{c['agency']}）"
        for i, c in enumerate(citations[:3], 1)
    ) or "（无）"

    snippet_text = "\n\n".join(
        f"[{i}] {c['snippet'][:200]}"
        for i, c in enumerate(citations[:2], 1)
    )

    return {
        "card_type": "text_notice",
        "main_title": {"title": "📋 监管政策解读", "desc": question[:40]},
        "emphasis_content": {
            "title": (answer[:80] + "...") if len(answer) > 80 else answer,
            "desc": "AI 政策解读",
        },
        "quote_area": {
            "title": "📖 政策要点",
            "quote_text": snippet_text[:400],
        },
        "horizontal_content_list": [
            {"keyname": "🏛️ 适用机构", "value": ", ".join(result["applicable_agencies"]) or "通用"},
            {"keyname": "📚 出处", "value": sources_text[:200]},
            {"keyname": "🎯 置信度", "value": confidence},
        ],
        "sub_title_text": sources_text[:400],
        "button_list": [
            {"text": "👍 答案有用", "action_url": f"/policy/feedback?type=up"},
            {"text": "👎 不准确", "action_url": f"/policy/feedback?type=down"},
            {"text": "📋 复制到聊天", "action_url": "/policy/copy"},
            {"text": "🔍 重新提问", "action_url": "/policy/ask"},
        ],
    }


def build_agency_list_card() -> Dict[str, Any]:
    """监管机构列表卡片。"""
    return {
        "card_type": "text_notice",
        "main_title": {"title": "🏛️ 监管机构列表", "desc": "选择要查询的机构类型"},
        "horizontal_content_list": [
            {"keyname": "🏦 银保监 CBIRC", "value": "银行保险监管制度"},
            {"keyname": "💰 央行 PBOC", "value": "货币政策与反洗钱"},
            {"keyname": "📈 证监会 CSRC", "value": "证券市场监管"},
            {"keyname": "🏛️ 金监总局 NFRA", "value": "统一监管政策"},
        ],
        "button_list": [
            {"text": "🏦 银保监政策", "action_url": "/policy/ask?agency=cbirc"},
            {"text": "💰 央行政策", "action_url": "/policy/ask?agency=pboc"},
            {"text": "📈 证监会政策", "action_url": "/policy/ask?agency=csrc"},
            {"text": "🔙 返回主页", "action_url": "/policy/home"},
        ],
    }


# ---------- 示例 / 演示 ----------

if __name__ == "__main__":
    import json
    print("=== 主页 ===")
    print(json.dumps(build_home_card(), ensure_ascii=False, indent=2))
    print("\n=== 问答 ===")
    print(json.dumps(build_answer_card("理财销售双录要求是什么"), ensure_ascii=False, indent=2))
    print("\n=== 机构列表 ===")
    print(json.dumps(build_agency_list_card(), ensure_ascii=False, indent=2))
