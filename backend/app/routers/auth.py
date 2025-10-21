"""Authentication endpoints for user registration and login."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta
from app.core.database import get_session
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.auth import get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, session: Session = Depends(get_session)):
    """
    Register a new user account.
    
    Creates a new user with the provided email, username, and password.
    The password is securely hashed before storage.
    
    Args:
        user_data: User registration data (email, username, password)
        session: Database session
        
    Returns:
        The created user information (without password)
        
    Raises:
        HTTPException 400: If username or email already exists
    """
    # Check if username already exists
    statement = select(User).where(User.username == user_data.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    existing_email = session.exec(statement).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """
    Login with username and password to receive JWT token.
    
    Authenticates user credentials and returns a JWT access token
    for accessing protected endpoints.
    
    Args:
        form_data: OAuth2 form data (username and password)
        session: Database session
        
    Returns:
        JWT access token and token type
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Get user by username
    statement = select(User).where(User.username == form_data.username)
    user = session.exec(statement).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    
    Returns information about the currently authenticated user
    based on the JWT token provided in the Authorization header.
    
    Args:
        current_user: The authenticated user (from JWT token)
        
    Returns:
        Current user information
    """
    return current_user
