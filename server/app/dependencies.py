"""集中依赖注入"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.services.auth_service import AuthService
from app.services.file_service import FileService
from app.services.folder_service import FolderService
from app.services.storage_service import StorageService


# ===== 通用依赖 =====
# 数据库会话
db_session = get_db

# 当前用户 ID
current_user_id = get_current_user_id


# ===== Service 工厂 =====
def get_file_service(db: AsyncSession = Depends(get_db)) -> FileService:
    return FileService(db)


def get_folder_service(db: AsyncSession = Depends(get_db)) -> FolderService:
    return FolderService(db)


def get_storage_service(db: AsyncSession = Depends(get_db)) -> StorageService:
    return StorageService(db)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)
