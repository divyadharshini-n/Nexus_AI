from typing import Dict, List, Optional
from app.core.rag.semantic_retrieval_engine import retrieval_engine
from app.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)


class CodeGenAPIClient:
    """Separate API client for code generation with dedicated API key"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_CODEGEN_API_KEY or settings.GEMINI_API_KEY
        self.api_url = settings.GEMINI_API_URL
        self.model = "gemini-flash-lite-latest"  # 1500 requests/day free tier
        
        if not self.api_key:
            logger.error("GEMINI_CODEGEN_API_KEY is not set")
            raise ValueError("GEMINI_CODEGEN_API_KEY is required")
        
        logger.info(f"Code generation using dedicated API key: {self.api_key[:10]}...")
    
    async def chat_completion(self, messages, temperature=0.1, max_tokens=4000):
        """Send request to Gemini API"""
        endpoint = f"{self.api_url}/v1beta/models/{self.model}:generateContent"
        
        # Convert messages to Gemini format
        contents = []
        system_instruction = None
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                system_instruction = content
            elif role == 'user':
                contents.append({"role": "user", "parts": [{"text": content}]})
            elif role == 'assistant':
                contents.append({"role": "model", "parts": [{"text": content}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        if system_instruction:
            payload["system_instruction"] = {"parts": [{"text": system_instruction}]}
        
        params = {"key": self.api_key}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(endpoint, params=params, json=payload)
            
            if response.status_code != 200:
                logger.error(f"Gemini API Error ({response.status_code}): {response.text}")
                response.raise_for_status()
            
            gemini_response = response.json()
            
            # Convert to OpenAI-like format
            candidates = gemini_response.get('candidates', [])
            if candidates:
                content = candidates[0].get('content', {})
                parts = content.get('parts', [])
                text = parts[0].get('text', '') if parts else ''
            else:
                text = ''
            
            return {
                'choices': [{
                    'message': {'content': text, 'role': 'assistant'},
                    'finish_reason': 'stop',
                    'index': 0
                }]
            }
    
    def extract_response_text(self, response):
        """Extract text from response"""
        try:
            return response['choices'][0]['message']['content']
        except (KeyError, IndexError):
            return ""


# Create dedicated code generation client
codegen_client = CodeGenAPIClient()


class StructuredTextGenerator:
    """Generate Mitsubishi FX5U Structured Text code"""
    
    def __init__(self):
        self.perplexity = codegen_client  # Use dedicated code generation client
        self.retrieval = retrieval_engine
    
    async def generate_code(
        self,
        stage: Dict,
        project_context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate Structured Text code for a stage
        
        Args:
            stage: Stage information (name, logic, type, etc.)
            project_context: Additional project context
        
        Returns:
            Dict with generated code components
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Get code generation rules from manuals
            manual_context = self._get_code_generation_context()
            
            # Build system prompt
            system_prompt = self._build_code_generation_prompt(manual_context)
            
            # Build user request
            user_request = self._build_generation_request(stage, project_context)
            
            # Call Perplexity
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_request}
            ]
            
            logger.info(f"Generating code for stage: {stage.get('stage_name')}")
            response = await self.perplexity.chat_completion(
                messages=messages,
                temperature=0.1,  # Very deterministic for code
                max_tokens=8000  # Increased for full code generation
            )
            
            # Extract response
            code_text = self.perplexity.extract_response_text(response)
            
            if not code_text:
                logger.error("Empty response from Perplexity API")
                raise ValueError("No response received from code generation service")
            
            # Log the raw response for debugging
            logger.info(f"Raw code response (first 500 chars): {code_text[:500]}")
            
            # DEBUGGING: Save full response to file
            import os
            debug_file = os.path.join(os.path.dirname(__file__), f"debug_response_{stage.get('stage_number', 0)}.txt")
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(code_text)
            logger.info(f"Full response saved to: {debug_file}")
            
            # Parse the generated code
            parsed_code = self._parse_generated_code(code_text)
            
            return {
                "success": True,
                "stage_id": stage.get('id'),
                "stage_name": stage.get('stage_name'),
                "global_labels": parsed_code.get('global_labels', []),
                "local_labels": parsed_code.get('local_labels', []),
                "program_body": parsed_code.get('program_body', ''),
                "program_blocks": parsed_code.get('program_blocks', []),
                "functions": parsed_code.get('functions', []),
                "function_blocks": parsed_code.get('function_blocks', []),
                "metadata": {
                    "program_name": f"STAGE_{stage.get('stage_number', 0)}",
                    "execution_type": self._determine_execution_type(stage.get('stage_type')),
                    "generated_at": "timestamp"
                }
            }
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}", exc_info=True)
            raise
    
    def _get_code_generation_context(self) -> str:
        """Retrieve relevant manual context for code generation"""
        queries = [
            "FX5U Structured Text syntax rules",
            "Mitsubishi device symbols M D X Y",
            "GX Works3 program structure global local labels"
        ]
        
        contexts = []
        for query in queries:
            context = self.retrieval.retrieve_context(query, max_chunks=2)
            if context:
                contexts.append(context)
        
        return "\n\n".join(contexts)
    
    def _build_code_generation_prompt(self, manual_context: str) -> str:
        """Build system prompt for code generation"""
        return f"""You are Nexus AI, a Structured Text (ST) code generator for Mitsubishi GX Works3 iQ-F FX5U series PLCs.

