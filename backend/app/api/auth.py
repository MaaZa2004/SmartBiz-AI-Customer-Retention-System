from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import jwt, JWTError

from app.core.db import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.auth import get_current_user
from app.core.limiter import limiter
from app.models.models import User
from app.schemas.schemas import UserCreate, UserResponse, Token, LoginRequest, TokenPayload

router = APIRouter(prefix="/auth", tags=["Authentication"])

ALLOWED_ROLES = ["Admin", "Business Analyst", "Manager"]

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with password hashing and role validation."""
    # Check if role is valid
    if user_in.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Allowed roles are: {ALLOWED_ROLES}"
        )
        
    # Check if email is already taken
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
        
    # Create user
    db_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and issue JWT access/refresh tokens. Rate limited (JSON body)."""
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Generate tokens
    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role
    )

@router.post("/login/swagger", response_model=Token)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
def login_swagger(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user via form-urlencoded data for Swagger UI OAuth2 workflow."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Generate tokens
    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role
    )

@router.post("/refresh", response_model=Token)
def refresh_token(token_data: dict, db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    refresh_token_str = token_data.get("refresh_token")
    if not refresh_token_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required."
        )
        
    try:
        payload = jwt.decode(refresh_token_str, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_41_UNAUTHORIZED, detail="Invalid refresh token")
        
    user = db.query(User).filter(User.email == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    # Generate a new set of tokens
    access_token = create_access_token(subject=user.email)
    new_refresh_token = create_refresh_token(subject=user.email)
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        role=user.role
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get profile of current logged-in user."""
    return current_user
