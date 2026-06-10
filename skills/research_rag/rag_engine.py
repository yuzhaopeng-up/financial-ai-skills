"""
研报RAG引擎
============
BM25 + TF-IDF 双路检索 + RRF 融合 + 多轮对话上下文 + 引用标注

支持：
  - 自然语言查询研报知识库
  - BM25 + TF-IDF 混合检索（RRF 融合）
  - 多轮对话上下文（最近 3 轮）
  - 引用来源标注（行业/公司/报告/页码）
  - PDF 研报解析（可选）
"""
from __future__ import annotations
import copy
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 依赖检测：优先使用安装的库，降级到轻量内置实现
# ---------------------------------------------------------------------------
try:
    from pdfminer.high_level import extract_text as _pdf_extract
    _PDF_AVAILABLE = True
except Exception:
    _PDF_AVAILABLE = False

try:
    import numpy as np
    _NUMPY_AVAILABLE = True
except Exception:
    _NUMPY_AVAILABLE = False
    np = None

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)          # .../skills/
RESEARCH_REPORT_DIR = os.path.join(SKILL_DIR, "research-report")
TEMPLATES_PATH = os.path.join(RESEARCH_REPORT_DIR, "report_templates.json")


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    """知识块。"""
    chunk_id: str
    source_type: str           # "industry" | "company" | "report"
    source_name: str           # "新能源" | "宁德时代" | "研报_XXX"
    section: str               # "行业趋势" | "公司基本面" | "财务" | "风险" | ...
    content: str               # 原始文本
    tokens: List[str] = field(default_factory=list)   # 分词结果
    importance: float = 1.0   # 章节权重（用于结果重排）

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Citation:
    """引用标注。"""
    chunk_id: str
    source_type: str
    source_name: str
    section: str
    snippet: str          # 匹配的原文片段
    score: float = 0.0

    def label(self) -> str:
        """人类可读的来源标签。"""
        return f"【{self.source_type}:{self.source_name}·{self.section}】"


@dataclass
class SearchResult:
    """检索结果。"""
    chunk: Chunk
    citation: Citation
    rrfrank: int = 0      # RRF 融合排名
    final_score: float = 0.0


@dataclass
class Turn:
    """对话轮次。"""
    query: str
    answer: str
    citations: List[Citation]
    timestamp: str


@dataclass
class RAGAnswer:
    """RAG 回答。"""
    query: str
    answer: str
    citations: List[Citation]
    conversation_turns: List[Turn]   # 最近 N 轮上下文
    sources_used: List[str]          # 涉及的知识源
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "answer": self.answer,
            "citations": [asdict(c) for c in self.citations],
            "conversation_turns": [
                {"query": t.query, "answer": t.answer, "timestamp": t.timestamp}
                for t in self.conversation_turns
            ],
            "sources_used": self.sources_used,
            "generated_at": self.generated_at,
        }


# ---------------------------------------------------------------------------
# 文本处理工具
# ---------------------------------------------------------------------------

def tokenize_chinese(text: str) -> List[str]:
    """轻量中文分词（正则 + 停用词过滤）。"""
    # 去除标点、英文、数字单独部分
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z]", " ", text)
    tokens = text.split()
    # 停用词
    stopwords = {
        "的", "了", "是", "在", "和", "与", "及", "为", "对", "等",
        "以", "于", "或", "而", "但", "及", "被", "将", "把", "从",
        "到", "由", "向", "此", "该", "这", "那", "有", "可", "也",
        "会", "能", "可", "已", "已", "曾", "并", "不", "很", "更",
        "上", "下", "中", "其", "所", "则", "之", "一", "年", "月",
    }
    return [t for t in tokens if len(t) >= 2 and t not in stopwords]


def compute_tf(tokens: List[str]) -> Dict[str, float]:
    """词频（TF）。"""
    if not tokens:
        return {}
    freq = Counter(tokens)
    total = len(tokens)
    return {t: f / total for t, f in freq.items()}