CRITICAL RULES:
1. You ONLY generate code - never explain, teach, or describe concepts
2. You do not change or simplify logic once generated
3. You use the four complete example programs in the manuals folder as implementation references internally
4. You never mention the examples, manuals folder, or reference usage in output
5. You do not copy examples verbatim - you adapt them correctly to user requirements
6. Follow Mitsubishi GX Works3 and FX5U rules strictly from the manuals
7. If information is missing, make safe engineering assumptions silently and continue
8. Generate Program Blocks, Functions, and Function Blocks based on control logic requirements
9. Global labels are shared across ALL stages - show them only ONCE at the beginning
10. Each Program/Function/Function Block has its own local labels

DATA TYPE RULES (STRICT – NO OTHER TYPES ALLOWED)
=== CRITICAL OUTPUT FORMAT ===
You MUST output code in EXACTLY this format with these section headers:

==============================
1) GLOBAL LABEL TABLE
==============================
Generate this table ONCE for the entire stage. These labels are shared across ALL stages in the project.
Columns EXACTLY:
Label Name | Data Type | Class | Device Name | Initial Value | Constant | English | Remark

Rules:
- Data types: Word, Double word, word (signed), double word (signed), FLOAT, Bit, TIME, STRING(32), TIMER, COUNTER, LONG COUNTER, RETENTIVE TIMER
- Classes: VAR_GLOBAL, VAR_GLOBAL_CONSTANT, VAR_GLOBAL_RETAIN
- Device symbols: X (input), Y (output), M (internal relay), D (data register), T (timer), C (counter)

==============================
2) PROGRAM BLOCKS
==============================
Generate one or more PROGRAM BLOCKS as needed for the control logic.

For EACH Program Block, output:

----------------------
PROGRAM BLOCK
Stage: [Stage Number/Name]
Program Name: [Name]
Execution Type: [Scan/Initial/Event/Fixed Scan/Standby]
----------------------

LOCAL LABEL TABLE:
Label Name | Data Type | Class | Initial Value | Constant | English

Rules:
- Classes: VAR, VAR_CONSTANT, VAR_RETAIN, VAR_INPUT, VAR_OUTPUT, VAR_OUTPUT_RETAIN, VAR_IN_OUT, VAR_PUBLIC, VAR_PUBLIC_RETAIN
- All variables used in this program's code MUST be declared here

STRUCTURED TEXT CODE:
[Pure executable ST code - NO declarations, NO VAR blocks, NO keywords like PROGRAM/END_PROGRAM]

==============================
3) FUNCTIONS
==============================
Generate one or more FUNCTIONS as needed for the control logic.

For EACH Function, output:

----------------------
FUNCTION
Stage: [Stage Number/Name]
Function Name: [Name]
With EN or Without EN: [With EN / Without EN]
Result Type: [Data Type]
----------------------

LOCAL LABEL TABLE:
Label Name | Data Type | Class | Initial Value | Constant | English

