import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.schemas.auth import UserInfo
from app.utils.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, email: str, username: str, password: str) -> User:
        # 检查邮箱唯一性
        result = await self.db.execute(select(User).where(User.email == email))
        if result.scalars().first():
            raise ValueError("邮箱已注册")

        # 检查用户名唯一性
        result = await self.db.execute(select(User).where(User.username == username))
        if result.scalars().first():
            raise ValueError("用户名已存在")

        # 创建用户
        user = User(
            email=email,
            username=username,
            password_hash=hash_password(password),
            storage_quota=settings.DEFAULT_STORAGE_QUOTA,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def login(self, email: str, password: str) -> dict:
        # 查询用户
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if not user or not verify_password(password, user.password_hash):
            raise ValueError("邮箱或密码错误")

        if not user.is_active:
            raise ValueError("账号已被禁用")

        # 签发 Token
        user_id_str = str(user.id)
        access_token = create_access_token(user_id_str, user.email)
        refresh_token = create_refresh_token(user_id_str)

        return {
            "code": "SUCCESS",
            "message": "登录成功",
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": UserInfo.model_validate(user).model_dump(),
            },
        }

    async def refresh_tokens(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
        except ValueError:
            raise ValueError("刷新令牌无效")

        if payload.get("type") != "refresh":
            raise ValueError("令牌类型错误")

        user_id = payload.get("sub")
        result = await self.db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalars().first()

        if not user or not user.is_active:
            raise ValueError("用户不存在或已被禁用")

        new_access = create_access_token(str(user.id), user.email)
        new_refresh = create_refresh_token(str(user.id))

        return {
            "code": "SUCCESS",
            "message": "刷新成功",
            "data": {
                "access_token": new_access,
                "refresh_token": new_refresh,
                "token_type": "Bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            },
        }