def compute_idf(token2docs: Dict[str, int], total_docs: int) -> Dict[str, float]:
    """IDF（Inverse Document Frequency）。"""
    idf = {}
    for token, doc_freq in token2docs.items():
        # 加 1 平滑，避免零除
        idf[token] = math.log((total_docs + 1) / (doc_freq + 1)) + 1
    return idf


# ---------------------------------------------------------------------------
# BM25 实现
# ---------------------------------------------------------------------------

class BM25:
    """BM25 排序算法（内置实现，无需外部依赖）。"""

    def __init__(self, chunks: List[Chunk], k1: float = 1.5, b: float = 0.75):
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.avgdl = 0.0
        self.doc_lengths: List[int] = []
        self.doc_tf: List[Dict[str, float]] = []
        self.token2docs: Dict[str, int] = defaultdict(int)  # 包含某词的文档数

        self._build_index()

    def _build_index(self):
        for chunk in self.chunks:
            tokens = chunk.tokens
            self.doc_lengths.append(len(tokens))
            tf = compute_tf(tokens)
            self.doc_tf.append(tf)
            for t in tf:
                self.token2docs[t] += 1

        self.avgdl = sum(self.doc_lengths) / max(len(self.doc_lengths), 1)
        N = len(self.chunks)
        self.idf = compute_idf(dict(self.token2docs), N)

    def score(self, query_tokens: List[str], doc_idx: int) -> float:
        """计算 BM25 分数。"""
        score = 0.0
        doc_len = self.doc_lengths[doc_idx]
        tf_doc = self.doc_tf[doc_idx]

        for t in query_tokens:
            if t not in self.idf:
                continue
            idf = self.idf[t]
            tf_q = tf_doc.get(t, 0.0)
            numerator = tf_q * (self.k1 + 1)
            denominator = tf_q + self.k1 * (1 - self.b + self.b * doc_len / max(self.avgdl, 1))
            score += idf * numerator / max(denominator, 1e-9)
        return score

    def search(self, query_tokens: List[str], top_k: int = 5) -> List[Tuple[int, float]]:
        """返回 (chunk_idx, bm25_score) 列表。"""
        scores = [self.score(query_tokens, i) for i in range(len(self.chunks))]
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]


# ---------------------------------------------------------------------------
# TF-IDF 余弦相似度
# ---------------------------------------------------------------------------

class TFIDFVectorizer:
    """TF-IDF 向量化器（内置实现，无需 sklearn）。"""

    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks
        self.idf: Dict[str, float] = {}
        self.doc_norms: List[float] = []
        self._build()

    def _build(self):
        token2docs: Dict[str, int] = defaultdict(int)
        doc_tfs: List[Dict[str, float]] = []

        for chunk in self.chunks:
            tokens = chunk.tokens
            tf = compute_tf(tokens)
            doc_tfs.append(tf)
            for t in tf:
                token2docs[t] += 1

        N = len(self.chunks)
        self.idf = compute_idf(dict(token2docs), N)

        # 计算每个文档的 L2 范数
        self.doc_norms = []
        for tf in doc_tfs:
            norm_sq = 0.0
            for t, tf_val in tf.items():
                idf = self.idf.get(t, 0.0)
                norm_sq += (tf_val * idf) ** 2
            self.doc_norms.append(math.sqrt(norm_sq) + 1e-9)

    def vectorize(self, tokens: List[str]) -> Dict[str, float]:
        """将 token 列表转换为 TF-IDF 向量（稀疏 dict 表示）。"""
        tf = compute_tf(tokens)
        vec = {}
        for t, tf_val in tf.items():
            if t in self.idf:
                vec[t] = tf_val * self.idf[t]
        return vec

    def cosine_score(self, query_vec: Dict[str, float], doc_idx: int) -> float:
        """计算 query 与指定文档的余弦相似度。"""
        doc_tf = self.doc_tf[doc_idx]
        doc_norm = self.doc_norms[doc_idx]

        dot = 0.0
        for t, q_val in query_vec.items():
            if t in doc_tf:
                idf = self.idf.get(t, 0.0)
                dot += q_val * doc_tf[t] * idf

        q_norm = math.sqrt(sum(v ** 2 for v in query_vec.values())) + 1e-9
        return dot / (q_norm * doc_norm)


