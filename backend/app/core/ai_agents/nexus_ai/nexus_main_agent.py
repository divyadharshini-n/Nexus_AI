from typing import Dict, List, Optional
from app.core.ai_agents.shared.perplexity_api_client import perplexity_client
from app.core.rag.semantic_retrieval_engine import retrieval_engine
from app.core.orchestration.system_prompt_manager import prompt_manager


class NexusAIAgent:
    def __init__(self):
        self.perplexity = perplexity_client
        self.retrieval = retrieval_engine
        self.conversation_history = []
        self.current_phase = "idle"
        
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.current_phase = "idle"
    
    async def chat(self, user_message: str, project_context: Optional[Dict] = None) -> Dict:
        """
        Main chat interface for Nexus AI
        
        Args:
            user_message: User's input message
            project_context: Optional project context (stages, previous code, etc.)
        
        Returns:
            Response dict with message and metadata
        """
        # Get system prompt
        system_prompt = prompt_manager.get_nexus_prompt()
        
        # Retrieve relevant manual context
        manual_context = retrieval_engine.retrieve_context(user_message, max_chunks=3)
        
        # Build messages for Perplexity
        messages = self._build_messages(
            system_prompt=system_prompt,
            user_message=user_message,
            manual_context=manual_context,
            project_context=project_context
        )
        
        # Call Perplexity API
        response = await self.perplexity.chat_completion(
            messages=messages,
            temperature=0.3,  # Lower temperature for more focused responses
            max_tokens=3000
        )
        
        # Extract response
        assistant_message = self.perplexity.extract_response_text(response)
        
        # Update conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return {
            "message": assistant_message,
            "phase": self._detect_phase(assistant_message),
            "manual_context_used": True if manual_context else False
        }
    
    def _build_messages(
        self,
        system_prompt: str,
        user_message: str,
        manual_context: str,
        project_context: Optional[Dict]
    ) -> List[Dict]:
        """Build message array for API"""
        messages = []
        
        # System prompt with manual context
        system_content = f"{system_prompt}\n\n"
        
        if manual_context:
            system_content += f"\n\n=== RELEVANT MANUAL INFORMATION ===\n{manual_context}\n"
        
        if project_context:
            system_content += f"\n\n=== PROJECT CONTEXT ===\n{project_context}\n"
        
        messages.append({
            "role": "system",
            "content": system_content
        })
        
        # Add conversation history (last 10 messages)
        for msg in self.conversation_history[-10:]:
            messages.append(msg)
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def _detect_phase(self, response: str) -> str:
        """Detect which phase Nexus is in based on response"""
        response_lower = response.lower()
        
        if "idle analysis" in response_lower or "idle stage" in response_lower:
            return "phase_1_idle"
        elif "safety analysis" in response_lower or "safety check" in response_lower:
            return "phase_2_safety"
        elif "planner" in response_lower or "stage segregation" in response_lower:
            return "phase_3_planner"
        elif "validation" in response_lower or "semantic validation" in response_lower:
            return "phase_4_validation"
        elif "confirmation" in response_lower or "should i generate" in response_lower:
            return "phase_5_confirmation"
        elif "structured text" in response_lower or "global label" in response_lower:
            return "phase_6_generation"
        else:
            return "conversational"


# Global instance
nexus_agent = NexusAIAgent()