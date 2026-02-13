from typing import Dict, List
from app.core.ai_agents.shared.perplexity_api_client import perplexity_client
from app.core.rag.semantic_retrieval_engine import retrieval_engine


class StageSegregator:
    """Segregates control logic into operational stages"""
    
    def __init__(self):
        self.perplexity = perplexity_client
        self.retrieval = retrieval_engine
    
    async def segregate(self, control_logic: str, analysis: Dict) -> Dict:
        """
        Segregate control logic into stages
        
        Args:
            control_logic: Full control logic description
            analysis: Analysis from ProcessFlowAnalyzer
        
        Returns:
            Dict with stages
        """
        # Build prompt for stage segregation
        system_prompt = self._build_segregation_prompt()
        
        # Get manual context about stages
        manual_context = retrieval_engine.retrieve_context(
            "PLC stage programming control flow stages",
            max_chunks=2
        )
        
        # Build messages
        messages = [
            {
                "role": "system",
                "content": f"{system_prompt}\n\n=== MANUAL CONTEXT ===\n{manual_context}"
            },
            {
                "role": "user",
                "content": f"""Analyze this control logic and segregate it into stages.

CONTROL LOGIC:
{control_logic}

ANALYSIS SUMMARY:
- Word count: {analysis['word_count']}
- Complexity: {analysis['complexity_score']}
- Has emergency logic: {analysis['has_emergency_logic']}
- Has safety logic: {analysis['has_safety_logic']}
- Detected actuators: {', '.join(analysis['detected_actuators'][:5])}

Provide the stage segregation in the following JSON format:
{{
  "stages": [
    {{
      "stage_number": 0,
      "stage_name": "Idle Stage",
      "stage_type": "idle",
      "description": "Brief description",
      "original_logic": "Exact logic from user input for this stage"
    }},
    ...
  ],
  "dependencies": [
    {{
      "from_stage": 0,
      "to_stage": 1,
      "condition": "Description of transition condition"
    }}
  ]
}}

CRITICAL RULES:
1. Stage 0 MUST be Idle Stage
2. Stage 1 MUST be Safety Check Stage
3. Extract ONLY the logic user provided - do NOT add new logic
4. Preserve exact user wording in original_logic
5. Each stage must have clear purpose
"""
            }
        ]
        
        # Call Perplexity
        response = await self.perplexity.chat_completion(
            messages=messages,
            temperature=0.2,  # Very deterministic
            max_tokens=3000
        )
        
        # Extract and parse response
        response_text = self.perplexity.extract_response_text(response)
        
        # Parse JSON from response
        import json
        import re
        
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                stages_data = json.loads(json_match.group())
                return stages_data
            except json.JSONDecodeError:
                pass
        
        # Fallback: Return basic structure
        return {
            "stages": [
                {
                    "stage_number": 0,
                    "stage_name": "Idle Stage",
                    "stage_type": "idle",
                    "description": "System idle state with all outputs safe",
                    "original_logic": "Initial safe state"
                },
                {
                    "stage_number": 1,
                    "stage_name": "Safety Check Stage",
                    "stage_type": "safety",
                    "description": "Verify safety conditions and interlocks",
                    "original_logic": "Safety validation"
                }
            ],
            "dependencies": [
                {
                    "from_stage": 0,
                    "to_stage": 1,
                    "condition": "System ready and no faults"
                }
            ]
        }
    
    def _build_segregation_prompt(self) -> str:
        """Build system prompt for stage segregation"""
        return """You are an expert PLC control system architect specializing in stage-based control flow design.

Your task is to analyze user-provided control logic and segregate it into clear operational stages.

MANDATORY STAGE STRUCTURE:
- Stage 0: Idle Stage (ALWAYS REQUIRED)
  Purpose: Safe baseline state, all outputs OFF, system ready
  
- Stage 1: Safety Check Stage (ALWAYS REQUIRED)
  Purpose: Verify interlocks, emergency conditions, system readiness
  
- Stage 2+: Process Stages (AS NEEDED)
  Purpose: Actual control operations, sequencing, automation

CRITICAL RULES:
1. NEVER add logic the user didn't provide
2. NEVER remove logic the user provided
3. NEVER change the meaning of user's logic
4. Extract and map user's exact words to appropriate stages
5. If user didn't mention idle/safety, create minimal placeholder stages
6. Each stage must have ONLY the logic relevant to it

OUTPUT FORMAT:
- JSON structure with stages array
- Each stage has: stage_number, stage_name, stage_type, description, original_logic
- Dependencies array showing stage transitions"""