class TFIDFIndex:
    """TF-IDF 索引（懒加载，第一次 search 时构建）。"""

    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks
        self._index: Optional[TFIDFVectorizer] = None
        self._doc_tfs: List[Dict[str, float]] = []

    def ensure_index(self):
        if self._index is None:
            # 提前构建 doc_tfs 供 cosine_score 使用
            self._doc_tfs = [compute_tf(c.tokens) for c in self.chunks]
            self._index = TFIDFVectorizer(self.chunks)
            # 注入 doc_tf（TFIDFVectorizer 不保存，这里用 monkey-patch）
            self._index.doc_tf = self._doc_tfs

    def search(self, query_tokens: List[str], top_k: int = 5) -> List[Tuple[int, float]]:
        self.ensure_index()
        query_vec = self._index.vectorize(query_tokens)
        scores = [self._index.cosine_score(query_vec, i) for i in range(len(self.chunks))]
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]


# ---------------------------------------------------------------------------
# RRF 融合
# ---------------------------------------------------------------------------

def rrf_fusion(
    bm25_results: List[Tuple[int, float]],
    tfidf_results: List[Tuple[int, float]],
    k: int = 60,
) -> List[Tuple[int, float, int]]:
    """
    Reciprocal Rank Fusion.
    返回: List[(chunk_idx, fused_score, rrfrank)]
    """
    scores: Dict[int, float] = defaultdict(float)

    for rank, (idx, score) in enumerate(bm25_results):
        scores[idx] += 1.0 / (k + rank + 1)

    for rank, (idx, score) in enumerate(tfidf_results):
        scores[idx] += 1.0 / (k + rank + 1)

    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(idx, s, r) for r, (idx, s) in enumerate(fused)]


# ---------------------------------------------------------------------------
# 知识库构建
# ---------------------------------------------------------------------------

def load_templates() -> Dict[str, Any]:
    """加载研报模板数据。"""
    if os.path.exists(TEMPLATES_PATH):
        with open(TEMPLATES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"industries": {}, "companies": {}}


def build_industry_chunks(templates: Dict[str, Any]) -> List[Chunk]:
    """从行业数据构建知识块。"""
    chunks = []
    for ind_name, ind_data in templates.get("industries", {}).items():
        if ind_name == "通用":
            continue
        sid = f"ind_{ind_name}"
        # 趋势
        chunks.append(Chunk(
            chunk_id=f"{sid}_trend",
            source_type="industry",
            source_name=ind_name,
            section="行业趋势",
            content="|".join(ind_data.get("trend_keywords", [])),
            importance=1.2,
        ))
        # 驱动
        chunks.append(Chunk(
            chunk_id=f"{sid}_driver",
            source_type="industry",
            source_name=ind_name,
            section="增长驱动",
            content="|".join(ind_data.get("drivers", [])),
            importance=1.1,
        ))
        # 风险
        chunks.append(Chunk(
            chunk_id=f"{sid}_risk",
            source_type="industry",
            source_name=ind_name,
            section="行业风险",
            content="|".join(ind_data.get("risks", [])),
            importance=1.0,
        ))
        # 龙头
        chunks.append(Chunk(
            chunk_id=f"{sid}_leader",
            source_type="industry",
            source_name=ind_name,
            section="龙头公司",
            content="|".join(ind_data.get("leaders", [])),
            importance=0.9,
        ))
        # 关键指标
        chunks.append(Chunk(
            chunk_id=f"{sid}_metric",
            source_type="industry",
            source_name=ind_name,
            section="关键指标",
            content="|".join(ind_data.get("key_metrics", [])),
            importance=0.8,
        ))
    return chunks


