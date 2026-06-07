"""Product Manual RAG Skill —— 产品手册检索增强生成。"""

from .rag_engine import Chunk, DocumentChunker, RetrievalHit, tokenize
from .retrievers import BM25Index, TFIDFIndex, rrf_fuse
from .product_manual_rag import ProductManualRAG, RAGFormatter

__version__ = "1.0.0"
__all__ = [
    "Chunk", "DocumentChunker", "RetrievalHit", "tokenize",
    "BM25Index", "TFIDFIndex", "rrf_fuse",
    "ProductManualRAG", "RAGFormatter",
]
