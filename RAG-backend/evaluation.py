"""
Evaluation module for RAG system.

This module provides evaluation metrics to assess RAG system performance:
1. Retrieval Metrics: Precision@k, Recall@k, average similarity scores
2. Faithfulness Metrics: How well answers are grounded in retrieved context

The evaluator can use custom test questions or load from test_questions.json.
It measures both the quality of retrieval (finding relevant chunks) and
the quality of generation (staying faithful to retrieved context).
"""

import json
import os
from typing import List, Dict, Any, Optional
from rag_pipeline import RAGPipeline


class Evaluator:
    """Evaluates RAG system performance."""
    
    def __init__(self, rag_pipeline: RAGPipeline):
        """
        Initialize evaluator.
        
        Args:
            rag_pipeline: RAG pipeline instance to evaluate
        """
        self.rag_pipeline = rag_pipeline
        self.default_test_questions = self._load_default_questions()
    
    def _load_default_questions(self) -> List[Dict[str, Any]]:
        """Load default test questions for evaluation."""
        # Try to load from JSON file first
        test_file = os.path.join(os.path.dirname(__file__), 'test_questions.json')
        if os.path.exists(test_file):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('test_questions', [])
            except Exception as e:
                print(f"Warning: Could not load test_questions.json: {e}. Using default questions.")
        
        # Fallback to hardcoded questions
        return [
            {
                "question": "What is Micro Center's return policy?",
                "expected_chunks": [],  # Will be filled based on actual retrieval
                "expected_keywords": ["return", "policy", "refund", "exchange"]
            },
            {
                "question": "How long do I have to return an item?",
                "expected_keywords": ["return", "time", "days", "period"]
            },
            {
                "question": "What items are eligible for return?",
                "expected_keywords": ["return", "eligible", "items", "products"]
            }
        ]
    
    def evaluate(self, test_questions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Run evaluation on test questions.
        
        Args:
            test_questions: List of test questions with expected results.
                          If None, uses default set.
        
        Returns:
            Evaluation results with metrics
        """
        if test_questions is None:
            test_questions = self.default_test_questions
        
        results = {
            'total_questions': len(test_questions),
            'retrieval_metrics': [],
            'faithfulness_scores': [],
            'overall_metrics': {}
        }
        
        for i, test_case in enumerate(test_questions):
            question = test_case['question']
            
            # Retrieve chunks
            retrieved_chunks = self.rag_pipeline.retrieve(question, top_k=5)
            
            # Calculate retrieval metrics
            retrieval_metrics = self._calculate_retrieval_metrics(
                question, retrieved_chunks, test_case
            )
            results['retrieval_metrics'].append({
                'question': question,
                'metrics': retrieval_metrics
            })
            
            # Generate answer and calculate faithfulness
            try:
                answer, citations = self.rag_pipeline.generate_answer(
                    question, retrieved_chunks
                )
                faithfulness = self._calculate_faithfulness(
                    answer, retrieved_chunks, question
                )
                results['faithfulness_scores'].append({
                    'question': question,
                    'answer': answer[:200] + '...' if len(answer) > 200 else answer,
                    'faithfulness_score': faithfulness
                })
            except Exception as e:
                results['faithfulness_scores'].append({
                    'question': question,
                    'error': str(e),
                    'faithfulness_score': 0.0
                })
        
        # Calculate overall metrics
        results['overall_metrics'] = self._calculate_overall_metrics(results)
        
        return results
    
    def _calculate_retrieval_metrics(self, question: str, retrieved_chunks: List[Dict[str, Any]],
                                    test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate retrieval quality metrics.
        
        Computes:
        - Precision@k: Proportion of retrieved chunks that are relevant
        - Recall@k: Proportion of expected keywords found in retrieved chunks
        - Average similarity score: Mean similarity of retrieved chunks
        
        Args:
            question: Test question
            retrieved_chunks: Chunks retrieved by the system
            test_case: Test case with expected_keywords for evaluation
            
        Returns:
            Dictionary with retrieval metrics
        """
        # Initialize metrics with defaults
        metrics = {
            'num_retrieved': len(retrieved_chunks),
            'avg_score': 0.0,
            'recall_at_k': 0.0,
            'precision_at_k': 0.0
        }
        
        if not retrieved_chunks:
            return metrics
        
        # Calculate average similarity score across retrieved chunks
        scores = [chunk.get('score', 0.0) for chunk in retrieved_chunks]
        metrics['avg_score'] = sum(scores) / len(scores) if scores else 0.0
        
        # Keyword-based relevance check (simple evaluation method)
        # Checks if retrieved chunks contain expected keywords
        expected_keywords = test_case.get('expected_keywords', [])
        if expected_keywords:
            relevant_count = 0
            for chunk in retrieved_chunks:
                chunk_text = chunk.get('text', '').lower()
                # Count chunks that contain at least one expected keyword
                if any(keyword.lower() in chunk_text for keyword in expected_keywords):
                    relevant_count += 1
            
            # Precision: relevant chunks / total retrieved chunks
            metrics['precision_at_k'] = relevant_count / len(retrieved_chunks) if retrieved_chunks else 0.0
            
            # Recall: relevant chunks / expected keywords (capped at 1.0)
            metrics['recall_at_k'] = min(1.0, relevant_count / len(expected_keywords)) if expected_keywords else 0.0
        
        return metrics
    
    def _calculate_faithfulness(self, answer: str, retrieved_chunks: List[Dict[str, Any]],
                               question: str) -> float:
        """
        Calculate faithfulness score (how well answer is grounded in retrieved context).
        
        Measures whether the generated answer is based on the retrieved chunks
        rather than hallucinated information. Uses a simple keyword overlap method
        that can be enhanced with more sophisticated techniques (e.g., semantic
        similarity, NLI models).
        
        Args:
            answer: Generated answer text
            retrieved_chunks: Chunks used to generate the answer
            question: Original question (not currently used, reserved for future)
            
        Returns:
            Faithfulness score between 0.0 and 1.0, where:
            - 0.0 = Answer has no relation to context
            - 1.0 = Answer is fully grounded in context
            
        Method:
            1. Extract terms from answer and context
            2. Calculate term overlap ratio
            3. Add bonus if citations are present in answer
        """
        if not retrieved_chunks or not answer:
            return 0.0
        
        # Step 1: Extract key terms from answer (simple word-based approach)
        answer_terms = set(answer.lower().split())
        
        # Step 2: Extract key terms from all retrieved chunks
        context_terms = set()
        for chunk in retrieved_chunks:
            chunk_text = chunk.get('text', '').lower()
            context_terms.update(chunk_text.split())
        
        # Step 3: Calculate term overlap
        if not context_terms:
            return 0.0
        
        overlap = len(answer_terms.intersection(context_terms))
        total_answer_terms = len(answer_terms)
        
        if total_answer_terms == 0:
            return 0.0
        
        # Step 4: Calculate base faithfulness score based on term overlap
        # Normalize by expected overlap ratio (0.5 = 50% of answer terms should match)
        faithfulness = min(1.0, overlap / (total_answer_terms * 0.5))
        
        # Step 5: Check if answer includes citations (indicates grounding)
        has_citations = any(
            chunk.get('chunk_id', '') in answer or 
            chunk.get('metadata', {}).get('source', '') in answer
            for chunk in retrieved_chunks
        )
        
        # Bonus for including citations (shows awareness of sources)
        if has_citations:
            faithfulness = min(1.0, faithfulness + 0.2)
        
        return faithfulness
    
    def _calculate_overall_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall evaluation metrics."""
        if not results['retrieval_metrics']:
            return {}
        
        # Average retrieval metrics
        avg_precision = sum(
            m['metrics']['precision_at_k'] 
            for m in results['retrieval_metrics']
        ) / len(results['retrieval_metrics'])
        
        avg_recall = sum(
            m['metrics']['recall_at_k'] 
            for m in results['retrieval_metrics']
        ) / len(results['retrieval_metrics'])
        
        avg_score = sum(
            m['metrics']['avg_score'] 
            for m in results['retrieval_metrics']
        ) / len(results['retrieval_metrics'])
        
        # Average faithfulness
        faithfulness_scores = [
            f['faithfulness_score'] 
            for f in results['faithfulness_scores']
            if 'error' not in f
        ]
        avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else 0.0
        
        return {
            'average_precision_at_k': avg_precision,
            'average_recall_at_k': avg_recall,
            'average_similarity_score': avg_score,
            'average_faithfulness': avg_faithfulness,
            'total_evaluated': len(results['retrieval_metrics'])
        }

