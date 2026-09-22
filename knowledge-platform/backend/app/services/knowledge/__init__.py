"""Knowledge layer management"""
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime
import networkx as nx

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """Manage knowledge graph with entities and relationships"""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
    
    def add_entity(self, entity_id: str, entity_type: str, properties: Dict = None):
        """Add entity to graph"""
        self.graph.add_node(entity_id, type=entity_type, **(properties or {}))
    
    def add_relationship(self, subject_id: str, object_id: str, 
                        predicate: str, weight: float = 1.0, properties: Dict = None):
        """Add relationship between entities"""
        self.graph.add_edge(
            subject_id, object_id,
            predicate=predicate,
            weight=weight,
            **(properties or {})
        )
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search entities by name"""
        results = []
        query_lower = query.lower()
        
        for node, data in self.graph.nodes(data=True):
            name = data.get("name", "").lower()
            if query_lower in name:
                results.append({
                    "id": node,
                    "name": data.get("name", ""),
                    "type": data.get("type", ""),
                    "score": 1.0 if query_lower == name else 0.5
                })
        
        return results[:limit]
    
    def get_related(self, entity_id: str, max_depth: int = 2) -> List[Dict]:
        """Get related entities"""
        related = []
        
        try:
            # Get direct neighbors
            successors = list(self.graph.successors(entity_id))
            predecessors = list(self.graph.predecessors(entity_id))
            
            for node_id in set(successors + predecessors):
                data = self.graph.nodes[node_id]
                related.append({
                    "id": node_id,
                    "name": data.get("name", ""),
                    "type": data.get("type", ""),
                    "relationship": "related"
                })
        except Exception as e:
            logger.error(f"Error getting related: {e}")
        
        return related
    
    def get_subgraph(self, entity_ids: List[str]) -> Dict:
        """Get subgraph for given entities"""
        subgraph = self.graph.subgraph(entity_ids)
        return {
            "nodes": [
                {"id": n, **data}
                for n, data in subgraph.nodes(data=True)
            ],
            "edges": [
                {"source": u, "target": v, **data}
                for u, v, data in subgraph.edges(data=True)
            ]
        }
    
    def to_dict(self) -> Dict:
        """Export graph as dictionary"""
        return {
            "nodes": [
                {"id": n, **data}
                for n, data in self.graph.nodes(data=True)
            ],
            "edges": [
                {"source": u, "target": v, **data}
                for u, v, data in self.graph.edges(data=True)
            ]
        }


class KnowledgeManager:
    """Manage knowledge base operations"""
    
    def __init__(self):
        self.graph = KnowledgeGraph()
        self.versions: Dict[str, List[Dict]] = {}
    
    def create_version(self, kb_id: str, version: str, description: str = ""):
        """Create a new version of knowledge"""
        if kb_id not in self.versions:
            self.versions[kb_id] = []
        
        self.versions[kb_id].append({
            "version": version,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "snapshot": self.graph.to_dict()
        })
    
    def get_version(self, kb_id: str, version: str) -> Optional[Dict]:
        """Get specific version"""
        versions = self.versions.get(kb_id, [])
        for v in versions:
            if v["version"] == version:
                return v
        return None
    
    def list_versions(self, kb_id: str) -> List[Dict]:
        """List all versions"""
        return self.versions.get(kb_id, [])


# Global knowledge manager
knowledge_manager = KnowledgeManager()