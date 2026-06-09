"""
监管政策智能问答引擎 - 核心模块

提供：
- RegulatoryPolicyRAG：主 RAG 类，支持 BM25+TF-IDF 双路检索
- RAGFormatter：格式化输出（text/json/card）
- Chunk：政策文档块数据结构
"""
from __future__ import annotations
import re
import os
import json
import math
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class Chunk:
    """政策文档块。"""
    chunk_id: str
    text: str
    agency: str           # 监管机构简称: cbirc/pboc/csrc/nfra/misc
    doc_title: str        # 政策文件名
    section: str          # 章节标题
    section_level: int    # 标题层级 1-4
    policy_ref: str       # 政策文号/发文字号
    effective_date: str    # 生效日期
    raw_path: str         # 原始文件路径
    keywords: List[str] = field(default_factory=list)
    normalized_section: str = ""  # 标准化章节名（用于匹配）

    def __post_init__(self):
        if not self.keywords:
            self.keywords = self._extract_keywords()

    def _extract_keywords(self) -> List[str]:
        """从文本中提取关键词（监管术语）。"""
        patterns = [
            r'第[一二三四五六七八九十百零\d]+条',
            r'[一二三四五六七八九十]+、',
            r'[（\(][^)）]+[）\)]',
            r'应当|必须|不得|禁止|可以|鼓励',
            r'\d+[年月日]',
            r'\d+个?工作日',
            r'\d+[亿万]元',
            r'[A-Z]{2,}.*?(?:办法|指引|规定|通知|意见)',
        ]
        text = self.text
        keywords = []
        for p in patterns:
            for m in re.finditer(p, text):
                kw = m.group().strip()
                if len(kw) > 2 and kw not in keywords:
                    keywords.append(kw)
        return keywords[:20]


# ============================================================================
# 工具函数
# ============================================================================

def normalize_text(text: str) -> str:
    """文本规范化：小写化 + 空格标准化。"""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def tokenize(text: str) -> List[str]:
    """中文分词（基于字符 n-gram，兼容纯 Python 环境）。"""
    text = normalize_text(text)
    # 移除标点
    text = re.sub(r'[，。、；：？！""''（）【】《》]', ' ', text)
    # 数字+汉字+英文 组成词
    tokens = []
    for chunk in re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+|\d+(?:\.\d+)?', text):
        if re.search(r'[\u4e00-\u9fff]', chunk):
            # 中文字符：做 2-4 字滑动窗口
            for i in range(len(chunk) - 1):
                for n in range(2, min(5, len(chunk) - i + 1)):
                    tokens.append(chunk[i:i+n])
        else:
            tokens.append(chunk)
    return tokens


def compute_tf(tokens: List[str]) -> Dict[str, float]:
    """计算词频 TF。"""
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    total = len(tokens) or 1
    return {t: c / total for t, c in freq.items()}


def compute_idf(corpus: List[List[str]]) -> Dict[str, float]:
    """计算逆文档频率 IDF。N = 文档总数，df(t) = 包含词 t 的文档数。"""
    N = len(corpus)
    idf = {}
    for tokens in corpus:
        for t in set(tokens):
            idf[t] = idf.get(t, 0) + 1
    # IDF 平滑：log((N + 1) / (df + 1)) + 1
    for t in idf:
        idf[t] = math.log((N + 1) / (idf[t] + 1)) + 1
    for t in set():
        if t not in idf:
            idf[t] = math.log((N + 1) / 1) + 1
    return idf


