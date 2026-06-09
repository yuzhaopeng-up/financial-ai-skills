"""监管政策 RAG 测试。"""
import os
import sys
import time
import json

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
sys.path.insert(0, SKILL_DIR)

from regulatory_policy_rag import RegulatoryPolicyRAG, RAGFormatter


def test_load_and_build():
    kb_dir = os.path.join(SKILL_DIR, "knowledge_base")
    rag = RegulatoryPolicyRAG()
    rag.load_knowledge_base(kb_dir)
    assert len(rag.chunks) > 0, "知识库为空"
    rag.build_index()
    assert rag.bm25 is not None
    assert rag.tfidf is not None
    print(f"✓ 加载 {len(rag.chunks)} 个政策块")


def test_query():
    kb_dir = os.path.join(SKILL_DIR, "knowledge_base")
    rag = RegulatoryPolicyRAG()
    rag.load_knowledge_base(kb_dir)
    rag.build_index()

    result = rag.query("理财销售双录要求是什么", top_k=3)
    assert not result.get("no_answer"), "未找到答案"
    assert len(result["citations"]) > 0
    assert "双录" in result["answer"] or "录音" in result["answer"] or "录像" in result["answer"]
    print(f"✓ 查询成功，答案包含 {len(result['citations'])} 条出处")


def test_agency_filter():
    kb_dir = os.path.join(SKILL_DIR, "knowledge_base")
    rag = RegulatoryPolicyRAG()
    rag.load_knowledge_base(kb_dir)
    rag.build_index()

    result = rag.query("信息披露", top_k=3, agency_filter="csrc")
    for c in result["citations"]:
        assert c["agency_key"] == "csrc", f"机构过滤失败: {c['agency_key']}"
    print("✓ 机构过滤正常")


def test_bench():
    kb_dir = os.path.join(SKILL_DIR, "knowledge_base")
    rag = RegulatoryPolicyRAG()
    rag.load_knowledge_base(kb_dir)
    rag.build_index()

    testset_path = os.path.join(SKILL_DIR, "tests", "testset.json")
    with open(testset_path, encoding="utf-8") as f:
        testset = json.load(f)

    total = len(testset)
    hit1 = hit3 = mrr_sum = 0
    total_ms = 0

    for item in testset:
        t0 = time.perf_counter()
        result = rag.query(item["question"], top_k=3)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        total_ms += elapsed_ms

        expected = item.get("expected_section", "")
        found = any(expected in (c["section"] + c.get("normalized_section", ""))
                    for c in result["citations"][:1])
        if found:
            hit1 += 1
        found_3 = any(expected in (c["section"] + c.get("normalized_section", ""))
                       for c in result["citations"][:3])
        if found_3:
            hit3 += 1
        for rank, c in enumerate(result["citations"][:3], 1):
            if expected in (c["section"] + c.get("normalized_section", "")):
                mrr_sum += 1 / rank
                break

    avg_ms = total_ms / total
    hit1_rate = hit1 / total
    hit3_rate = hit3 / total
    mrr = mrr_sum / total

    print(f"\n  测试集: {total} 条")
    print(f"  Hit@1: {hit1}/{total} = {hit1_rate:.2%}")
    print(f"  Hit@3: {hit3}/{total} = {hit3_rate:.2%}")
    print(f"  MRR:   {mrr:.4f}")
    print(f"  平均检索耗时: {avg_ms:.1f} ms")

    # 零依赖关键词检索 Hit@1 目标 ≥ 66%（MMRE baseline）
    assert hit1_rate >= 0.66, f"Hit@1 {hit1_rate:.2%} 未达标（要求≥66%）"
    assert avg_ms < 50, f"检索耗时 {avg_ms:.1f}ms 超标（要求<50ms）"
    print("✓ 性能测试通过")


def test_formatters():
    kb_dir = os.path.join(SKILL_DIR, "knowledge_base")
    rag = RegulatoryPolicyRAG()
    rag.load_knowledge_base(kb_dir)
    rag.build_index()

    result = rag.query("双录要求", top_k=2)
    text = RAGFormatter.format_text(result)
    assert len(text) > 50
    card = RAGFormatter.format_card(result)
    assert "card_type" in card
    print("✓ 格式化器正常")


if __name__ == "__main__":
    print("=== 监管政策 RAG 测试 ===")
    test_load_and_build()
    test_query()
    test_agency_filter()
    test_formatters()
    test_bench()
    print("\n✅ 全部测试通过！")
