import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

# Load and preprocess tokens
def _load_allowed_tokens():
    raw = os.getenv("API_BEARER_TOKENS", "")
    return set(token.strip() for token in raw.split(",") if token.strip())

ALLOWED_TOKENS = _load_allowed_tokens()

def verify_api_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Used in API endpoints via FastAPI Depends"""
    token = credentials.credentials
    if credentials.scheme.lower() != "bearer" or token not in ALLOWED_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Bearer token",
        )
    return token  # You can also return user info if desired

def verify_ws_token(token: str) -> bool:
    """Used in WebSocket routes"""
    return token in ALLOWED_TOKENS