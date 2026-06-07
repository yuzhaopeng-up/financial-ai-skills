#!/usr/bin/env python3
"""
Product Manual RAG CLI
======================
基于产品手册的智能问答 CLI。

子命令:
  ask       - 问答
  index     - 构建/查看索引
  list      - 列出已加载产品手册
  ingest    - 添加新手册
  bench     - 检索效果评估 (Hit@K / MRR)
"""
import argparse
import json
import os
import sys
import time

# 兼容 "脚本直接运行" 与 "包内导入" 两种调用方式
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(THIS_DIR)
sys.path.insert(0, os.path.dirname(SKILL_ROOT))  # 让 import skill 路径可用

try:
    from product_manual_rag.product_manual_rag import ProductManualRAG, RAGFormatter
except Exception:
    sys.path.insert(0, SKILL_ROOT)
    from product_manual_rag import ProductManualRAG, RAGFormatter

DEFAULT_KB = os.path.join(SKILL_ROOT, "knowledge_base")


def _build(kb_dir: str) -> ProductManualRAG:
    rag = ProductManualRAG()
    stats = rag.load_knowledge_base(kb_dir)
    if not stats:
        print(f"⚠️ 知识库目录为空: {kb_dir}", file=sys.stderr)
    info = rag.build_index()
    print(f"📚 已加载 {info['products']} 个产品手册, "
          f"切分为 {info['chunks']} 个 chunk, "
          f"平均长度 {info.get('avg_chunk_chars','-')} 字。",
          file=sys.stderr)
    return rag


def cmd_ask(args):
    rag = _build(args.kb)
    t0 = time.time()
    result = rag.query(args.question, top_k=args.top_k, product_filter=args.product)
    dt = (time.time() - t0) * 1000
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.format == "card":
        print(json.dumps(RAGFormatter.format_card(result), ensure_ascii=False, indent=2))
    else:
        print(RAGFormatter.format_text(result))
        print(f"\n⏱️  检索耗时 {dt:.1f} ms")


def cmd_index(args):
    rag = _build(args.kb)
    info = rag.build_index()
    print(json.dumps({"index": info}, ensure_ascii=False, indent=2))


def cmd_list(args):
    rag = _build(args.kb)
    by_product = {}
    for c in rag.chunks:
        by_product.setdefault(c.product, []).append(c)
    for p, chunks in by_product.items():
        sections = sorted({c.section for c in chunks})
        print(f"📕 {p}  ({len(chunks)} chunks, {len(sections)} sections)")
        for s in sections:
            print(f"    • {s}")


def cmd_ingest(args):
    rag = ProductManualRAG()
    rag.load_knowledge_base(args.kb)
    added = rag.add_manual_file(args.product, args.file)
    rag.build_index()
    print(f"✅ 已添加 {args.product}, 新增 {added} 个 chunk。")


def cmd_bench(args):
    """轻量评估：传入 JSON 列表 [{q, expected_product, expected_section}, ...]"""
    rag = _build(args.kb)
    with open(args.testset, "r", encoding="utf-8") as f:
        cases = json.load(f)
    hit_at_1 = hit_at_3 = mrr = 0
    total = len(cases)
    for case in cases:
        result = rag.query(case["q"], top_k=5)
        ranks = []
        for i, c in enumerate(result["citations"]):
            ok_p = c["product"] == case.get("expected_product")
            ok_s = (not case.get("expected_section")) or (
                case["expected_section"] in c["section"]
            )
            if ok_p and ok_s:
                ranks.append(i + 1)
        if ranks:
            top_rank = ranks[0]
            if top_rank == 1:
                hit_at_1 += 1
            if top_rank <= 3:
                hit_at_3 += 1
            mrr += 1.0 / top_rank
    report = {
        "total": total,
        "Hit@1": round(hit_at_1 / total, 3) if total else 0,
        "Hit@3": round(hit_at_3 / total, 3) if total else 0,
        "MRR": round(mrr / total, 3) if total else 0,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Product Manual RAG CLI")
    parser.add_argument("--kb", default=DEFAULT_KB, help="知识库目录")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ask = sub.add_parser("ask", help="问答")
    p_ask.add_argument("question", help="问题文本")
    p_ask.add_argument("--top-k", type=int, default=3)
    p_ask.add_argument("--product", default=None, help="限定产品名")
    p_ask.add_argument("--format", choices=["text", "json", "card"], default="text")
    p_ask.set_defaults(func=cmd_ask)

    p_idx = sub.add_parser("index", help="构建/查看索引")
    p_idx.set_defaults(func=cmd_index)

    p_list = sub.add_parser("list", help="列出已加载手册")
    p_list.set_defaults(func=cmd_list)

    p_ing = sub.add_parser("ingest", help="添加新手册")
    p_ing.add_argument("--product", required=True)
    p_ing.add_argument("--file", required=True)
    p_ing.set_defaults(func=cmd_ingest)

    p_bench = sub.add_parser("bench", help="检索效果评估")
    p_bench.add_argument("--testset", required=True)
    p_bench.set_defaults(func=cmd_bench)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
