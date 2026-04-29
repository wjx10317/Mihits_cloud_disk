import pytest
from app.models.user import User


@pytest.mark.asyncio
async def test_create_user(db_session):
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
    )
    db_session.add(user)
    await db_session.flush()

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.storage_quota == 5368709120  # 5GB
    assert user.storage_used == 0
    assert user.is_active is True


@pytest.mark.asyncio
async def test_user_email_unique(db_session):
    from sqlalchemy.exc import IntegrityError

    user1 = User(email="same@example.com", username="user1", password_hash="h1")
    user2 = User(email="same@example.com", username="user2", password_hash="h2")
    db_session.add(user1)
    await db_session.flush()

    db_session.add(user2)
    with pytest.raises(IntegrityError):
        await db_session.flush()


@pytest.mark.asyncio
async def test_user_username_unique(db_session):
    from sqlalchemy.exc import IntegrityError

    user1 = User(email="a@example.com", username="sameuser", password_hash="h1")
    user2 = User(email="b@example.com", username="sameuser", password_hash="h2")
    db_session.add(user1)
    await db_session.flush()

    db_session.add(user2)
    with pytest.raises(IntegrityError):
        await db_session.flush()