def build_company_chunks(templates: Dict[str, Any]) -> List[Chunk]:
    """从公司数据构建知识块。"""
    chunks = []
    for comp_name, comp_data in templates.get("companies", {}).items():
        sid = f"comp_{comp_name}"
        # 业务
        chunks.append(Chunk(
            chunk_id=f"{sid}_biz",
            source_type="company",
            source_name=comp_name,
            section="主营业务",
            content="|".join(comp_data.get("business_segments", [])),
            importance=1.2,
        ))
        # 护城河
        chunks.append(Chunk(
            chunk_id=f"{sid}_moat",
            source_type="company",
            source_name=comp_name,
            section="护城河",
            content="|".join(comp_data.get("moat", [])),
            importance=1.3,
        ))
        # 亮点
        chunks.append(Chunk(
            chunk_id=f"{sid}_highlight",
            source_type="company",
            source_name=comp_name,
            section="公司亮点",
            content="|".join(comp_data.get("highlights", [])),
            importance=1.1,
        ))
        # 风险
        chunks.append(Chunk(
            chunk_id=f"{sid}_risk",
            source_type="company",
            source_name=comp_name,
            section="公司风险",
            content="|".join(comp_data.get("risks", [])),
            importance=1.0,
        ))
    return chunks


def build_knowledge_base() -> List[Chunk]:
    """构建完整知识库。"""
    templates = load_templates()
    chunks = []
    chunks += build_industry_chunks(templates)
    chunks += build_company_chunks(templates)

    # 分词
    for chunk in chunks:
        chunk.tokens = tokenize_chinese(chunk.content)

    return chunks


# ---------------------------------------------------------------------------
# 答案生成（模板拼装 + LLM-free 规则引擎）
# ---------------------------------------------------------------------------

