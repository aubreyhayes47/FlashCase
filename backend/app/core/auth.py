"""Authentication dependencies for protected routes."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from typing import Optional
from app.core.database import get_session
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.auth import TokenData

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        token: The JWT token from the Authorization header
        session: Database session
        
    Returns:
        The authenticated User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode the token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Extract username from token
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Get user from database
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current authenticated and active user.
    
    Args:
        current_user: The current user from get_current_user
        
    Returns:
        The authenticated and active User object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
