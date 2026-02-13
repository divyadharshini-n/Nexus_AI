from typing import Dict, List
import re


class ProcessFlowAnalyzer:
    """Analyzes control logic to understand process flow"""
    
    def __init__(self):
        self.flow_keywords = {
            'start': ['start', 'begin', 'initialize', 'init', 'startup'],
            'stop': ['stop', 'end', 'shutdown', 'halt', 'terminate'],
            'emergency': ['emergency', 'e-stop', 'estop', 'abort', 'panic'],
            'safety': ['safety', 'interlock', 'guard', 'protect', 'secure'],
            'sensor': ['sensor', 'detect', 'check', 'verify', 'confirm'],
            'actuator': ['motor', 'valve', 'cylinder', 'conveyor', 'pump', 'heater'],
            'condition': ['if', 'when', 'while', 'until', 'after', 'before'],
            'sequence': ['then', 'next', 'after', 'following', 'subsequently']
        }
    
    def analyze(self, control_logic: str) -> Dict:
        """
        Analyze control logic text
        
        Returns:
            Dict with analysis results
        """
        analysis = {
            'has_start_logic': self._detect_keywords(control_logic, self.flow_keywords['start']),
            'has_stop_logic': self._detect_keywords(control_logic, self.flow_keywords['stop']),
            'has_emergency_logic': self._detect_keywords(control_logic, self.flow_keywords['emergency']),
            'has_safety_logic': self._detect_keywords(control_logic, self.flow_keywords['safety']),
            'detected_sensors': self._extract_devices(control_logic, 'sensor'),
            'detected_actuators': self._extract_devices(control_logic, 'actuator'),
            'has_conditions': self._detect_keywords(control_logic, self.flow_keywords['condition']),
            'has_sequence': self._detect_keywords(control_logic, self.flow_keywords['sequence']),
            'complexity_score': self._calculate_complexity(control_logic),
            'word_count': len(control_logic.split()),
            'line_count': len(control_logic.split('\n'))
        }
        
        return analysis
    
    def _detect_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if any keyword exists in text"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)
    
    def _extract_devices(self, text: str, device_type: str) -> List[str]:
        """Extract device mentions from text"""
        devices = []
        keywords = self.flow_keywords.get(device_type, [])
        
        for keyword in keywords:
            pattern = r'\b' + keyword + r'\w*\b'
            matches = re.findall(pattern, text.lower())
            devices.extend(matches)
        
        return list(set(devices))  # Remove duplicates
    
    def _calculate_complexity(self, text: str) -> int:
        """Calculate complexity score based on various factors"""
        score = 0
        
        # More words = more complex
        word_count = len(text.split())
        score += min(word_count // 50, 5)  # Max 5 points
        
        # More conditions = more complex
        condition_count = sum(1 for kw in self.flow_keywords['condition'] if kw in text.lower())
        score += min(condition_count, 5)  # Max 5 points
        
        # More devices = more complex
        actuator_count = len(self._extract_devices(text, 'actuator'))
        score += min(actuator_count, 5)  # Max 5 points
        
        return score


# Global instance
flow_analyzer = ProcessFlowAnalyzer()