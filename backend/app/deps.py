from fastapi import Depends, Header, HTTPException

from .config import settings


def require_api_key(x_api_key: str = Header(None), authorization: str = Header(None)):
    token = x_api_key
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    if token != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return token
