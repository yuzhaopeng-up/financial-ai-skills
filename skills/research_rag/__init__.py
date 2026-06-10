"""
research_rag - 研报RAG检索引擎
==============================
BM25 + TF-IDF 双路检索 + RRF 融合 + 多轮对话上下文 + 引用标注

Usage:
    from research_rag import ResearchRAGEngine, query

    answer = query("宁德时代储能业务竞争力分析")
    print(answer.answer)
"""
from __future__ import annotations

from .rag_engine import (
    # 核心引擎
    ResearchRAGEngine,
    # 数据模型
    Chunk,
    Citation,
    SearchResult,
    Turn,
    RAGAnswer,
    # 便捷函数
    query,
    get_engine,
    # PDF 解析
    parse_pdf_chunk,
    # 索引类（暴露给高级用户）
    BM25,
    TFIDFIndex,
    # 工具函数
    tokenize_chinese,
    compute_tf,
    compute_idf,
    rrf_fusion,
    # 知识库构建
    load_templates,
    build_knowledge_base,
    build_industry_chunks,
    build_company_chunks,
    # 配置路径
    HERE,
    SKILL_DIR,
    RESEARCH_REPORT_DIR,
    TEMPLATES_PATH,
)

__all__ = [
    "ResearchRAGEngine",
    "Chunk",
    "Citation",
    "SearchResult",
    "Turn",
    "RAGAnswer",
    "query",
    "get_engine",
    "parse_pdf_chunk",
    "BM25",
    "TFIDFIndex",
    "tokenize_chinese",
    "compute_tf",
    "compute_idf",
    "rrf_fusion",
    "load_templates",
    "build_knowledge_base",
    "build_industry_chunks",
    "build_company_chunks",
    "HERE",
    "SKILL_DIR",
    "RESEARCH_REPORT_DIR",
    "TEMPLATES_PATH",
]
