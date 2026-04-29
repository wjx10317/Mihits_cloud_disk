from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest
from app.services.auth_service import AuthService
from app.middleware.error_handler import AppException

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        await service.register(req.email, req.username, req.password)
        await db.commit()
        return {"code": "SUCCESS", "message": "注册成功"}
    except ValueError as e:
        error_msg = str(e)
        if "邮箱" in error_msg:
            raise AppException(code="EMAIL_ALREADY_EXISTS", message=error_msg, status_code=409)
        elif "用户名" in error_msg:
            raise AppException(
                code="USERNAME_ALREADY_EXISTS", message=error_msg, status_code=409
            )
        raise AppException(code="REGISTER_FAILED", message=error_msg, status_code=400)


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        result = await service.login(req.email, req.password)
        await db.commit()
        return result
    except ValueError as e:
        raise AppException(code="INVALID_CREDENTIALS", message=str(e), status_code=401)


@router.post("/refresh")
async def refresh_token(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        result = await service.refresh_tokens(req.refresh_token)
        await db.commit()
        return result
    except ValueError as e:
        raise AppException(code="TOKEN_INVALID", message=str(e), status_code=401)


@router.post("/logout")
async def logout():
    return {"code": "SUCCESS", "message": "退出成功"}
