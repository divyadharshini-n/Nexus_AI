from typing import Dict, List
from app.core.ai_agents.shared.perplexity_api_client import perplexity_client
from app.core.ra_system.safety_retrieval_engine import safety_retrieval_engine


class RAInterrogator:
    """Risk Assessment Interrogator - Validates code against safety rules"""
    
    def __init__(self):
        self.perplexity = perplexity_client
        self.safety_retrieval = safety_retrieval_engine
    
    async def interrogate_code(
        self,
        project_id: int,
        code: Dict,
        embeddings_dir: str
    ) -> Dict:
        """
        Interrogate generated code against safety manual
        
        Args:
            project_id: Project ID
            code: Generated code dict
            embeddings_dir: Directory with safety embeddings
        
        Returns:
            Interrogation result
        """
        # Load safety manual
        loaded = self.safety_retrieval.load_safety_manual(project_id, embeddings_dir)
        
        if not loaded:
            return {
                "success": False,
                "error": "No safety manual found for this project. Please upload a safety manual first."
            }
        
        # Get relevant safety rules
        code_text = code.get('program_body', '')
        safety_context = self.safety_retrieval.retrieve_context(
            project_id,
            code_text,
            max_chunks=5
        )
        
        # Build interrogation prompt
        system_prompt = self._build_interrogation_prompt()
        user_request = self._build_interrogation_request(code, safety_context)
        
        # Call Perplexity
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_request}
        ]
        
        response = await self.perplexity.chat_completion(
            messages=messages,
            temperature=0.1,
            max_tokens=2500
        )
        
        # Parse response
        interrogation_text = self.perplexity.extract_response_text(response)
        result = self._parse_interrogation_result(interrogation_text)
        
        return result
    
    def _build_interrogation_prompt(self) -> str:
        """Build system prompt for RA interrogation"""
        return """You are a Safety Assessment Expert specializing in PLC control systems.

Your task is to interrogate generated PLC code against the user's safety manual and identify potential safety violations.

Output your assessment in this EXACT format:

==============================
SAFETY ASSESSMENT
==============================
Overall Status: [SAFE / WARNING / UNSAFE]
Severity: [LOW / MEDIUM / HIGH / CRITICAL]

==============================
SAFETY COMPLIANCE CHECK
==============================
[Analysis of code against safety rules]

==============================
POTENTIAL HAZARDS IDENTIFIED
==============================
[List potential hazards, one per line]
- Hazard 1: [Description]
- Hazard 2: [Description]
...

==============================
SAFETY VIOLATIONS
==============================
[List any safety rule violations]
- Violation 1: [Rule violated + explanation]
- Violation 2: [Rule violated + explanation]
...

==============================
REQUIRED ACTIONS
==============================
[List required safety improvements]
- Action 1: [What must be done]
- Action 2: [What must be done]
...

==============================
RECOMMENDATIONS
==============================
[Additional safety recommendations]
- Recommendation 1
- Recommendation 2
...

Be thorough and focus on SAFETY-CRITICAL issues. If code is safe, say so clearly."""

    def _build_interrogation_request(self, code: Dict, safety_context: str) -> str:
        """Build interrogation request"""
        return f"""Interrogate this PLC code against the safety manual.

=== GENERATED CODE ===
Program Name: {code.get('program_name', 'Unknown')}
Execution Type: {code.get('execution_type', 'Unknown')}

Global Labels:
{self._format_labels(code.get('global_labels', []))}

Local Labels:
{self._format_labels(code.get('local_labels', []))}

Program Body:
{code.get('program_body', '')}

=== RELEVANT SAFETY RULES ===
{safety_context}

Perform complete safety assessment and identify all potential hazards."""

    def _format_labels(self, labels: List[Dict]) -> str:
        """Format labels for display"""
        if not labels:
            return "No labels"
        
        lines = []
        for label in labels[:10]:  # Limit to first 10
            lines.append(f"- {label.get('name', 'N/A')}: {label.get('data_type', 'N/A')}")
        
        if len(labels) > 10:
            lines.append(f"... and {len(labels) - 10} more")
        
        return "\n".join(lines)
    
    def _parse_interrogation_result(self, interrogation_text: str) -> Dict:
        """Parse interrogation result"""
        result = {
            "success": True,
            "safe": False,
            "status": "UNSAFE",
            "severity": "UNKNOWN",
            "compliance_analysis": "",
            "hazards": [],
            "violations": [],
            "required_actions": [],
            "recommendations": []
        }
        
        # Extract status
        if "Overall Status: SAFE" in interrogation_text:
            result["safe"] = True
            result["status"] = "SAFE"
        elif "Overall Status: WARNING" in interrogation_text:
            result["safe"] = True
            result["status"] = "WARNING"
        
        # Extract severity
        if "Severity: LOW" in interrogation_text:
            result["severity"] = "LOW"
        elif "Severity: MEDIUM" in interrogation_text:
            result["severity"] = "MEDIUM"
        elif "Severity: HIGH" in interrogation_text:
            result["severity"] = "HIGH"
        elif "Severity: CRITICAL" in interrogation_text:
            result["severity"] = "CRITICAL"
        
        # Parse sections
        lines = interrogation_text.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            if 'SAFETY COMPLIANCE CHECK' in line:
                current_section = 'compliance'
                section_content = []
            elif 'POTENTIAL HAZARDS' in line:
                if current_section == 'compliance':
                    result['compliance_analysis'] = '\n'.join(section_content).strip()
                current_section = 'hazards'
                section_content = []
            elif 'SAFETY VIOLATIONS' in line:
                if current_section == 'hazards':
                    result['hazards'] = self._extract_list_items(section_content)
                current_section = 'violations'
                section_content = []
            elif 'REQUIRED ACTIONS' in line:
                if current_section == 'violations':
                    result['violations'] = self._extract_list_items(section_content)
                current_section = 'actions'
                section_content = []
            elif 'RECOMMENDATIONS' in line:
                if current_section == 'actions':
                    result['required_actions'] = self._extract_list_items(section_content)
                current_section = 'recommendations'
                section_content = []
            elif current_section and line.strip() and not line.startswith('==='):
                section_content.append(line)
        
        # Parse last section
        if current_section == 'recommendations':
            result['recommendations'] = self._extract_list_items(section_content)
        
        return result
    
    def _extract_list_items(self, lines: List[str]) -> List[str]:
        """Extract list items from lines"""
        items = []
        for line in lines:
            if line.strip().startswith('-'):
                items.append(line.strip()[1:].strip())
        return items


# Global instance
ra_interrogator = RAInterrogator()