"""文件业务逻辑"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.folder import File, Folder, UploadSession
from app.models.user import User
from app.middleware.error_handler import AppException
from app.config import settings


class FileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ===== 文件列表 =====
    async def list_files(
        self, user_id: str, folder_id: Optional[str] = None,
        page: int = 1, page_size: int = 50,
        sort: str = "name", order: str = "asc",
        file_type: Optional[str] = None,
    ) -> dict:
        """获取文件列表（文件夹优先）"""
        uid = uuid.UUID(user_id)

        # 文件夹查询
        folder_conditions = [Folder.user_id == uid, Folder.is_deleted == False]
        if folder_id:
            folder_conditions.append(Folder.parent_id == uuid.UUID(folder_id))
        else:
            folder_conditions.append(Folder.parent_id == None)  # noqa: E711

        folder_result = await self.db.execute(
            select(Folder).where(and_(*folder_conditions)).order_by(Folder.name)
        )
        folders = folder_result.scalars().all()

        # 文件查询
        file_conditions = [File.user_id == uid, File.is_deleted == False]
        if folder_id:
            file_conditions.append(File.folder_id == uuid.UUID(folder_id))
        else:
            file_conditions.append(File.folder_id == None)  # noqa: E711

        if file_type:
            type_map = {
                "image": ["image/%"],
                "document": ["application/pdf", "application/msword", "application/vnd.%", "text/%"],
                "video": ["video/%"],
                "audio": ["audio/%"],
            }
            if file_type in type_map:
                type_filters = type_map[file_type]
                or_conditions = []
                for tf in type_filters:
                    or_conditions.append(File.mime_type.ilike(tf))
                from sqlalchemy import or_
                file_conditions.append(or_(*or_conditions))

        # 排序
        sort_column = File.name
        if sort == "size":
            sort_column = File.size
        elif sort == "type":
            sort_column = File.extension
        elif sort == "created_at":
            sort_column = File.created_at

        if order == "desc":
            sort_column = sort_column.desc()
        else:
            sort_column = sort_column.asc()

        # 总数
        count_result = await self.db.execute(
            select(func.count()).select_from(File).where(and_(*file_conditions))
        )
        total = count_result.scalar() or 0

        file_result = await self.db.execute(
            select(File)
            .where(and_(*file_conditions))
            .order_by(sort_column)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        files = file_result.scalars().all()

        return {
            "folders": [self._folder_to_dict(f) for f in folders],
            "files": [self._file_to_dict(f) for f in files],
            "total": total + len(folders),
            "page": page,
            "page_size": page_size,
        }

    # ===== 创建空文件 =====
    async def create_file(self, user_id: str, folder_id: Optional[str], name: str) -> File:
        """创建空文件记录"""
        uid = uuid.UUID(user_id)
        extension = name.rsplit(".", 1)[-1] if "." in name else None

        file = File(
            user_id=uid,
            folder_id=uuid.UUID(folder_id) if folder_id else None,
            name=name,
            extension=extension,
            size=0,
            storage_key="",
        )
        self.db.add(file)
        await self.db.flush()
        return file

    # ===== 重命名 =====
    async def rename_file(self, file_id: uuid.UUID, user_id: str, name: str) -> File:
        """重命名文件"""
        file = await self._get_file(file_id, user_id)

        # 检查同级重名
        await self._check_file_name_conflict(file.user_id, file.folder_id, name, exclude_id=file.id)

        file.name = name
        file.extension = name.rsplit(".", 1)[-1] if "." in name else None
        await self.db.flush()
        return file

    # ===== 移动 =====
    async def move_files(self, user_id: str, file_ids: list[str], folder_ids: list[str], target_folder_id: Optional[str]) -> int:
        """移动文件和文件夹到目标目录"""
        uid = uuid.UUID(user_id)
        count = 0

        # 验证目标目录
        if target_folder_id:
            target_folder = await self._get_folder(uuid.UUID(target_folder_id), user_id)
            # 检查循环引用
            for fid_str in folder_ids:
                if uuid.UUID(fid_str) == target_folder.id:
                    raise AppException(code="CIRCULAR_MOVE", message="不能移动到自身子目录", status_code=400)

        # 移动文件
        for fid_str in file_ids:
            file = await self._get_file(uuid.UUID(fid_str), user_id)
            file.folder_id = uuid.UUID(target_folder_id) if target_folder_id else None
            count += 1

        # 移动文件夹
        for fid_str in folder_ids:
            folder = await self._get_folder(uuid.UUID(fid_str), user_id)
            folder.parent_id = uuid.UUID(target_folder_id) if target_folder_id else None
            # 更新路径
            if target_folder_id:
                folder.path = f"{target_folder.path}/{folder.name}"
            else:
                folder.path = f"/{folder.name}"
            count += 1

        await self.db.flush()
        return count

    # ===== 复制 =====
    async def copy_files(self, user_id: str, file_ids: list[str], target_folder_id: Optional[str]) -> int:
        """复制文件到目标目录"""
        count = 0
        for fid_str in file_ids:
            original = await self._get_file(uuid.UUID(fid_str), user_id)
            new_file = File(
                user_id=original.user_id,
                folder_id=uuid.UUID(target_folder_id) if target_folder_id else None,
                name=original.name,
                extension=original.extension,
                mime_type=original.mime_type,
                size=original.size,
                storage_key=original.storage_key,  # MinIO 不复制对象，共享存储键
                file_hash=original.file_hash,
            )
            self.db.add(new_file)
            count += 1
        await self.db.flush()
        return count

    # ===== 软删除 =====
    async def delete_files(self, file_ids: list[str], user_id: str) -> int:
        """软删除文件"""
        uid = uuid.UUID(user_id)
        count = 0
        for fid_str in file_ids:
            file = await self._get_file(uuid.UUID(fid_str), user_id)
            file.is_deleted = True
            file.deleted_at = datetime.now(timezone.utc)
            count += 1
        await self.db.flush()
        return count

    # ===== 回收站 =====
    async def list_trash(self, user_id: str) -> list[dict]:
        """获取回收站列表"""
        uid = uuid.UUID(user_id)

        # 已删除的文件
        file_result = await self.db.execute(
            select(File).where(and_(File.user_id == uid, File.is_deleted == True))
            .order_by(File.deleted_at.desc())
        )
        files = file_result.scalars().all()

        # 已删除的文件夹
        folder_result = await self.db.execute(
            select(Folder).where(and_(Folder.user_id == uid, Folder.is_deleted == True))
            .order_by(Folder.deleted_at.desc())
        )
        folders = folder_result.scalars().all()

        items = []
        for f in folders:
            items.append({
                "id": str(f.id), "name": f.name, "type": "folder",
                "size": 0, "original_path": f.path, "deleted_at": f.deleted_at.isoformat() if f.deleted_at else None,
            })
        for f in files:
            items.append({
                "id": str(f.id), "name": f.name, "type": "file",
                "size": f.size, "original_path": f.name, "deleted_at": f.deleted_at.isoformat() if f.deleted_at else None,
            })
        return items

    async def restore_items(self, user_id: str, items: list[dict]) -> int:
        """恢复回收站项目"""
        count = 0
        for item in items:
            item_id = uuid.UUID(item["id"])
            item_type = item["type"]

            if item_type == "file":
                result = await self.db.execute(select(File).where(File.id == item_id))
                file = result.scalars().first()
                if file and file.is_deleted:
                    file.is_deleted = False
                    file.deleted_at = None
                    count += 1
            elif item_type == "folder":
                result = await self.db.execute(select(Folder).where(Folder.id == item_id))
                folder = result.scalars().first()
                if folder and folder.is_deleted:
                    folder.is_deleted = False
                    folder.deleted_at = None
                    # 恢复子文件
                    sub_result = await self.db.execute(
                        select(File).where(and_(File.folder_id == item_id, File.is_deleted == True))
                    )
                    for f in sub_result.scalars().all():
                        f.is_deleted = False
                        f.deleted_at = None
                    count += 1

        await self.db.flush()
        return count

    async def purge_items(self, user_id: str, items: list[dict]) -> int:
        """彻底删除项目（同时删除 MinIO 对象）"""
        count = 0
        for item in items:
            item_id = uuid.UUID(item["id"])
            item_type = item["type"]

            if item_type == "file":
                result = await self.db.execute(select(File).where(File.id == item_id))
                file = result.scalars().first()
                if file:
                    # 删除 MinIO 对象
                    if file.storage_key:
                        try:
                            from app.utils.minio_client import delete_object, get_bucket_name
                            delete_object(get_bucket_name(user_id), file.storage_key)
                        except Exception:
                            pass  # MinIO 不可用时仍删除数据库记录
                    # 更新用户存储空间
                    user_result = await self.db.execute(select(User).where(User.id == file.user_id))
                    user = user_result.scalars().first()
                    if user:
                        user.storage_used = max(0, user.storage_used - file.size)
                    await self.db.delete(file)
                    count += 1
            elif item_type == "folder":
                # 递归删除子文件
                sub_result = await self.db.execute(select(File).where(File.folder_id == item_id))
                for f in sub_result.scalars().all():
                    if f.storage_key:
                        try:
                            from app.utils.minio_client import delete_object, get_bucket_name
                            delete_object(get_bucket_name(user_id), f.storage_key)
                        except Exception:
                            pass
                    user_result = await self.db.execute(select(User).where(User.id == f.user_id))
                    user = user_result.scalars().first()
                    if user:
                        user.storage_used = max(0, user.storage_used - f.size)
                    await self.db.delete(f)
                    count += 1
                # 删除文件夹
                result = await self.db.execute(select(Folder).where(Folder.id == item_id))
                folder = result.scalars().first()
                if folder:
                    await self.db.delete(folder)
                    count += 1

        await self.db.flush()
        return count

    async def empty_trash(self, user_id: str) -> int:
        """清空回收站"""
        items = await self.list_trash(user_id)
        return await self.purge_items(user_id, items)

    # ===== 搜索 =====
    async def search_files(self, user_id: str, keyword: str, file_type: Optional[str] = None, limit: int = 50) -> dict:
        """搜索文件"""
        uid = uuid.UUID(user_id)
        like_pattern = f"%{keyword}%"

        # 搜索文件夹
        folder_conditions = [
            Folder.user_id == uid, Folder.is_deleted == False,
            Folder.name.ilike(like_pattern),
        ]
        folder_result = await self.db.execute(
            select(Folder).where(and_(*folder_conditions)).limit(limit)
        )
        folders = folder_result.scalars().all()

        # 搜索文件
        file_conditions = [
            File.user_id == uid, File.is_deleted == False,
            File.name.ilike(like_pattern),
        ]
        if file_type:
            type_map = {
                "image": ["image/%"],
                "document": ["application/pdf", "application/msword", "application/vnd.%", "text/%"],
                "video": ["video/%"],
                "audio": ["audio/%"],
            }
            if file_type in type_map:
                from sqlalchemy import or_
                or_conditions = [File.mime_type.ilike(tf) for tf in type_map[file_type]]
                file_conditions.append(or_(*or_conditions))

        file_result = await self.db.execute(
            select(File).where(and_(*file_conditions)).limit(limit)
        )
        files = file_result.scalars().all()

        return {
            "folders": [self._folder_to_dict(f) for f in folders],
            "files": [self._file_to_dict(f) for f in files],
        }

    # ===== 上传相关 =====
    async def upload_small_file(self, user_id: str, folder_id: Optional[str], name: str, size: int, storage_key: str, mime_type: Optional[str] = None, file_hash: Optional[str] = None) -> File:
        """小文件上传完成后创建记录"""
        uid = uuid.UUID(user_id)

        # 检查存储空间
        await self._check_storage(uid, size)

        extension = name.rsplit(".", 1)[-1] if "." in name else None

        file = File(
            user_id=uid,
            folder_id=uuid.UUID(folder_id) if folder_id else None,
            name=name,
            extension=extension,
            mime_type=mime_type,
            size=size,
            storage_key=storage_key,
            file_hash=file_hash,
        )
        self.db.add(file)

        # 更新用户存储空间
        user_result = await self.db.execute(select(User).where(User.id == uid))
        user = user_result.scalars().first()
        if user:
            user.storage_used += size

        await self.db.flush()
        return file

    async def create_upload_session(self, user_id: str, upload_id: str, storage_key: str, file_name: str, folder_id: Optional[str], total_chunks: int, file_size: int, file_hash: Optional[str] = None) -> UploadSession:
        """创建上传会话"""
        uid = uuid.UUID(user_id)

        # 检查存储空间
        await self._check_storage(uid, file_size)

        session = UploadSession(
            user_id=uid,
            upload_id=upload_id,
            storage_key=storage_key,
            file_name=file_name,
            folder_id=uuid.UUID(folder_id) if folder_id else None,
            total_chunks=total_chunks,
            file_size=file_size,
            file_hash=file_hash,
            status="uploading",
            expires_at=datetime.now(timezone.utc) + __import__("datetime").timedelta(hours=24),
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_upload_session(self, upload_id: str, user_id: str) -> UploadSession:
        """获取上传会话"""
        uid = uuid.UUID(user_id)
        result = await self.db.execute(
            select(UploadSession).where(
                and_(UploadSession.upload_id == upload_id, UploadSession.user_id == uid)
            )
        )
        session = result.scalars().first()
        if not session:
            raise AppException(code="UPLOAD_SESSION_NOT_FOUND", message="上传会话不存在", status_code=404)
        if session.status == "expired" or (session.expires_at and session.expires_at < datetime.now(timezone.utc)):
            raise AppException(code="UPLOAD_SESSION_EXPIRED", message="上传会话已过期", status_code=410)
        return session

    async def complete_upload(self, upload_id: str, user_id: str, name: str, folder_id: Optional[str], size: int, file_hash: Optional[str] = None) -> File:
        """完成分片上传，创建文件记录"""
        session = await self.get_upload_session(upload_id, user_id)
        uid = uuid.UUID(user_id)

        # 更新会话状态
        session.status = "completed"

        extension = name.rsplit(".", 1)[-1] if "." in name else None
        file = File(
            user_id=uid,
            folder_id=uuid.UUID(folder_id) if folder_id else None,
            name=name,
            extension=extension,
            size=size,
            storage_key=session.storage_key,
            file_hash=file_hash,
        )
        self.db.add(file)

        # 更新用户存储空间
        user_result = await self.db.execute(select(User).where(User.id == uid))
        user = user_result.scalars().first()
        if user:
            user.storage_used += size

        await self.db.flush()
        return file

    async def get_download_url(self, file_id: uuid.UUID, user_id: str) -> dict:
        """生成下载签名 URL"""
        file = await self._get_file(file_id, user_id)
        try:
            from app.utils.minio_client import get_presigned_url, get_bucket_name
            url = get_presigned_url(get_bucket_name(user_id), file.storage_key)
        except Exception:
            raise AppException(code="DOWNLOAD_FAILED", message="生成下载链接失败", status_code=500)

        return {"download_url": url, "expires_in": 3600}

    # ===== 内部方法 =====

    async def _get_file(self, file_id: uuid.UUID, user_id: str) -> File:
        uid = uuid.UUID(user_id)
        result = await self.db.execute(
            select(File).where(and_(File.id == file_id, File.user_id == uid, File.is_deleted == False))
        )
        file = result.scalars().first()
        if not file:
            raise AppException(code="FILE_NOT_FOUND", message="文件不存在", status_code=404)
        return file

    async def _get_folder(self, folder_id: uuid.UUID, user_id: str) -> Folder:
        uid = uuid.UUID(user_id)
        result = await self.db.execute(
            select(Folder).where(and_(Folder.id == folder_id, Folder.user_id == uid, Folder.is_deleted == False))
        )
        folder = result.scalars().first()
        if not folder:
            raise AppException(code="FOLDER_NOT_FOUND", message="文件夹不存在", status_code=404)
        return folder

    async def _check_file_name_conflict(self, user_id: uuid.UUID, folder_id: Optional[uuid.UUID], name: str, exclude_id: uuid.UUID | None = None):
        conditions = [File.user_id == user_id, File.name == name, File.is_deleted == False]
        if folder_id:
            conditions.append(File.folder_id == folder_id)
        else:
            conditions.append(File.folder_id == None)  # noqa: E711
        if exclude_id:
            conditions.append(File.id != exclude_id)
        result = await self.db.execute(select(File).where(and_(*conditions)))
        if result.scalars().first():
            raise AppException(code="NAME_CONFLICT", message="同级已存在同名文件", status_code=409)

    async def _check_storage(self, user_id: uuid.UUID, file_size: int):
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if user and user.storage_used + file_size > user.storage_quota:
            raise AppException(code="STORAGE_EXCEEDED", message="存储空间不足", status_code=403)

    @staticmethod
    def _file_to_dict(file: File) -> dict:
        return {
            "id": str(file.id), "user_id": str(file.user_id),
            "folder_id": str(file.folder_id) if file.folder_id else None,
            "name": file.name, "extension": file.extension,
            "mime_type": file.mime_type, "size": file.size,
            "storage_key": file.storage_key, "file_hash": file.file_hash,
            "created_at": file.created_at.isoformat() if file.created_at else None,
            "updated_at": file.updated_at.isoformat() if file.updated_at else None,
        }

    @staticmethod
    def _folder_to_dict(folder: Folder) -> dict:
        return {
            "id": str(folder.id), "user_id": str(folder.user_id),
            "parent_id": str(folder.parent_id) if folder.parent_id else None,
            "name": folder.name, "path": folder.path,
            "created_at": folder.created_at.isoformat() if folder.created_at else None,
            "updated_at": folder.updated_at.isoformat() if folder.updated_at else None,
        }
