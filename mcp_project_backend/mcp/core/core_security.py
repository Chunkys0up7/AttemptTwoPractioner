import secrets
import hashlib
from typing import Optional
from passlib.context import CryptContext

def generate_api_key(prefix: str = "mcp_", length: int = 32) -> str:
    """Generate a secure API key.
    
    Args:
        prefix: Optional prefix for the API key
        length: Length of the random part of the key
        
    Returns:
        A secure API key string
    """
    # Generate random bytes and convert to hex
    random_bytes = secrets.token_bytes(length)
    random_hex = random_bytes.hex()
    
    # Combine prefix and random part
    return f"{prefix}{random_hex}"

def hash_api_key(key: str) -> str:
    """Hash an API key using SHA-256.
    
    Args:
        key: The API key to hash
        
    Returns:
        The hashed API key
    """
    return hashlib.sha256(key.encode()).hexdigest()

def verify_api_key(provided_key: str, stored_hash: str) -> bool:
    """Verify if a provided API key matches a stored hash.
    
    Args:
        provided_key: The API key to verify
        stored_hash: The stored hash to compare against
        
    Returns:
        True if the key matches the hash, False otherwise
    """
    return hash_api_key(provided_key) == stored_hash

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash using bcrypt."""
    return pwd_context.verify(plain_password, hashed_password) 