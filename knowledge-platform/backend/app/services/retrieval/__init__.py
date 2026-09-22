"""Hybrid retrieval engine"""
from typing import Any, Dict, List, Optional
import time
import logging
from datetime import datetime

from backend.app.services.indexing import hybrid_index

logger = logging.getLogger(__name__)


class MetadataFilter:
    """Filter results by metadata"""
    
    def apply(self, results: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply metadata filters to results"""
        if not filters:
            return results
        
        filtered = []
        for result in results:
            metadata = result.get("metadata", {})
            match = True
            
            for key, value in filters.items():
                if key not in metadata:
                    match = False
                    break
                if metadata[key] != value:
                    match = False
                    break
            
            if match:
                filtered.append(result)
        
        return filtered


class Reranker:
    """Rerank results for better relevance"""
    
    def rerank(self, query: str, results: List[Dict], top_k: int = 10) -> List[Dict]:
        """Rerank results using various signals"""
        query_terms = set(query.lower().split())
        
        for result in results:
            content = result.get("content", "").lower()
            
            # Calculate term overlap
            content_terms = set(content.split())
            overlap = len(query_terms & content_terms)
            
            # Position bonus (earlier is better)
            position_bonus = 1.0 / (1 + result.get("position", 0))
            
            # Length penalty (too short or too long)
            content_len = len(content)
            length_score = 1.0 if 100 < content_len < 1000 else 0.8
            
            # Combine scores
            result["rerank_score"] = (
                result.get("hybrid_score", 0.0) * 0.5 +
                overlap * 0.3 +
                position_bonus * 0.1 +
                length_score * 0.1
            )
        
        results.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
        return results[:top_k]


class RetrievalEngine:
    """Main retrieval engine"""
    
    def __init__(self):
        self.metadata_filter = MetadataFilter()
        self.reranker = Reranker()
    
    async def search(self, query: str, kb_ids: List[str], 
                    metadata_filters: Dict = None, limit: int = 10,
                    search_type: str = "hybrid") -> Dict[str, Any]:
        """Perform hybrid search"""
        start_time = time.time()
        
        # Apply metadata filters
        if metadata_filters:
            results = self.metadata_filter.apply(
                hybrid_index.search(query, limit * 2, metadata_filters),
                metadata_filters
            )
        else:
            results = hybrid_index.search(query, limit * 2)
        
        # Rerank
        results = self.reranker.rerank(query, results, limit)
        
        latency = (time.time() - start_time) * 1000
        
        return {
            "query": query,
            "results": results,
            "total": len(results),
            "latency_ms": latency,
            "search_type": search_type
        }
    
    async def keyword_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Keyword-only search"""
        return hybrid_index.keyword_index.search(query, limit)
    
    async def vector_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Vector-only search"""
        return hybrid_index.vector_index.search(query, limit)
    
    async def graph_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Graph-based search"""
        return hybrid_index.graph_index.search(query, limit)


# Global retrieval engine
retrieval_engine = RetrievalEngine()