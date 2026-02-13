from typing import Dict
from app.core.planner.process_flow_analyzer import flow_analyzer
from app.core.planner.stage_segregator import StageSegregator
from app.core.planner.dependency_mapper import dependency_mapper


class PlannerOrchestrator:
    """Main orchestrator for the planning phase"""
    
    def __init__(self):
        self.flow_analyzer = flow_analyzer
        self.stage_segregator = StageSegregator()
        self.dependency_mapper = dependency_mapper
    
    async def create_plan(self, control_logic: str) -> Dict:
        """
        Create complete plan from control logic
        
        Args:
            control_logic: User's control logic description
        
        Returns:
            Complete plan with stages and dependencies
        """
        # Step 1: Validate input
        validation = self._validate_input(control_logic)
        if not validation['valid']:
            return {
                "success": False,
                "error": validation['error']
            }
        
        # Step 2: Analyze control logic
        analysis = self.flow_analyzer.analyze(control_logic)
        
        # Step 3: Segregate into stages
        segregation = await self.stage_segregator.segregate(control_logic, analysis)
        
        # Step 4: Validate dependencies
        dependency_validation = self.dependency_mapper.validate_dependencies(
            segregation['stages'],
            segregation.get('dependencies', [])
        )
        
        # Step 5: Build transition graph
        transition_graph = self.dependency_mapper.build_transition_graph(
            segregation['stages'],
            segregation.get('dependencies', [])
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "stages": segregation['stages'],
            "dependencies": segregation.get('dependencies', []),
            "dependency_validation": dependency_validation,
            "transition_graph": transition_graph,
            "total_stages": len(segregation['stages'])
        }
    
    def _validate_input(self, control_logic: str) -> Dict:
        """Validate input control logic"""
        if not control_logic or not control_logic.strip():
            return {
                "valid": False,
                "error": "Control logic cannot be empty"
            }
        
        word_count = len(control_logic.split())
        
        # Minimum elaboration requirement
        if word_count < 50:
            return {
                "valid": False,
                "error": f"Control logic too brief ({word_count} words). Please provide at least 50 words describing the complete control process."
            }
        
        return {"valid": True}


# Global instance
planner_orchestrator = PlannerOrchestrator()