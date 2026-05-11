"""存储空间业务逻辑"""
import uuid
from typing import Optional

from sqlalchemy import select, and_, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.folder import File
from app.models.user import User
from app.middleware.error_handler import AppException
from app.config import settings


class StorageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_storage_usage(self, user_id: str) -> dict:
        """获取用户存储空间使用情况（含分类统计）"""
        uid = uuid.UUID(user_id)

        # 获取用户信息
        result = await self.db.execute(select(User).where(User.id == uid))
        user = result.scalars().first()
        if not user:
            raise AppException(code="USER_NOT_FOUND", message="用户不存在", status_code=404)

        total_quota = user.storage_quota
        used_quota = user.storage_used
        available_quota = max(0, total_quota - used_quota)
        usage_percentage = round((used_quota / total_quota * 100) if total_quota > 0 else 0, 1)

        # 按文件类型分类统计
        category_breakdown = await self._get_category_breakdown(uid)

        return {
            "total_quota": total_quota,
            "used_quota": used_quota,
            "available_quota": available_quota,
            "usage_percentage": usage_percentage,
            "category_breakdown": category_breakdown,
        }

    async def check_storage(self, user_id: str, file_size: int) -> bool:
        """检查用户是否有足够的存储空间（带行锁）"""
        uid = uuid.UUID(user_id)

        # 使用行锁防止并发超额
        result = await self.db.execute(
            select(User).where(User.id == uid).with_for_update()
        )
        user = result.scalars().first()
        if not user:
            raise AppException(code="USER_NOT_FOUND", message="用户不存在", status_code=404)

        if user.storage_used + file_size > user.storage_quota:
            raise AppException(
                code="STORAGE_EXCEEDED",
                message=f"存储空间不足，需要 {self._format_size(file_size)}，"
                        f"剩余 {self._format_size(user.storage_quota - user.storage_used)}",
                status_code=403,
            )
        return True

    async def update_storage_used(self, user_id: str, delta: int) -> int:
        """原子更新用户存储用量（增加或减少）"""
        uid = uuid.UUID(user_id)

        result = await self.db.execute(
            select(User).where(User.id == uid).with_for_update()
        )
        user = result.scalars().first()
        if not user:
            raise AppException(code="USER_NOT_FOUND", message="用户不存在", status_code=404)

        new_used = max(0, user.storage_used + delta)
        user.storage_used = new_used
        await self.db.flush()
        return new_used

    async def update_quota(self, user_id: str, new_quota: int) -> dict:
        """更新用户存储配额"""
        uid = uuid.UUID(user_id)

        result = await self.db.execute(select(User).where(User.id == uid))
        user = result.scalars().first()
        if not user:
            raise AppException(code="USER_NOT_FOUND", message="用户不存在", status_code=404)

        if new_quota < user.storage_used:
            raise AppException(
                code="QUOTA_TOO_SMALL",
                message=f"新配额不能小于已使用空间（{self._format_size(user.storage_used)}）",
                status_code=400,
            )

        user.storage_quota = new_quota
        await self.db.flush()
        return {
            "storage_quota": new_quota,
            "storage_used": user.storage_used,
        }

    async def _get_category_breakdown(self, uid: uuid.UUID) -> dict:
        """按文件 MIME 类型聚合统计存储用量"""
        # 使用 SQL CASE 语句进行分类聚合
        result = await self.db.execute(
            select(
                func.coalesce(func.sum(
                    case(
                        (File.mime_type.ilike("image/%"), File.size),
                        else_=0,
                    )
                ), 0).label("image"),
                func.coalesce(func.sum(
                    case(
                        (File.mime_type.ilike("video/%"), File.size),
                        else_=0,
                    )
                ), 0).label("video"),
                func.coalesce(func.sum(
                    case(
                        (File.mime_type.ilike("audio/%"), File.size),
                        else_=0,
                    )
                ), 0).label("audio"),
                func.coalesce(func.sum(
                    case(
                        (
                            File.mime_type.ilike("application/pdf")
                            | File.mime_type.ilike("application/msword")
                            | File.mime_type.ilike("application/vnd.%")
                            | File.mime_type.ilike("text/%"),
                            File.size,
                        ),
                        else_=0,
                    )
                ), 0).label("document"),
                func.coalesce(func.sum(
                    case(
                        (
                            ~File.mime_type.ilike("image/%")
                            & ~File.mime_type.ilike("video/%")
                            & ~File.mime_type.ilike("audio/%")
                            & ~File.mime_type.ilike("application/pdf")
                            & ~File.mime_type.ilike("application/msword")
                            & ~File.mime_type.ilike("application/vnd.%")
                            & ~File.mime_type.ilike("text/%"),
                            File.size,
                        ),
                        else_=0,
                    )
                ), 0).label("other"),
            ).where(
                and_(File.user_id == uid, File.is_deleted == False)
            )
        )
        row = result.one()
        return {
            "image": row.image or 0,
            "video": row.video or 0,
            "document": row.document or 0,
            "audio": row.audio or 0,
            "other": row.other or 0,
        }

    @staticmethod
    def _format_size(size: int) -> str:
        """格式化文件大小"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}PB"
