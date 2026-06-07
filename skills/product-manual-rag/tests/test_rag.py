"""单元 + 端到端测试。"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, SKILL)

from product_manual_rag import ProductManualRAG, RAGFormatter
from rag_engine import DocumentChunker, tokenize


def test_tokenize_chinese():
    toks = tokenize("金葵花理财起购金额是多少")
    assert any("金葵" in t or "葵花" in t for t in toks), toks
    assert "金" in toks and "葵" in toks


def test_tokenize_ascii():
    toks = tokenize("LPR 利率 3.45% 起")
    assert "lpr" in toks
    assert any("3.45" in t for t in toks)


def test_chunker_splits_by_heading():
    text = "# 一、概述\n这是第一段。\n## 二、规则\n这是第二段。"
    chunks = DocumentChunker().chunk(text, product="测试产品")
    titles = [c.section for c in chunks]
    assert any("一" in t for t in titles), titles
    assert any("二" in t for t in titles), titles


def test_e2e_ask_jinkuihua():
    kb = os.path.join(SKILL, "knowledge_base")
    rag = ProductManualRAG()
    rag.load_knowledge_base(kb)
    rag.build_index()
    r = rag.query("金葵花理财起购金额是多少", top_k=3)
    assert r["citations"], "should have citations"
    top = r["citations"][0]
    assert top["product"] == "招行金葵花理财", top
    # 答案或出处中应有「1 万」或「50 万」等起购鐈值关键词
    blob = (r["answer"] + " " + " ".join(c["snippet"] for c in r["citations"]))
    assert any(k in blob for k in ["1 万", "1万", "50 万", "50万", "万元"]), blob


def test_e2e_ask_pingan():
    kb = os.path.join(SKILL, "knowledge_base")
    rag = ProductManualRAG()
    rag.load_knowledge_base(kb)
    rag.build_index()
    r = rag.query("平安白金卡年费多少", top_k=3)
    assert r["citations"][0]["product"] == "平安信用卡白金卡"


def test_formatter_text():
    kb = os.path.join(SKILL, "knowledge_base")
    rag = ProductManualRAG()
    rag.load_knowledge_base(kb)
    rag.build_index()
    r = rag.query("建行惠懂你最高额度", top_k=2)
    txt = RAGFormatter.format_text(r)
    assert "出处" in txt
    assert "建行" in txt


def test_no_answer():
    rag = ProductManualRAG()
    rag.add_manual_text("空白产品", "暂无内容")
    rag.build_index()
    r = rag.query("地球到火星距离多少光年")
    # 即便低质量库也应返回结构，不抛异常
    assert "answer" in r and "citations" in r


def run_all():
    failures = 0
    funcs = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    for fn in funcs:
        try:
            fn()
            print(f"  ✅ {fn.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"  ❌ {fn.__name__}: {e}")
        except Exception as e:
            failures += 1
            print(f"  💥 {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{'='*40}\n{len(funcs)-failures}/{len(funcs)} passed.")
    return failures


if __name__ == "__main__":
    raise SystemExit(run_all())