class BM25:
    """BM25 检索器。"""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.avgdl = 0
        self.documents: List[List[str]] = []
        self.doc_lens: List[int] = []
        self.idf: Dict[str, float] = {}

    def build(self, chunk_texts: List[str]):
        """构建 BM25 索引。"""
        self.documents = [tokenize(t) for t in chunk_texts]
        self.doc_lens = [len(d) for d in self.documents]
        self.avgdl = sum(self.doc_lens) / len(self.doc_lens) if self.doc_lens else 1
        self.idf = compute_idf(self.documents)

    def score(self, query: str, doc_idx: int) -> float:
        """计算 query 对单个文档的 BM25 分数。"""
        query_tokens = tokenize(query)
        doc = self.documents[doc_idx]
        doc_len = self.doc_lens[doc_idx]
        score = 0.0
        for t in query_tokens:
            if t not in self.idf:
                continue
            tf = doc.count(t)
            idf = self.idf[t]
            num = tf * (self.k1 + 1)
            denom = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
            score += idf * num / denom if denom > 0 else 0
        return score

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """返回 [(doc_idx, score)] 列表，按分数降序。"""
        scores = [(i, self.score(query, i)) for i in range(len(self.documents))]
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]


class TFIDF:
    """TF-IDF 检索器（余弦相似度）。"""

    def __init__(self):
        self.doc_vectors: List[Dict[str, float]] = []
        self.query_vector: Dict[str, float] = {}
        self.doc_norms: List[float] = []

    def build(self, chunk_texts: List[str]):
        """构建 TF-IDF 索引。"""
        self.chunk_texts = chunk_texts  # 保存原始文本
        corpus = [tokenize(t) for t in chunk_texts]
        idf = compute_idf(corpus)
        self.doc_vectors = []
        for tokens in corpus:
            tf = compute_tf(tokens)
            vec = {t: tf[t] * idf.get(t, 0) for t in tf}
            self.doc_vectors.append(vec)
        self.doc_norms = [
            math.sqrt(sum(v * v for v in vec.values())) or 1
            for vec in self.doc_vectors
        ]

    def score(self, query: str, doc_idx: int) -> float:
        """计算余弦相似度。"""
        query_tokens = tokenize(query)
        query_tf = compute_tf(query_tokens)
        corpus = [tokenize(t) for t in []]  # 空，用现成的
        # 重新算 idf（简化版：只基于已有 doc_vectors）
        vec = self.doc_vectors[doc_idx]
        norm = self.doc_norms[doc_idx] or 1
        score = 0.0
        for t, tf_q in query_tf.items():
            if t in vec:
                # 这里简化：直接用 tf_q * vec[t] / norm
                score += tf_q * vec[t] / norm
        return score

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """返回 [(doc_idx, score)] 列表。"""
        n = len(self.doc_vectors)
        scores = [(i, self._score_query_doc(query, i)) for i in range(n)]
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]

    def _score_query_doc(self, query: str, doc_idx: int) -> float:
        """计算 query 与单个文档的余弦相似度。"""
        query_tokens = tokenize(query)
        query_tf = compute_tf(query_tokens)
        # 简化 IDF：假设所有词都出现在多个文档中
        idf_approx = 2.0
        query_vec = {t: tf * idf_approx for t, tf in query_tf.items()}
        q_norm = math.sqrt(sum(v * v for v in query_vec.values())) or 1
        doc_vec = self.doc_vectors[doc_idx]
        d_norm = self.doc_norms[doc_idx] or 1
        score = 0.0
        for t, qv in query_vec.items():
            if t in doc_vec:
                score += qv * doc_vec[t] / (q_norm * d_norm)
        return score


# ============================================================================
# RAG 引擎
# ============================================================================

AGENCY_LABELS = {
    'cbirc': '银保监',
    'pboc': '央行',
    'csrc': '证监会',
    'nfra': '金监总局',
    'misc': '其他监管',
}

# 监管机构优先级（发文机构加权用）
AGENCY_WEIGHTS = {
    'cbirc': 1.2,
    'pboc': 1.2,
    'csrc': 1.1,
    'nfra': 1.2,
    'misc': 0.9,
}


def _normalize_section(section: str) -> str:
    """提取干净的章节名（去掉"第X条"前缀和括号内容）。"""
    s = re.sub(r'^#+\s*', '', section).strip()
    s = re.sub(r'^第[一二三四五六七八九十百零\d]+条[（(][^）)]+[）)]\s*', '', s)
    s = re.sub(r'^[一二三四五六七八九十百]+、[一-鿿]+', '', s)
    return s.strip()


