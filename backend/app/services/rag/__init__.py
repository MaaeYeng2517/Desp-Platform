"""Context engineering layer"""
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Build context for LLM from retrieved documents"""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
    
    async def build(self, query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build context from search results"""
        # Deduplication
        deduplicated = await self._deduplicate(results)
        
        # Relevance filter
        relevant = await self._filter_relevance(query, deduplicated)
        
        # Context compression
        compressed = await self._compress(relevant)
        
        # Context ordering
        ordered = await self._order(compressed)
        
        # Context budget
        final_context = await self._apply_budget(ordered)
        
        return {
            "context": final_context,
            "sources": [r.get("doc_id", r.get("chunk_id", "")) for r in final_context],
            "total_tokens": sum(r.get("token_count", 0) for r in final_context),
            "built_at": datetime.utcnow().isoformat()
        }
    
    async def _deduplicate(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate chunks"""
        seen = set()
        unique = []
        
        for result in results:
            chunk_id = result.get("chunk_id") or result.get("doc_id")
            if chunk_id and chunk_id not in seen:
                seen.add(chunk_id)
                unique.append(result)
        
        return unique
    
    async def _filter_relevance(self, query: str, results: List[Dict]) -> List[Dict]:
        """Filter by relevance threshold"""
        return [r for r in results if r.get("score", 0) > 0.1]
    
    async def _compress(self, results: List[Dict]) -> List[Dict]:
        """Compress context by truncating long content"""
        compressed = []
        
        for result in results:
            content = result.get("content", "")
            if len(content) > 500:
                result["content"] = content[:500] + "..."
                result["token_count"] = len(result["content"].split())
            compressed.append(result)
        
        return compressed
    
    async def _order(self, results: List[Dict]) -> List[Dict]:
        """Order by relevance score"""
        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)
    
    async def _apply_budget(self, results: List[Dict]) -> List[Dict]:
        """Apply token budget"""
        selected = []
        total_tokens = 0
        
        for result in results:
            tokens = result.get("token_count", len(result.get("content", "").split()))
            if total_tokens + tokens <= self.max_tokens:
                selected.append(result)
                total_tokens += tokens
            else:
                break
        
        return selected


class RAGEngine:
    """RAG pipeline for question answering"""
    
    def __init__(self):
        self.context_builder = ContextBuilder()
    
    async def answer(self, query: str, kb_ids: List[str], 
                    metadata_filters: Dict = None, limit: int = 5,
                    temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate answer using RAG"""
        from backend.app.services.retrieval import retrieval_engine
        
        # Retrieve relevant documents
        search_results = await retrieval_engine.search(
            query, kb_ids, metadata_filters, limit
        )
        
        # Build context
        context_data = await self.context_builder.build(query, search_results["results"])
        
        # Generate answer (placeholder - in production, use LLM)
        answer = await self._generate_answer(query, context_data, temperature, max_tokens)
        
        # Extract citations
        citations = await self._extract_citations(context_data)
        
        return {
            "answer": answer,
            "sources": search_results["results"],
            "citations": citations,
            "latency_ms": search_results["latency_ms"],
            "token_usage": {
                "prompt": context_data["total_tokens"],
                "completion": len(answer.split()),
                "total": context_data["total_tokens"] + len(answer.split())
            }
        }
    
    async def _generate_answer(self, query: str, context_data: Dict,
                              temperature: float, max_tokens: int) -> str:
        """Generate answer using LLM"""
        # Placeholder - in production, call OpenAI/Anthropic API
        context_text = "\n\n".join([
            f"Source {i+1}: {r['content'][:200]}"
            for i, r in enumerate(context_data["context"])
        ])
        
        return f"Based on the retrieved context:\n\n{context_text[:500]}\n\nAnswer: This is a placeholder answer to '{query}'."
    
    async def _extract_citations(self, context_data: Dict) -> List[Dict]:
        """Extract citations from context"""
        citations = []
        for i, source in enumerate(context_data["context"]):
            citations.append({
                "index": i + 1,
                "source": source.get("doc_id", source.get("chunk_id", "")),
                "content_preview": source.get("content", "")[:100]
            })
        return citations


# Global RAG engine
rag_engine = RAGEngine()