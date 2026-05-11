"""M4 存储空间模块测试"""
import pytest

from app.services.storage_service import StorageService
from app.services.auth_service import AuthService
from app.models.folder import File, Folder
from app.models.user import User
from app.utils.auth import hash_password
from app.middleware.error_handler import AppException
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """创建测试用户"""
    user = User(
        email="storage@test.com",
        username="storageuser",
        password_hash=hash_password("Test123456"),
    )
    db_session.add(user)
    await db_session.flush()
    return user


class TestStorageService:
    """存储空间服务测试"""

    @pytest.mark.asyncio
    async def test_get_storage_usage_empty(self, db_session, test_user):
        """测试空用户的存储使用情况"""
        service = StorageService(db_session)
        result = await service.get_storage_usage(str(test_user.id))

        assert result["total_quota"] == 5 * 1024 * 1024 * 1024
        assert result["used_quota"] == 0
        assert result["available_quota"] == 5 * 1024 * 1024 * 1024
        assert result["usage_percentage"] == 0
        breakdown = result["category_breakdown"]
        assert breakdown["image"] == 0
        assert breakdown["video"] == 0

    @pytest.mark.asyncio
    async def test_get_storage_usage_with_files(self, db_session, test_user):
        """测试有文件时的存储使用情况"""
        folder = Folder(
            user_id=test_user.id,
            name="test-folder",
            path="/test-folder",
        )
        db_session.add(folder)
        await db_session.flush()

        files = [
            File(user_id=test_user.id, folder_id=folder.id, name="photo.jpg",
                 extension="jpg", mime_type="image/jpeg", size=1024 * 1024,
                 storage_key="key1"),
            File(user_id=test_user.id, folder_id=folder.id, name="video.mp4",
                 extension="mp4", mime_type="video/mp4", size=5 * 1024 * 1024,
                 storage_key="key2"),
            File(user_id=test_user.id, folder_id=folder.id, name="doc.pdf",
                 extension="pdf", mime_type="application/pdf", size=512 * 1024,
                 storage_key="key3"),
            File(user_id=test_user.id, folder_id=folder.id, name="song.mp3",
                 extension="mp3", mime_type="audio/mpeg", size=2 * 1024 * 1024,
                 storage_key="key4"),
            File(user_id=test_user.id, folder_id=folder.id, name="archive.zip",
                 extension="zip", mime_type="application/zip", size=3 * 1024 * 1024,
                 storage_key="key5"),
        ]
        for f in files:
            db_session.add(f)
        await db_session.flush()

        total_size = sum(f.size for f in files)
        test_user.storage_used = total_size
        await db_session.flush()

        service = StorageService(db_session)
        result = await service.get_storage_usage(str(test_user.id))

        assert result["used_quota"] == total_size
        breakdown = result["category_breakdown"]
        assert breakdown["image"] == 1024 * 1024
        assert breakdown["video"] == 5 * 1024 * 1024
        assert breakdown["document"] == 512 * 1024
        assert breakdown["audio"] == 2 * 1024 * 1024
        assert breakdown["other"] == 3 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_check_storage_enough(self, db_session, test_user):
        """测试存储空间足够时通过检查"""
        service = StorageService(db_session)
        result = await service.check_storage(str(test_user.id), 1024)
        assert result is True

    @pytest.mark.asyncio
    async def test_check_storage_exceeded(self, db_session, test_user):
        """测试存储空间不足时抛异常"""
        service = StorageService(db_session)
        with pytest.raises(AppException) as exc_info:
            await service.check_storage(str(test_user.id), 6 * 1024 * 1024 * 1024)
        assert exc_info.value.code == "STORAGE_EXCEEDED"

    @pytest.mark.asyncio
    async def test_update_storage_used_increase(self, db_session, test_user):
        """测试增加存储用量"""
        service = StorageService(db_session)
        new_used = await service.update_storage_used(str(test_user.id), 1024 * 1024)
        assert new_used == 1024 * 1024

    @pytest.mark.asyncio
    async def test_update_storage_used_decrease(self, db_session, test_user):
        """测试减少存储用量"""
        service = StorageService(db_session)
        await service.update_storage_used(str(test_user.id), 5 * 1024 * 1024)
        new_used = await service.update_storage_used(str(test_user.id), -2 * 1024 * 1024)
        assert new_used == 3 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_update_storage_used_not_below_zero(self, db_session, test_user):
        """测试存储用量不会低于 0"""
        service = StorageService(db_session)
        new_used = await service.update_storage_used(str(test_user.id), -100)
        assert new_used == 0

    @pytest.mark.asyncio
    async def test_update_quota_success(self, db_session, test_user):
        """测试成功更新配额"""
        service = StorageService(db_session)
        result = await service.update_quota(str(test_user.id), 10 * 1024 * 1024 * 1024)
        assert result["storage_quota"] == 10 * 1024 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_update_quota_too_small(self, db_session, test_user):
        """测试新配额小于已使用空间"""
        service = StorageService(db_session)
        test_user.storage_used = 3 * 1024 * 1024 * 1024
        await db_session.flush()

        with pytest.raises(AppException) as exc_info:
            await service.update_quota(str(test_user.id), 1 * 1024 * 1024 * 1024)
        assert exc_info.value.code == "QUOTA_TOO_SMALL"

    @pytest.mark.asyncio
    async def test_format_size(self):
        """测试文件大小格式化"""
        assert StorageService._format_size(0) == "0.0B"
        assert "KB" in StorageService._format_size(1024)
        assert "MB" in StorageService._format_size(1024 * 1024)
        assert "GB" in StorageService._format_size(1024 * 1024 * 1024)

    @pytest.mark.asyncio
    async def test_deleted_files_not_in_breakdown(self, db_session, test_user):
        """测试已删除文件不计入分类统计"""
        folder = Folder(
            user_id=test_user.id, name="test", path="/test",
        )
        db_session.add(folder)
        await db_session.flush()

        deleted_file = File(
            user_id=test_user.id, folder_id=folder.id, name="deleted.jpg",
            extension="jpg", mime_type="image/jpeg", size=5 * 1024 * 1024,
            storage_key="deleted-key", is_deleted=True,
        )
        db_session.add(deleted_file)
        await db_session.flush()

        test_user.storage_used = 0
        await db_session.flush()

        service = StorageService(db_session)
        result = await service.get_storage_usage(str(test_user.id))
        assert result["category_breakdown"]["image"] == 0
