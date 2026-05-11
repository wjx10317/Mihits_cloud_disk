"""全局异常处理"""
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


class AppException(Exception):
    """应用业务异常"""
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """业务异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Pydantic 校验异常处理器"""
    errors = exc.errors()
    # 取第一个错误的中文提示
    message = "参数校验失败"
    if errors:
        loc = " -> ".join(str(l) for l in errors[0].get("loc", []))
        msg = errors[0].get("msg", "")
        message = f"{loc}: {msg}" if loc else msg

    return JSONResponse(
        status_code=422,
        content={"code": "VALIDATION_ERROR", "message": message},
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """数据库完整性约束异常处理器"""
    logger.warning(f"数据库完整性错误: {str(exc)}")
    return JSONResponse(
        status_code=409,
        content={"code": "DATABASE_ERROR", "message": "数据冲突，请检查是否重复"},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局未捕获异常处理器"""
    logger.error(f"未处理异常: {type(exc).__name__}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": "INTERNAL_ERROR", "message": "服务器内部错误，请稍后重试"},
    )
