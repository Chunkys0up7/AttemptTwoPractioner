from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from mcp.db.base_class import Base
from mcp.core.security import generate_api_key, hash_api_key

class APIKey(Base):
    """Model for storing API keys."""
    
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    key_hash = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(String, nullable=False)  # User ID or system
    
    # Optional: Link to a specific user or service
    owner_id = Column(String, nullable=True)
    owner_type = Column(String, nullable=True)  # e.g., "user", "service"
    
    def __init__(self, name: str, created_by: str, owner_id: str = None, owner_type: str = None):
        """Initialize a new API key.
        
        Args:
            name: A descriptive name for the API key
            created_by: ID of the user or system creating the key
            owner_id: Optional ID of the key owner
            owner_type: Optional type of the key owner
        """
        self.name = name
        self.created_by = created_by
        self.owner_id = owner_id
        self.owner_type = owner_type
        
        # Generate and hash the API key
        raw_key = generate_api_key()
        self.key_hash = hash_api_key(raw_key)
        
        # Store the raw key temporarily for the initial response
        self._raw_key = raw_key
    
    @property
    def raw_key(self) -> str:
        """Get the raw API key (only available immediately after creation)."""
        if not hasattr(self, '_raw_key'):
            raise ValueError("Raw API key is only available immediately after creation")
        return self._raw_key
    
    def verify_key(self, key: str) -> bool:
        """Verify if a provided key matches this API key's hash."""
        return hash_api_key(key) == self.key_hash
    
    def is_expired(self) -> bool:
        """Check if the API key has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if the API key is valid (active and not expired)."""
        return self.is_active and not self.is_expired() 