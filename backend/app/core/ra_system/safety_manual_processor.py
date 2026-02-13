from pathlib import Path
from typing import Dict, List
import PyPDF2
from docx import Document
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import json


class SafetyManualProcessor:
    """Process and embed user's safety manual"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
    
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
    
    def process_and_embed(
        self,
        file_path: str,
        output_dir: str,
        project_id: int
    ) -> Dict:
        """
        Process safety manual and create embeddings
        
        Returns:
            Dict with processing results
        """
        try:
            # Extract text
            text = self.extract_text(file_path)
            
            if not text or len(text) < 100:
                return {
                    "success": False,
                    "error": "Safety manual content too short or empty"
                }
            
            # Chunk text
            chunks = self.chunk_text(text)
            
            if not chunks:
                return {
                    "success": False,
                    "error": "Failed to create chunks from safety manual"
                }
            
            # Create embeddings
            embeddings = self.create_embeddings(chunks)
            
            # Create FAISS index
            index = self.create_faiss_index(embeddings)
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            index_file = output_path / f"safety_manual_{project_id}.faiss"
            faiss.write_index(index, str(index_file))
            
            # Save chunks
            chunks_file = output_path / f"safety_manual_{project_id}_chunks.pkl"
            with open(chunks_file, 'wb') as f:
                pickle.dump(chunks, f)
            
            # Save metadata
            metadata = {
                "project_id": project_id,
                "total_chunks": len(chunks),
                "original_file": Path(file_path).name,
                "word_count": len(text.split())
            }
            metadata_file = output_path / f"safety_manual_{project_id}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return {
                "success": True,
                "chunks_count": len(chunks),
                "word_count": len(text.split()),
                "index_path": str(index_file),
                "chunks_path": str(chunks_file),
                "metadata_path": str(metadata_file)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
safety_manual_processor = SafetyManualProcessor()