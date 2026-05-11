"""回收站路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.middleware.error_handler import AppException
from app.schemas.file import TrashRestoreRequest
from app.services.file_service import FileService

router = APIRouter(prefix="/api/v1/trash", tags=["回收站"])


@router.get("")
async def list_trash(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    items = await service.list_trash(user_id)
    return {"code": "SUCCESS", "message": "获取成功", "data": items}


@router.post("/restore")
async def restore_items(
    req: TrashRestoreRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    try:
        count = await service.restore_items(user_id, req.items)
        await db.commit()
        return {"code": "SUCCESS", "message": f"已恢复 {count} 个项目", "data": {"count": count}}
    except AppException:
        raise


@router.delete("/purge")
async def purge_items(
    req: TrashRestoreRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    try:
        count = await service.purge_items(user_id, req.items)
        await db.commit()
        return {"code": "SUCCESS", "message": f"已彻底删除 {count} 个项目", "data": {"count": count}}
    except AppException:
        raise


@router.delete("/empty")
async def empty_trash(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    try:
        count = await service.empty_trash(user_id)
        await db.commit()
        return {"code": "SUCCESS", "message": f"已清空回收站，删除 {count} 个项目", "data": {"count": count}}
    except AppException:
        raise