# 标题层级加权
SECTION_LEVEL_WEIGHTS = {
    1: 1.5,   # 章
    2: 1.3,   # 节
    3: 1.1,   # 条
    4: 1.0,   # 小节
}


class RegulatoryPolicyRAG:
    """监管政策 RAG 引擎。"""

    def __init__(self):
        self.chunks: List[Chunk] = []
        self.bm25: Optional[BM25] = None
        self.tfidf: Optional[TFIDF] = None
        self._built = False

    def load_knowledge_base(self, kb_dir: str):
        """加载政策知识库目录。"""
        kb_path = Path(kb_dir)
        if not kb_path.exists():
            raise FileNotFoundError(f"知识库目录不存在: {kb_dir}")

        self.chunks = []
        chunk_id = 0

        for agency_dir in kb_path.iterdir():
            if not agency_dir.is_dir():
                continue
            agency = agency_dir.name.lower()
            if agency not in AGENCY_LABELS:
                agency = 'misc'

            for md_file in agency_dir.glob("*.md"):
                doc_title = md_file.stem
                content = md_file.read_text(encoding='utf-8')
                new_chunks = self._parse_doc(content, agency, doc_title, str(md_file))
                for c in new_chunks:
                    c.chunk_id = f"chunk_{chunk_id:04d}"
                    chunk_id += 1
                self.chunks.extend(new_chunks)

        # 也扫描 misc 目录（如果存在）
        misc_dir = kb_path / "misc"
        if misc_dir.exists() and misc_dir.is_dir():
            for md_file in misc_dir.glob("*.md"):
                doc_title = md_file.stem
                content = md_file.read_text(encoding='utf-8')
                new_chunks = self._parse_doc(content, 'misc', doc_title, str(md_file))
                for c in new_chunks:
                    c.chunk_id = f"chunk_{chunk_id:04d}"
                    chunk_id += 1
                self.chunks.extend(new_chunks)

    def _parse_doc(self, content: str, agency: str, doc_title: str, raw_path: str) -> List[Chunk]:
        """解析政策文档为块。"""
        chunks = []
        # 提取文号和生效日期
        policy_ref = ""
        effective_date = ""
        m = re.search(r'文号[：:]\s*([^\n]+)', content)
        if m:
            policy_ref = m.group(1).strip()
        m = re.search(r'生效日期[：:]\s*([^\n]+)', content)
        if m:
            effective_date = m.group(1).strip()

        # 按标题拆分章节
        # 匹配标题：# 第一章 / ## 第一节 / ### 第xxx条 / #### 小节名
        heading_pattern = r'^(#{1,4})\s+(.+)$'
        lines = content.split('\n')
        current_section = "总则"
        current_level = 1
        current_text_parts = []

        def flush():
            nonlocal current_text_parts, current_section, current_level
            if current_text_parts:
                text = '\n'.join(current_text_parts).strip()
                if text:
                    keywords = self._extract_policy_keywords(text)
                    chunks.append(Chunk(
                        chunk_id="",
                        text=text,
                        agency=agency,
                        doc_title=doc_title,
                        section=current_section,
                        section_level=current_level,
                        policy_ref=policy_ref,
                        effective_date=effective_date,
                        raw_path=raw_path,
                        keywords=keywords,
                        normalized_section=_normalize_section(current_section),
                    ))
                current_text_parts = []

        for line in lines:
            m = re.match(heading_pattern, line.strip())
            if m:
                flush()
                current_level = len(m.group(1))
                current_section = m.group(2).strip()
            else:
                # 跳过列表项标题（排除 "1. xxx" 格式的列表项，避免被当章节）
                stripped = line.strip()
                if re.match(r'^\d+\.\s+[^\d]', stripped):
                    # 列表项：合并到当前节
                    current_text_parts.append(stripped)
                elif stripped:
                    current_text_parts.append(stripped)

        flush()
        return chunks

    def _extract_policy_keywords(self, text: str) -> List[str]:
        """提取监管政策关键词。"""
        patterns = [
            r'第[一二三四五六七八九十百零\d]+条',
            r'[一二三四五六七八九十百]+、',
            r'应当|必须|不得|禁止|可以|鼓励',
            r'\d+个?工作日',
            r'\d+[亿万]元',
            r'\d+%|百分之\d+',
            r'[A-Z]{2,}.*?(?:办法|指引|规定|通知|意见)',
        ]
        keywords = []
        for p in patterns:
            for m in re.finditer(p, text):
                kw = m.group().strip()
                if len(kw) > 2 and kw not in keywords:
                    keywords.append(kw)
        return keywords[:20]

    def build_index(self):
        """构建 BM25 + TF-IDF 索引。"""
        if not self.chunks:
            raise ValueError("没有可索引的文档块，请先调用 load_knowledge_base")

        chunk_texts = [c.text for c in self.chunks]

        self.bm25 = BM25()
        self.bm25.build(chunk_texts)

        self.tfidf = TFIDF()
        self.tfidf.documents = chunk_texts  # 记录原始文本用于检索
        self.tfidf.build(chunk_texts)

        self._built = True

    def query(
        self,
        question: str,
        top_k: int = 3,
        agency_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        查询政策。

        Args:
            question: 自然语言问题
            top_k: 返回 top_k 条检索结果
            agency_filter: 限定监管机构 (cbirc/pboc/csrc/nfra/misc)

        Returns:
            dict，含 answer, citations, agency,合规要点
        """
        if not self._built:
            raise ValueError("索引未构建，请先调用 build_index()")

        # 双路检索
        bm25_scores = self.bm25.search(question, top_k * 2)
        tfidf_scores = self.tfidf.search(question, top_k * 2)

        # RRF 融合
        rrf_scores: Dict[int, float] = {}
        k_rrf = 60
        for rank, (idx, score) in enumerate(bm25_scores):
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (k_rrf + rank + 1)
        for rank, (idx, score) in enumerate(tfidf_scores):
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1 / (k_rrf + rank + 1)

        # 机构加权 + 章节层级加权
        for idx, rrf in list(rrf_scores.items()):
            chunk = self.chunks[idx]
            agency_weight = AGENCY_WEIGHTS.get(chunk.agency, 1.0)
            section_weight = SECTION_LEVEL_WEIGHTS.get(chunk.section_level, 1.0)
            rrf_scores[idx] = rrf * agency_weight * section_weight

        # 排序
        sorted_results = sorted(rrf_scores.items(), key=lambda x: -x[1])[:top_k]

        # 过滤机构
        if agency_filter:
            sorted_results = [
                (idx, s) for idx, s in sorted_results
                if self.chunks[idx].agency == agency_filter
            ]

        # 构建答案
        citations = []
        answer_parts = []
        applicable_agencies = set()

        for idx, score in sorted_results:
            chunk = self.chunks[idx]
            applicable_agencies.add(AGENCY_LABELS.get(chunk.agency, chunk.agency))

            citation = {
                "chunk_id": chunk.chunk_id,
                "agency": AGENCY_LABELS.get(chunk.agency, chunk.agency),
                "agency_key": chunk.agency,
                "doc_title": chunk.doc_title,
                "section": chunk.section,
                "normalized_section": chunk.normalized_section,
                "policy_ref": chunk.policy_ref,
                "effective_date": chunk.effective_date,
                "snippet": chunk.text[:300],
                "score": round(score, 4),
            }
            citations.append(citation)
            answer_parts.append(chunk.text[:500])

        # 生成答案摘要
        if answer_parts:
            answer = self._summarize_answer(question, answer_parts, citations)
        else:
            answer = "抱歉，知识库中未找到与该问题相关的政策依据。建议扩大查询范围或联系合规部门。"

        return {
            "answer": answer,
            "citations": citations,
            "applicable_agencies": sorted(applicable_agencies),
            "question": question,
            "top_k": len(sorted_results),
            "no_answer": len(sorted_results) == 0,
        }

    def _summarize_answer(
        self,
        question: str,
        answer_parts: List[str],
        citations: List[Dict],
    ) -> str:
        """从检索结果中提取答案摘要。"""
        combined = "\n\n".join(answer_parts[:2])

        # 尝试提取关键句子
        key_sentences = []
        for part in answer_parts[:2]:
            sentences = re.split(r'[。；\n]', part)
            for s in sentences:
                s = s.strip()
                if len(s) > 10:
                    key_sentences.append(s)

        # 按和问题关键词匹配程度排序
        q_tokens = set(tokenize(question))
        scored_sents = []
        for s in key_sentences:
            s_tokens = set(tokenize(s))
            overlap = len(q_tokens & s_tokens)
            scored_sents.append((overlap, s))

        scored_sents.sort(key=lambda x: -x[0])
        top_sents = [s for _, s in scored_sents[:3]]

        if top_sents:
            return "。".join(top_sents) + "。"
        return combined[:400] if combined else "根据检索结果，相关政策要点已在上方列出。"


# ============================================================================
# 格式化器
# ============================================================================

class RAGFormatter:
    """RAG 输出格式化器。"""

    @staticmethod
    def format_text(result: Dict[str, Any]) -> str:
        """格式化输出为纯文本。"""
        lines = ["=" * 60]
        lines.append(f"问题：{result['question']}")
        lines.append(f"适用机构：{', '.join(result['applicable_agencies'])}")
        lines.append("=" * 60)
        lines.append("")
        lines.append("【答案】")
        lines.append(result['answer'])
        lines.append("")
        lines.append("【出处】")
        for i, c in enumerate(result['citations'], 1):
            lines.append(f"  {i}. [{c['agency']}] {c['doc_title']} · {c['section']}")
            if c['policy_ref']:
                lines.append(f"     文号：{c['policy_ref']}")
            if c['effective_date']:
                lines.append(f"     生效：{c['effective_date']}")
        return '\n'.join(lines)

    @staticmethod
    def format_json(result: Dict[str, Any]) -> str:
        """格式化输出为 JSON。"""
        return json.dumps(result, ensure_ascii=False, indent=2)

    @staticmethod
    def format_card(result: Dict[str, Any]) -> Dict[str, Any]:
        """格式化输出为企微卡片（结构化字典）。"""
        citations = result['citations']
        sources_text = "\n".join(
            f"[{i}] {c['doc_title']} · {c['section']}（{c['agency']}）"
            for i, c in enumerate(citations[:3], 1)
        ) or "（无）"

        snippet_text = "\n".join(
            c['snippet'][:150] + "..." if len(c['snippet']) > 150 else c['snippet']
            for c in citations[:2]
        )

        return {
            "card_type": "text_notice",
            "main_title": {
                "title": "📋 监管政策智能解读",
                "desc": result['question'][:40],
            },
            "emphasis_content": {
                "title": result['answer'][:80] + "..." if len(result['answer']) > 80 else result['answer'],
                "desc": "AI 政策解读",
            },
            "quote_area": {
                "title": "📖 政策原文要点",
                "quote_text": snippet_text,
            },
            "horizontal_content_list": [
                {"keyname": "🏛️ 适用机构", "value": ", ".join(result['applicable_agencies']) or "通用"},
                {"keyname": "📚 出处", "value": f"{len(citations)} 条"},
                {"keyname": "🎯 置信度", "value": "高" if not result.get("no_answer") else "低"},
            ],
            "sub_title_text": sources_text[:400],
            "button_list": [
                {"text": "👍 答案有用", "action_url": "/policy/feedback?type=up"},
                {"text": "👎 不准确", "action_url": "/policy/feedback?type=down"},
                {"text": "📋 复制到聊天", "action_url": "/policy/copy"},
                {"text": "🔍 重新提问", "action_url": "/policy/ask"},
            ],
        }
