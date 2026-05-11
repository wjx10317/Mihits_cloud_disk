"""M2 文件管理模块测试"""
import pytest
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.folder import Folder, File, UploadSession
from app.models.user import User
from app.services.folder_service import FolderService
from app.services.file_service import FileService
from app.services.auth_service import AuthService
from app.utils.auth import hash_password
from app.middleware.error_handler import AppException


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """创建测试用户"""
    user = User(
        email="test@mihits.com",
        username="testuser",
        password_hash=hash_password("TestPass123"),
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
def user_id(test_user) -> str:
    return str(test_user.id)


# ===== 文件夹测试 =====

class TestFolderService:
    @pytest.mark.asyncio
    async def test_create_root_folder(self, db_session, test_user, user_id):
        service = FolderService(db_session)
        folder = await service.create_folder(user_id, None, "文档")
        assert folder.name == "文档"
        assert folder.path == "/文档"
        assert folder.parent_id is None

    @pytest.mark.asyncio
    async def test_create_subfolder(self, db_session, test_user, user_id):
        service = FolderService(db_session)
        parent = await service.create_folder(user_id, None, "文档")
        child = await service.create_folder(user_id, str(parent.id), "工作")
        assert child.parent_id == parent.id
        assert child.path == "/文档/工作"

    @pytest.mark.asyncio
    async def test_create_duplicate_folder_fails(self, db_session, test_user, user_id):
        service = FolderService(db_session)
        await service.create_folder(user_id, None, "文档")
        with pytest.raises(AppException) as exc_info:
            await service.create_folder(user_id, None, "文档")
        assert exc_info.value.code == "NAME_CONFLICT"

    @pytest.mark.asyncio
    async def test_rename_folder(self, db_session, test_user, user_id):
        service = FolderService(db_session)
        folder = await service.create_folder(user_id, None, "文档")
        renamed = await service.rename_folder(folder.id, user_id, "资料")
        assert renamed.name == "资料"
        assert renamed.path == "/资料"

    @pytest.mark.asyncio
    async def test_rename_folder_updates_children(self, db_session, test_user, user_id):
        service = FolderService(db_session)
        parent = await service.create_folder(user_id, None, "文档")
        child = await service.create_folder(user_id, str(parent.id), "工作")
        await service.rename_folder(parent.id, user_id, "资料")
        # 子文件夹路径应更新
        result = await db_session.execute(select(Folder).where(Folder.id == child.id))
        updated_child = result.scalars().first()
        assert "/资料/" in updated_child.path

    @pytest.mark.asyncio
    async def test_get_folder_tree(self, db_session, test_user, user_id):
        service = FolderService(db_session)
        await service.create_folder(user_id, None, "文档")
        await service.create_folder(user_id, None, "图片")
        tree = await service.get_folder_tree(user_id)
        assert len(tree) == 2

    @pytest.mark.asyncio
    async def test_get_breadcrumb(self, db_session, test_user, user_id):
        service = FolderService(db_session)
        parent = await service.create_folder(user_id, None, "文档")
        child = await service.create_folder(user_id, str(parent.id), "工作")
        breadcrumb = await service.get_breadcrumb(child.id, user_id)
        assert len(breadcrumb) == 2
        assert breadcrumb[0]["name"] == "文档"
        assert breadcrumb[1]["name"] == "工作"

    @pytest.mark.asyncio
    async def test_soft_delete_folder(self, db_session, test_user, user_id):
        service = FolderService(db_session)
        folder = await service.create_folder(user_id, None, "待删除")
        count = await service.delete_folders([str(folder.id)], user_id)
        assert count == 1
        # 验证已软删除
        result = await db_session.execute(select(Folder).where(Folder.id == folder.id))
        deleted = result.scalars().first()
        assert deleted.is_deleted is True
        assert deleted.deleted_at is not None


# ===== 文件测试 =====

class TestFileService:
    @pytest.mark.asyncio
    async def test_create_file(self, db_session, test_user, user_id):
        service = FileService(db_session)
        file = await service.create_file(user_id, None, "测试.txt")
        assert file.name == "测试.txt"
        assert file.extension == "txt"
        assert file.size == 0

    @pytest.mark.asyncio
    async def test_rename_file(self, db_session, test_user, user_id):
        service = FileService(db_session)
        file = await service.create_file(user_id, None, "旧名.txt")
        renamed = await service.rename_file(file.id, user_id, "新名.txt")
        assert renamed.name == "新名.txt"
        assert renamed.extension == "txt"

    @pytest.mark.asyncio
    async def test_list_files_empty(self, db_session, test_user, user_id):
        service = FileService(db_session)
        result = await service.list_files(user_id)
        assert result["total"] == 0
        assert len(result["files"]) == 0
        assert len(result["folders"]) == 0

    @pytest.mark.asyncio
    async def test_list_files_with_content(self, db_session, test_user, user_id):
        folder_service = FolderService(db_session)
        file_service = FileService(db_session)
        await folder_service.create_folder(user_id, None, "文档")
        await file_service.create_file(user_id, None, "测试.txt")
        result = await file_service.list_files(user_id)
        assert result["total"] == 2  # 1 folder + 1 file

    @pytest.mark.asyncio
    async def test_soft_delete_file(self, db_session, test_user, user_id):
        service = FileService(db_session)
        file = await service.create_file(user_id, None, "待删.txt")
        count = await service.delete_files([str(file.id)], user_id)
        assert count == 1
        result = await db_session.execute(select(File).where(File.id == file.id))
        deleted = result.scalars().first()
        assert deleted.is_deleted is True

    @pytest.mark.asyncio
    async def test_move_files(self, db_session, test_user, user_id):
        folder_service = FolderService(db_session)
        file_service = FileService(db_session)
        folder = await folder_service.create_folder(user_id, None, "目标")
        file = await file_service.create_file(user_id, None, "移动.txt")
        count = await file_service.move_files(
            user_id, [str(file.id)], [], str(folder.id)
        )
        assert count == 1
        result = await db_session.execute(select(File).where(File.id == file.id))
        moved = result.scalars().first()
        assert moved.folder_id == folder.id

    @pytest.mark.asyncio
    async def test_copy_files(self, db_session, test_user, user_id):
        folder_service = FolderService(db_session)
        file_service = FileService(db_session)
        folder = await folder_service.create_folder(user_id, None, "目标")
        file = await file_service.create_file(user_id, None, "复制.txt")
        count = await file_service.copy_files(
            user_id, [str(file.id)], str(folder.id)
        )
        assert count == 1

    @pytest.mark.asyncio
    async def test_search_files(self, db_session, test_user, user_id):
        service = FileService(db_session)
        await service.create_file(user_id, None, "项目报告.pdf")
        await service.create_file(user_id, None, "会议纪要.docx")
        result = await service.search_files(user_id, "项目")
        assert len(result["files"]) == 1
        assert result["files"][0]["name"] == "项目报告.pdf"


# ===== 回收站测试 =====

class TestTrashService:
    @pytest.mark.asyncio
    async def test_list_trash_empty(self, db_session, test_user, user_id):
        service = FileService(db_session)
        items = await service.list_trash(user_id)
        assert len(items) == 0

    @pytest.mark.asyncio
    async def test_restore_file(self, db_session, test_user, user_id):
        service = FileService(db_session)
        file = await service.create_file(user_id, None, "恢复.txt")
        await service.delete_files([str(file.id)], user_id)
        count = await service.restore_items(user_id, [{"id": str(file.id), "type": "file"}])
        assert count == 1
        result = await db_session.execute(select(File).where(File.id == file.id))
        restored = result.scalars().first()
        assert restored.is_deleted is False

    @pytest.mark.asyncio
    async def test_purge_file(self, db_session, test_user, user_id):
        service = FileService(db_session)
        file = await service.create_file(user_id, None, "彻底删除.txt")
        await service.delete_files([str(file.id)], user_id)
        count = await service.purge_items(user_id, [{"id": str(file.id), "type": "file"}])
        assert count == 1
        # 验证已从数据库删除
        result = await db_session.execute(select(File).where(File.id == file.id))
        assert result.scalars().first() is None

    @pytest.mark.asyncio
    async def test_empty_trash(self, db_session, test_user, user_id):
        service = FileService(db_session)
        file1 = await service.create_file(user_id, None, "文件1.txt")
        file2 = await service.create_file(user_id, None, "文件2.txt")
        await service.delete_files([str(file1.id), str(file2.id)], user_id)
        count = await service.empty_trash(user_id)
        assert count >= 2


# ===== 上传会话测试 =====

class TestUploadSession:
    @pytest.mark.asyncio
    async def test_create_upload_session(self, db_session, test_user, user_id):
        service = FileService(db_session)
        session = await service.create_upload_session(
            user_id=user_id,
            upload_id="test-upload-id-123",
            storage_key=f"{user_id}/test.mp4",
            file_name="test.mp4",
            folder_id=None,
            total_chunks=10,
            file_size=50 * 1024 * 1024,
            file_hash="abc123",
        )
        assert session.upload_id == "test-upload-id-123"
        assert session.status == "uploading"
        assert session.total_chunks == 10

    @pytest.mark.asyncio
    async def test_get_upload_session_not_found(self, db_session, test_user, user_id):
        service = FileService(db_session)
        with pytest.raises(AppException) as exc_info:
            await service.get_upload_session("nonexistent", user_id)
        assert exc_info.value.code == "UPLOAD_SESSION_NOT_FOUND"
