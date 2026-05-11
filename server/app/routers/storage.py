"""存储空间路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.middleware.error_handler import AppException
from app.schemas.storage import StorageQuotaUpdate
from app.services.storage_service import StorageService

router = APIRouter(prefix="/api/v1/storage", tags=["存储空间"])


@router.get("/usage")
async def get_storage_usage(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取存储空间使用情况"""
    service = StorageService(db)
    result = await service.get_storage_usage(user_id)
    return {"code": "SUCCESS", "message": "获取成功", "data": result}


@router.put("/quota")
async def update_quota(
    req: StorageQuotaUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """更新存储配额"""
    service = StorageService(db)
    try:
        result = await service.update_quota(user_id, req.storage_quota)
        await db.commit()
        return {"code": "SUCCESS", "message": "配额更新成功", "data": result}
    except AppException:
        raise
