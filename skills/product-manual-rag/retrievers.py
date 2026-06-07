"""
RAG 检索器：BM25 + TF-IDF 双路 + RRF 融合。
"""
from __future__ import annotations
import math
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional

try:
    from .rag_engine import Chunk, RetrievalHit, tokenize
except ImportError:  # 直接作为脚本/独立模块导入时
    from rag_engine import Chunk, RetrievalHit, tokenize


class BM25Index:
    """经典 BM25Okapi 实现（k1=1.5, b=0.75）。"""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: List[Chunk] = []
        self.doc_freq: Dict[str, int] = defaultdict(int)
        self.doc_len: List[int] = []
        self.tf: List[Counter] = []
        self.avg_len: float = 0.0
        self.N: int = 0
        self._idf_cache: Dict[str, float] = {}

    def build(self, chunks: List[Chunk]) -> None:
        self.chunks = chunks
        self.tf = []
        self.doc_len = []
        self.doc_freq = defaultdict(int)
        for c in chunks:
            # 只对 section 标题加权，产品名交由上层 _infer_product 处理
            toks = tokenize(c.text) + tokenize(c.section) * 3
            tf = Counter(toks)
            self.tf.append(tf)
            self.doc_len.append(len(toks))
            for term in tf.keys():
                self.doc_freq[term] += 1
        self.N = len(chunks)
        self.avg_len = sum(self.doc_len) / self.N if self.N else 0.0
        self._idf_cache = {
            t: math.log(1 + (self.N - df + 0.5) / (df + 0.5))
            for t, df in self.doc_freq.items()
        }

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float, List[str]]]:
        q_toks = tokenize(query)
        scores: Dict[int, float] = defaultdict(float)
        matched: Dict[int, set] = defaultdict(set)
        for term in set(q_toks):
            idf = self._idf_cache.get(term)
            if idf is None:
                continue
            for i, tf in enumerate(self.tf):
                f = tf.get(term, 0)
                if not f:
                    continue
                dl = self.doc_len[i]
                denom = f + self.k1 * (1 - self.b + self.b * dl / (self.avg_len or 1))
                scores[i] += idf * (f * (self.k1 + 1)) / (denom or 1)
                matched[i].add(term)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [(i, s, sorted(matched[i])) for i, s in ranked]


class TFIDFIndex:
    """TF-IDF 余弦相似度（补充 BM25 在短查询下的稳定性）。"""

    def __init__(self):
        self.chunks: List[Chunk] = []
        self.vectors: List[Dict[str, float]] = []
        self.norms: List[float] = []
        self.idf: Dict[str, float] = {}

    def build(self, chunks: List[Chunk]) -> None:
        self.chunks = chunks
        N = len(chunks)
        doc_freq: Dict[str, int] = defaultdict(int)
        tfs: List[Counter] = []
        for c in chunks:
            tf = Counter(tokenize(c.text) + tokenize(c.section) * 3)
            tfs.append(tf)
            for t in tf.keys():
                doc_freq[t] += 1
        self.idf = {t: math.log((N + 1) / (df + 1)) + 1 for t, df in doc_freq.items()}
        self.vectors = []
        self.norms = []
        for tf in tfs:
            length = sum(tf.values()) or 1
            v = {t: (c / length) * self.idf.get(t, 0.0) for t, c in tf.items()}
            self.vectors.append(v)
            self.norms.append(math.sqrt(sum(x * x for x in v.values())) or 1.0)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float, List[str]]]:
        q_toks = tokenize(query)
        if not q_toks:
            return []
        q_tf = Counter(q_toks)
        q_len = sum(q_tf.values())
        q_vec = {t: (c / q_len) * self.idf.get(t, 0.0) for t, c in q_tf.items()}
        q_norm = math.sqrt(sum(x * x for x in q_vec.values())) or 1.0
        scored: List[Tuple[int, float, List[str]]] = []
        for i, v in enumerate(self.vectors):
            if not v:
                continue
            common = set(v.keys()) & set(q_vec.keys())
            if not common:
                continue
            dot = sum(q_vec[t] * v[t] for t in common)
            sim = dot / (q_norm * self.norms[i])
            scored.append((i, sim, sorted(common)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


def rrf_fuse(
    *result_lists: List[Tuple[int, float, List[str]]],
    k: int = 60,
    top_k: int = 5,
) -> List[Tuple[int, float, List[str]]]:
    """Reciprocal Rank Fusion —— 多路检索结果融合。"""
    score: Dict[int, float] = defaultdict(float)
    terms: Dict[int, set] = defaultdict(set)
    for results in result_lists:
        for rank, (idx, _s, ts) in enumerate(results):
            score[idx] += 1.0 / (k + rank + 1)
            terms[idx].update(ts)
    ordered = sorted(score.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [(i, s, sorted(terms[i])) for i, s in ordered]
