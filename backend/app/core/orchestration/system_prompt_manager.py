from pathlib import Path
from typing import Optional
from app.config import settings


class SystemPromptManager:
    def __init__(self):
        self.prompts_path = Path(settings.SYSTEM_PROMPTS_PATH)
    
    def load_prompt(self, agent_name: str, version: str = "current") -> str:
        """
        Load system prompt for an agent
        
        Args:
            agent_name: 'nexus_ai' or 'ai_dude'
            version: Version to load (default: 'current')
        
        Returns:
            System prompt text
        """
        prompt_file = self.prompts_path / agent_name / f"{version}.txt"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def save_prompt(self, agent_name: str, version: str, content: str):
        """
        Save system prompt
        
        Args:
            agent_name: 'nexus_ai' or 'ai_dude'
            version: Version name
            content: Prompt content
        """
        agent_dir = self.prompts_path / agent_name
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        prompt_file = agent_dir / f"{version}.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def get_nexus_prompt(self) -> str:
        """Get current Nexus AI prompt"""
        return self.load_prompt("nexus_ai", "current")
    
    def get_aidude_prompt(self) -> str:
        """Get current AI Dude prompt"""
        return self.load_prompt("ai_dude", "current")


# Global instance
prompt_manager = SystemPromptManager()