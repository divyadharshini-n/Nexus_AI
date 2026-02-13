import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup paths
root_dir = Path(__file__).parent.parent
backend_dir = root_dir / "backend"
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)
sys.path.append(str(backend_dir))

import os
from typing import List
import PyPDF2
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import pickle

# Get paths from environment
MANUALS_PATH = Path(root_dir) / "data" / "manuals"
EMBEDDINGS_PATH = Path(root_dir) / "data" / "embeddings"


class ManualProcessor:
    def __init__(self):
        print("🔄 Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384  # Dimension of all-MiniLM-L6-v2
        self.chunks = []
        self.metadata = []
        
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF file"""
        print(f"  📄 Reading: {pdf_path.name}")
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page_text
            return text
        except Exception as e:
            print(f"  ❌ Error reading {pdf_path.name}: {e}")
            return ""
    
    def extract_text_from_txt(self, txt_path: Path) -> str:
        """Extract text from TXT file"""
        print(f"  📄 Reading: {txt_path.name}")
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"  ❌ Error reading {txt_path.name}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def process_manual_folder(self, folder_path: Path, manual_type: str):
        """Process all manuals in a folder"""
        print(f"\n📁 Processing {manual_type} manuals from: {folder_path}")
        
        if not folder_path.exists():
            print(f"  ⚠️  Folder not found: {folder_path}")
            return
        
        # Process PDF files
        pdf_files = list(folder_path.glob("*.pdf"))
        for pdf_file in pdf_files:
            text = self.extract_text_from_pdf(pdf_file)
            if text:
                chunks = self.chunk_text(text)
                print(f"    ✅ Created {len(chunks)} chunks from {pdf_file.name}")
                
                for i, chunk in enumerate(chunks):
                    self.chunks.append(chunk)
                    self.metadata.append({
                        "source": pdf_file.name,
                        "type": manual_type,
                        "chunk_id": i,
                        "total_chunks": len(chunks)
                    })
        
        # Process TXT files
        txt_files = list(folder_path.glob("*.txt"))
        for txt_file in txt_files:
            text = self.extract_text_from_txt(txt_file)
            if text:
                chunks = self.chunk_text(text)
                print(f"    ✅ Created {len(chunks)} chunks from {txt_file.name}")
                
                for i, chunk in enumerate(chunks):
                    self.chunks.append(chunk)
                    self.metadata.append({
                        "source": txt_file.name,
                        "type": manual_type,
                        "chunk_id": i,
                        "total_chunks": len(chunks)
                    })
    
    def create_embeddings(self):
        """Create embeddings for all chunks"""
        if not self.chunks:
            print("\n❌ No chunks to process!")
            return None
        
        print(f"\n🔄 Creating embeddings for {len(self.chunks)} chunks...")
        embeddings = self.model.encode(self.chunks, show_progress_bar=True)
        print(f"✅ Embeddings created: shape {embeddings.shape}")
        return embeddings
    
    def create_faiss_index(self, embeddings):
        """Create FAISS index"""
        print("\n🔄 Creating FAISS index...")
        index = faiss.IndexFlatL2(self.dimension)
        index.add(embeddings.astype('float32'))
        print(f"✅ FAISS index created with {index.ntotal} vectors")
        return index
    
    def save_index(self, index):
        """Save FAISS index and metadata"""
        # Create directories
        faiss_dir = EMBEDDINGS_PATH / "faiss_index"
        metadata_dir = EMBEDDINGS_PATH / "metadata"
        faiss_dir.mkdir(parents=True, exist_ok=True)
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_path = faiss_dir / "manual_index.faiss"
        faiss.write_index(index, str(index_path))
        print(f"\n💾 FAISS index saved to: {index_path}")
        
        # Save chunks
        chunks_path = metadata_dir / "chunks.pkl"
        with open(chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
        print(f"💾 Chunks saved to: {chunks_path}")
        
        # Save metadata
        metadata_path = metadata_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)
        print(f"💾 Metadata saved to: {metadata_path}")
        
        print("\n✅ All RAG components saved successfully!")


def main():
    print("=" * 60)
    print("🚀 MANUAL PROCESSING & RAG SYSTEM SETUP")
    print("=" * 60)
    
    processor = ManualProcessor()
    
    # Process FX5U manuals
    fx5u_path = MANUALS_PATH / "fx5u"
    processor.process_manual_folder(fx5u_path, "FX5U")
    
    # Process GX Works3 manuals
    gx_works3_path = MANUALS_PATH / "gx_works3"
    processor.process_manual_folder(gx_works3_path, "GX_Works3")
    
    # Process datatype conversion rules
    datatype_file = MANUALS_PATH / "datatype_converted.txt"
    if datatype_file.exists():
        print(f"\n📁 Processing datatype conversion rules")
        text = processor.extract_text_from_txt(datatype_file)
        if text:
            chunks = processor.chunk_text(text, chunk_size=300)
            print(f"    ✅ Created {len(chunks)} chunks")
            for i, chunk in enumerate(chunks):
                processor.chunks.append(chunk)
                processor.metadata.append({
                    "source": "datatype_converted.txt",
                    "type": "Datatype_Rules",
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                })
    
    # Create embeddings
    embeddings = processor.create_embeddings()
    
    if embeddings is not None:
        # Create and save FAISS index
        index = processor.create_faiss_index(embeddings)
        processor.save_index(index)
        
        print("\n" + "=" * 60)
        print("✅ RAG SYSTEM SETUP COMPLETE!")
        print("=" * 60)
        print(f"📊 Total chunks processed: {len(processor.chunks)}")
        print(f"📊 Total manuals processed: {len(set(m['source'] for m in processor.metadata))}")
    else:
        print("\n❌ No manuals found to process!")
        print("Please place your PDF/TXT manuals in:")
        print(f"  - {fx5u_path}")
        print(f"  - {gx_works3_path}")
        print(f"  - {datatype_file}")


if __name__ == "__main__":
    main()