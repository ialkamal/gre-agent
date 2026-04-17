"""API dependencies."""
from fastapi import Header, HTTPException
from typing import Optional


async def verify_api_key(x_api_key: Optional[str] = Header(default=None)):
    """
    Verify API key for authenticated endpoints.
    
    In production, implement proper API key validation.
    For development, this is a placeholder.
    """
    # For development, allow requests without API key
    # In production, uncomment the following:
    # if not x_api_key:
    #     raise HTTPException(status_code=401, detail="API key required")
    # if x_api_key != settings.api_key:
    #     raise HTTPException(status_code=403, detail="Invalid API key")
    pass
