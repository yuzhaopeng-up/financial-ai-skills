#!/usr/bin/env python3
"""
research_rag CLI
================
研报RAG检索引擎命令行入口。

子命令:
  query   - 单次查询（支持 --format）
  search  - 仅检索，不生成答案
  chat    - 多轮对话（交互式）
  stats   - 查看知识库统计
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, SKILL)

from rag_engine import ResearchRAGEngine, load_templates


def _format_text(answer) -> str:
    lines = [answer.answer, ""]
    if answer.citations:
        lines.append("─── 引用来源 ───")
        for i, c in enumerate(answer.citations, 1):
            lines.append(f"  [{i}] {c.label()}: {c.snippet[:80]}...")
    if answer.sources_used:
        lines.append(f"\n📚 涉及来源：{', '.join(answer.sources_used)}")
    lines.append(f"\n🕐 生成时间：{answer.generated_at}")
    return "\n".join(lines)


def _format_json(answer) -> str:
    return json.dumps(answer.to_dict(), ensure_ascii=False, indent=2)


def _format_md(answer) -> str:
    lines = ["# RAG 答案\n", answer.answer]
    if answer.citations:
        lines.append("\n## 引用来源\n")
        for i, c in enumerate(answer.citations, 1):
            lines.append(f"- **[{i}] {c.label()}**: {c.snippet}")
    lines.append(f"\n> 生成时间：{answer.generated_at} | 来源：{', '.join(answer.sources_used)}")
    return "\n".join(lines)


def _format_citations(answer) -> str:
    lines = ["# 引用列表\n"]
    for i, c in enumerate(answer.citations, 1):
        lines.append(f"## [{i}] {c.label()}")
        lines.append(f"- **类型**: {c.source_type}")
        lines.append(f"- **来源**: {c.source_name}")
        lines.append(f"- **章节**: {c.section}")
        lines.append(f"- **摘要**: {c.snippet}")
        lines.append(f"- **得分**: {c.score:.4f}")
        lines.append("")
    return "\n".join(lines)


def cmd_query(args):
    eng = ResearchRAGEngine(max_turns=args.max_turns, top_k=args.top_k)
    answer = eng.query(args.text)

    if args.format == "json":
        print(_format_json(answer))
    elif args.format == "md":
        print(_format_md(answer))
    elif args.format == "citations":
        print(_format_citations(answer))
    else:
        print(_format_text(answer))


def cmd_search(args):
    eng = ResearchRAGEngine(top_k=args.top_k)
    results = eng.search(args.text)
    print(f"🔍 检索「{args.text}」，返回 {len(results)} 条结果：\n")
    for i, r in enumerate(results, 1):
        c = r.chunk
        print(f"[{i}] {c.source_type}:{c.source_name} · {c.section} (score={r.final_score:.4f})")
        print(f"     {c.content[:100]}...")
        print()


def cmd_chat(args):
    eng = ResearchRAGEngine(max_turns=5, top_k=5)
    print("💬 研报RAG 多轮对话（输入 quit 退出）\n")
    while True:
        try:
            text = input("👤 你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye.")
            break
        if not text:
            continue
        if text.lower() in ("quit", "exit", "q"):
            print("bye.")
            break
        answer = eng.query(text)
        print(f"\n🤖 RAG：\n{_format_text(answer)}\n")
        print("─" * 40)


def cmd_stats(args):
    eng = ResearchRAGEngine()
    chunks = eng.chunks
    templates = load_templates()

    # 统计
    type_count: dict = {}
    for c in chunks:
        type_count[c.source_type] = type_count.get(c.source_type, 0) + 1

    print("📊 研报RAG 知识库统计")
    print("=" * 40)
    print(f"  总 Chunk 数：{len(chunks)}")
    print(f"  BM25 索引：已构建" if eng._bm25 else "  BM25 索引：未构建")
    print(f"  TF-IDF 索引：已构建" if eng._tfidf else "  TF-IDF 索引：未构建")
    print("")
    print(f"  按类型分布：")
    for t, n in sorted(type_count.items()):
        print(f"    • {t}：{n} 条")
    print("")
    print(f"  行业数量：{len(templates['industries'])}")
    print(f"  公司数量：{len(templates['companies'])}")


def main():
    parser = argparse.ArgumentParser(description="研报RAG检索引擎 CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # query
    p_q = sub.add_parser("query", help="单次查询")
    p_q.add_argument("text", help="查询文本")
    p_q.add_argument("--format", "-f", choices=["text", "json", "md", "citations"], default="text")
    p_q.add_argument("--max-turns", type=int, default=3, help="多轮对话最大轮数（默认3）")
    p_q.add_argument("--top-k", "-k", type=int, default=5, help="返回结果数（默认5）")
    p_q.set_defaults(func=cmd_query)

    # search
    p_s = sub.add_parser("search", help="仅检索不生成答案")
    p_s.add_argument("text", help="查询文本")
    p_s.add_argument("--top-k", "-k", type=int, default=5)
    p_s.set_defaults(func=cmd_search)

    # chat
    p_c = sub.add_parser("chat", help="多轮对话（交互式）")
    p_c.set_defaults(func=cmd_chat)

    # stats
    p_t = sub.add_parser("stats", help="查看知识库统计")
    p_t.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
