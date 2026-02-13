from typing import Dict, List
from app.core.ai_agents.shared.perplexity_api_client import perplexity_client
from app.core.ra_system.default_safety_retrieval import default_safety_retrieval


class DefaultSafetyChecker:
    """Safety checker using default preloaded manuals"""
    
    def __init__(self):
        self.perplexity = perplexity_client
        self.retrieval = default_safety_retrieval
    
    async def check_code_safety(self, code: Dict) -> Dict:
        """
        Check generated code against default safety manuals
        
        Args:
            code: Generated code dict
        
        Returns:
            Safety check result
        """
        # Load default safety manual
        loaded = self.retrieval.load_default_safety_manual()
        
        if not loaded:
            return {
                "success": False,
                "error": "No default safety manuals found. Please add safety manuals to data/manuals/user_safety_manuals/"
            }
        
        # Get relevant safety rules
        code_text = code.get('program_body', '')
        safety_context = self.retrieval.retrieve_context(code_text, max_chunks=5)
        
        # Get metadata
        metadata = self.retrieval.get_metadata()
        
        # Build safety check prompt
        system_prompt = self._build_safety_check_prompt()
        user_request = self._build_check_request(code, safety_context, metadata)
        
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
        check_text = self.perplexity.extract_response_text(response)
        result = self._parse_check_result(check_text)
        
        # Add metadata
        result["manuals_used"] = metadata.get("manual_sources", [])
        result["total_manuals"] = metadata.get("total_manuals", 0)
        
        return result
    
    def _build_safety_check_prompt(self) -> str:
        """Build system prompt for safety check"""
        return """You are an Industrial Safety Expert specializing in PLC control systems and workplace safety standards.

Your task is to check generated PLC code against industrial safety standards and identify potential safety violations, missing safety checks, and hazards.

Output your assessment in this EXACT format:

==============================
SAFETY CHECK RESULT
==============================
Overall Status: [PASS / WARNING / FAIL]
Risk Level: [LOW / MEDIUM / HIGH / CRITICAL]

==============================
SAFETY STANDARDS COMPLIANCE
==============================
[Analysis of code compliance with safety standards]

==============================
MISSING SAFETY CHECKS
==============================
[List missing safety implementations]
- Missing Check 1: [Description]
- Missing Check 2: [Description]
...

==============================
SAFETY VIOLATIONS FOUND
==============================
[List safety rule violations]
- Violation 1: [Rule + Explanation]
- Violation 2: [Rule + Explanation]
...

==============================
POTENTIAL HAZARDS
==============================
[List potential hazards]
- Hazard 1: [Description + Risk]
- Hazard 2: [Description + Risk]
...

==============================
REQUIRED CORRECTIONS
==============================
[List mandatory safety corrections]
- Correction 1: [What must be fixed]
- Correction 2: [What must be fixed]
...

==============================
SAFETY RECOMMENDATIONS
==============================
[Additional safety improvements]
- Recommendation 1
- Recommendation 2
...

Be thorough and focus on INDUSTRIAL SAFETY. Flag all potential risks."""

    def _build_check_request(self, code: Dict, safety_context: str, metadata: Dict) -> str:
        """Build safety check request"""
        manuals_list = ", ".join(metadata.get("manual_sources", []))
        
        return f"""Perform safety check on this PLC code against industrial safety standards.

=== GENERATED CODE ===
Program Name: {code.get('program_name', 'Unknown')}
Execution Type: {code.get('execution_type', 'Unknown')}

Global Labels:
{self._format_labels(code.get('global_labels', []))}

Local Labels:
{self._format_labels(code.get('local_labels', []))}

Program Body:
{code.get('program_body', '')}

=== APPLICABLE SAFETY STANDARDS ===
Source Manuals: {manuals_list}
Total Manuals: {metadata.get('total_manuals', 0)}

Relevant Safety Rules:
{safety_context}

Perform comprehensive safety check and identify ALL missing safety checks, violations, and hazards."""

    def _format_labels(self, labels: List[Dict]) -> str:
        """Format labels for display"""
        if not labels:
            return "No labels"
        
        lines = []
        for label in labels[:10]:
            lines.append(f"- {label.get('name', 'N/A')}: {label.get('data_type', 'N/A')}")
        
        if len(labels) > 10:
            lines.append(f"... and {len(labels) - 10} more")
        
        return "\n".join(lines)
    
    def _parse_check_result(self, check_text: str) -> Dict:
        """Parse safety check result"""
        result = {
            "success": True,
            "passed": False,
            "status": "FAIL",
            "risk_level": "UNKNOWN",
            "compliance_analysis": "",
            "missing_checks": [],
            "violations": [],
            "hazards": [],
            "required_corrections": [],
            "recommendations": []
        }
        
        # Extract status
        if "Overall Status: PASS" in check_text:
            result["passed"] = True
            result["status"] = "PASS"
        elif "Overall Status: WARNING" in check_text:
            result["passed"] = True
            result["status"] = "WARNING"
        
        # Extract risk level
        if "Risk Level: LOW" in check_text:
            result["risk_level"] = "LOW"
        elif "Risk Level: MEDIUM" in check_text:
            result["risk_level"] = "MEDIUM"
        elif "Risk Level: HIGH" in check_text:
            result["risk_level"] = "HIGH"
        elif "Risk Level: CRITICAL" in check_text:
            result["risk_level"] = "CRITICAL"
        
        # Parse sections
        lines = check_text.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            if 'SAFETY STANDARDS COMPLIANCE' in line:
                current_section = 'compliance'
                section_content = []
            elif 'MISSING SAFETY CHECKS' in line:
                if current_section == 'compliance':
                    result['compliance_analysis'] = '\n'.join(section_content).strip()
                current_section = 'missing'
                section_content = []
            elif 'SAFETY VIOLATIONS' in line:
                if current_section == 'missing':
                    result['missing_checks'] = self._extract_list_items(section_content)
                current_section = 'violations'
                section_content = []
            elif 'POTENTIAL HAZARDS' in line:
                if current_section == 'violations':
                    result['violations'] = self._extract_list_items(section_content)
                current_section = 'hazards'
                section_content = []
            elif 'REQUIRED CORRECTIONS' in line:
                if current_section == 'hazards':
                    result['hazards'] = self._extract_list_items(section_content)
                current_section = 'corrections'
                section_content = []
            elif 'SAFETY RECOMMENDATIONS' in line:
                if current_section == 'corrections':
                    result['required_corrections'] = self._extract_list_items(section_content)
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
default_safety_checker = DefaultSafetyChecker()