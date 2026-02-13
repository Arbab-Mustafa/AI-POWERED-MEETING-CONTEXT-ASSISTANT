"""
Authentication Controller
Handles user registration, login, Google OAuth, and JWT token management
"""
from datetime import timedelta
from typing import Optional, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings, DatabaseManager
from app.services.base import AuthService
from app.repositories.base import UserRepository
from app.schemas.base import UserCreate, LoginRequest, UserResponse, TokenResponse
from app.utils.helpers import SecurityUtils
from app.core.config import logger

# Initialize router
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Database dependency
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    if db_manager.AsyncSessionLocal is None:
        await db_manager.initialize()
    
    async with db_manager.AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
    
    Returns:
        User model instance
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Decode token
    payload = SecurityUtils.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Get user from database
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )
    
    return user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with email and password.
    
    Args:
        user_data: User registration data (email, name, password)
        db: Database session
    
    Returns:
        JWT access token and user information
    """
    try:
        auth_service = AuthService(db)
        user_repo = UserRepository(db)
        
        # Check if user already exists
        existing_user = await user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = await auth_service.create_user(user_data)
        
        # Generate access token
        access_token = SecurityUtils.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        logger.info(f"New user registered: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    
    Args:
        login_data: Login credentials (email and password)
        db: Database session
    
    Returns:
        JWT access token and user information
    """
    try:
        auth_service = AuthService(db)
        
        # Authenticate user
        user = await auth_service.authenticate_user(login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate access token
        access_token = SecurityUtils.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current user from JWT token
    
    Returns:
        User information
    """
    return UserResponse.from_orm(current_user)


@router.post("/google/callback", response_model=TokenResponse)
async def google_oauth_callback(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Google OAuth callback.
    
    Args:
        code: Authorization code from Google
        db: Database session
    
    Returns:
        JWT access token and user information
    """
    try:
        auth_service = AuthService(db)
        
        # Exchange code for user info and create/get user
        user =await auth_service.get_or_create_google_user(code)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to authenticate with Google"
            )
        
        # Generate access token
        access_token = SecurityUtils.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        logger.info(f"User authenticated via Google: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user = Depends(get_current_user)
):
    """
    Refresh access token for authenticated user.
    
    Args:
        current_user: Current user from JWT token
    
    Returns:
        New JWT access token
    """
    try:
        # Generate new access token
        access_token = SecurityUtils.create_access_token(
            data={"sub": str(current_user.id), "email": current_user.email}
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.from_orm(current_user)
        )
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.delete("/logout")
async def logout(current_user = Depends(get_current_user)):
    """
    Logout current user (frontend should discard token).
    
    Args:
        current_user: Current user from JWT token
    
    Returns:
        Success message
    """
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}


@router.get("/health")
async def health_check():
    """Health check endpoint for authentication service."""
    return {
        "status": "healthy",
        "service": "authentication",
        "version": settings.APP_VERSION
    }
