from pathlib import Path
from typing import List, Dict
import faiss
import pickle
import json


class SafetyRetrievalEngine:
    """Retrieve relevant safety rules for code validation"""
    
    def __init__(self):
        self._model = None
        self.cache = {}  # Cache loaded indices
    
    @property
    def model(self):
        """Lazy load the model only when needed"""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
        return self._model
    
    def load_safety_manual(self, project_id: int, embeddings_dir: str) -> bool:
        """Load safety manual embeddings for a project"""
        if project_id in self.cache:
            return True
        
        embeddings_path = Path(embeddings_dir)
        
        # Load FAISS index
        index_file = embeddings_path / f"safety_manual_{project_id}.faiss"
        if not index_file.exists():
            return False
        
        index = faiss.read_index(str(index_file))
        
        # Load chunks
        chunks_file = embeddings_path / f"safety_manual_{project_id}_chunks.pkl"
        with open(chunks_file, 'rb') as f:
            chunks = pickle.load(f)
        
        # Load metadata
        metadata_file = embeddings_path / f"safety_manual_{project_id}_metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Cache
        self.cache[project_id] = {
            "index": index,
            "chunks": chunks,
            "metadata": metadata
        }
        
        return True
    
    def retrieve(self, project_id: int, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant safety rules
        
        Args:
            project_id: Project ID
            query: Query text (e.g., generated code snippet)
            top_k: Number of results to return
        
        Returns:
            List of relevant safety rules
        """
        if project_id not in self.cache:
            return []
        
        cache_data = self.cache[project_id]
        index = cache_data["index"]
        chunks = cache_data["chunks"]
        
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
    
    def retrieve_context(self, project_id: int, query: str, max_chunks: int = 3) -> str:
        """
        Retrieve safety context as a single string
        
        Args:
            project_id: Project ID
            query: Query text
            max_chunks: Maximum chunks to return
        
        Returns:
            Formatted safety context string
        """
        results = self.retrieve(project_id, query, top_k=max_chunks)
        
        if not results:
            return "No safety manual uploaded for this project."
        
        context_parts = []
        for result in results:
            context_parts.append(result['content'])
        
        return "\n\n---\n\n".join(context_parts)


# Global instance
safety_retrieval_engine = SafetyRetrievalEngine()