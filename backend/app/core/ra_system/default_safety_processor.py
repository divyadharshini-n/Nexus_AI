from pathlib import Path
from typing import Dict, List
import PyPDF2
from docx import Document
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import json
from app.config import settings


class DefaultSafetyProcessor:
    """Process and embed default safety manuals from project folder"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
        self.default_manuals_dir = Path(settings.ROOT_DIR) / "data" / "manuals" / "user_safety_manuals"
        self.embeddings_dir = Path(settings.EMBEDDINGS_PATH) / "default_safety_manuals"
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract PDF: {str(e)}")
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from Word document"""
        try:
            doc = Document(file_path)
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            return "\n".join(text)
        except Exception as e:
            raise Exception(f"Failed to extract DOCX: {str(e)}")
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Failed to extract TXT: {str(e)}")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from any supported format"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif extension == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise Exception(f"Unsupported file type: {extension}")
    
    def chunk_text(self, text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def create_embeddings(self, chunks: List[str]) -> np.ndarray:
        """Create embeddings for chunks"""
        return self.model.encode(chunks, show_progress_bar=False)
    
    def create_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Create FAISS index"""
        index = faiss.IndexFlatL2(self.dimension)
        index.add(embeddings.astype('float32'))
        return index
    
    def get_default_manuals(self) -> List[Path]:
        """Get all default safety manuals from directory"""
        if not self.default_manuals_dir.exists():
            return []
        
        supported_extensions = ['.pdf', '.docx', '.doc', '.txt']
        manuals = []
        
        for ext in supported_extensions:
            manuals.extend(self.default_manuals_dir.glob(f"*{ext}"))
        
        return manuals
    
    def process_default_manuals(self) -> Dict:
        """
        Process all default safety manuals and create unified embeddings
        
        Returns:
            Dict with processing results
        """
        # Get all default manuals
        manuals = self.get_default_manuals()
        
        if not manuals:
            return {
                "success": False,
                "error": "No default safety manuals found in data/manuals/user_safety_manuals/"
            }
        
        # Extract text from all manuals
        all_text = []
        manual_sources = []
        
        for manual_path in manuals:
            try:
                text = self.extract_text(str(manual_path))
                if text and len(text) > 100:
                    all_text.append(text)
                    manual_sources.append(manual_path.name)
            except Exception as e:
                print(f"Failed to process {manual_path.name}: {str(e)}")
        
        if not all_text:
            return {
                "success": False,
                "error": "Failed to extract text from default safety manuals"
            }
        
        # Combine all text
        combined_text = "\n\n=== MANUAL SEPARATOR ===\n\n".join(all_text)
        
        # Chunk combined text
        chunks = self.chunk_text(combined_text)
        
        if not chunks:
            return {
                "success": False,
                "error": "Failed to create chunks from default safety manuals"
            }
        
        # Create embeddings
        embeddings = self.create_embeddings(chunks)
        
        # Create FAISS index
        index = self.create_faiss_index(embeddings)
        
        # Create output directory
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_file = self.embeddings_dir / "default_safety_index.faiss"
        faiss.write_index(index, str(index_file))
        
        # Save chunks
        chunks_file = self.embeddings_dir / "default_safety_chunks.pkl"
        with open(chunks_file, 'wb') as f:
            pickle.dump(chunks, f)
        
        # Save metadata
        metadata = {
            "total_chunks": len(chunks),
            "total_manuals": len(manual_sources),
            "manual_sources": manual_sources,
            "word_count": len(combined_text.split())
        }
        metadata_file = self.embeddings_dir / "default_safety_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "chunks_count": len(chunks),
            "manuals_processed": len(manual_sources),
            "manual_sources": manual_sources,
            "word_count": len(combined_text.split()),
            "index_path": str(index_file),
            "chunks_path": str(chunks_file),
            "metadata_path": str(metadata_file)
        }
    
    def is_default_index_ready(self) -> bool:
        """Check if default safety index exists"""
        index_file = self.embeddings_dir / "default_safety_index.faiss"
        chunks_file = self.embeddings_dir / "default_safety_chunks.pkl"
        metadata_file = self.embeddings_dir / "default_safety_metadata.json"
        
        return (index_file.exists() and 
                chunks_file.exists() and 
                metadata_file.exists())


# Global instance
default_safety_processor = DefaultSafetyProcessor()