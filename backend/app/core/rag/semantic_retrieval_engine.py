from typing import List, Dict, Optional
from app.core.rag.faiss_vector_store import vector_store


class SemanticRetrievalEngine:
    def __init__(self):
        self.vector_store = vector_store
    
    def retrieve(self, query: str, top_k: int = 5, filter_type: Optional[str] = None) -> List[Dict]:
        """
        Retrieve relevant manual content
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_type: Filter by manual type (FX5U, GX_Works3, Datatype_Rules)
        
        Returns:
            List of relevant chunks with metadata
        """
        # Search in vector store
        results = self.vector_store.search(query, top_k=top_k * 2)  # Get more, then filter
        
        # Filter by type if specified
        if filter_type:
            results = [r for r in results if r['metadata']['type'] == filter_type]
        
        # Return top_k results
        return results[:top_k]
    
    def retrieve_context(self, query: str, max_chunks: int = 3) -> str:
        """
        Retrieve context as a single string for LLM
        
        Args:
            query: Search query
            max_chunks: Maximum number of chunks to include
        
        Returns:
            Formatted context string
        """
        results = self.retrieve(query, top_k=max_chunks)
        
        if not results:
            return "No relevant information found in manuals."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result['metadata']['source']
            content = result['content']
            context_parts.append(f"[Source: {source}]\n{content}\n")
        
        return "\n---\n".join(context_parts)


# Global instance
retrieval_engine = SemanticRetrievalEngine()