"""
Utility module for security, token management, and common helpers.
"""

import os
import logging
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)


class SecurityUtils:
    """Security utilities for password and token management."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt directly.
        
        bcrypt automatically truncates at 72 bytes.
        """
        # Convert password to bytes
        password_bytes = password.encode('utf-8')
        
        # bcrypt will automatically truncate at 72 bytes
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash using bcrypt directly."""
        try:
            password_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode and validate JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None


class DateTimeUtils:
    """Utilities for datetime handling."""
    
    @staticmethod
    def add_minutes(dt: datetime, minutes: int) -> datetime:
        """Add minutes to datetime."""
        return dt + timedelta(minutes=minutes)
    
    @staticmethod
    def is_within_range(
        dt: datetime,
        start: datetime,
        end: datetime
    ) -> bool:
        """Check if datetime is within range."""
        return start <= dt <= end
    
    @staticmethod
    def get_day_name(dt: datetime) -> str:
        """Get day name from datetime."""
        return dt.strftime("%A")
    
    @staticmethod
    def get_time_slot(dt: datetime) -> str:
        """Get time slot (e.g., '9am', '3pm')."""
        return dt.strftime("%I%p").lower()


class ValidationUtils:
    """Utilities for data validation."""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Basic email validation."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Basic URL validation."""
        import re
        pattern = r'^https?://'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """Validate password strength."""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        return True, "Password is strong"


class StringUtils:
    """Utilities for string manipulation."""
    
    @staticmethod
    def truncate(text: str, length: int = 100) -> str:
        """Truncate text to specified length."""
        if len(text) <= length:
            return text
        return text[:length] + "..."
    
    @staticmethod
    def slugify(text: str) -> str:
        """Convert text to URL-friendly slug."""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')
    
    @staticmethod
    def generate_unique_code(prefix: str = "") -> str:
        """Generate unique code using UUID."""
        code = str(uuid.uuid4())[:8].upper()
        if prefix:
            return f"{prefix}_{code}"
        return code


__all__ = [
    "SecurityUtils",
    "DateTimeUtils",
    "ValidationUtils",
    "StringUtils",
    "pwd_context"
]