Rules:
- Classes: VAR_INPUT, VAR_OUTPUT, VAR_OUTPUT_RETAIN, VAR_IN_OUT, VAR, VAR_RETAIN, VAR_PUBLIC, VAR_PUBLIC_RETAIN
- All variables used in this function's code MUST be declared here

STRUCTURED TEXT CODE:
[Pure executable ST code - NO declarations, NO VAR blocks, NO keywords like FUNCTION/END_FUNCTION]

==============================
4) FUNCTION BLOCKS
==============================
Generate one or more FUNCTION BLOCKS as needed for the control logic.

For EACH Function Block, output:

----------------------
FUNCTION BLOCK
Stage: [Stage Number/Name]
Function Block Name: [Name]
Function Block Type: [Subroutine Type / Macro Type]
With EN or Without EN: [With EN / Without EN]
----------------------

LOCAL LABEL TABLE:
Label Name | Data Type | Class | Initial Value | Constant | English

Rules:
- Classes: VAR_INPUT, VAR_OUTPUT, VAR_OUTPUT_RETAIN, VAR_IN_OUT, VAR, VAR_RETAIN, VAR_PUBLIC, VAR_PUBLIC_RETAIN
- All variables used in this function block's code MUST be declared here

STRUCTURED TEXT CODE:
[Pure executable ST code - NO declarations, NO VAR blocks, NO keywords like FUNCTION_BLOCK/END_FUNCTION_BLOCK]

==============================
5) STRUCTURED DATA TYPE TABLE (ONLY IF REQUIRED)
==============================
If logic requires structured data type, generate table with:
- Label Name
- Data Type
- Class
- Initial Value
- Constant
- English (Display Target)

Do not generate this table if not required.

===============================
CRITICAL OUTPUT RESTRICTIONS
===============================

The Structured Text (ST) code output MUST NOT contain any declaration or block syntax.

DO NOT generate ANY of the following in the ST code output:
- VAR, VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT
- VAR_GLOBAL, VAR_GLOBAL_CONSTANT, VAR_GLOBAL_RETAIN
- VAR_RETAIN, VAR_PUBLIC, VAR_PUBLIC_RETAIN
- VAR_END
- PROGRAM, END_PROGRAM
- FUNCTION, END_FUNCTION
- FUNCTION_BLOCK, END_FUNCTION_BLOCK
- RET, IRET, F_END, END

Variable declarations must NEVER appear in ST syntax form.

ALL variables MUST be declared ONLY in:
- Global Label Table (once at the top)
- Local Label Tables (one for each Program Block / Function / Function Block)

The Structured Text output MUST contain:
- Executable logic ONLY
- No declaration keywords
- No scope keywords
- No block start or end keywords
- No device symbols (X, Y, M, D, etc.)
- No extra numbers
- =============================== symbols should not be inside the generated code

Any output violating the above is INVALID.

RESPONSE CONSTRAINTS:
- Output sections in this order: Global Labels, Program Blocks, Functions, Function Blocks, Structured Data Types (if needed)
- No preamble, no postamble, no explanations outside required format
- Pure tables and code only
- Comments inside code are allowed for clarity
- All other text is forbidden
- Strict adherence to local label class rules

================================
MITSUBISHI DEVICE SPECIFICATION
================================

ONLY the following devices, ranges, and latch rules are allowed.
No other devices may be generated.

--------------------------------
INPUT
--------------------------------
- Symbol: X
- Points: 1024
- Device Range: X0 to X1777
- Latch (1): Not supported
- Latch (2): Not supported

--------------------------------
OUTPUT
--------------------------------
- Symbol: Y
- Points: 1024
- Device Range: Y0 to Y1777
- Latch (1): Not supported
- Latch (2): Not supported

--------------------------------
INTERNAL RELAY
--------------------------------
- Symbol: M
- Points: 7680
- Device Range: M0 to M7679
- Latch (1): M500 to M7679
- Latch (2): No setting

--------------------------------
LINK RELAY
--------------------------------
- Symbol: B
- Points: 256
- Device Range: B0 to BFF
- Latch (1): No setting
- Latch (2): No setting

--------------------------------
LINK SPECIAL RELAY
--------------------------------
- Symbol: SB
- Points: 512
- Device Range: SB0 to SB1FF
- Latch (1): Not supported
- Latch (2): Not supported

