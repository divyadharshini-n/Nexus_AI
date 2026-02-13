from typing import Dict, Optional
from app.core.ai_agents.shared.perplexity_api_client import perplexity_client
from app.core.rag.semantic_retrieval_engine import retrieval_engine
from app.core.orchestration.system_prompt_manager import prompt_manager


class AIDudeAgent:
    def __init__(self):
        self.perplexity = perplexity_client
        self.retrieval = retrieval_engine
        self.conversation_history = []
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
    
    async def query(
        self,
        user_question: str,
        code_context: Optional[str] = None,
        stage_context: Optional[Dict] = None
    ) -> Dict:
        """
        Answer user questions about code, GX Works3, and FX5U
        
        Args:
            user_question: User's question
            code_context: Generated code to explain
            stage_context: Current stage information
        
        Returns:
            Response dict with answer
        """
        # Get system prompt
        system_prompt = prompt_manager.get_aidude_prompt()
        
        # Retrieve relevant manual context
        manual_context = retrieval_engine.retrieve_context(user_question, max_chunks=3)
        
        # Build messages
        messages = self._build_messages(
            system_prompt=system_prompt,
            user_question=user_question,
            manual_context=manual_context,
            code_context=code_context,
            stage_context=stage_context
        )
        
        # Call Perplexity API
        response = await self.perplexity.chat_completion(
            messages=messages,
            temperature=0.2,  # Very focused, concise responses
            max_tokens=1500
        )
        
        # Extract response
        answer = self.perplexity.extract_response_text(response)
        
        # Update history
        self.conversation_history.append({
            "role": "user",
            "content": user_question
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": answer
        })
        
        return {
            "answer": answer,
            "manual_grounded": True if manual_context else False
        }
    
    def _build_messages(
        self,
        system_prompt: str,
        user_question: str,
        manual_context: str,
        code_context: Optional[str],
        stage_context: Optional[Dict]
    ) -> list:
        """Build message array for API"""
        messages = []
        
        # System prompt
        system_content = f"{system_prompt}\n\n"
        
        # Add manual context (CRITICAL for grounding)
        if manual_context:
            system_content += f"\n\n=== MANUAL REFERENCE ===\n{manual_context}\n"
        
        # Add code context if provided
        if code_context:
            system_content += f"\n\n=== CODE TO EXPLAIN ===\n{code_context}\n"
        
        # Add stage context if provided
        if stage_context:
            system_content += f"\n\n=== STAGE CONTEXT ===\n{stage_context}\n"
        
        system_content += "\n\nIMPORTANT: Be CONCISE. Provide only the required answer. Do not over-explain."
        
        messages.append({
            "role": "system",
            "content": system_content
        })
        
        # Add conversation history (last 6 messages)
        for msg in self.conversation_history[-6:]:
            messages.append(msg)
        
        # Add current question
        messages.append({
            "role": "user",
            "content": user_question
        })
        
        return messages


# Global instance
aidude_agent = AIDudeAgent()