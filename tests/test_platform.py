"""Test script for Knowledge Engineering Platform"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.services.ingestion import ingestion_engine
from backend.app.services.processing import processing_engine
from backend.app.services.indexing import hybrid_index
from backend.app.services.retrieval import retrieval_engine
from backend.app.services.rag import rag_engine
from backend.app.services.evaluation import evaluation_engine


async def test_ingestion():
    """Test ingestion engine"""
    print("Testing Ingestion Engine...")
    
    result = await ingestion_engine.ingest("file", {
        "filename": "test.txt",
        "content": "This is a test document for the knowledge engineering platform."
    })
    
    assert result["type"] == "file"
    assert "checksum" in result
    print("✓ Ingestion Engine working")


async def test_processing():
    """Test processing engine"""
    print("Testing Processing Engine...")
    
    content = "This is a test document. It has multiple sentences. We will process it."
    result = await processing_engine.process(content, "file")
    
    assert "chunks" in result
    assert len(result["chunks"]) > 0
    assert "entities" in result
    print("✓ Processing Engine working")


async def test_indexing():
    """Test indexing engine"""
    print("Testing Indexing Engine...")
    
    hybrid_index.index(
        "doc_1",
        "Test document content for indexing",
        {"source": "test", "category": "testing"}
    )
    
    results = hybrid_index.search("test document", limit=5)
    assert len(results) > 0
    print("✓ Indexing Engine working")


async def test_retrieval():
    """Test retrieval engine"""
    print("Testing Retrieval Engine...")
    
    result = await retrieval_engine.search(
        "test document",
        ["kb_1"],
        limit=5
    )
    
    assert "results" in result
    assert "latency_ms" in result
    print("✓ Retrieval Engine working")


async def test_rag():
    """Test RAG engine"""
    print("Testing RAG Engine...")
    
    result = await rag_engine.answer(
        "What is this test about?",
        ["kb_1"],
        limit=3
    )
    
    assert "answer" in result
    assert "sources" in result
    assert "citations" in result
    print("✓ RAG Engine working")


async def test_evaluation():
    """Test evaluation engine"""
    print("Testing Evaluation Engine...")
    
    # Register test dataset
    test_questions = [
        {
            "question": "test question",
            "expected_source": "test.pdf"
        }
    ]
    evaluation_engine.register_dataset("test_dataset", test_questions)
    
    # Run evaluation
    result = await evaluation_engine.evaluate("kb_1", "test_dataset")
    
    assert "metrics" in result
    assert "results" in result
    assert "recall" in result["metrics"]
    print("✓ Evaluation Engine working")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Knowledge Engineering Platform - Tests")
    print("=" * 60)
    
    try:
        await test_ingestion()
        await test_processing()
        await test_indexing()
        await test_retrieval()
        await test_rag()
        await test_evaluation()
        
        print("=" * 60)
        print("All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())