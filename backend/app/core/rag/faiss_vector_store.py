import faiss
import pickle
import json
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings


class FAISSVectorStore:
    def __init__(self):
        self.model = None
        self.index = None
        self.chunks = None
        self.metadata = None
        self.is_loaded = False
        
    def load(self):
        """Load FAISS index and metadata"""
        if self.is_loaded:
            return
        
        print("Loading RAG system...")
        
        # Load embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Setup paths
        embeddings_path = Path(settings.EMBEDDINGS_PATH)
        faiss_dir = embeddings_path / "faiss_index"
        metadata_dir = embeddings_path / "metadata"
        
        # Load FAISS index
        index_path = faiss_dir / "manual_index.faiss"
        if not index_path.exists():
            raise FileNotFoundError(f"FAISS index not found at {index_path}")
        self.index = faiss.read_index(str(index_path))
        
        # Load chunks
        chunks_path = metadata_dir / "chunks.pkl"
        with open(chunks_path, 'rb') as f:
            self.chunks = pickle.load(f)
        
        # Load metadata
        metadata_path = metadata_dir / "metadata.json"
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        
        self.is_loaded = True
        print(f"RAG system loaded: {len(self.chunks)} chunks available")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant chunks"""
        if not self.is_loaded:
            self.load()
        
        # Create query embedding
        query_embedding = self.model.encode([query])
        
        # Search in FAISS
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Prepare results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.chunks):
                results.append({
                    "rank": i + 1,
                    "content": self.chunks[idx],
                    "metadata": self.metadata[idx],
                    "score": float(distance)
                })
        
        return results


# Global instance
vector_store = FAISSVectorStore()