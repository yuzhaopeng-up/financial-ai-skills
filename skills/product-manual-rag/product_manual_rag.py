"""
Product Manual RAG —— 顶层 API：索引构建、查询、出处标注、可选 LLM Re-Rank。
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import asdict
from typing import Dict, List, Optional, Tuple, Any

try:
    from .rag_engine import Chunk, DocumentChunker, RetrievalHit, tokenize
    from .retrievers import BM25Index, TFIDFIndex, rrf_fuse
except ImportError:  # 当模块被直接导入（非包导入）时
    from rag_engine import Chunk, DocumentChunker, RetrievalHit, tokenize
    from retrievers import BM25Index, TFIDFIndex, rrf_fuse


_BANK_NAMES = {"招行", "招商", "平安", "建行", "建设", "工行", "工商", "中行", "中信", "农行", "交行", "邮储", "民生", "浦发", "兴业", "广发", "华夏"}
_GENERIC = {"理财", "产品", "手册", "信用卡", "贷款", "企业", "个人", "微贷", "服务", "智能", "机构"}


def re_findall_keywords(name: str) -> List[str]:
    """从产品名中抽取高識别词（去除银行名/通用词后的核心标签）。"""
    words: List[str] = []
    s = name
    for b in _BANK_NAMES:
        if b in s:
            s = s.replace(b, " ")
    for g in _GENERIC:
        if g in s:
            s = s.replace(g, " ")
    # 取连续中文子串 + sliding window 2-4 字所有候选
    for m in re.finditer(r"[\u4e00-\u9fff]{2,}", s):
        chunk = m.group(0)
        if 2 <= len(chunk) <= 8:
            words.append(chunk)
        # sliding window 取所有 2-4 字子串
        for size in (2, 3, 4):
            for i in range(len(chunk) - size + 1):
                words.append(chunk[i:i + size])
    # 原生英文/数字名称
    for m in re.finditer(r"[A-Za-z0-9]{2,}", name):
        words.append(m.group(0))
    return words


class ProductManualRAG:
    """
    产品手册 RAG 主入口。

    使用示例:
        rag = ProductManualRAG()
        rag.add_manual_text("金葵花理财", text, source_file="金葵花.md")
        rag.build_index()
        ans = rag.query("起购金额是多少?", top_k=3)
        print(ans["answer"], ans["citations"])
    """

    def __init__(self, chunk_max_chars: int = 400, chunk_overlap: int = 50):
        self.chunker = DocumentChunker(max_chars=chunk_max_chars, overlap=chunk_overlap)
        self.chunks: List[Chunk] = []
        self.bm25 = BM25Index()
        self.tfidf = TFIDFIndex()
        self._built = False

    # ---------- 索引构建 ----------

    def add_manual_text(self, product: str, text: str, source_file: str = "") -> int:
        """添加产品手册文本，自动切分。返回新增 chunk 数。"""
        new_chunks = self.chunker.chunk(text, product=product, source_file=source_file)
        self.chunks.extend(new_chunks)
        self._built = False
        return len(new_chunks)

    def add_manual_file(self, product: str, path: str) -> int:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        return self.add_manual_text(product, text, source_file=os.path.basename(path))

    def load_knowledge_base(self, kb_dir: str) -> Dict[str, int]:
        """
        加载知识库目录：
        - kb_dir/<产品名>/*.md 或 *.txt
        - 或 kb_dir/<产品名>.md 单文件
        """
        stats: Dict[str, int] = {}
        if not os.path.isdir(kb_dir):
            return stats
        for entry in sorted(os.listdir(kb_dir)):
            full = os.path.join(kb_dir, entry)
            if os.path.isdir(full):
                product = entry
                cnt = 0
                for sub in sorted(os.listdir(full)):
                    if sub.lower().endswith((".md", ".txt")):
                        cnt += self.add_manual_file(product, os.path.join(full, sub))
                stats[product] = cnt
            elif entry.lower().endswith((".md", ".txt")):
                product = os.path.splitext(entry)[0]
                stats[product] = self.add_manual_file(product, full)
        return stats

    def build_index(self) -> Dict[str, int]:
        if not self.chunks:
            return {"chunks": 0, "products": 0}
        self.bm25.build(self.chunks)
        self.tfidf.build(self.chunks)
        self._built = True
        return {
            "chunks": len(self.chunks),
            "products": len({c.product for c in self.chunks}),
            "avg_chunk_chars": round(
                sum(len(c.text) for c in self.chunks) / len(self.chunks), 1
            ),
        }

    # ---------- 检索 ----------

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        product_filter: Optional[str] = None,
    ) -> List[RetrievalHit]:
        if not self._built:
            self.build_index()
        # 自动推断产品：查询中出现哪个已加载产品名的关键字则默认 filter
        if product_filter is None:
            inferred = self._infer_product(query)
            if inferred:
                product_filter = inferred
        bm = self.bm25.search(query, top_k=top_k * 3)
        tf = self.tfidf.search(query, top_k=top_k * 3)
        fused = rrf_fuse(bm, tf, top_k=top_k * 6)

        # 意图 bonus：查询含「金额/额度/起购/利率/费率/期限/时间/多少/几」时，
        # 优先含有数字 + 货币/百分号/天数的 chunk
        import re
        intent_keywords = ("金额", "额度", "起购", "起点", "利率", "费率",
                           "期限", "期间", "多少", "几个", "几年",
                           "门槛", "费用", "年费", "保额", "代价")
        has_intent = any(k in query for k in intent_keywords)
        num_pat = re.compile(r"\d+([.,]\d+)?\s*(万|%|千|亿|元|天|个月|年|次|件|个|期|同)")

        boosted: List[Tuple[int, float, List[str]]] = []
        for idx, score, terms in fused:
            bonus = 0.0
            ch = self.chunks[idx]
            q_toks = set(tokenize(query))
            sec_toks = set(tokenize(ch.section))
            # 查询词出现在章节标题中 → 强相关信号
            sec_overlap = q_toks & sec_toks
            if sec_overlap:
                bonus += 0.005 * len(sec_overlap)
            # 查询词在 chunk 正文中的独特命中（扣除产品名这种通用命中）
            text_toks = set(tokenize(ch.text))
            unique_matches = (q_toks & text_toks) - set(tokenize(ch.product))
            if unique_matches:
                bonus += 0.002 * len(unique_matches)
            boosted.append((idx, score + bonus, terms))
        boosted.sort(key=lambda x: x[1], reverse=True)

        hits: List[RetrievalHit] = []
        for idx, score, terms in boosted:
            chunk = self.chunks[idx]
            if product_filter and chunk.product != product_filter:
                continue
            hits.append(RetrievalHit(
                chunk=chunk,
                score=round(score, 4),
                matched_terms=terms[:10],
                retrieval_method="hybrid",
            ))
            if len(hits) >= top_k:
                break
        return hits

    def _infer_product(self, query: str) -> Optional[str]:
        """从查询中推断明确提及的产品名。"""
        products = {c.product for c in self.chunks}
        scores = {}
        for p in products:
            keys = set([p])
            keys.update(re_findall_keywords(p))
            # 以“最长命中字数”作为打分，避免“招”这种单字被多个产品误匹配
            hits = [k for k in keys if k and k in query]
            scores[p] = max((len(k) for k in hits), default=0)
        best = max(scores.items(), key=lambda x: x[1]) if scores else (None, 0)
        return best[0] if best[1] >= 2 else None

    # ---------- 问答（抽取式） ----------

    def query(
        self,
        question: str,
        top_k: int = 3,
        product_filter: Optional[str] = None,
        max_answer_chars: int = 350,
    ) -> Dict[str, Any]:
        """
        抽取式问答 —— 不依赖 LLM，直接基于 Top-K 段落拼接答案 + 出处。
        返回结构:
            {
              "question": str,
              "answer": str,              # 抽取拼接的答案文本
              "citations": [              # 出处列表
                {"product","section","page","snippet","score"}
              ],
              "hits": [...],              # 原始命中(可用于二次处理)
              "no_answer": bool,          # 命中过弱时为 True
            }
        """
        hits = self.retrieve(question, top_k=top_k, product_filter=product_filter)
        if not hits:
            return {
                "question": question,
                "answer": "未在产品手册中找到相关内容，建议联系客户经理或查阅纸质资料。",
                "citations": [],
                "hits": [],
                "no_answer": True,
            }

        # 弱命中识别：top1 分数偏低 + 关键词命中数少
        top = hits[0]
        weak = top.score < 0.012 and len(top.matched_terms) <= 1
        # 答案抽取：从 Top1 段落中找包含最多查询关键词的句子
        answer_text = self._extract_answer(question, hits, max_chars=max_answer_chars)
        citations = []
        for h in hits:
            snippet = h.chunk.text.strip().replace("\n", " ")
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            citations.append({
                "product": h.chunk.product,
                "section": h.chunk.section,
                "page": h.chunk.page,
                "source_file": h.chunk.source_file,
                "snippet": snippet,
                "score": h.score,
                "matched_terms": h.matched_terms,
            })

        return {
            "question": question,
            "answer": answer_text,
            "citations": citations,
            "hits": [asdict(h.chunk) | {"score": h.score} for h in hits],
            "no_answer": weak,
        }

    def _extract_answer(
        self, question: str, hits: List[RetrievalHit], max_chars: int = 350
    ) -> str:
        """从 Top-K 段落中挑出关键词命中最密集的句子，拼接为答案。"""
        import re
        q_tokens = set(tokenize(question))
        scored_sentences: List[Tuple[float, str, str]] = []
        for h in hits[:3]:
            sentences = re.split(r"(?<=[。！？!?\.\n])\s*", h.chunk.text)
            for s in sentences:
                s = s.strip()
                if not s or len(s) < 4:
                    continue
                s_tokens = set(tokenize(s))
                overlap = len(q_tokens & s_tokens)
                if overlap == 0:
                    continue
                density = overlap / (len(s_tokens) or 1)
                score = overlap + density * 2
                scored_sentences.append((score, s, h.chunk.product))
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        picked: List[str] = []
        total = 0
        used_products = []
        for _sc, s, prod in scored_sentences:
            if s in picked:
                continue
            if total + len(s) > max_chars:
                break
            picked.append(s)
            used_products.append(prod)
            total += len(s)
            if len(picked) >= 4:
                break
        if not picked:
            head = hits[0].chunk.text.strip().replace("\n", " ")
            return head[:max_chars]
        return " ".join(picked)

    # ---------- 持久化 ----------

    def dump_index(self, path: str) -> None:
        data = {
            "chunks": [asdict(c) for c in self.chunks],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_index(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.chunks = [Chunk(**c) for c in data["chunks"]]
        self.build_index()


class RAGFormatter:
    """格式化输出（适配企微 / 飞书卡片 / CLI）。"""

    @staticmethod
    def format_text(result: Dict[str, Any]) -> str:
        lines = [f"❓ 问题：{result['question']}", ""]
        if result.get("no_answer"):
            lines.append("⚠️ 未在手册中找到直接答案（命中较弱），以下为最接近的内容：")
        lines.append(f"💡 答案：{result['answer']}")
        lines.append("")
        if result["citations"]:
            lines.append("📚 出处：")
            for i, c in enumerate(result["citations"], 1):
                page = f" P{c['page']}" if c.get("page") else ""
                lines.append(
                    f"  [{i}] 《{c['product']}》 → {c['section']}{page}"
                    f"  (匹配度 {c['score']})"
                )
                lines.append(f"      {c['snippet']}")
        return "\n".join(lines)

    @staticmethod
    def format_card(result: Dict[str, Any]) -> Dict[str, Any]:
        """企微/飞书 template_card 格式。"""
        sources = "\n".join(
            f"[{i}] {c['product']} · {c['section']}" for i, c in enumerate(result["citations"][:3], 1)
        )
        return {
            "card_type": "text_notice",
            "main_title": {"title": "📖 产品手册问答", "desc": result["question"][:30]},
            "emphasis_content": {
                "title": result["answer"][:80] + ("..." if len(result["answer"]) > 80 else ""),
                "desc": "AI 抽取答案",
            },
            "horizontal_content_list": [
                {"keyname": "出处", "value": sources or "（无）"},
                {"keyname": "命中数", "value": str(len(result["citations"]))},
                {"keyname": "置信度", "value": "高" if not result.get("no_answer") else "低（建议复核）"},
            ],
        }
