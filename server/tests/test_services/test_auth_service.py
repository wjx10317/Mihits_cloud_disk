import pytest
from app.services.auth_service import AuthService
from app.utils.auth import hash_password


@pytest.mark.asyncio
async def test_register_success(db_session):
    service = AuthService(db_session)
    user = await service.register(
        email="new@example.com",
        username="newuser",
        password="Password123",
    )
    assert user is not None
    assert user.email == "new@example.com"
    assert user.username == "newuser"
    assert user.id is not None


@pytest.mark.asyncio
async def test_register_duplicate_email(db_session):
    service = AuthService(db_session)
    await service.register(email="dup@example.com", username="user1", password="Password123")
    await db_session.flush()

    with pytest.raises(ValueError, match="邮箱已注册"):
        await service.register(email="dup@example.com", username="user2", password="Password123")


@pytest.mark.asyncio
async def test_register_duplicate_username(db_session):
    service = AuthService(db_session)
    await service.register(email="a@example.com", username="sameuser", password="Password123")
    await db_session.flush()

    with pytest.raises(ValueError, match="用户名已存在"):
        await service.register(email="b@example.com", username="sameuser", password="Password123")


@pytest.mark.asyncio
async def test_login_success(db_session):
    service = AuthService(db_session)
    await service.register(email="user@example.com", username="testuser", password="Password123")
    await db_session.flush()

    result = await service.login(email="user@example.com", password="Password123")
    assert result["code"] == "SUCCESS"
    assert "access_token" in result["data"]
    assert "refresh_token" in result["data"]
    assert result["data"]["user"]["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(db_session):
    service = AuthService(db_session)
    await service.register(email="user@example.com", username="testuser", password="Password123")
    await db_session.flush()

    with pytest.raises(ValueError, match="邮箱或密码错误"):
        await service.login(email="user@example.com", password="WrongPassword1")


@pytest.mark.asyncio
async def test_login_user_not_found(db_session):
    service = AuthService(db_session)
    with pytest.raises(ValueError, match="邮箱或密码错误"):
        await service.login(email="nobody@example.com", password="Password123")


@pytest.mark.asyncio
async def test_refresh_tokens(db_session):
    service = AuthService(db_session)
    await service.register(email="refresh@example.com", username="refreshuser", password="Password123")
    await db_session.flush()

    login_result = await service.login(email="refresh@example.com", password="Password123")
    refresh_token = login_result["data"]["refresh_token"]

    result = await service.refresh_tokens(refresh_token)
    assert result["code"] == "SUCCESS"
    assert "access_token" in result["data"]
    assert "refresh_token" in result["data"]
