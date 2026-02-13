import httpx
from typing import List, Dict, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class PerplexityAPIClient:
    def __init__(self):
        # Using Google Gemini as AI provider
        self.provider = getattr(settings, 'AI_PROVIDER', 'gemini').lower()
        
        self.api_key = settings.GEMINI_API_KEY
        self.api_url = settings.GEMINI_API_URL
        self.default_model = "gemini-flash-lite-latest"  # 1500 requests/day
        
        if not self.api_key:
            logger.error("GEMINI_API_KEY is not set in environment")
            raise ValueError("GEMINI_API_KEY is required")
        
        logger.info("Using Google Gemini as AI provider")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> Dict:
        """
        Send chat completion request to Google Gemini API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (if None, uses default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            API response dict (converted to match expected format)
        """
        # Use default model if none specified
        if model is None:
            model = self.default_model
        
        # Build Gemini API endpoint
        endpoint = f"{self.api_url}/v1beta/models/{model}:generateContent"
        
        logger.info(f"Making Gemini API call with key: {self.api_key[:10]}...{self.api_key[-5:]}")
        logger.info(f"API URL: {endpoint}")
        logger.info(f"Model: {model}")
        
        # Convert messages to Gemini format
        # Gemini uses "contents" array with "parts" structure
        contents = []
        system_instruction = None
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                system_instruction = content
            elif role == 'user':
                contents.append({
                    "role": "user",
                    "parts": [{"text": content}]
                })
            elif role == 'assistant':
                contents.append({
                    "role": "model",
                    "parts": [{"text": content}]
                })
        
        # Build Gemini request payload
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        # Add system instruction if present (v1beta feature)
        if system_instruction:
            payload["system_instruction"] = {
                "parts": [{"text": system_instruction}]
            }
        
        # Gemini uses API key as query parameter
        params = {"key": self.api_key}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                endpoint,
                params=params,
                json=payload
            )
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"Gemini API Error ({response.status_code}): {error_detail}")
                logger.error(f"Request payload: {payload}")
                response.raise_for_status()
            
            gemini_response = response.json()
            
            # Convert Gemini response to expected format (OpenAI-like)
            # This maintains compatibility with downstream code
            converted_response = self._convert_gemini_response(gemini_response)
            return converted_response
    
    def _convert_gemini_response(self, gemini_response: Dict) -> Dict:
        """
        Convert Gemini API response to OpenAI-compatible format
        to maintain compatibility with existing code
        """
        try:
            # Extract text from Gemini response
            candidates = gemini_response.get('candidates', [])
            if candidates:
                content = candidates[0].get('content', {})
                parts = content.get('parts', [])
                if parts:
                    text = parts[0].get('text', '')
                else:
                    text = ''
            else:
                text = ''
            
            # Convert to OpenAI-like format
            return {
                'choices': [{
                    'message': {
                        'content': text,
                        'role': 'assistant'
                    },
                    'finish_reason': 'stop',
                    'index': 0
                }],
                'model': gemini_response.get('modelVersion', self.default_model),
                'usage': gemini_response.get('usageMetadata', {})
            }
        except Exception as e:
            logger.error(f"Error converting Gemini response: {e}")
            logger.error(f"Original response: {gemini_response}")
            # Return minimal valid response
            return {
                'choices': [{
                    'message': {
                        'content': '',
                        'role': 'assistant'
                    },
                    'finish_reason': 'error',
                    'index': 0
                }]
            }
    
    def extract_response_text(self, response: Dict) -> str:
        """Extract text from API response (works with converted format)"""
        try:
            return response['choices'][0]['message']['content']
        except (KeyError, IndexError):
            return ""


# Global instance
perplexity_client = PerplexityAPIClient()