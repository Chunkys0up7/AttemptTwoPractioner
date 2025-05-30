from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from mcp.db.models.api_key import APIKey

class APIKeyService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_api_key(
        self,
        name: str,
        created_by: str,
        owner_id: Optional[str] = None,
        owner_type: Optional[str] = None,
        expires_in_days: Optional[int] = None
    ) -> APIKey:
        """Create a new API key.
        
        Args:
            name: A descriptive name for the API key
            created_by: ID of the user or system creating the key
            owner_id: Optional ID of the key owner
            owner_type: Optional type of the key owner
            expires_in_days: Optional number of days until the key expires
            
        Returns:
            The created APIKey instance with the raw key available
        """
        # Create the API key
        api_key = APIKey(
            name=name,
            created_by=created_by,
            owner_id=owner_id,
            owner_type=owner_type
        )
        
        # Set expiration if specified
        if expires_in_days:
            api_key.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Save to database
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        
        return api_key
    
    def get_api_key(self, key_id: int) -> Optional[APIKey]:
        """Get an API key by ID.
        
        Args:
            key_id: The ID of the API key to retrieve
            
        Returns:
            The APIKey instance if found, None otherwise
        """
        return self.db.query(APIKey).filter(APIKey.id == key_id).first()
    
    def list_api_keys(
        self,
        owner_id: Optional[str] = None,
        owner_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[APIKey]:
        """List API keys with optional filtering.
        
        Args:
            owner_id: Optional owner ID to filter by
            owner_type: Optional owner type to filter by
            active_only: Whether to only return active keys
            
        Returns:
            List of matching APIKey instances
        """
        query = self.db.query(APIKey)
        
        if owner_id:
            query = query.filter(APIKey.owner_id == owner_id)
        if owner_type:
            query = query.filter(APIKey.owner_type == owner_type)
        if active_only:
            query = query.filter(APIKey.is_active == True)
        
        return query.all()
    
    def deactivate_api_key(self, key_id: int) -> APIKey:
        """Deactivate an API key.
        
        Args:
            key_id: The ID of the API key to deactivate
            
        Returns:
            The deactivated APIKey instance
            
        Raises:
            HTTPException if the key is not found
        """
        api_key = self.get_api_key(key_id)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        api_key.is_active = False
        self.db.commit()
        self.db.refresh(api_key)
        
        return api_key
    
    def validate_api_key(self, key: str) -> Optional[APIKey]:
        """Validate an API key and update its last used timestamp.
        
        Args:
            key: The API key to validate
            
        Returns:
            The APIKey instance if valid, None otherwise
        """
        # Find the key by its hash
        key_hash = APIKey.hash_api_key(key)
        api_key = self.db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
        
        if not api_key or not api_key.is_valid():
            return None
        
        # Update last used timestamp
        api_key.last_used_at = datetime.utcnow()
        self.db.commit()
        
        return api_key 