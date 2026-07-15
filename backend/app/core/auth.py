from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import List

from app.core.config import settings
from app.core.db import get_db
from app.models.models import User
from app.schemas.schemas import TokenPayload

# OAuth2 scheme pointing to our swagger form-urlencoded login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login/swagger")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """FastAPI dependency to retrieve the currently logged in user by decoding the JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "access":
            raise credentials_exception
            
        token_data = TokenPayload(sub=username)
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == token_data.sub).first()
    if user is None:
        raise credentials_exception
    return user

class RoleChecker:
    """Dependency class to enforce role-based access control (RBAC)."""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {self.allowed_roles}",
            )
        return current_user

# Pre-defined role dependencies for clean usage in routes
require_admin = RoleChecker(["Admin"])
require_analyst = RoleChecker(["Admin", "Business Analyst"])
require_manager = RoleChecker(["Admin", "Manager"])
# Anyone who is authenticated can access general endpoints
require_authenticated = get_current_user
