import hmac
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
from jose import jwt, JWTError
import bcrypt
from app.core.config import settings

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def generate_api_key() -> tuple[str, str]:
    """
    Generates a secure agent API key and its SHA-256 hash.
    Returns: (raw_key, hashed_key)
    """
    raw_key = f"agnt_{secrets.token_urlsafe(32)}"
    hashed_key = hash_api_key(raw_key)
    return raw_key, hashed_key

def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

def create_access_token(subject: Union[str, Any], role: str = "agent", expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def sign_webhook_payload(payload: str, secret: Optional[str] = None) -> str:
    """
    Signs a webhook payload with HMAC-SHA256.
    """
    signing_secret = (secret or settings.WEBHOOK_SIGNING_SECRET).encode("utf-8")
    signature = hmac.new(signing_secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"sha256={signature}"

def verify_webhook_signature(payload: str, signature_header: str, secret: Optional[str] = None) -> bool:
    """
    Verifies an HMAC-SHA256 signature in constant time.
    """
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected_sig = sign_webhook_payload(payload, secret)
    return hmac.compare_digest(expected_sig, signature_header)
