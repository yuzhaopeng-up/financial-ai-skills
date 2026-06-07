"""Product Manual RAG Skill —— 产品手册检索增强生成。"""

import sys
from pathlib import Path

# 支持直接运行测试时的绝对导入
if __name__ == "__main__" or not __package__:
    sys.path.insert(0, str(Path(__file__).parent))
    from rag_engine import Chunk, DocumentChunker, RetrievalHit, tokenize
    from retrievers import BM25Index, TFIDFIndex, rrf_fuse
    from product_manual_rag import ProductManualRAG, RAGFormatter
else:
    from .rag_engine import Chunk, DocumentChunker, RetrievalHit, tokenize
    from .retrievers import BM25Index, TFIDFIndex, rrf_fuse
    from .product_manual_rag import ProductManualRAG, RAGFormatter

__version__ = "1.0.0"
__all__ = [
    "Chunk", "DocumentChunker", "RetrievalHit", "tokenize",
    "BM25Index", "TFIDFIndex", "rrf_fuse",
    "ProductManualRAG", "RAGFormatter",
]