def generate_answer(query: str, results: List[SearchResult]) -> str:
    """基于检索结果生成答案（规则模板引擎，无需外部 LLM）。"""
    if not results:
        return "抱歉，知识库中未找到与您查询相关的内容。建议尝试更换关键词，或补充行业/公司名称。"

    query_lower = query.lower()
    parts: List[str] = []

    # 判断查询类型
    is_company_query = any(
        kw in query for kw in ["公司", "企业", "龙头", "宁德", "比亚迪",
                               "招商银行", "贵州茅台", "宝钢"]
    )
    is_industry_query = any(
        kw in query for kw in ["行业", "趋势", "市场", "赛道"]
    )
    is_risk_query = any(
        kw in query for kw in ["风险", "风险点", "担忧", "不利"]
    )
    is_metric_query = any(
        kw in query for kw in ["指标", "估值", "财务", "ROE", "PE", "PB"]
    )
    is_driver_query = any(
        kw in query for kw in ["驱动", "增长", "动力", "利好", "催化"]
    )

    # 收集各来源信息
    industry_info: Dict[str, Dict[str, str]] = {}
    company_info: Dict[str, Dict[str, str]] = {}

    for res in results:
        c = res.chunk
        src = c.source_name
        sec = c.section

        if c.source_type == "industry":
            if src not in industry_info:
                industry_info[src] = {}
            industry_info[src][sec] = c.content.replace("|", "、")

        elif c.source_type == "company":
            if src not in company_info:
                company_info[src] = {}
            company_info[src][sec] = c.content.replace("|", "、")

    # 生成回答
    if is_company_query and company_info:
        for comp, secs in company_info.items():
            parts.append(f"🏢 **{comp}** 关键信息：")
            if "护城河" in secs:
                parts.append(f"  • 护城河：{secs['护城河']}")
            if "主营业务" in secs:
                parts.append(f"  • 主营业务：{secs['主营业务']}")
            if "公司亮点" in secs:
                parts.append(f"  • 近期亮点：{secs['公司亮点']}")
            if "公司风险" in secs:
                parts.append(f"  ⚠️ 关注风险：{secs['公司风险']}")
            parts.append("")

    if is_industry_query and industry_info:
        for ind, secs in industry_info.items():
            parts.append(f"📈 **{ind}** 行业扫描：")
            if "行业趋势" in secs:
                parts.append(f"  • 核心趋势：{secs['行业趋势']}")
            if "增长驱动" in secs:
                parts.append(f"  • 增长驱动：{secs['增长驱动']}")
            if "龙头公司" in secs:
                parts.append(f"  • 龙头公司：{secs['龙头公司']}")
            parts.append("")

    if is_risk_query:
        risk_items = []
        for res in results:
            c = res.chunk
            if "风险" in c.section:
                risk_items.append(f"  ⚠ {c.source_name}·{c.section}：{c.content.replace('|', '；')}")
        if risk_items:
            parts.append("🔍 **风险提示汇总**：")
            parts.extend(risk_items[:5])
            parts.append("")

    if is_metric_query:
        metric_items = []
        for res in results:
            c = res.chunk
            if c.section in ("关键指标", "财务", "护城河"):
                metric_items.append(f"  • {c.source_name}：{c.content.replace('|', '；')}")
        if metric_items:
            parts.append("📊 **关键指标参考**：")
            parts.extend(metric_items[:5])
            parts.append("")

    if is_driver_query:
        driver_items = []
        for res in results:
            c = res.chunk
            if "驱动" in c.section or "增长" in c.section or "亮点" in c.section:
                driver_items.append(f"  🚀 {c.source_name}：{c.content.replace('|', '；')}")
        if driver_items:
            parts.append("🚀 **增长驱动与催化剂**：")
            parts.extend(driver_items[:5])
            parts.append("")

    # 默认摘要
    if not parts:
        parts.append("📋 **综合信息汇总**（根据您的查询）：")
        for res in results[:4]:
            c = res.chunk
            parts.append(f"  • {c.source_type}:{c.source_name}·{c.section}：{c.content[:60]}...")

    return "\n".join(parts).strip()


# ---------------------------------------------------------------------------
# PDF 解析（可选功能）
# ---------------------------------------------------------------------------

def parse_pdf_chunk(pdf_path: str) -> List[Chunk]:
    """从 PDF 文件解析知识块。"""
    if not _PDF_AVAILABLE:
        return []
    try:
        text = _pdf_extract(pdf_path)
        # 按段落分割
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
        chunks = []
        for i, para in enumerate(paragraphs):
            tokens = tokenize_chinese(para)
            if len(tokens) < 3:
                continue
            chunks.append(Chunk(
                chunk_id=f"pdf_{os.path.basename(pdf_path)}_p{i}",
                source_type="report",
                source_name=os.path.basename(pdf_path),
                section=f"第{i+1}段",
                content=para[:500],
                tokens=tokens,
                importance=1.0,
            ))
        return chunks
    except Exception as e:
        return []


# ---------------------------------------------------------------------------
# 核心 RAG 引擎
# ---------------------------------------------------------------------------

