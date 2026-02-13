from pathlib import Path
from typing import Dict
from app.core.input_processing.document_parser import document_parser
from app.core.input_processing.voice_processor import voice_processor


class MultimodalHandler:
    """Handle all input types"""
    
    def __init__(self):
        self.document_parser = document_parser
        self.voice_processor = voice_processor
        
        self.supported_document_types = ['.pdf', '.docx', '.doc', '.txt']
        self.supported_audio_types = ['.wav']
    
    def process_file(self, file_path: str) -> Dict:
        """
        Process any supported file type
        
        Returns:
            Dict with extracted text and metadata
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # Check if file exists
        if not path.exists():
            return {
                "success": False,
                "error": "File not found"
            }
        
        # Route to appropriate processor
        if extension in self.supported_document_types:
            return self.document_parser.parse_file(file_path)
        elif extension in self.supported_audio_types:
            return self.voice_processor.process_audio(file_path)
        else:
            return {
                "success": False,
                "error": f"Unsupported file type: {extension}. Supported: {', '.join(self.supported_document_types + self.supported_audio_types)}"
            }
    
    def get_supported_types(self) -> Dict:
        """Get list of supported file types"""
        return {
            "documents": self.supported_document_types,
            "audio": self.supported_audio_types,
            "all": self.supported_document_types + self.supported_audio_types
        }


# Global instance
multimodal_handler = MultimodalHandler()