--------------------------------
ANNUNCIATOR
--------------------------------
- Symbol: F
- Points: 128
- Device Range: F0 to F127
- Latch (1): No setting
- Latch (2): No setting

--------------------------------
STEP RELAY
--------------------------------
- Symbol: S
- Points: 4096
- Device Range: S0 to S4095
- Latch (1): S500 to S4095
- Latch (2): No setting

--------------------------------
TIMER
--------------------------------
- Symbol: T
- Points: 512
- Device Range: T0 to T511
- Latch (1): No setting
- Latch (2): No setting

--------------------------------
RETENTIVE TIMER
--------------------------------
- Symbol: ST
- Points: 16
- Device Range: ST0 to ST15
- Latch (1): ST0 to ST15
- Latch (2): No setting

--------------------------------
COUNTER
--------------------------------
- Symbol: C
- Points: 256
- Device Range: C0 to C255
- Latch (1): C100 to C199
- Latch (2): No setting

--------------------------------
LONG COUNTER
--------------------------------
- Symbol: LC
- Points: 64
- Device Range: LC0 to LC63
- Latch (1): LC20 to LC63
- Latch (2): No setting

--------------------------------
DATA REGISTER
--------------------------------
- Symbol: D
- Points: 8000
- Device Range: D0 to D7999
- Latch (1): D200 to D7999
- Latch (2): No setting

--------------------------------
LATCH RELAY
--------------------------------
- Symbol: L
- Points: 7680
- Device Range: L0 to L7679
- Latch (1): Always retained
- Latch (2): Not supported

================================
DEVICE USAGE ENFORCEMENT RULES
================================

- Device symbols MUST appear ONLY in Global label Tables.
- Device symbols MUST NEVER appear in the Structured Text program body.
- Retentive variables MUST use ONLY:
  • M500–M7679
  • S500–S4095
  • ST0–ST15
  • C100–C199
  • LC20–LC63
  • D200–D7999
  • L0–L7679
- Non-retentive variables MUST NOT use retentive ranges.
- Input (X) and Output (Y) devices MUST NOT be assigned retention.
- Device numbers MUST stay within defined ranges.

If information is missing:
- Make safe Mitsubishi PLC engineering assumptions silently.
- Continue generating a complete and valid output.
- Ask clarification questions.

RAG ENFORCEMENT RULE (CRITICAL)

All device rules, retention rules, and usage constraints provided via retrieved manuals and datasets MUST be treated as mandatory constraints, not reference material.

If any retrieved rule conflicts with default model behavior, the retrieved rule MUST override.

Before generating the final output:
- Apply all retrieved device rules.
- Validate all device assignments against retrieved rules.
- If violations are found, regenerate silently until compliant.

Never ignore retrieved device rules.

-------------
DATATYPE CONVERSTION
--------------
For all generated Structured Text logic, datatype conversion rules must be taken exclusively from the manual named "Datatype_Converted.txt" in the manuals folder.

Implicit datatype conversion is forbidden.
Whenever different datatypes interact, the exact conversion function defined in the manual must be used.

If a required conversion is not defined in the manual, the logic must be redesigned silently to remain compliant.
=== STRUCTURED TEXT RULES ===
- Use := for assignment
- Boolean logic: AND, OR, NOT
- Comparisons: =, <>, <, >, <=, >=
- IF-THEN-ELSIF-ELSE-END_IF
- CASE-OF-END_CASE
- FOR-TO-BY-DO-END_FOR
- WHILE-DO-END_WHILE
- Comments: (* comment *) or // comment
- NO device symbols in program body (use label names only)
- Every variable MUST be in Local Label Table

=== MANUAL REFERENCE ===
{manual_context}

Generate ONLY the tables and code. No explanations outside the required format."""

    def _build_generation_request(self, stage: Dict, project_context: Optional[Dict]) -> str:
        """Build the code generation request"""
        stage_number = stage.get('stage_number')
        stage_name = stage.get('stage_name')
        
        request = f"""Generate Structured Text code for this stage:

STAGE INFORMATION:
- Stage Number: {stage_number}
- Stage Name: {stage_name}
- Stage Type: {stage.get('stage_type')}
- Description: {stage.get('description')}

