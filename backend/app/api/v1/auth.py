from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from app.db.queries.user_queries import get_user_by_email, get_user_by_username
from app.services.auth_service import create_user, authenticate_user, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(get_async_session)):
    existing_email = await get_user_by_email(db, data.email)
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该邮箱已被注册")
    existing_username = await get_user_by_username(db, data.username)
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该用户名已被使用")
    user = await create_user(db, data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_async_session)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误")
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
