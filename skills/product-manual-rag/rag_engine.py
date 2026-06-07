"""
Product Manual RAG Engine - 产品手册检索增强生成引擎
=======================================================
基于 TF-IDF + BM25 双路检索的轻量级 RAG 实现。
零外部依赖（仅标准库），毫秒级响应，适合企业内网/边缘部署。

设计目标：
- 输入: 自然语言问题（如"招行金葵花理财起购金额是多少"）
- 输出: Top-K 相关段落 + 出处标注（产品名/章节/页码）
- 支持: 多产品手册同时索引、增量更新、中英文混合

作者: ArkClaw (Financial AI Community)
"""

from __future__ import annotations

import json
import math
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any


# ----------------------------- 中文分词（轻量） -----------------------------

# 简易中文 bigram + ASCII 词分词器。线上可平替为 jieba，避免额外依赖。
_ASCII_WORD = re.compile(r"[A-Za-z0-9_+\-./%]+")
_CJK = re.compile(r"[\u4e00-\u9fff]")
_STOPWORDS = {
    "的", "了", "是", "和", "与", "及", "或", "在", "我", "你", "他", "她",
    "我们", "你们", "他们", "为", "对", "向", "把", "被", "等", "一个", "这个",
    "那个", "并", "但", "也", "都", "就", "还", "可以", "可能", "需要", "如果",
    "the", "a", "an", "is", "are", "of", "and", "or", "to", "for", "in", "on",
    "by", "with", "as", "at", "be", "this", "that", "it", "from",
}


def tokenize(text: str) -> List[str]:
    """混合分词：ASCII 单词 + 中文 bigram。"""
    if not text:
        return []
    text = text.lower()
    tokens: List[str] = []
    # ASCII 词
    for m in _ASCII_WORD.finditer(text):
        w = m.group(0)
        if w and w not in _STOPWORDS:
            tokens.append(w)
    # 中文 bigram
    cjk_chars = _CJK.findall(text)
    cjk_seq = "".join(cjk_chars)
    for i in range(len(cjk_seq) - 1):
        bg = cjk_seq[i:i + 2]
        if bg not in _STOPWORDS:
            tokens.append(bg)
    # 中文 unigram（提升单字关键词命中率，如"率""费"）
    for c in cjk_chars:
        if c not in _STOPWORDS and len(c) == 1:
            tokens.append(c)
    return tokens


# ----------------------------- 数据结构 -----------------------------

@dataclass
class Chunk:
    """文档切片单元 —— RAG 检索最小粒度。"""
    chunk_id: str
    text: str
    product: str           # 产品名 (如 "金葵花理财")
    section: str           # 章节 (如 "三、申购赎回")
    page: Optional[int] = None
    source_file: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalHit:
    """检索命中结果。"""
    chunk: Chunk
    score: float
    matched_terms: List[str]
    retrieval_method: str  # "bm25" | "tfidf" | "hybrid"


# ----------------------------- 文档切分器 -----------------------------

class DocumentChunker:
    """
    文档切分器 —— 按"章节标题"+"段落长度"双策略切分。
    - 优先按 markdown 标题/章节号切分
    - 单 chunk 超过 max_chars 时按句号/换行二次切分
    """

    # 只匹配“真正的章节标题”：markdown #/##/...，或 中文数字章节号（二、/第二章）。
    # 不要把“1. xxx / 1.xxx” 这种列表项误判为标题。
    HEADING = re.compile(
        r"^\s*("
        r"#{1,6}\s+.+"                                       # markdown 标题
        r"|第[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e\u5343]+[章节条款]\s*.+"  # 第三章、第五节
        r"|[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341]+、\s*\S.+"           # 三、xxx
        r")$",
        re.MULTILINE,
    )

    def __init__(self, max_chars: int = 400, overlap: int = 50):
        self.max_chars = max_chars
        self.overlap = overlap

    def chunk(self, text: str, product: str, source_file: str = "") -> List[Chunk]:
        if not text or not text.strip():
            return []
        lines = text.split("\n")
        sections: List[Tuple[str, List[str]]] = []
        cur_title = "前言"
        cur_buf: List[str] = []
        for line in lines:
            if self.HEADING.match(line.strip()):
                if cur_buf:
                    sections.append((cur_title, cur_buf))
                cur_title = re.sub(r"^#+\s*", "", line.strip())[:80]
                cur_buf = []
            else:
                cur_buf.append(line)
        if cur_buf:
            sections.append((cur_title, cur_buf))

        chunks: List[Chunk] = []
        idx = 0
        for sec_title, buf in sections:
            body = "\n".join(buf).strip()
            if not body:
                continue
            for piece in self._split_long(body):
                idx += 1
                chunks.append(Chunk(
                    chunk_id=f"{product}::{idx:04d}",
                    text=piece,
                    product=product,
                    section=sec_title,
                    source_file=source_file,
                ))
        return chunks

    def _split_long(self, body: str) -> List[str]:
        if len(body) <= self.max_chars:
            return [body]
        # 按句号切，再按 max_chars 合并
        sentences = re.split(r"(?<=[。！？!?\.\n])\s*", body)
        sentences = [s for s in sentences if s and s.strip()]
        pieces: List[str] = []
        cur = ""
        for s in sentences:
            if len(cur) + len(s) <= self.max_chars:
                cur += s
            else:
                if cur:
                    pieces.append(cur)
                # overlap：尾部保留少量上下文
                tail = cur[-self.overlap:] if self.overlap and cur else ""
                cur = tail + s
        if cur:
            pieces.append(cur)
        return pieces
