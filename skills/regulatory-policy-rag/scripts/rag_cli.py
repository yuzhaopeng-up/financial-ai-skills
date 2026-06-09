#!/usr/bin/env python3
"""
监管政策 RAG CLI

用法:
  python3 rag_cli.py ask "问题" [--format text|json|card] [--agency cbirc|pboc|csrc]
  python3 rag_cli.py list
  python3 rag_cli.py ingest --agency cbirc --file ./file.md
  python3 rag_cli.py bench --testset tests/testset.json
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
sys.path.insert(0, SKILL_DIR)

from regulatory_policy_rag import RegulatoryPolicyRAG, RAGFormatter


def cmd_ask(args):
    kb_dir = os.path.join(SKILL_DIR, "knowledge_base")
    rag = RegulatoryPolicyRAG()
    rag.load_knowledge_base(kb_dir)
    rag.build_index()

    result = rag.query(args.question, top_k=args.top_k, agency_filter=args.agency)

    if args.format == "json":
        print(RAGFormatter.format_json(result))
    elif args.format == "card":
        card = RAGFormatter.format_card(result)
        print(json.dumps(card, ensure_ascii=False, indent=2))
    else:
        print(RAGFormatter.format_text(result))


def cmd_list(args):
    kb_dir = os.path.join(SKILL_DIR, "knowledge_base")
    rag = RegulatoryPolicyRAG()
    rag.load_knowledge_base(kb_dir)
    rag.build_index()

    by_agency = {}
    for c in rag.chunks:
        by_agency.setdefault(c.agency, set()).add(c.doc_title)

    print(f"已加载政策库（共 {len(rag.chunks)} 个政策块）：")
    print()
    for agency, titles in sorted(by_agency.items()):
        label = {"cbirc": "银保监", "pboc": "央行", "csrc": "证监会", "nfra": "金监总局", "misc": "其他"}.get(agency, agency)
        print(f"  [{label}] {', '.join(sorted(titles))}")


def cmd_ingest(args):
    if not os.path.exists(args.file):
        print(f"文件不存在: {args.file}")
        sys.exit(1)

    kb_dir = os.path.join(SKILL_DIR, "knowledge_base", args.agency)
    os.makedirs(kb_dir, exist_ok=True)

    dest = os.path.join(kb_dir, os.path.basename(args.file))
    with open(args.file, 'r', encoding='utf-8') as src:
        content = src.read()
    with open(dest, 'w', encoding='utf-8') as dst:
        dst.write(content)

    print(f"已入库：{dest}")
    print("提示：重新运行 ask 命令即可检索新文件")


def cmd_bench(args):
    import time
    kb_dir = os.path.join(SKILL_DIR, "knowledge_base")
    rag = RegulatoryPolicyRAG()
    rag.load_knowledge_base(kb_dir)
    rag.build_index()

    testset_path = args.testset or os.path.join(SKILL_DIR, "tests", "testset.json")
    if not os.path.exists(testset_path):
        print(f"测试集不存在: {testset_path}")
        sys.exit(1)

    with open(testset_path, encoding='utf-8') as f:
        testset = json.load(f)

    total = len(testset)
    hit1 = hit3 = mrr_sum = 0
    total_ms = 0

    for item in testset:
        question = item["question"]
        expected = item.get("expected_section", "")

        t0 = time.perf_counter()
        result = rag.query(question, top_k=3)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        total_ms += elapsed_ms

        # 同时检查 section 和 normalized_section
        def match_in_citations(citations_list):
            for c in citations_list:
                combined = c["section"] + (c.get("normalized_section") or "")
                if expected in combined:
                    return True
            return False

        found_1 = match_in_citations(result["citations"][:1])
        found_3 = match_in_citations(result["citations"][:3])
        if found_1:
            hit1 += 1
        if found_3:
            hit3 += 1

        for rank, c in enumerate(result["citations"][:3], 1):
            combined = c["section"] + (c.get("normalized_section") or "")
            if expected in combined:
                mrr_sum += 1 / rank
                break

    avg_ms = total_ms / total
    print(f"测试集: {total} 条")
    print(f"Hit@1: {hit1}/{total} = {hit1/total:.2%}")
    print(f"Hit@3: {hit3}/{total} = {hit3/total:.2%}")
    print(f"MRR:   {mrr_sum/total:.4f}")
    print(f"平均检索耗时: {avg_ms:.1f} ms")


def main():
    parser = argparse.ArgumentParser(description="监管政策 RAG CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_ask = sub.add_parser("ask", help="提问")
    p_ask.add_argument("question", help="问题内容")
    p_ask.add_argument("--format", default="text", choices=["text", "json", "card"])
    p_ask.add_argument("--agency", help="限定监管机构(cbirc/pboc/csrc/nfra/misc)")
    p_ask.add_argument("--top-k", type=int, default=3)

    p_list = sub.add_parser("list", help="列出已加载政策")

    p_ingest = sub.add_parser("ingest", help="添加新政策文件")
    p_ingest.add_argument("--agency", required=True, help="监管机构")
    p_ingest.add_argument("--file", required=True, help="文件路径")

    p_bench = sub.add_parser("bench", help="检索效果评估")
    p_bench.add_argument("--testset", help="测试集 JSON 路径")

    args = parser.parse_args()

    if args.cmd == "ask":
        cmd_ask(args)
    elif args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "ingest":
        cmd_ingest(args)
    elif args.cmd == "bench":
        cmd_bench(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