class ResearchRAGEngine:
    """
    研报 RAG 检索引擎。

    使用 BM25 + TF-IDF 双路检索，RRF 融合，支持多轮对话上下文。
    知识库来源：research_report 技能的 report_templates.json（行业+公司数据）。
    """

    def __init__(self, max_turns: int = 3, top_k: int = 5):
        """
        Args:
            max_turns: 多轮对话保留最近 N 轮
            top_k: 每次检索返回的最大结果数
        """
        self.max_turns = max_turns
        self.top_k = top_k
        self.conversation: List[Turn] = []   # 对话历史
        self._chunks: Optional[List[Chunk]] = None
        self._bm25: Optional[BM25] = None
        self._tfidf: Optional[TFIDFIndex] = None

    @property
    def chunks(self) -> List[Chunk]:
        if self._chunks is None:
            self._chunks = build_knowledge_base()
        return self._chunks

    def _ensure_indexes(self):
        if self._bm25 is None:
            self._bm25 = BM25(self.chunks)
            self._tfidf = TFIDFIndex(self.chunks)

    def search(self, query: str, top_k: Optional[int] = None) -> List[SearchResult]:
        """
        检索查询，返回融合排序结果。

        Args:
            query: 自然语言查询
            top_k: 返回结果数，默认 self.top_k
        """
        self._ensure_indexes()
        k = top_k or self.top_k

        # 扩展查询（融入对话历史）
        expanded_query = self._expand_with_history(query)
        query_tokens = tokenize_chinese(expanded_query)

        if not query_tokens:
            return []

        # BM25 检索
        bm25_results = self._bm25.search(query_tokens, top_k=k * 2)

        # TF-IDF 检索
        tfidf_results = self._tfidf.search(query_tokens, top_k=k * 2)

        # RRF 融合
        fused = rrf_fusion(bm25_results, tfidf_results)

        # 构建 SearchResult
        results = []
        for rank, (idx, fused_score, rrfrank) in enumerate(fused[:k]):
            chunk = self.chunks[idx]
            citation = Citation(
                chunk_id=chunk.chunk_id,
                source_type=chunk.source_type,
                source_name=chunk.source_name,
                section=chunk.section,
                snippet=chunk.content[:200],
                score=fused_score,
            )
            results.append(SearchResult(
                chunk=chunk,
                citation=citation,
                rrfrank=rank + 1,
                final_score=fused_score,
            ))

        return results

    def _expand_with_history(self, query: str) -> str:
        """将最近对话内容拼入查询，实现上下文感知。"""
        parts = [query]
        for turn in self.conversation[-self.max_turns:]:
            parts.append(turn.query)
            parts.append(turn.answer[:100])
        return " ".join(parts)

    def query(self, user_query: str) -> RAGAnswer:
        """
        主入口：接收用户查询，返回带引用的答案。

        Args:
            user_query: 自然语言查询，例如 "宁德时代储能业务竞争力分析"
        """
        # 检索
        results = self.search(user_query)

        # 生成答案
        answer_text = generate_answer(user_query, results)

        # 收集引用
        citations = [r.citation for r in results]

        # 收集来源
        sources = list(set(f"{c.source_type}:{c.source_name}" for c in citations))

        # 更新对话历史
        turn = Turn(
            query=user_query,
            answer=answer_text,
            citations=citations,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.conversation.append(turn)
        # 保留最近 N 轮
        self.conversation = self.conversation[-self.max_turns:]

        return RAGAnswer(
            query=user_query,
            answer=answer_text,
            citations=citations,
            conversation_turns=self.conversation[:-1],   # 不含当前轮
            sources_used=sources,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def clear_history(self):
        """清空对话历史。"""
        self.conversation = []

    def add_pdf(self, pdf_path: str) -> int:
        """加载额外 PDF 到知识库，返回新增 chunk 数。"""
        new_chunks = parse_pdf_chunk(pdf_path)
        if not new_chunks:
            return 0
        self._chunks = None   # 强制重建
        self._bm25 = None
        self._tfidf = None
        return len(new_chunks)


# ---------------------------------------------------------------------------
# 便捷函数
# ---------------------------------------------------------------------------

_DEFAULT_ENGINE: Optional[ResearchRAGEngine] = None

def get_engine() -> ResearchRAGEngine:
    global _DEFAULT_ENGINE
    if _DEFAULT_ENGINE is None:
        _DEFAULT_ENGINE = ResearchRAGEngine()
    return _DEFAULT_ENGINE


def query(query: str) -> RAGAnswer:
    """单次查询（使用全局引擎）。"""
    return get_engine().query(query)
