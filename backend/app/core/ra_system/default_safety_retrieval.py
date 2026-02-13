from pathlib import Path
from typing import List, Dict
import faiss
import pickle
import json
from sentence_transformers import SentenceTransformer
from app.config import settings


class DefaultSafetyRetrieval:
    """Retrieve safety rules from default preloaded manuals"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embeddings_dir = Path(settings.EMBEDDINGS_PATH) / "default_safety_manuals"
        self.cache = None
    
    def load_default_safety_manual(self) -> bool:
        """Load default safety manual embeddings"""
        if self.cache is not None:
            return True
        
        # Load FAISS index
        index_file = self.embeddings_dir / "default_safety_index.faiss"
        if not index_file.exists():
            return False
        
        index = faiss.read_index(str(index_file))
        
        # Load chunks
        chunks_file = self.embeddings_dir / "default_safety_chunks.pkl"
        with open(chunks_file, 'rb') as f:
            chunks = pickle.load(f)
        
        # Load metadata
        metadata_file = self.embeddings_dir / "default_safety_metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Cache
        self.cache = {
            "index": index,
            "chunks": chunks,
            "metadata": metadata
        }
        
        return True
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant safety rules from default manuals
        
        Args:
            query: Query text (e.g., generated code snippet)
            top_k: Number of results to return
        
        Returns:
            List of relevant safety rules
        """
        if self.cache is None:
            return []
        
        index = self.cache["index"]
        chunks = self.cache["chunks"]
        
        # Create query embedding
        query_embedding = self.model.encode([query])
        
        # Search
        distances, indices = index.search(query_embedding.astype('float32'), top_k)
        
        # Prepare results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(chunks):
                results.append({
                    "rank": i + 1,
                    "content": chunks[idx],
                    "score": float(distance)
                })
        
        return results
    
    def retrieve_context(self, query: str, max_chunks: int = 5) -> str:
        """
        Retrieve safety context as a single string
        
        Args:
            query: Query text
            max_chunks: Maximum chunks to return
        
        Returns:
            Formatted safety context string
        """
        results = self.retrieve(query, top_k=max_chunks)
        
        if not results:
            return "No default safety manuals loaded."
        
        context_parts = []
        for result in results:
            context_parts.append(result['content'])
        
        return "\n\n---\n\n".join(context_parts)
    
    def get_metadata(self) -> Dict:
        """Get metadata about loaded default manuals"""
        if self.cache is None:
            return {}
        return self.cache.get("metadata", {})


# Global instance
default_safety_retrieval = DefaultSafetyRetrieval()