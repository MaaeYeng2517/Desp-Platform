"""
Token-Embedded Chunk Retriever.

A self-contained retrieval system that:

1. Splits raw text into **token-aware chunks** (bounded by token count,
   not character count) using ``TokenChunker``.
2. Generates **dense embedding vectors** for each chunk via
   ``sentence-transformers`` (with a hash-based fallback).
3. Stores the embedded chunks in an in-memory **VectorIndex** with
   metadata support.
4. Retrieves the most relevant chunks for a query using **cosine
   similarity** on the embedding vectors.

Usage
-----
::

    from backend.app.services.token_retriever import token_retriever

    # Ingest a document
    token_retriever.add_document(
        doc_id="doc_001",
        text="Data engineering is the process of ...",
        metadata={"source": "manual", "category": "overview"},
    )

    # Retrieve
    results = await token_retriever.search("what is data engineering?")
    for r in results["results"]:
        print(r["content"], r["score"])
"""
from typing import Any, Dict, List, Optional
import uuid
import logging
import time
from datetime import datetime

from backend.app.services.chunking import TokenChunker
from backend.app.services.embedding import EmbeddingService
from backend.app.services.indexing import VectorIndex

logger = logging.getLogger(__name__)


class TokenEmbeddedChunkRetriever:
    """
    End-to-end retriever for token-embedded chunks.

    Combines token-aware chunking, dense embedding generation, and
    vector-similarity search into a single interface.
    """

    def __init__(
        self,
        chunk_size: int = 256,
        chunk_overlap: int = 64,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        embedding_dim: int = 384,
        top_k: int = 5,
        score_threshold: float = 0.0,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self.score_threshold = score_threshold

        self.chunker = TokenChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            model_name=embedding_model,
        )
        self.embedder = EmbeddingService(
            model_name=embedding_model,
            vector_size=embedding_dim,
        )
        self.vector_index = VectorIndex()
        # Expose embedding dim from the loaded service
        self.vector_index.dim = embedding_dim

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Chunk, embed, and index a single document.

        Parameters
        ----------
        doc_id : str
            Unique identifier for the document.
        text : str
            Full text content of the document.
        metadata : dict, optional
            Metadata to attach to every chunk.
        chunk_size : int, optional
            Override the default chunk size.
        chunk_overlap : int, optional
            Override the default chunk overlap.

        Returns
        -------
        dict
            Summary with ``doc_id``, ``chunk_ids``, ``num_chunks``,
            and ``token_count``.
        """
        import asyncio

        meta = metadata or {}
        meta.setdefault("doc_id", doc_id)
        meta.setdefault("doc_title", doc_id)

        # 1. Token-aware chunking
        chunks = asyncio.run(self.chunker.chunk(
            text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        ))

        # 2. Attach metadata and chunk IDs
        indexed_chunks: List[Dict[str, Any]] = []
        total_tokens = 0
        for i, chunk in enumerate(chunks):
            chunk["chunk_id"] = f"{doc_id}__{i}"
            chunk["metadata"] = {
                **meta,
                "chunk_index": i,
            }
            chunk["doc_id"] = doc_id
            total_tokens += chunk.get("token_count", 0)
            indexed_chunks.append(chunk)

        # 3. Batch-index with embeddings
        chunk_ids = self.vector_index.index_chunks(indexed_chunks)

        logger.info(
            "Document '%s' indexed: %d chunks, %d tokens",
            doc_id,
            len(chunk_ids),
            total_tokens,
        )

        return {
            "doc_id": doc_id,
            "chunk_ids": chunk_ids,
            "num_chunks": len(chunk_ids),
            "token_count": total_tokens,
            "indexed_at": datetime.utcnow().isoformat(),
        }

    async def add_document_async(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Async-compatible version of :meth:`add_document`."""
        meta = metadata or {}
        meta.setdefault("doc_id", doc_id)
        meta.setdefault("doc_title", doc_id)

        chunks = await self.chunker.chunk(
            text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        indexed_chunks: List[Dict[str, Any]] = []
        total_tokens = 0
        for i, chunk in enumerate(chunks):
            chunk["chunk_id"] = f"{doc_id}__{i}"
            chunk["metadata"] = {
                **meta,
                "chunk_index": i,
            }
            chunk["doc_id"] = doc_id
            total_tokens += chunk.get("token_count", 0)
            indexed_chunks.append(chunk)

        chunk_ids = self.vector_index.index_chunks(indexed_chunks)

        logger.info(
            "Document '%s' indexed: %d chunks, %d tokens",
            doc_id,
            len(chunk_ids),
            total_tokens,
        )

        return {
            "doc_id": doc_id,
            "chunk_ids": chunk_ids,
            "num_chunks": len(chunk_ids),
            "token_count": total_tokens,
            "indexed_at": datetime.utcnow().isoformat(),
        }

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    async def search(
        self,
        query: str,
        kb_ids: Optional[List[str]] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        score_threshold: Optional[float] = None,
        include_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Retrieve the top-k most relevant chunks for *query*.

        Parameters
        ----------
        query : str
            User query string.
        kb_ids : list[str], optional
            Filter results to these knowledge-base IDs (stored in
            chunk metadata).
        metadata_filters : dict, optional
            Additional metadata key-value filters.
        limit : int, optional
            Override ``self.top_k``.
        score_threshold : float, optional
            Minimum similarity score (0–1).
        include_metadata : bool
            Include full chunk metadata in results.

        Returns
        -------
        dict
            ``query``, ``results``, ``total``, ``latency_ms``,
            ``model``, ``is_embedding_loaded``.
        """
        start = time.time()
        top_k = limit or self.top_k
        threshold = score_threshold if score_threshold is not None else self.score_threshold

        # Combine filters
        filters: Dict[str, Any] = dict(metadata_filters or {})
        if kb_ids:
            filters["kb_id"] = kb_ids[0] if len(kb_ids) == 1 else filters.get("kb_id")

        # Vector search via the embedding service
        results = self.vector_index.search(
            query, limit=top_k * 3, metadata_filter=filters or None
        )

        # Apply score threshold
        if threshold > 0:
            results = [r for r in results if r["score"] >= threshold]

        # Sort and trim
        results = sorted(results, key=lambda r: r["score"], reverse=True)[:top_k]

        # Optionally strip metadata
        if not include_metadata:
            for r in results:
                r.pop("metadata", None)

        latency = (time.time() - start) * 1000

        return {
            "query": query,
            "results": results,
            "total": len(results),
            "latency_ms": round(latency, 2),
            "model": self.embedder.model_name,
            "is_embedding_loaded": self.embedder.is_loaded,
            "embedding_dim": self.embedder.dim(),
        }

    # ------------------------------------------------------------------
    # Management
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Remove all indexed chunks."""
        self.vector_index.embeddings.clear()
        self.vector_index.chunk_store.clear()
        logger.info("Vector index cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Return index statistics."""
        return {
            "total_chunks": len(self.vector_index.embeddings),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "embedding_model": self.embedder.model_name,
            "embedding_dim": self.embedder.dim(),
            "is_embedding_loaded": self.embedder.is_loaded,
            "top_k": self.top_k,
            "score_threshold": self.score_threshold,
        }

    def delete_document(self, doc_id: str) -> int:
        """Remove all chunks belonging to *doc_id*. Returns removed count."""
        removed = 0
        to_remove = [
            cid for cid, doc in self.vector_index.chunk_store.items()
            if doc.get("metadata", {}).get("doc_id") == doc_id
        ]
        for cid in to_remove:
            self.vector_index.delete(cid)
            removed += 1
        logger.info("Deleted document '%s': %d chunks removed", doc_id, removed)
        return removed


# Global retriever instance
token_retriever = TokenEmbeddedChunkRetriever()
