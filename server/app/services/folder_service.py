"""文件夹业务逻辑"""
import uuid
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.folder import Folder, File
from app.middleware.error_handler import AppException


class FolderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_folder(self, user_id: str, parent_id: Optional[str], name: str) -> Folder:
        """创建文件夹"""
        uid = uuid.UUID(user_id)

        # 构建路径
        if parent_id:
            parent = await self._get_folder(uuid.UUID(parent_id), user_id)
            path = f"{parent.path}/{name}"
        else:
            path = f"/{name}"

        # 检查同级重名
        await self._check_name_conflict(uid, parent_id, name)

        folder = Folder(
            user_id=uid,
            parent_id=uuid.UUID(parent_id) if parent_id else None,
            name=name,
            path=path,
        )
        self.db.add(folder)
        await self.db.flush()
        return folder

    async def rename_folder(self, folder_id: uuid.UUID, user_id: str, name: str) -> Folder:
        """重命名文件夹"""
        folder = await self._get_folder(folder_id, user_id)

        # 检查同级重名
        await self._check_name_conflict(
            folder.user_id,
            str(folder.parent_id) if folder.parent_id else None,
            name,
            exclude_id=folder.id,
        )

        old_name = folder.name
        folder.name = name
        # 更新路径：替换路径中旧名称
        old_path = folder.path
        parent_path = old_path[: old_path.rfind(f"/{old_name}")]
        folder.path = f"{parent_path}/{name}"

        # 递归更新子文件夹路径
        await self._update_children_paths(folder.id, old_path, folder.path)

        await self.db.flush()
        return folder

    async def get_folder_tree(self, user_id: str) -> list[dict]:
        """获取用户的完整目录树"""
        uid = uuid.UUID(user_id)
        result = await self.db.execute(
            select(Folder).where(
                and_(Folder.user_id == uid, Folder.is_deleted == False)
            ).order_by(Folder.name)
        )
        folders = result.scalars().all()

        # 构建树形结构
        folder_map = {}
        roots = []
        for f in folders:
            node = {"id": str(f.id), "name": f.name, "parent_id": str(f.parent_id) if f.parent_id else None, "children": []}
            folder_map[str(f.id)] = node

        for f in folders:
            node = folder_map[str(f.id)]
            if f.parent_id and str(f.parent_id) in folder_map:
                folder_map[str(f.parent_id)]["children"].append(node)
            else:
                roots.append(node)

        return roots

    async def get_breadcrumb(self, folder_id: uuid.UUID, user_id: str) -> list[dict]:
        """获取面包屑路径"""
        path_items = []
        current = await self._get_folder(folder_id, user_id)

        while current:
            path_items.insert(0, {"id": str(current.id), "name": current.name})
            if current.parent_id:
                current = await self._get_folder(current.parent_id, user_id)
            else:
                break

        return path_items

    async def delete_folders(self, folder_ids: list[str], user_id: str) -> int:
        """软删除文件夹"""
        from datetime import datetime, timezone
        uid = uuid.UUID(user_id)
        count = 0
        for fid_str in folder_ids:
            fid = uuid.UUID(fid_str)
            folder = await self._get_folder(fid, user_id)
            folder.is_deleted = True
            folder.deleted_at = datetime.now(timezone.utc)
            # 同时软删除子文件
            result = await self.db.execute(
                select(File).where(and_(File.folder_id == fid, File.is_deleted == False))
            )
            for f in result.scalars().all():
                f.is_deleted = True
                f.deleted_at = datetime.now(timezone.utc)
            count += 1
        await self.db.flush()
        return count

    async def _get_folder(self, folder_id: uuid.UUID, user_id: str) -> Folder:
        """获取文件夹，不存在则抛异常"""
        uid = uuid.UUID(user_id)
        result = await self.db.execute(
            select(Folder).where(
                and_(Folder.id == folder_id, Folder.user_id == uid, Folder.is_deleted == False)
            )
        )
        folder = result.scalars().first()
        if not folder:
            raise AppException(code="FOLDER_NOT_FOUND", message="文件夹不存在", status_code=404)
        return folder

    async def _check_name_conflict(
        self, user_id: uuid.UUID, parent_id: Optional[str], name: str, exclude_id: uuid.UUID | None = None
    ):
        """检查同级重名"""
        conditions = [
            Folder.user_id == user_id,
            Folder.name == name,
            Folder.is_deleted == False,
        ]
        if parent_id:
            conditions.append(Folder.parent_id == uuid.UUID(parent_id))
        else:
            conditions.append(Folder.parent_id == None)  # noqa: E711
        if exclude_id:
            conditions.append(Folder.id != exclude_id)

        result = await self.db.execute(select(Folder).where(and_(*conditions)))
        if result.scalars().first():
            raise AppException(code="NAME_CONFLICT", message="同级已存在同名文件夹", status_code=409)

    async def _update_children_paths(self, parent_id: uuid.UUID, old_path: str, new_path: str):
        """递归更新子文件夹路径"""
        result = await self.db.execute(
            select(Folder).where(
                and_(Folder.parent_id == parent_id, Folder.is_deleted == False)
            )
        )
        children = result.scalars().all()
        for child in children:
            child.path = child.path.replace(old_path, new_path, 1)
            await self._update_children_paths(child.id, old_path, new_path)
