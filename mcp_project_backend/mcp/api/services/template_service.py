from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ...db.models.workflow_template import WorkflowTemplate, WorkflowTemplateVersion
from ...schemas.template import TemplateCreate, TemplateUpdate, TemplateVersionCreate

class TemplateService:
    """Service for managing workflow templates and their versions."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_template(self, template_data: TemplateCreate, user_id: int) -> WorkflowTemplate:
        """Create a new workflow template with initial version."""
        template = WorkflowTemplate(
            name=template_data.name,
            description=template_data.description,
            category=template_data.category,
            metadata=template_data.metadata,
            is_public=template_data.is_public,
            created_by=user_id
        )
        self.db.add(template)
        self.db.flush()
        
        # Create initial version
        version = WorkflowTemplateVersion(
            template_id=template.id,
            version=1,
            content=template_data.content,
            changes="Initial version",
            created_by=user_id
        )
        self.db.add(version)
        self.db.commit()
        return template
    
    def get_template(self, template_id: int) -> Optional[WorkflowTemplate]:
        """Get a template by ID."""
        return self.db.query(WorkflowTemplate).filter(WorkflowTemplate.id == template_id).first()
    
    def list_templates(
        self,
        user_id: int,
        category: Optional[str] = None,
        search: Optional[str] = None,
        public_only: bool = False
    ) -> List[WorkflowTemplate]:
        """List templates with optional filtering."""
        query = self.db.query(WorkflowTemplate)
        
        if public_only:
            query = query.filter(WorkflowTemplate.is_public == True)
        else:
            query = query.filter(
                (WorkflowTemplate.created_by == user_id) |
                (WorkflowTemplate.is_public == True)
            )
        
        if category:
            query = query.filter(WorkflowTemplate.category == category)
        
        if search:
            query = query.filter(
                (WorkflowTemplate.name.ilike(f"%{search}%")) |
                (WorkflowTemplate.description.ilike(f"%{search}%"))
            )
        
        return query.all()
    
    def update_template(
        self,
        template_id: int,
        template_data: TemplateUpdate,
        user_id: int
    ) -> Optional[WorkflowTemplate]:
        """Update a template and create a new version if content changed."""
        template = self.get_template(template_id)
        if not template or template.created_by != user_id:
            return None
        
        # Update template metadata
        for field, value in template_data.dict(exclude_unset=True).items():
            if field != 'content':
                setattr(template, field, value)
        
        # Create new version if content changed
        if template_data.content:
            latest_version = self.db.query(WorkflowTemplateVersion)\
                .filter(WorkflowTemplateVersion.template_id == template_id)\
                .order_by(WorkflowTemplateVersion.version.desc())\
                .first()
            
            new_version = WorkflowTemplateVersion(
                template_id=template_id,
                version=latest_version.version + 1 if latest_version else 1,
                content=template_data.content,
                changes=template_data.changes or "Updated template",
                created_by=user_id
            )
            self.db.add(new_version)
        
        self.db.commit()
        return template
    
    def delete_template(self, template_id: int, user_id: int) -> bool:
        """Delete a template and all its versions."""
        template = self.get_template(template_id)
        if not template or template.created_by != user_id:
            return False
        
        self.db.delete(template)
        self.db.commit()
        return True
    
    def get_template_version(
        self,
        template_id: int,
        version: Optional[int] = None
    ) -> Optional[WorkflowTemplateVersion]:
        """Get a specific version of a template."""
        query = self.db.query(WorkflowTemplateVersion)\
            .filter(WorkflowTemplateVersion.template_id == template_id)
        
        if version:
            query = query.filter(WorkflowTemplateVersion.version == version)
        else:
            query = query.order_by(WorkflowTemplateVersion.version.desc())
        
        return query.first()
    
    def list_template_versions(self, template_id: int) -> List[WorkflowTemplateVersion]:
        """List all versions of a template."""
        return self.db.query(WorkflowTemplateVersion)\
            .filter(WorkflowTemplateVersion.template_id == template_id)\
            .order_by(WorkflowTemplateVersion.version.desc())\
            .all()
    
    def get_template_stats(self, user_id: int) -> Dict[str, Any]:
        """Get statistics about templates."""
        total_templates = self.db.query(WorkflowTemplate)\
            .filter(WorkflowTemplate.created_by == user_id)\
            .count()
        
        public_templates = self.db.query(WorkflowTemplate)\
            .filter(
                WorkflowTemplate.created_by == user_id,
                WorkflowTemplate.is_public == True
            )\
            .count()
        
        categories = self.db.query(WorkflowTemplate.category)\
            .filter(WorkflowTemplate.created_by == user_id)\
            .distinct()\
            .count()
        
        return {
            "total_templates": total_templates,
            "public_templates": public_templates,
            "categories": categories
        } 