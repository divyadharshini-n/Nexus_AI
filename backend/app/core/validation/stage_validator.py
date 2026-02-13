from typing import Dict, List
from app.core.ai_agents.shared.perplexity_api_client import perplexity_client
from app.core.rag.semantic_retrieval_engine import retrieval_engine


class StageValidator:
    """Validate stage logic semantically and logically"""
    
    def __init__(self):
        self.perplexity = perplexity_client
        self.retrieval = retrieval_engine
    
    async def validate_stage(self, stage: Dict) -> Dict:
        """
        Validate a stage's logic
        
        Args:
            stage: Stage data with logic
        
        Returns:
            Validation result
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Get validation rules from manuals
            manual_context = self._get_validation_context()
            
            # Build validation prompt
            system_prompt = self._build_validation_prompt(manual_context)
            
            # Build validation request
            user_request = self._build_validation_request(stage)
            
            # Call Perplexity
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_request}
            ]
            
            logger.info(f"Calling Perplexity API for stage validation: {stage.get('stage_name')}")
            response = await self.perplexity.chat_completion(
                messages=messages,
                temperature=0.1,  # Lower temperature for more consistent, less creative validation
                max_tokens=2000
            )
            
            # Parse response
            validation_text = self.perplexity.extract_response_text(response)
            
            if not validation_text:
                logger.error("Empty response from Perplexity API")
                raise ValueError("No response received from validation service")
            
            # Parse validation result
            result = self._parse_validation_result(validation_text)
            logger.info(f"Validation completed for stage {stage.get('stage_name')}: {result['status']}")
            
            return result
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}", exc_info=True)
            raise
    
    def _get_validation_context(self) -> str:
        """Get manual context for validation"""
        queries = [
            "PLC safety requirements interlocks",
            "FX5U device constraints limits",
            "Structured Text programming rules"
        ]
        
        contexts = []
        for query in queries:
            context = self.retrieval.retrieve_context(query, max_chunks=2)
            if context:
                contexts.append(context)
        
        return "\n\n".join(contexts)
    
    def _build_validation_prompt(self, manual_context: str) -> str:
        """Build system prompt for validation"""
        return f"""You are an expert PLC safety and logic validator specializing in Mitsubishi FX5U PLCs.

Your task is to validate stage logic and provide comprehensive feedback in TWO sections:
1. Standard Issues & Recommendations (simple list format)
2. Categorized Issues with Severity Levels (detailed format)

CRITICAL INSTRUCTIONS FOR CONSISTENT VALIDATION:
1. **Be STRICT about CRITICAL issues** - Only mark as CRITICAL if:
   - Safety violation (emergency stop, safety interlocks missing)
   - Logical impossibility (contradictory conditions)
   - Missing mandatory PLC requirements
   
2. **Do NOT hallucinate or create new issues** - Only flag real problems you can clearly identify in the logic

3. **Recognize improvements** - If logic mentions safety features, interlocks, or proper sequencing, acknowledge it positively

4. **Be consistent** - If logic contains proper:
   - Emergency stop handling → Do NOT flag missing emergency stop
   - Safety interlocks → Do NOT flag missing safety
   - State management → Do NOT flag missing state control
   - Alarm handling → Do NOT flag missing alarms

5. **PASS the validation if**:
   - Logic describes clear conditions and actions
   - Basic safety considerations are present
   - No obvious contradictions or safety violations exist

6. **Only FAIL if truly critical issues exist** - Don't fail for minor improvements or suggestions

Output your validation in this EXACT format:

==============================
VALIDATION STATUS
==============================
Status: [PASS / FAIL]
(Use PASS if no CRITICAL issues, FAIL if CRITICAL issues exist)

