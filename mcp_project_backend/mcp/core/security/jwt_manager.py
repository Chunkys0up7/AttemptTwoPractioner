from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from mcp.core.config import settings

class JWTManager:
    """
    Manages creation, decoding, and validation of JSON Web Tokens (JWTs).
    Provides static methods for access token creation and decoding.
    """
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Creates a JWT access token with the given data and expiration.
        Args:
            data (dict): The payload data to encode in the token.
            expires_delta (Optional[timedelta]): Optional expiration delta. Defaults to settings.ACCESS_TOKEN_EXPIRE_MINUTES.
        Returns:
            str: The encoded JWT token as a string.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decodes a JWT token and returns the payload if valid.
        Args:
            token (str): The JWT token to decode.
        Returns:
            Optional[Dict[str, Any]]: The decoded payload if valid, otherwise None.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None
