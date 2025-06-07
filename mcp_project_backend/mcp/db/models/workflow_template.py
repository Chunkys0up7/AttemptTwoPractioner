from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from ..base import Base

class WorkflowTemplate(Base):
    """Model for storing workflow templates with version tracking."""
    
    __tablename__ = 'workflow_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    category = Column(String(100))
    template_metadata = Column(JSON)
    is_public = Column(Boolean, default=False)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    versions = relationship("WorkflowTemplateVersion", back_populates="template", cascade="all, delete-orphan")
    creator = relationship("User", back_populates="created_templates")
    
    def __repr__(self):
        return f"<WorkflowTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"

class WorkflowTemplateVersion(Base):
    """Model for tracking versions of workflow templates."""
    
    __tablename__ = 'workflow_template_versions'

    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey('workflow_templates.id'), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(JSON, nullable=False)
    changes = Column(String(1000))
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    template = relationship("WorkflowTemplate", back_populates="versions")
    creator = relationship("User", back_populates="created_template_versions")
    
    def __repr__(self):
        return f"<WorkflowTemplateVersion(template_id={self.template_id}, version={self.version})>" 