from uuid import uuid4
from jose import jwt, JWTError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from typing import Dict, Any
from datetime import timedelta, datetime
from backend.core.config import settings
from backend.core.exceptions import UnauthorizedException

ph = PasswordHasher()

def hash_password(password : str) -> str:
    """Hash the password using argon2 library comes with default salt."""
    hashed = ph.hash(password)
    return hashed

def verify_password(hashed_password : str, plain_password : str) -> bool:
    """Verify the password against the hashed password."""
    try:
        return ph.verify(hashed_password, plain_password)
    
    except VerifyMismatchError:
        return False

def create_tokens(data: Dict[str, Any]) -> tuple[str, str]:
    """Create both JWT access token and refresh token."""
    to_encode = data.copy()

    #Creates short-lived JWT access token
    access = jwt.encode({
        "sub": to_encode,
        "exp": datetime.utcnow() + timedelta(minutes=settings.AUTH_TOKEN_EXP_MIN),
        "type": "access"
    }, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    #Creates long‑lived JWT refresh token
    refresh = jwt.encode({
        "sub": to_encode,
        "exp": datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh",
        "jti": str(uuid4())
    }, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return access, refresh

def verify_token(token: str, expected_type: str) -> dict:
    """Decode and validate a JWT."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        raise UnauthorizedException("Invalid or expired token")

    # Enforce token type — prevents access tokens
    # being used on the /refresh endpoint and vice versa
    if payload.get("type") != expected_type:
        raise UnauthorizedException("Wrong token type")

    return payload