==============================
ISSUES
==============================
- [List each issue as a simple bullet point]
- [Focus on what's wrong or missing]

==============================
RECOMMENDATIONS
==============================
- [List each recommendation as a simple bullet point]
- [Provide actionable suggestions]

==============================
CATEGORIZED ISSUES
==============================

For each categorized issue, use this format:

[CRITICAL] Issue Title
Description: Brief explanation of the problem
Recommended Logic: 
<Provide ready-made control logic in plain words that user can copy/paste>

**USE MODERATE/OPTIONAL FOR**:
- Performance improvements
- Additional features
- Enhanced monitoring
- Optimization suggestions
- Better practices

**USE CRITICAL ONLY FOR**:
- Safety violations
- Logical contradictions
- Mandatory PLC requirements missing

Example:
[MODERATE] Enhanced Alarm Notification  
Description: Adding comprehensive alarm notifications would improve system monitoring.
Recommended Logic:
If tank level exceeds 90% of maximum capacity, activate high level warning alarm. Send notification to operator panel. Continue normal operation but increase monitoring frequency to every 2 seconds.

==============================
ANALYSIS SUMMARY
==============================
Semantic Analysis: [Brief analysis of logic meaning and clarity]
Logical Consistency: [Check for contradictions, conflicts]
Safety Compliance: [Safety requirements assessment]

=== MANUAL REFERENCE ===
{manual_context}

Remember: 
- Only CRITICAL issues cause validation to FAIL
- Provide complete, copy-paste ready control logic recommendations
- Use plain language, not code or device assignments
- Focus on what the system should DO, not how to configure it technically"""

    def _build_validation_request(self, stage: Dict) -> str:
        """Build validation request"""
        logic = stage.get('edited_logic') or stage.get('original_logic', '')
        
        return f"""Validate this stage logic:

STAGE INFORMATION:
- Stage Number: {stage.get('stage_number')}
- Stage Name: {stage.get('stage_name')}
- Stage Type: {stage.get('stage_type')}

LOGIC TO VALIDATE:
{logic}

Perform complete validation and provide detailed analysis."""

    def _parse_validation_result(self, validation_text: str) -> Dict:
        """Parse validation result with both simple and categorized issues"""
        result = {
            "valid": False,
            "status": "FAIL",
            "semantic_analysis": "",
            "logical_consistency": "",
            "safety_compliance": "",
            "issues": [],  # Simple string list
            "recommendations": [],  # Simple string list
            "categorized_issues": []  # Detailed severity-based issues
        }
        
        # Extract status
        if "Status: PASS" in validation_text:
            result["valid"] = True
            result["status"] = "PASS"
        
        # Parse sections
        lines = validation_text.split('\n')
        current_section = None
        current_issue = None
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Detect sections
            if 'VALIDATION STATUS' in line:
                current_section = 'status'
                continue
            elif line == '==============================':
                continue
            elif 'CATEGORIZED ISSUES' in line:
                current_section = 'categorized'
                continue
            elif line_stripped.startswith('ISSUES') and 'CATEGORIZED' not in line:
                current_section = 'issues'
                continue
            elif 'RECOMMENDATIONS' in line:
                current_section = 'recommendations'
                continue
            elif 'ANALYSIS SUMMARY' in line:
                current_section = 'analysis'
                continue
            
            # Parse simple issues
            if current_section == 'issues' and line_stripped.startswith('-'):
                issue = line_stripped[1:].strip()
                if issue:
                    result['issues'].append(issue)
            
            # Parse simple recommendations
            elif current_section == 'recommendations' and line_stripped.startswith('-'):
                rec = line_stripped[1:].strip()
                if rec:
                    result['recommendations'].append(rec)
            
            # Parse categorized issues
            elif current_section == 'categorized' and line_stripped:
                if line_stripped.startswith('[CRITICAL]'):
                    if current_issue:
                        result['categorized_issues'].append(current_issue)
                    current_issue = {
                        'severity': 'critical',
                        'title': line_stripped.replace('[CRITICAL]', '').strip(),
                        'description': '',
                        'recommended_logic': ''
                    }
                elif line_stripped.startswith('[MODERATE]'):
                    if current_issue:
                        result['categorized_issues'].append(current_issue)
                    current_issue = {
                        'severity': 'moderate',
                        'title': line_stripped.replace('[MODERATE]', '').strip(),
                        'description': '',
                        'recommended_logic': ''
                    }
                elif line_stripped.startswith('[OPTIONAL]'):
                    if current_issue:
                        result['categorized_issues'].append(current_issue)
                    current_issue = {
                        'severity': 'optional',
                        'title': line_stripped.replace('[OPTIONAL]', '').strip(),
                        'description': '',
                        'recommended_logic': ''
                    }
                elif current_issue:
                    if line_stripped.startswith('Description:'):
                        current_issue['description'] = line_stripped.replace('Description:', '').strip()
                    elif line_stripped.startswith('Recommended Logic:'):
                        current_issue['recommended_logic'] = ''
                    elif current_issue.get('description') and not line_stripped.startswith('Recommended Logic:'):
                        if 'recommended_logic' in current_issue:
                            current_issue['recommended_logic'] += line_stripped + ' '
            
            # Parse analysis
            elif current_section == 'analysis' and line_stripped:
                if line_stripped.startswith('Semantic Analysis:'):
                    result['semantic_analysis'] = line_stripped.replace('Semantic Analysis:', '').strip()
                elif line_stripped.startswith('Logical Consistency:'):
                    result['logical_consistency'] = line_stripped.replace('Logical Consistency:', '').strip()
                elif line_stripped.startswith('Safety Compliance:'):
                    result['safety_compliance'] = line_stripped.replace('Safety Compliance:', '').strip()
        
        # Add last categorized issue
        if current_issue:
            result['categorized_issues'].append(current_issue)
        
        # Validation passes only if no CRITICAL categorized issues
        critical_count = sum(1 for issue in result['categorized_issues'] if issue['severity'] == 'critical')
        if critical_count == 0:
            result['valid'] = True
            result['status'] = 'PASS'
        
        return result

    def _fallback_validation(self, stage: Dict) -> Dict:
        """
        Fallback validation logic when API is unavailable
        Performs basic rule-based validation
        """
        logic = stage.get('edited_logic') or stage.get('original_logic', '')
        issues = []
        recommendations = []
        
        # Basic validation checks
        if not logic or len(logic.strip()) < 10:
            issues.append("Logic appears too short or empty")
            recommendations.append("Provide more detailed logic description")
        
        # Check for common safety keywords
        safety_keywords = ['emergency', 'stop', 'safety', 'interlock', 'alarm']
        has_safety = any(keyword in logic.lower() for keyword in safety_keywords)
        
        # Check for basic structure
        has_conditions = any(word in logic.lower() for word in ['if', 'when', 'while', 'condition'])
        has_actions = any(word in logic.lower() for word in ['then', 'set', 'turn', 'activate', 'start'])
        
        semantic_analysis = "Basic structural validation performed. "
        if has_conditions and has_actions:
            semantic_analysis += "Logic contains conditional statements and actions. "
        else:
            semantic_analysis += "Logic may lack proper conditional structure. "
            issues.append("Missing clear conditional logic (if/when/then)")
        
        logical_consistency = "Basic consistency check performed. "
        if len(logic.split()) > 5:
            logical_consistency += "Logic has sufficient detail. "
        else:
            logical_consistency += "Logic may need more detail. "
            recommendations.append("Add more specific details about inputs, conditions, and outputs")
        
        safety_compliance = ""
        if has_safety:
            safety_compliance = "Safety-related keywords detected in logic. "
        else:
            safety_compliance = "No explicit safety keywords found. "
            recommendations.append("Consider adding safety interlocks or emergency stop conditions")
        
        # Determine overall status
        if len(issues) == 0:
            status = "PASS"
            valid = True
            semantic_analysis += "Stage logic appears valid."
        elif len(issues) <= 2:
            status = "WARNING"
            valid = True
            semantic_analysis += "Stage has minor issues but can proceed."
        else:
            status = "FAIL"
            valid = False
            semantic_analysis += "Stage has significant issues that should be addressed."
        
        recommendations.append("Note: Full AI validation unavailable. Basic rule-based validation applied.")
        recommendations.append("Configure Perplexity API key for comprehensive validation.")
        
        return {
            "valid": valid,
            "status": status,
            "semantic_analysis": semantic_analysis,
            "logical_consistency": logical_consistency,
            "safety_compliance": safety_compliance,
            "issues": issues,
            "recommendations": recommendations,
            "categorized_issues": []  # No categorized issues in fallback
        }


# Global instance
stage_validator = StageValidator()