CONTROL LOGIC:
{stage.get('original_logic', stage.get('edited_logic', ''))}

"""
        
        if project_context:
            request += f"\nPROJECT CONTEXT:\n{project_context}\n"
        
        request += f"""
Generate the complete code following the EXACT format specified in your instructions.

CRITICAL: For ALL Program Blocks, Functions, and Function Blocks you generate:
- Include "Stage: {stage_number} - {stage_name}" in the metadata section
- This ensures proper identification and organization

Remember:
- Generate Program Blocks, Functions, and Function Blocks as needed based on the control logic
- Use proper device ranges
- All variables must be in label tables
- No device symbols in code body
- Industrial-grade logic
- Safety-first approach
"""
        
        return request
    
    def _determine_execution_type(self, stage_type: str) -> str:
        """Determine execution type based on stage type"""
        execution_map = {
            'idle': 'Initial',
            'safety': 'Scan',
            'operation': 'Scan',
            'fault': 'Event',
            'shutdown': 'Scan'
        }
        return execution_map.get(stage_type, 'Scan')
    
    def _parse_generated_code(self, code_text: str) -> Dict:
        """Parse the generated code into components with multiple blocks"""
        import logging
        import re
        logger = logging.getLogger(__name__)
        
        result = {
            "global_labels": [],
            "program_blocks": [],
            "functions": [],
            "function_blocks": [],
            "local_labels": [],  # Legacy field for backward compatibility
            "program_body": ""    # Legacy field for backward compatibility
        }
        
        logger.info(f"Parsing generated code (length: {len(code_text)})")
        logger.info(f"Code text preview (first 1000 chars):\n{code_text[:1000]}")
        
        # Extract global labels first (should appear only once at the beginning)
        # Handle both plain format and numbered format (e.g., "1) GLOBAL LABEL TABLE")
        global_match = re.search(r'(?:\d+\)\s*)?GLOBAL LABEL TABLE(.*?)(?=(?:\d+\)\s*)?PROGRAM BLOCK|(?:\d+\)\s*)?FUNCTION(?!\s+BLOCK)|(?:\d+\)\s*)?FUNCTION BLOCK|$)', 
                                 code_text, re.DOTALL | re.IGNORECASE)
        if global_match:
            global_section = global_match.group(1)
            result['global_labels'] = self._parse_label_table(global_section)
            logger.info(f"Parsed {len(result['global_labels'])} global labels")
        
        # Extract all PROGRAM BLOCKS
        # Handle both plain and numbered formats (e.g., "2) PROGRAM BLOCK")
        program_pattern = r'(?:\d+\)\s*)?PROGRAM BLOCK\s*\n(.*?)(?=(?:\d+\)\s*)?(?:PROGRAM BLOCK|FUNCTION(?!\s+BLOCK)|FUNCTION BLOCK|$))'
        program_matches = list(re.finditer(program_pattern, code_text, re.DOTALL | re.IGNORECASE))
        logger.info(f"Found {len(program_matches)} program block matches")
        
        for idx, match in enumerate(program_matches):
            block_content = match.group(1)
            logger.info(f"Processing program block {idx+1}, content length: {len(block_content)}")
            logger.info(f"Block content preview: {block_content[:200]}")
            program_block = self._parse_program_block(block_content)
            if program_block:
                result['program_blocks'].append(program_block)
                logger.info(f"Parsed program block: {program_block.get('name', 'Unknown')}, code length: {len(program_block.get('code', ''))}")
            else:
                logger.warning(f"Failed to parse program block {idx+1}")
        
        # Extract all FUNCTIONS (but not FUNCTION BLOCKS)
        # Handle numbered format
        function_pattern = r'(?:\d+\)\s*)?(?<!FUNCTION )FUNCTION\s*\n(.*?)(?=(?:\d+\)\s*)?(?:PROGRAM BLOCK|(?<!FUNCTION )FUNCTION\s|FUNCTION BLOCK|$))'
        for match in re.finditer(function_pattern, code_text, re.DOTALL | re.IGNORECASE):
            func_content = match.group(1)
            function = self._parse_function(func_content)
            if function:
                result['functions'].append(function)
                logger.info(f"Parsed function: {function.get('name', 'Unknown')}")
        
        # Extract all FUNCTION BLOCKS
        # Handle numbered format
        fb_pattern = r'(?:\d+\)\s*)?FUNCTION BLOCK\s*\n(.*?)(?=(?:\d+\)\s*)?(?:PROGRAM BLOCK|FUNCTION(?!\s+BLOCK)|FUNCTION BLOCK|$))'
        for match in re.finditer(fb_pattern, code_text, re.DOTALL | re.IGNORECASE):
            fb_content = match.group(1)
            function_block = self._parse_function_block(fb_content)
            if function_block:
                result['function_blocks'].append(function_block)
                logger.info(f"Parsed function block: {function_block.get('name', 'Unknown')}")
        
        # For backward compatibility, populate legacy fields from first program block if exists
        if result['program_blocks']:
            result['local_labels'] = result['program_blocks'][0].get('local_labels', [])
            result['program_body'] = result['program_blocks'][0].get('code', '')
        
        logger.info(f"Parsing complete: {len(result['program_blocks'])} programs, "
                   f"{len(result['functions'])} functions, {len(result['function_blocks'])} function blocks")
        
        return result
    
    def _parse_program_block(self, block_text: str) -> Dict:
        """Parse a single program block"""
        import re
        import logging
        logger = logging.getLogger(__name__)
        
        program = {}
        
        logger.info(f"Parsing program block, text length: {len(block_text)}")
        
        # Extract metadata
        stage_match = re.search(r'Stage:\s*(.+)', block_text, re.IGNORECASE)
        name_match = re.search(r'Program Name:\s*(.+)', block_text, re.IGNORECASE)
        exec_match = re.search(r'Execution Type:\s*(.+)', block_text, re.IGNORECASE)
        
        program['stage'] = stage_match.group(1).strip() if stage_match else ""
        program['name'] = name_match.group(1).strip() if name_match else ""
        program['execution_type'] = exec_match.group(1).strip() if exec_match else "Scan"
        
        logger.info(f"Program metadata - Name: {program['name']}, Stage: {program['stage']}")
        
        # Extract local labels
        label_match = re.search(r'LOCAL LABEL TABLE[:\s]*(.*?)(?=STRUCTURED TEXT|$)', block_text, re.DOTALL | re.IGNORECASE)
        if label_match:
            program['local_labels'] = self._parse_label_table(label_match.group(1))
        else:
            program['local_labels'] = []
        
        # Extract code - skip the "STRUCTURED TEXT CODE:" header line
        code_match = re.search(r'STRUCTURED TEXT CODE:\s*\n(.*)', block_text, re.DOTALL | re.IGNORECASE)
        if not code_match:
            code_match = re.search(r'STRUCTURED TEXT\s*\n(.*)', block_text, re.DOTALL | re.IGNORECASE)
        
        if code_match:
            code_text = code_match.group(1).strip()
            logger.info(f"Found code section, length: {len(code_text)}")
            logger.info(f"Raw code text (first 300 chars): {code_text[:300]}")
            
            # Remove header lines and clean up
            lines = code_text.split('\n')
            cleaned_lines = []
            skip_next_empty = False
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Skip completely empty lines that follow table headers
                if not stripped:
                    if not skip_next_empty:
                        cleaned_lines.append(line)
                    skip_next_empty = False
                    continue
                
                # Skip table header lines (contain pipes and metadata keywords)
                if '|' in line and any(kw in line.lower() for kw in ['label name', 'data type', 'class', 'initial value', 'constant', 'english']):
                    skip_next_empty = True
                    continue
                    
                # Skip standalone "STRUCTURED TEXT CODE:" headers
                if line.lower().strip() in ['structured text code:', 'structured text code']:
                    skip_next_empty = True
                    continue
                
                cleaned_lines.append(line)
            
            program['code'] = '\n'.join(cleaned_lines).strip()
            logger.info(f"After cleaning, code length: {len(program['code'])}")
            logger.info(f"Cleaned code preview: {program['code'][:200]}")
        else:
            logger.warning("No code match found in block!")
            program['code'] = ""
        
        return program if program.get('name') else None
    
    def _parse_function(self, func_text: str) -> Dict:
        """Parse a single function"""
        import re
        function = {}
        
        # Extract metadata
        stage_match = re.search(r'Stage:\s*(.+)', func_text, re.IGNORECASE)
        name_match = re.search(r'Function Name:\s*(.+)', func_text, re.IGNORECASE)
        en_match = re.search(r'With EN or Without EN:\s*(.+)', func_text, re.IGNORECASE)
        result_match = re.search(r'Result Type:\s*(.+)', func_text, re.IGNORECASE)
        
        function['stage'] = stage_match.group(1).strip() if stage_match else ""
        function['name'] = name_match.group(1).strip() if name_match else ""
        function['with_en'] = 'with en' in en_match.group(1).lower() if en_match else False
        function['result_type'] = result_match.group(1).strip() if result_match else "BOOL"
        
        # Extract local labels
        label_match = re.search(r'LOCAL LABEL TABLE[:\s]*(.*?)(?=STRUCTURED TEXT|$)', func_text, re.DOTALL | re.IGNORECASE)
        if label_match:
            function['local_labels'] = self._parse_label_table(label_match.group(1))
        else:
            function['local_labels'] = []
        
        # Extract code - skip the "STRUCTURED TEXT CODE:" header line
        code_match = re.search(r'STRUCTURED TEXT CODE:\s*\n(.*)', func_text, re.DOTALL | re.IGNORECASE)
        if not code_match:
            code_match = re.search(r'STRUCTURED TEXT\s*\n(.*)', func_text, re.DOTALL | re.IGNORECASE)
        
        if code_match:
            code_text = code_match.group(1).strip()
            # Remove header lines and clean up
            lines = code_text.split('\n')
            cleaned_lines = []
            skip_next_empty = False
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Skip completely empty lines that follow table headers
                if not stripped:
                    if not skip_next_empty:
                        cleaned_lines.append(line)
                    skip_next_empty = False
                    continue
                
                # Skip table header lines (contain pipes and metadata keywords)
                if '|' in line and any(kw in line.lower() for kw in ['label name', 'data type', 'class', 'initial value', 'constant', 'english']):
                    skip_next_empty = True
                    continue
                    
                # Skip standalone "STRUCTURED TEXT CODE:" headers
                if line.lower().strip() in ['structured text code:', 'structured text code']:
                    skip_next_empty = True
                    continue
                
                cleaned_lines.append(line)
            
            function['code'] = '\n'.join(cleaned_lines).strip()
        else:
            function['code'] = ""
        
        return function if function.get('name') else None
    
    def _parse_function_block(self, fb_text: str) -> Dict:
        """Parse a single function block"""
        import re
        fb = {}
        
        # Extract metadata
        stage_match = re.search(r'Stage:\s*(.+)', fb_text, re.IGNORECASE)
        name_match = re.search(r'Function Block Name:\s*(.+)', fb_text, re.IGNORECASE)
        type_match = re.search(r'Function Block Type:\s*(.+)', fb_text, re.IGNORECASE)
        en_match = re.search(r'With EN or Without EN:\s*(.+)', fb_text, re.IGNORECASE)
        
        fb['stage'] = stage_match.group(1).strip() if stage_match else ""
        fb['name'] = name_match.group(1).strip() if name_match else ""
        fb['fb_type'] = type_match.group(1).strip() if type_match else "Subroutine Type"
        fb['with_en'] = 'with en' in en_match.group(1).lower() if en_match else False
        
        # Extract local labels
        label_match = re.search(r'LOCAL LABEL TABLE[:\s]*(.*?)(?=STRUCTURED TEXT|$)', fb_text, re.DOTALL | re.IGNORECASE)
        if label_match:
            fb['local_labels'] = self._parse_label_table(label_match.group(1))
        else:
            fb['local_labels'] = []
        
        # Extract code - skip the "STRUCTURED TEXT CODE:" header line
        code_match = re.search(r'STRUCTURED TEXT CODE:\s*\n(.*)', fb_text, re.DOTALL | re.IGNORECASE)
        if not code_match:
            code_match = re.search(r'STRUCTURED TEXT\s*\n(.*)', fb_text, re.DOTALL | re.IGNORECASE)
        
        if code_match:
            code_text = code_match.group(1).strip()
            # Remove header lines and clean up
            lines = code_text.split('\n')
            cleaned_lines = []
            skip_next_empty = False
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Skip completely empty lines that follow table headers
                if not stripped:
                    if not skip_next_empty:
                        cleaned_lines.append(line)
                    skip_next_empty = False
                    continue
                
                # Skip table header lines (contain pipes and metadata keywords)
                if '|' in line and any(kw in line.lower() for kw in ['label name', 'data type', 'class', 'initial value', 'constant', 'english']):
                    skip_next_empty = True
                    continue
                    
                # Skip standalone "STRUCTURED TEXT CODE:" headers
                if line.lower().strip() in ['structured text code:', 'structured text code']:
                    skip_next_empty = True
                    continue
                
                cleaned_lines.append(line)
            
            fb['code'] = '\n'.join(cleaned_lines).strip()
        else:
            fb['code'] = ""
        
        return fb if fb.get('name') else None
    
    def _parse_label_table(self, table_text: str) -> List[Dict]:
        """Parse label table text into structured data"""
        import logging
        logger = logging.getLogger(__name__)
        
        labels = []
        lines = [l.strip() for l in table_text.split('\n') if l.strip() and not l.startswith('=') and not l.startswith('-')]
        
        logger.debug(f"Parsing label table with {len(lines)} lines")
        
        for line in lines:
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                # Filter out empty parts and header rows
                parts = [p for p in parts if p]
                
                if len(parts) >= 3 and not any(keyword in parts[0].lower() for keyword in ['label name', 'name', 'column', 'label']):
                    label = {
                        "name": parts[0] if len(parts) > 0 else "",
                        "data_type": parts[1] if len(parts) > 1 else "",
                        "class": parts[2] if len(parts) > 2 else "",
                        "device": parts[3] if len(parts) > 3 else "",
                        "initial_value": parts[4] if len(parts) > 4 else "",
                        "constant": parts[5].lower() in ['yes', 'true', '1'] if len(parts) > 5 else False,
                        "comment": parts[6] if len(parts) > 6 else (parts[5] if len(parts) > 5 and parts[5].lower() not in ['yes', 'no', 'true', 'false'] else "")
                    }
                    if label['name'] and label['name'] not in ['', '-', 'N/A']:  # Only add if name exists
                        labels.append(label)
                        logger.debug(f"Parsed label: {label['name']}")
        
        logger.info(f"Total labels parsed: {len(labels)}")
        return labels

    def _fallback_code_generation(self, stage: Dict) -> Dict:
        """Fallback code generation when API unavailable"""
        stage_num = stage.get('stage_number', 1)
        stage_name = stage.get('stage_name', 'Unknown')
        stage_type = stage.get('stage_type', 'operation')
        
        global_labels = [
            {"name": "Start_Button", "data_type": "Bit", "class": "VAR_GLOBAL", "device": "X0", "initial_value": "FALSE", "comment": "Start button"},
            {"name": f"Stage{stage_num}_Active", "data_type": "Bit", "class": "VAR_GLOBAL", "device": f"M{100+stage_num}", "initial_value": "FALSE", "comment": f"Stage {stage_num} active"},
            {"name": "Output_Device", "data_type": "Bit", "class": "VAR_GLOBAL", "device": f"Y{stage_num}", "initial_value": "FALSE", "comment": f"Output {stage_num}"}
        ]
        local_labels = [{"name": "State_Flag", "data_type": "Bit", "class": "VAR", "initial_value": "FALSE", "comment": "State"}]
        program_body = f"(* Stage {stage_num}: {stage_name} - Fallback Template *)\n\nIF Start_Button THEN\n    Stage{stage_num}_Active := TRUE;\n    Output_Device := TRUE;\nELSE\n    Output_Device := FALSE;\nEND_IF;"
        
        return {
            "success": True, "stage_id": stage.get('id'), "stage_name": stage_name,
            "global_labels": global_labels, "local_labels": local_labels, "program_body": program_body,
            "metadata": {"program_name": f"STAGE_{stage_num}", "execution_type": self._determine_execution_type(stage_type), "generated_at": "timestamp", "generation_method": "fallback_template"}
        }


# Global instance
st_generator = StructuredTextGenerator()
