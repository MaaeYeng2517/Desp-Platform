"""Tests for the Token-Embedded Chunk Retriever system."""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.services.chunking import TokenChunker
from backend.app.services.embedding import EmbeddingService
from backend.app.services.token_retriever import TokenEmbeddedChunkRetriever


SAMPLE_TEXT = """
Data engineering is a process of collecting, cleaning, and transforming data into a
format that is suitable for analysis. Data engineers build pipelines that move data
from various sources to a centralized repository. Common tools include Apache
Airflow for orchestration, dbt for transformation, and PostgreSQL for storage.

A data pipeline typically follows a medallion architecture: Bronze (raw), Silver
(cleaned), and Gold (business-ready). This architecture ensures data quality
and consistency at each stage of the pipeline.

Data quality is critical for reliable analytics. Quality checks include schema
validation, null detection, duplicate detection, and business rule enforcement.
These checks help prevent bad data from propagating to downstream systems.

Vector search uses embedding models to convert text into dense vectors. The
vectors capture semantic meaning, allowing similar documents to be retrieved
even when they don't share exact keyword matches. This is the foundation of
modern RAG systems.
"""


def test_token_chunker():
    """TokenChunker produces token-bounded chunks."""
    print("Testing TokenChunker...")
    chunker = TokenChunker(chunk_size=50, chunk_overlap=10)
    chunks = asyncio.run(chunker.chunk(SAMPLE_TEXT))
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk["token_count"] <= 60  # slight tolerance
        assert "content" in chunk
        assert "chunk_index" in chunk
    print(f"  Chunks created: {len(chunks)}")
    print("  TokenChunker: PASS")


def test_embedding_service():
    """EmbeddingService produces vectors of the correct dimension."""
    print("Testing EmbeddingService...")
    svc = EmbeddingService()
    vec = svc.embed_query("hello world")
    assert len(vec) == svc.dim()
    assert len(vec) == svc.vector_size
    assert isinstance(vec[0], float)
    print(f"  Embedding dim: {len(vec)}")
    print("  EmbeddingService: PASS")


def test_embedding_fallback():
    """Fallback embeddings are deterministic."""
    print("Testing EmbeddingService fallback...")
    svc = EmbeddingService()
    svc._model = None  # force fallback
    v1 = svc.embed_query("test text")
    v2 = svc.embed_query("test text")
    assert v1 == v2
    assert len(v1) == svc.vector_size
    print("  Fallback deterministic: PASS")


def test_token_retriever_ingest_and_search():
    """Full ingest + search cycle returns relevant chunks."""
    print("Testing TokenEmbeddedChunkRetriever...")
    retriever = TokenEmbeddedChunkRetriever(
        chunk_size=256,
        chunk_overlap=64,
        top_k=3,
        score_threshold=0.0,
    )

    # Ingest
    result = retriever.add_document(
        doc_id="doc_001",
        text=SAMPLE_TEXT,
        metadata={"source": "test", "category": "data-engineering"},
    )
    assert result["num_chunks"] > 0
    assert result["token_count"] > 0
    print(f"  Ingested: {result['num_chunks']} chunks, {result['token_count']} tokens")

    # Search with a relevant query
    search_result = asyncio.run(retriever.search(
        query="What tools are used in data pipelines?",
    ))
    assert "results" in search_result
    assert search_result["total"] > 0
    top = search_result["results"][0]
    assert "content" in top
    assert "score" in top
    print(f"  Top result score: {top['score']:.4f}")
    print(f"  Top result preview: {top['content'][:80]}...")
    print("  Retriever ingest+search: PASS")


def test_token_retriever_metadata_filter():
    """Metadata filtering narrows results."""
    print("Testing metadata filter...")
    retriever = TokenEmbeddedChunkRetriever(top_k=5)

    retriever.add_document(
        doc_id="doc_a",
        text="Topic A content about machine learning.",
        metadata={"kb_id": "kb_1", "category": "ml"},
    )
    retriever.add_document(
        doc_id="doc_b",
        text="Topic B content about database design.",
        metadata={"kb_id": "kb_2", "category": "db"},
    )

    result = asyncio.run(retriever.search(
        query="machine learning",
        metadata_filters={"kb_id": "kb_1"},
    ))
    # Results should only come from kb_1
    for r in result["results"]:
        assert r.get("metadata", {}).get("kb_id") == "kb_1"
    print(f"  Filtered results: {result['total']}")
    print("  Metadata filter: PASS")


def test_token_retriever_clear_and_stats():
    """clear() and get_stats() work correctly."""
    print("Testing clear + stats...")
    retriever = TokenEmbeddedChunkRetriever()
    retriever.add_document(
        doc_id="doc_clear_test",
        text="Some test content here.",
        metadata={"source": "test"},
    )
    stats = retriever.get_stats()
    assert stats["total_chunks"] > 0

    retriever.clear()
    stats = retriever.get_stats()
    assert stats["total_chunks"] == 0
    print("  Clear + stats: PASS")


def test_token_retriever_delete_document():
    """delete_document removes all chunks for a doc_id."""
    print("Testing delete_document...")
    retriever = TokenEmbeddedChunkRetriever()
    retriever.add_document(
        doc_id="doc_to_delete",
        text="Content to be deleted.",
        metadata={"source": "temp"},
    )
    retriever.add_document(
        doc_id="doc_keep",
        text="Content to keep.",
        metadata={"source": "temp"},
    )

    removed = retriever.delete_document("doc_to_delete")
    assert removed > 0

    stats = retriever.get_stats()
    assert stats["total_chunks"] > 0  # doc_keep still present

    removed_again = retriever.delete_document("doc_to_delete")
    assert removed_again == 0

    print(f"  Deleted: {removed} chunks")
    print("  Delete document: PASS")


def test_retriever_reuses_vector_index():
    """The retriever uses the updated VectorIndex with real embeddings."""
    print("Testing VectorIndex integration...")
    retriever = TokenEmbeddedChunkRetriever()
    assert retriever.vector_index.dim == retriever.embedder.vector_size
    assert retriever.vector_index._service is retriever.embedder
    print("  VectorIndex uses EmbeddingService: PASS")


if __name__ == "__main__":
    print("=" * 60)
    print("Token-Embedded Chunk Retriever — Tests")
    print("=" * 60)

    test_token_chunker()
    test_embedding_service()
    test_embedding_fallback()
    test_retriever_reuses_vector_index()
    test_token_retriever_ingest_and_search()
    test_token_retriever_metadata_filter()
    test_token_retriever_clear_and_stats()
    test_token_retriever_delete_document()

    print("=" * 60)
    print("All tests passed!")
    print("=" * 60)
