from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class GeneratedCode(Base):
    __tablename__ = "generated_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("stages.id"), nullable=True)
    
    # Code components
    global_labels = Column(JSON, nullable=True)
    local_labels = Column(JSON, nullable=True)
    structured_data_types = Column(JSON, nullable=True)
    program_body = Column(Text, nullable=True)
    
    # New structure for multiple blocks
    program_blocks = Column(JSON, nullable=True)  # Array of program blocks
    functions = Column(JSON, nullable=True)  # Array of functions
    function_blocks = Column(JSON, nullable=True)  # Array of function blocks
    
    # Metadata
    program_name = Column(String(255), nullable=True)
    execution_type = Column(String(100), nullable=True)
    code_metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="generated_codes")
    stage = relationship("Stage", back_populates="generated_codes")
    version_history = relationship("VersionHistory", back_populates="code", cascade="all, delete-orphan")