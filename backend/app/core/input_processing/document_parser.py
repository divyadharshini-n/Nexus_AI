from pathlib import Path
from typing import Dict
import PyPDF2
from docx import Document


class DocumentParser:
    """Parse documents to extract text"""
    
    def parse_pdf(self, file_path: str) -> str:
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
            raise Exception(f"Failed to parse PDF: {str(e)}")
    
    def parse_word(self, file_path: str) -> str:
        """Extract text from Word document"""
        try:
            doc = Document(file_path)
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            return "\n".join(text)
        except Exception as e:
            raise Exception(f"Failed to parse Word document: {str(e)}")
    
    def parse_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Failed to parse TXT file: {str(e)}")
    
    def parse_file(self, file_path: str) -> Dict:
        """
        Parse any supported file type
        
        Returns:
            Dict with extracted text and metadata
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        try:
            if extension == '.pdf':
                text = self.parse_pdf(file_path)
            elif extension in ['.docx', '.doc']:
                text = self.parse_word(file_path)
            elif extension == '.txt':
                text = self.parse_txt(file_path)
            else:
                raise Exception(f"Unsupported file type: {extension}")
            
            return {
                "success": True,
                "text": text,
                "filename": path.name,
                "file_type": extension[1:],  # Remove the dot
                "word_count": len(text.split())
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filename": path.name
            }


# Global instance
document_parser = DocumentParser()