"""Indexing layer for hybrid search"""
from typing import Any, Dict, List, Optional
import logging
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class KeywordIndex:
    """BM25 keyword index"""
    
    def __init__(self):
        self.documents: Dict[str, Dict] = {}
        self.doc_count = 0
    
    def index(self, doc_id: str, content: str, metadata: Dict = None):
        """Index a document for keyword search"""
        self.documents[doc_id] = {
            "content": content,
            "metadata": metadata or {},
            "indexed_at": datetime.utcnow().isoformat()
        }
        self.doc_count = len(self.documents)
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Simple keyword search"""
        results = []
        query_terms = set(query.lower().split())
        
        for doc_id, doc in self.documents.items():
            content_lower = doc["content"].lower()
            score = 0
            
            for term in query_terms:
                if term in content_lower:
                    score += 1.0 / (1 + content_lower.count(term))
            
            if score > 0:
                results.append({
                    "doc_id": doc_id,
                    "score": score,
                    "content": doc["content"][:200],
                    "metadata": doc["metadata"]
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def delete(self, doc_id: str):
        """Remove document from index"""
        self.documents.pop(doc_id, None)
        self.doc_count = len(self.documents)


class VectorIndex:
    """Vector index using Qdrant"""
    
    def __init__(self):
        self.collection_name = "knowledge_chunks"
        self.embeddings: Dict[str, List[float]] = {}
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector (simplified)"""
        # In production, use actual embedding model
        # This is a placeholder using text hashing
        import numpy as np
        
        hash_val = hashlib.md5(text.encode()).hexdigest()
        # Create deterministic vector from hash
        np.random.seed(int(hash_val[:8], 16))
        return np.random.rand(384).tolist()
    
    def index(self, chunk_id: str, content: str, metadata: Dict = None):
        """Index a chunk with vector embedding"""
        embedding = self._generate_embedding(content)
        self.embeddings[chunk_id] = embedding
    
    def search(self, query: str, limit: int = 10, 
               metadata_filter: Dict = None) -> List[Dict[str, Any]]:
        """Vector similarity search"""
        query_embedding = self._generate_embedding(query)
        results = []
        
        for chunk_id, embedding in self.embeddings.items():
            # Cosine similarity
            similarity = self._cosine_similarity(query_embedding, embedding)
            
            results.append({
                "chunk_id": chunk_id,
                "score": similarity,
                "metadata": metadata_filter or {}
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity"""
        import numpy as np
        
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        
        return float(dot_product / (norm_v1 * norm_v2))
    
    def delete(self, chunk_id: str):
        """Remove chunk from index"""
        self.embeddings.pop(chunk_id, None)


class MetadataIndex:
    """Metadata filtering index"""
    
    def __init__(self):
        self.index: Dict[str, Dict] = {}
    
    def index(self, doc_id: str, metadata: Dict):
        """Index document metadata"""
        self.index[doc_id] = metadata
    
    def search(self, filters: Dict[str, Any], limit: int = 10) -> List[str]:
        """Search by metadata filters"""
        results = []
        
        for doc_id, metadata in self.index.items():
            match = True
            
            for key, value in filters.items():
                if key not in metadata or metadata[key] != value:
                    match = False
                    break
            
            if match:
                results.append(doc_id)
                if len(results) >= limit:
                    break
        
        return results
    
    def delete(self, doc_id: str):
        """Remove from index"""
        self.index.pop(doc_id, None)


class GraphIndex:
    """Knowledge graph index"""
    
    def __init__(self):
        self.graph: Dict[str, Dict] = {}
    
    def index(self, entity_id: str, entity_data: Dict):
        """Index entity in graph"""
        self.graph[entity_id] = entity_data
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search entities"""
        results = []
        query_lower = query.lower()
        
        for entity_id, data in self.graph.items():
            name = data.get("name", "").lower()
            if query_lower in name:
                results.append({
                    "entity_id": entity_id,
                    "name": data.get("name", ""),
                    "type": data.get("type", ""),
                    "score": 1.0
                })
        
        return results[:limit]


class HybridIndex:
    """Combine multiple indexes"""
    
    def __init__(self):
        self.keyword_index = KeywordIndex()
        self.vector_index = VectorIndex()
        self.metadata_index = MetadataIndex()
        self.graph_index = GraphIndex()
    
    def index(self, doc_id: str, content: str, metadata: Dict = None):
        """Index in all indexes"""
        self.keyword_index.index(doc_id, content, metadata)
        self.vector_index.index(doc_id, content, metadata)
        self.metadata_index.index(doc_id, metadata or {})
    
    def search(self, query: str, limit: int = 10, 
               metadata_filter: Dict = None) -> List[Dict[str, Any]]:
        """Hybrid search across all indexes"""
        keyword_results = self.keyword_index.search(query, limit)
        vector_results = self.vector_index.search(query, limit, metadata_filter)
        
        # Combine results with weighted scoring
        combined = {}
        
        for result in keyword_results:
            doc_id = result["doc_id"]
            combined[doc_id] = {
                "doc_id": doc_id,
                "keyword_score": result["score"],
                "vector_score": 0.0,
                "content": result["content"],
                "metadata": result["metadata"]
            }
        
        for result in vector_results:
            chunk_id = result["chunk_id"]
            if chunk_id in combined:
                combined[chunk_id]["vector_score"] = result["score"]
            else:
                combined[chunk_id] = {
                    "doc_id": chunk_id,
                    "keyword_score": 0.0,
                    "vector_score": result["score"],
                    "content": "",
                    "metadata": result.get("metadata", {})
                }
        
        # Calculate hybrid score
        results = []
        for doc_id, data in combined.items():
            data["hybrid_score"] = (data["keyword_score"] * 0.4 + 
                                   data["vector_score"] * 0.6)
            results.append(data)
        
        results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return results[:limit]


# Global index manager
hybrid_index = HybridIndex()