from typing import Dict


class InputValidator:
    """Validate input control logic"""
    
    def __init__(self):
        self.min_word_count = 50
        self.max_word_count = 5000
    
    def validate(self, text: str) -> Dict:
        """
        Validate control logic text
        
        Returns:
            Dict with validation result
        """
        if not text or not text.strip():
            return {
                "valid": False,
                "error": "Control logic cannot be empty"
            }
        
        word_count = len(text.split())
        
        if word_count < self.min_word_count:
            return {
                "valid": False,
                "error": f"Control logic too brief ({word_count} words). Please provide at least {self.min_word_count} words describing the complete control process.",
                "word_count": word_count,
                "required": self.min_word_count
            }
        
        if word_count > self.max_word_count:
            return {
                "valid": False,
                "error": f"Control logic too long ({word_count} words). Maximum {self.max_word_count} words allowed.",
                "word_count": word_count,
                "max_allowed": self.max_word_count
            }
        
        return {
            "valid": True,
            "word_count": word_count
        }


# Global instance
input_validator = InputValidator()