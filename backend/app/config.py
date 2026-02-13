from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load .env file explicitly
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Get root directory (ai-plc-platform folder)
ROOT_DIR = Path(__file__).parent.parent.parent
# Backend directory
BACKEND_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    ROOT_DIR: str = str(ROOT_DIR)
    # Application
    APP_NAME: str = "AI PLC Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = ""
    
    @property
    def get_database_url(self) -> str:
        """Get absolute database URL to avoid path issues"""
        if self.DATABASE_URL and not self.DATABASE_URL.startswith("sqlite:///./"):
            return self.DATABASE_URL
        # Convert relative SQLite path to absolute
        db_path = BACKEND_DIR / "database" / "plc_platform.db"
        return f"sqlite:///{db_path}"
    MONGODB_URL: Optional[str] = None
    MONGODB_DB_NAME: Optional[str] = "plc_platform"
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Provider API (Google Gemini)
    AI_PROVIDER: str = "gemini"  # Using Google Gemini
    GEMINI_API_KEY: Optional[str] = None  # For AI Dude chatbot
    GEMINI_CODEGEN_API_KEY: Optional[str] = None  # For Code Generation (separate quota)
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com"
    
    # OpenAI
    OPENAI_API_KEY: str
    

    # Voice Recognition
    VOICE_RECOGNITION_SERVICE: str = "google"
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: str = "txt,pdf,docx,doc,wav,mp3"
    
    # Paths - Computed properties
    @property
    def MANUALS_PATH(self) -> str:
        return str(ROOT_DIR / "data" / "manuals")
    
    @property
    def EMBEDDINGS_PATH(self) -> str:
        return str(ROOT_DIR / "data" / "embeddings")
    
    @property
    def UPLOADS_PATH(self) -> str:
        return str(ROOT_DIR / "data" / "uploads")
    
    @property
    def EXPORTS_PATH(self) -> str:
        return str(ROOT_DIR / "data" / "exports")
    
    @property
    def REPORTS_PATH(self) -> str:
        return str(ROOT_DIR / "data" / "reports")
    
    @property
    def SYSTEM_PROMPTS_PATH(self) -> str:
        return str(ROOT_DIR / "data" / "system_prompts")
    
    @property
    def KNOWLEDGE_BASE_PATH(self) -> str:
        return str(ROOT_DIR / "data" / "knowledge_base")
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def LOG_FILE(self) -> str:
        return str(ROOT_DIR / "logs" / "app.log")
    
    class Config:
        env_file = str(env_path)
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()