from typing import List, Dict


class DependencyMapper:
    """Maps dependencies between stages"""
    
    def validate_dependencies(self, stages: List[Dict], dependencies: List[Dict]) -> Dict:
        """
        Validate stage dependencies
        
        Returns:
            Dict with validation results and warnings
        """
        warnings = []
        errors = []
        
        # Check all stages are referenced
        stage_numbers = [s['stage_number'] for s in stages]
        
        for dep in dependencies:
            from_stage = dep['from_stage']
            to_stage = dep['to_stage']
            
            if from_stage not in stage_numbers:
                errors.append(f"Dependency references non-existent stage: {from_stage}")
            
            if to_stage not in stage_numbers:
                errors.append(f"Dependency references non-existent stage: {to_stage}")
            
            if from_stage >= to_stage:
                warnings.append(f"Backwards dependency: Stage {from_stage} → {to_stage}")
        
        # Check for unreachable stages
        reachable_stages = {0}  # Stage 0 is always reachable
        for dep in dependencies:
            if dep['from_stage'] in reachable_stages:
                reachable_stages.add(dep['to_stage'])
        
        for stage_num in stage_numbers:
            if stage_num not in reachable_stages and stage_num != 0:
                warnings.append(f"Stage {stage_num} may be unreachable")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def build_transition_graph(self, stages: List[Dict], dependencies: List[Dict]) -> Dict:
        """Build transition graph for visualization"""
        graph = {
            "nodes": [],
            "edges": []
        }
        
        # Add nodes
        for stage in stages:
            graph["nodes"].append({
                "id": stage['stage_number'],
                "label": stage['stage_name'],
                "type": stage['stage_type']
            })
        
        # Add edges
        for dep in dependencies:
            graph["edges"].append({
                "from": dep['from_stage'],
                "to": dep['to_stage'],
                "label": dep.get('condition', '')
            })
        
        return graph


# Global instance
dependency_mapper = DependencyMapper()