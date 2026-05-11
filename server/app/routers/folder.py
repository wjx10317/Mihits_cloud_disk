"""文件夹路由"""
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.middleware.error_handler import AppException
from app.schemas.file import FolderCreate, FolderRename
from app.services.folder_service import FolderService

router = APIRouter(prefix="/api/v1/folders", tags=["文件夹"])


@router.get("/tree")
async def get_folder_tree(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FolderService(db)
    tree = await service.get_folder_tree(user_id)
    return {"code": "SUCCESS", "message": "获取成功", "data": tree}


@router.post("")
async def create_folder(
    req: FolderCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FolderService(db)
    try:
        folder = await service.create_folder(
            user_id, str(req.parent_id) if req.parent_id else None, req.name
        )
        await db.commit()
        return {
            "code": "SUCCESS", "message": "创建成功",
            "data": {"id": str(folder.id), "name": folder.name, "path": folder.path},
        }
    except AppException:
        raise
    except Exception as e:
        raise AppException(code="CREATE_FAILED", message=str(e), status_code=400)


@router.put("/{folder_id}/rename")
async def rename_folder(
    folder_id: UUID,
    req: FolderRename,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FolderService(db)
    try:
        folder = await service.rename_folder(folder_id, user_id, req.name)
        await db.commit()
        return {
            "code": "SUCCESS", "message": "重命名成功",
            "data": {"id": str(folder.id), "name": folder.name, "path": folder.path},
        }
    except AppException:
        raise
    except Exception as e:
        raise AppException(code="RENAME_FAILED", message=str(e), status_code=400)


@router.get("/{folder_id}/path")
async def get_folder_path(
    folder_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FolderService(db)
    try:
        breadcrumb = await service.get_breadcrumb(folder_id, user_id)
        return {"code": "SUCCESS", "message": "获取成功", "data": breadcrumb}
    except AppException:
        raise
