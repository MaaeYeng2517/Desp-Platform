"""Evaluation system for RAG and knowledge quality"""
from typing import Any, Dict, List, Optional
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculate evaluation metrics"""
    
    def calculate_recall(self, retrieved: List[str], expected: List[str]) -> float:
        """Calculate retrieval recall"""
        if not expected:
            return 1.0
        
        retrieved_set = set(retrieved)
        expected_set = set(expected)
        
        intersection = retrieved_set & expected_set
        return len(intersection) / len(expected_set)
    
    def calculate_precision(self, retrieved: List[str], expected: List[str]) -> float:
        """Calculate retrieval precision"""
        if not retrieved:
            return 0.0
        
        retrieved_set = set(retrieved)
        expected_set = set(expected)
        
        intersection = retrieved_set & expected_set
        return len(intersection) / len(retrieved_set)
    
    def calculate_mrr(self, retrieved: List[str], expected: List[str]) -> float:
        """Calculate Mean Reciprocal Rank"""
        expected_set = set(expected)
        
        for i, item in enumerate(retrieved):
            if item in expected_set:
                return 1.0 / (i + 1)
        
        return 0.0
    
    def calculate_ndcg(self, retrieved: List[str], expected: List[str], 
                      k: int = 10) -> float:
        """Calculate Normalized Discounted Cumulative Gain"""
        # Simplified NDCG calculation
        dcg = 0.0
        for i, item in enumerate(retrieved[:k]):
            if item in expected:
                dcg += 1.0 / (i + 1)
        
        # Ideal DCG
        ideal_dcg = sum(1.0 / (i + 1) for i in range(min(len(expected), k)))
        
        if ideal_dcg == 0:
            return 0.0
        
        return dcg / ideal_dcg
    
    def calculate_faithfulness(self, answer: str, context: str) -> float:
        """Calculate faithfulness of answer to context"""
        # Simplified - check if answer terms appear in context
        answer_terms = set(answer.lower().split())
        context_terms = set(context.lower().split())
        
        if not answer_terms:
            return 0.0
        
        overlap = answer_terms & context_terms
        return len(overlap) / len(answer_terms)
    
    def calculate_context_relevance(self, query: str, context: str) -> float:
        """Calculate relevance of context to query"""
        query_terms = set(query.lower().split())
        context_terms = set(context.lower().split())
        
        if not query_terms:
            return 0.0
        
        overlap = query_terms & context_terms
        return len(overlap) / len(query_terms)


class EvaluationEngine:
    """Main evaluation engine"""
    
    def __init__(self):
        self.metrics = MetricsCalculator()
        self.datasets: Dict[str, List[Dict]] = {}
    
    def register_dataset(self, dataset_id: str, questions: List[Dict]):
        """Register evaluation dataset"""
        self.datasets[dataset_id] = questions
    
    async def evaluate(self, kb_id: str, dataset_id: str = None,
                      questions: List[Dict] = None) -> Dict[str, Any]:
        """Run evaluation on knowledge base"""
        from backend.app.services.retrieval import retrieval_engine
        from backend.app.services.rag import rag_engine
        
        eval_questions = questions or self.datasets.get(dataset_id, [])
        if not eval_questions:
            return {"error": "No evaluation questions provided"}
        
        results = []
        all_retrieved = []
        all_expected = []
        
        for question_data in eval_questions:
            question = question_data["question"]
            expected_source = question_data.get("expected_source", "")
            
            # Perform search
            search_result = await retrieval_engine.search(question, [kb_id], limit=5)
            
            retrieved_chunks = [r.get("doc_id", r.get("chunk_id", "")) 
                              for r in search_result["results"]]
            
            # Calculate metrics
            recall = self.metrics.calculate_recall(retrieved_chunks, [expected_source])
            precision = self.metrics.calculate_precision(retrieved_chunks, [expected_source])
            mrr = self.metrics.calculate_mrr(retrieved_chunks, [expected_source])
            
            # Generate answer
            rag_result = await rag_engine.answer(question, [kb_id])
            
            # Calculate answer metrics
            context_text = " ".join([s.get("content", "") for s in rag_result["sources"]])
            faithfulness = self.metrics.calculate_faithfulness(
                rag_result["answer"], context_text
            )
            context_relevance = self.metrics.calculate_context_relevance(
                question, context_text
            )
            
            result = {
                "question": question,
                "expected_source": expected_source,
                "retrieved": retrieved_chunks,
                "recall": recall,
                "precision": precision,
                "mrr": mrr,
                "faithfulness": faithfulness,
                "context_relevance": context_relevance,
                "answer": rag_result["answer"],
                "latency_ms": search_result["latency_ms"]
            }
            results.append(result)
            
            all_retrieved.extend(retrieved_chunks)
            all_expected.append(expected_source)
        
        # Calculate overall metrics
        overall_metrics = {
            "recall": sum(r["recall"] for r in results) / len(results),
            "precision": sum(r["precision"] for r in results) / len(results),
            "mrr": sum(r["mrr"] for r in results) / len(results),
            "faithfulness": sum(r["faithfulness"] for r in results) / len(results),
            "context_relevance": sum(r["context_relevance"] for r in results) / len(results),
            "total_questions": len(results),
            "passed": sum(1 for r in results if r["recall"] > 0.5)
        }
        
        overall_metrics["overall_score"] = (
            overall_metrics["recall"] * 0.3 +
            overall_metrics["precision"] * 0.2 +
            overall_metrics["mrr"] * 0.2 +
            overall_metrics["faithfulness"] * 0.15 +
            overall_metrics["context_relevance"] * 0.15
        )
        
        return {
            "metrics": overall_metrics,
            "results": results,
            "evaluated_at": datetime.utcnow().isoformat()
        }


# Global evaluation engine
evaluation_engine = EvaluationEngine()