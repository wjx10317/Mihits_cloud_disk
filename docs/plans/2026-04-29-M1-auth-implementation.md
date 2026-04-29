# M1 用户认证模块 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现网盘客户端的用户注册、登录和会话管理功能，包括后端 API 和前端页面。

**Architecture:** 后端 FastAPI 提供 JWT 双 Token 认证 API（注册/登录/刷新/登出），前端 Electron + Vue 3 实现登录注册页面和 Pinia 用户状态管理，Token 加密存储在 electron-store。

**Tech Stack:** FastAPI 0.109+ / SQLAlchemy 2.0 / Alembic / PyJWT / bcrypt / slowapi / PostgreSQL 16 / Vue 3 / Element Plus / Pinia / Axios / electron-store / TypeScript

---

## Task 1: 初始化项目结构与 Git 仓库

**Files:**
- Create: `server/app/__init__.py`
- Create: `server/app/main.py`
- Create: `server/app/config.py`
- Create: `server/app/database.py`
- Create: `server/requirements.txt`
- Create: `server/pyproject.toml`
- Create: `server/alembic.ini`
- Create: `.gitignore`
- Create: `README.md`

**Step 1: 初始化 Git 仓库**
```bash
cd d:\colin\ai_coding\Mihits_wangpan
git init
```

**Step 2: 创建 .gitignore**
```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/
env/
*.egg

# Node
node_modules/
dist-electron/
dist/
.output/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Env
.env
.env.local
.env.production

# Logs
*.log
logs/

# Testing
.coverage
htmlcov/
.pytest_cache/

# Electron
release/

# WorkBuddy
.workbuddy/
```

**Step 3: 创建后端项目骨架**

`server/app/__init__.py` — 空文件

`server/app/config.py`:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Mihits Cloud"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mihits_cloud"

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_PREFIX: str = "mihits-"
    MINIO_SECURE: bool = False

    # Rate Limiting
    LOGIN_RATE_LIMIT: str = "5/minute"

    # Storage
    DEFAULT_STORAGE_QUOTA: int = 5 * 1024 * 1024 * 1024  # 5GB

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

`server/app/database.py`:
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

`server/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
```

`server/requirements.txt`:
```
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy[asyncio]==2.0.35
asyncpg==0.29.0
alembic==1.13.2
pydantic[email]==2.9.2
pydantic-settings==2.5.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
slowapi==0.1.9
httpx==0.27.2
pytest==8.3.3
pytest-asyncio==0.24.0
pytest-cov==5.0.0
aiosqlite==0.20.0
```

`server/pyproject.toml`:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=app --cov-report=term-missing"
```

**Step 4: 创建 Alembic 配置**

`server/alembic.ini`:
```ini
[alembic]
script_location = migrations
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/mihits_cloud

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

**Step 5: 创建 README.md**
```markdown
# Mihits 网盘客户端

桌面端网盘应用，基于 Electron + Vue 3 + FastAPI。

## 技术栈

- 前端：Vue 3 + Element Plus + Pinia + TypeScript
- 桌面：Electron (electron-vite)
- 后端：FastAPI + SQLAlchemy 2.0 + PostgreSQL
- 存储：MinIO

## 开发

详见 `docs/plans/` 目录下的设计文档。
```

**Step 6: 提交**
```bash
git add .
git commit -m "chore: initialize project structure with FastAPI backend skeleton"
```

---

## Task 2: 后端 — 用户模型与数据库迁移

**Files:**
- Create: `server/app/models/__init__.py`
- Create: `server/app/models/user.py`
- Create: `server/migrations/env.py`
- Create: `server/migrations/versions/001_create_users.py`
- Test: `server/tests/__init__.py`
- Test: `server/tests/conftest.py`
- Test: `server/tests/test_models/test_user.py`

**Step 1: 写失败测试 — 用户模型**

`server/tests/__init__.py` — 空文件

`server/tests/conftest.py`:
```python
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database import Base


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
```

`server/tests/test_models/__init__.py` — 空文件

`server/tests/test_models/test_user.py`:
```python
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
```

**Step 2: 运行测试确认失败**
```bash
cd server && python -m pytest tests/test_models/test_user.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'app.models.user'`

**Step 3: 实现用户模型**

`server/app/models/__init__.py`:
```python
from app.models.user import User

__all__ = ["User"]
```

`server/app/models/user.py`:
```python
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, BigInteger, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_quota: Mapped[int] = mapped_column(BigInteger, nullable=False, default=5368709120)
    storage_used: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<User {self.username}>"
```

**Step 4: 运行测试确认通过**
```bash
cd server && python -m pytest tests/test_models/test_user.py -v
```
Expected: PASS

**Step 5: 提交**
```bash
git add .
git commit -m "feat: add User model with email/username uniqueness constraints"
```

---

## Task 3: 后端 — Pydantic Schema（请求/响应模型）

**Files:**
- Create: `server/app/schemas/__init__.py`
- Create: `server/app/schemas/auth.py`
- Test: `server/tests/test_schemas/test_auth.py`

**Step 1: 写失败测试 — Schema 校验**

`server/tests/test_schemas/__init__.py` — 空文件

`server/tests/test_schemas/test_auth.py`:
```python
import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest, LoginRequest


def test_register_request_valid():
    req = RegisterRequest(
        email="user@example.com",
        username="testuser",
        password="Password123",
    )
    assert req.email == "user@example.com"
    assert req.username == "testuser"


def test_register_request_invalid_email():
    with pytest.raises(ValidationError):
        RegisterRequest(email="not-an-email", username="testuser", password="Password123")


def test_register_request_short_username():
    with pytest.raises(ValidationError):
        RegisterRequest(email="user@example.com", username="ab", password="Password123")


def test_register_request_invalid_username_chars():
    with pytest.raises(ValidationError):
        RegisterRequest(email="user@example.com", username="user!@#", password="Password123")


def test_register_request_weak_password():
    with pytest.raises(ValidationError):
        RegisterRequest(email="user@example.com", username="testuser", password="weak")


def test_login_request_valid():
    req = LoginRequest(email="user@example.com", password="Password123")
    assert req.email == "user@example.com"


def test_login_request_invalid_email():
    with pytest.raises(ValidationError):
        LoginRequest(email="not-email", password="Password123")
```

**Step 2: 运行测试确认失败**
```bash
cd server && python -m pytest tests/test_schemas/test_auth.py -v
```
Expected: FAIL — `ModuleNotFoundError`

**Step 3: 实现 Schema**

`server/app/schemas/__init__.py` — 空文件

`server/app/schemas/auth.py`:
```python
import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8, max_length=32)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("密码必须包含至少一个大写字母")
        if not re.search(r"[a-z]", v):
            raise ValueError("密码必须包含至少一个小写字母")
        if not re.search(r"[0-9]", v):
            raise ValueError("密码必须包含至少一个数字")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserInfo(BaseModel):
    id: UUID
    email: str
    username: str
    storage_quota: int
    storage_used: int

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserInfo


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class AuthResponse(BaseModel):
    code: str
    message: str
    data: Optional[dict] = None
```

**Step 4: 运行测试确认通过**
```bash
cd server && python -m pytest tests/test_schemas/test_auth.py -v
```
Expected: PASS

**Step 5: 提交**
```bash
git add .
git commit -m "feat: add auth Pydantic schemas with validation rules"
```

---

## Task 4: 后端 — JWT 工具与密码哈希

**Files:**
- Create: `server/app/utils/__init__.py`
- Create: `server/app/utils/auth.py`
- Test: `server/tests/test_utils/test_auth.py`

**Step 1: 写失败测试 — JWT 与密码**

`server/tests/test_utils/__init__.py` — 空文件

`server/tests/test_utils/test_auth.py`:
```python
import pytest
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_hash_and_verify_password():
    password = "MyPassword123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False


def test_create_access_token():
    token = create_access_token(user_id="test-uuid", email="user@example.com")
    assert isinstance(token, str)
    payload = decode_token(token)
    assert payload["sub"] == "test-uuid"
    assert payload["email"] == "user@example.com"
    assert payload["type"] == "access"


def test_create_refresh_token():
    token = create_refresh_token(user_id="test-uuid")
    payload = decode_token(token)
    assert payload["sub"] == "test-uuid"
    assert payload["type"] == "refresh"


def test_decode_expired_token():
    from app.utils.auth import create_access_token
    import time

    # 创建一个立即过期的 token
    token = create_access_token(user_id="test-uuid", email="user@example.com", expires_minutes=-1)
    with pytest.raises(Exception):
        decode_token(token)


def test_decode_invalid_token():
    with pytest.raises(Exception):
        decode_token("invalid.token.string")
```

**Step 2: 运行测试确认失败**
```bash
cd server && python -m pytest tests/test_utils/test_auth.py -v
```
Expected: FAIL

**Step 3: 实现工具函数**

`server/app/utils/__init__.py` — 空文件

`server/app/utils/auth.py`:
```python
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: str, email: str, expires_minutes: int | None = None
) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": user_id,
        "email": email,
        "type": "access",
        "exp": expires,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str, expires_days: int | None = None) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        days=expires_days or settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": expires,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Token 无效: {str(e)}") from e
```

**Step 4: 运行测试确认通过**
```bash
cd server && python -m pytest tests/test_utils/test_auth.py -v
```
Expected: PASS

**Step 5: 提交**
```bash
git add .
git commit -m "feat: add JWT token creation/verification and password hashing utilities"
```

---

## Task 5: 后端 — 认证服务层

**Files:**
- Create: `server/app/services/__init__.py`
- Create: `server/app/services/auth_service.py`
- Test: `server/tests/test_services/test_auth_service.py`

**Step 1: 写失败测试 — 认证服务**

`server/tests/test_services/__init__.py` — 空文件

`server/tests/test_services/test_auth_service.py`:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.auth_service import AuthService


@pytest.fixture
def mock_db():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def auth_service(mock_db):
    return AuthService(mock_db)


@pytest.mark.asyncio
async def test_register_success(auth_service, mock_db):
    # mock 不存在重复用户
    mock_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))))

    result = await auth_service.register(
        email="new@example.com",
        username="newuser",
        password="Password123",
    )
    assert result is not None
    assert mock_db.add.called


@pytest.mark.asyncio
async def test_register_duplicate_email(auth_service, mock_db):
    from app.models.user import User
    existing = User(email="exists@example.com", username="exists", password_hash="h")

    mock_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=existing)))))

    with pytest.raises(ValueError, match="邮箱已注册"):
        await auth_service.register(email="exists@example.com", username="new", password="Password123")


@pytest.mark.asyncio
async def test_register_duplicate_username(auth_service, mock_db):
    from app.models.user import User
    existing = User(email="other@example.com", username="exists", password_hash="h")

    # 第一次查询 email 不存在，第二次查询 username 存在
    call_count = 0
    async def mock_execute(stmt):
        nonlocal call_count
        call_count += 1
        result = MagicMock()
        result.scalars.return_value.first.return_value = existing if call_count == 2 else None
        return result

    mock_db.execute = mock_execute

    with pytest.raises(ValueError, match="用户名已存在"):
        await auth_service.register(email="new@example.com", username="exists", password="Password123")


@pytest.mark.asyncio
async def test_login_success(auth_service, mock_db):
    from app.models.user import User
    from app.utils.auth import hash_password

    user = User(email="user@example.com", username="testuser", password_hash=hash_password("Password123"))

    mock_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=user)))))

    result = await auth_service.login(email="user@example.com", password="Password123")
    assert result["code"] == "SUCCESS"
    assert "access_token" in result["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(auth_service, mock_db):
    from app.models.user import User
    from app.utils.auth import hash_password

    user = User(email="user@example.com", username="testuser", password_hash=hash_password("Password123"))

    mock_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=user)))))

    with pytest.raises(ValueError, match="邮箱或密码错误"):
        await auth_service.login(email="user@example.com", password="WrongPassword123")


@pytest.mark.asyncio
async def test_login_user_not_found(auth_service, mock_db):
    mock_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))))

    with pytest.raises(ValueError, match="邮箱或密码错误"):
        await auth_service.login(email="nobody@example.com", password="Password123")
```

**Step 2: 运行测试确认失败**
```bash
cd server && python -m pytest tests/test_services/test_auth_service.py -v
```
Expected: FAIL

**Step 3: 实现认证服务**

`server/app/services/__init__.py` — 空文件

`server/app/services/auth_service.py`:
```python
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.schemas.auth import UserInfo
from app.utils.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, email: str, username: str, password: str) -> User:
        # 检查邮箱唯一性
        result = await self.db.execute(select(User).where(User.email == email))
        if result.scalars().first():
            raise ValueError("邮箱已注册")

        # 检查用户名唯一性
        result = await self.db.execute(select(User).where(User.username == username))
        if result.scalars().first():
            raise ValueError("用户名已存在")

        # 创建用户
        user = User(
            email=email,
            username=username,
            password_hash=hash_password(password),
            storage_quota=settings.DEFAULT_STORAGE_QUOTA,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def login(self, email: str, password: str) -> dict:
        # 查询用户
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if not user or not verify_password(password, user.password_hash):
            raise ValueError("邮箱或密码错误")

        if not user.is_active:
            raise ValueError("账号已被禁用")

        # 签发 Token
        user_id_str = str(user.id)
        access_token = create_access_token(user_id_str, user.email)
        refresh_token = create_refresh_token(user_id_str)

        return {
            "code": "SUCCESS",
            "message": "登录成功",
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": UserInfo.model_validate(user).model_dump(),
            },
        }

    async def refresh_tokens(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
        except ValueError:
            raise ValueError("刷新令牌无效")

        if payload.get("type") != "refresh":
            raise ValueError("令牌类型错误")

        user_id = payload.get("sub")
        result = await self.db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalars().first()

        if not user or not user.is_active:
            raise ValueError("用户不存在或已被禁用")

        new_access = create_access_token(str(user.id), user.email)
        new_refresh = create_refresh_token(str(user.id))

        return {
            "code": "SUCCESS",
            "message": "刷新成功",
            "data": {
                "access_token": new_access,
                "refresh_token": new_refresh,
                "token_type": "Bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            },
        }
```

**Step 4: 运行测试确认通过**
```bash
cd server && python -m pytest tests/test_services/test_auth_service.py -v
```
Expected: PASS

**Step 5: 提交**
```bash
git add .
git commit -m "feat: add AuthService with register, login, and refresh token logic"
```

---

## Task 6: 后端 — 认证路由与中间件

**Files:**
- Create: `server/app/routers/__init__.py`
- Create: `server/app/routers/auth.py`
- Create: `server/app/middleware/__init__.py`
- Create: `server/app/middleware/auth.py`
- Create: `server/app/middleware/error_handler.py`
- Modify: `server/app/main.py`
- Test: `server/tests/test_routers/test_auth.py`

**Step 1: 写失败测试 — 认证 API 端点**

`server/tests/test_routers/__init__.py` — 空文件

`server/tests/test_routers/test_auth.py`:
```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_register_api(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "Password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "SUCCESS"
    assert data["message"] == "注册成功"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    # 第一次注册
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "username": "user1", "password": "Password123"},
    )
    # 重复邮箱
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "username": "user2", "password": "Password123"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_login_api(client):
    # 先注册
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "username": "loginuser", "password": "Password123"},
    )
    # 登录
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "Password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "SUCCESS"
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@example.com", "username": "wronguser", "password": "Password123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "WrongPassword1"},
    )
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_refresh_token_api(client):
    # 注册并登录
    await client.post(
        "/api/v1/auth/register",
        json={"email": "refresh@example.com", "username": "refreshuser", "password": "Password123"},
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "refresh@example.com", "password": "Password123"},
    )
    refresh_token = login_resp.json()["data"]["refresh_token"]

    # 刷新
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
```

**Step 2: 运行测试确认失败**
```bash
cd server && python -m pytest tests/test_routers/test_auth.py -v
```
Expected: FAIL

**Step 3: 实现路由和中间件**

`server/app/routers/__init__.py` — 空文件

`server/app/middleware/__init__.py` — 空文件

`server/app/middleware/error_handler.py`:
```python
from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
    )
```

`server/app/middleware/auth.py`:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.auth import decode_token

security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="TOKEN_INVALID")
        return payload["sub"]
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="TOKEN_INVALID")
```

`server/app/routers/auth.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest, AuthResponse
from app.services.auth_service import AuthService
from app.middleware.error_handler import AppException

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        user = await service.register(req.email, req.username, req.password)
        await db.commit()
        return {"code": "SUCCESS", "message": "注册成功"}
    except ValueError as e:
        error_msg = str(e)
        if "邮箱" in error_msg:
            raise AppException(code="EMAIL_ALREADY_EXISTS", message=error_msg, status_code=409)
        elif "用户名" in error_msg:
            raise AppException(code="USERNAME_ALREADY_EXISTS", message=error_msg, status_code=409)
        raise AppException(code="REGISTER_FAILED", message=error_msg, status_code=400)


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        result = await service.login(req.email, req.password)
        await db.commit()
        return result
    except ValueError as e:
        raise AppException(code="INVALID_CREDENTIALS", message=str(e), status_code=401)


@router.post("/refresh")
async def refresh_token(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        result = await service.refresh_tokens(req.refresh_token)
        await db.commit()
        return result
    except ValueError as e:
        raise AppException(code="TOKEN_INVALID", message=str(e), status_code=401)


@router.post("/logout")
async def logout():
    return {"code": "SUCCESS", "message": "退出成功"}
```

**Step 4: 更新 main.py 注册路由和异常处理器**

更新 `server/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth
from app.middleware.error_handler import AppException, app_exception_handler

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_exception_handler(AppException, app_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
```

**Step 5: 运行测试确认通过**
```bash
cd server && python -m pytest tests/test_routers/test_auth.py -v
```
Expected: PASS

**Step 6: 提交**
```bash
git add .
git commit -m "feat: add auth API routes with register, login, refresh, and logout endpoints"
```

---

## Task 7: 后端 — 集成测试与覆盖率确认

**Files:**
- Create: `server/tests/test_integration/test_auth_flow.py`

**Step 1: 写完整集成测试**

`server/tests/test_integration/__init__.py` — 空文件

`server/tests/test_integration/test_auth_flow.py`:
```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_full_auth_flow(client):
    """完整认证流程：注册 → 登录 → 刷新Token → 访问受保护资源"""
    # 1. 注册
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "flow@example.com", "username": "flowuser", "password": "FlowPass123"},
    )
    assert reg_resp.status_code == 200
    assert reg_resp.json()["code"] == "SUCCESS"

    # 2. 登录
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "flow@example.com", "password": "FlowPass123"},
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()["data"]
    assert "access_token" in login_data
    assert "refresh_token" in login_data
    assert login_data["user"]["email"] == "flow@example.com"

    # 3. 刷新 Token
    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_data["refresh_token"]},
    )
    assert refresh_resp.status_code == 200
    new_tokens = refresh_resp.json()["data"]
    assert new_tokens["access_token"] != login_data["access_token"]

    # 4. 登出
    logout_resp = await client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 200


@pytest.mark.asyncio
async def test_register_validation_errors(client):
    """注册参数校验"""
    # 无效邮箱
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "not-email", "username": "user1", "password": "Password123"},
    )
    assert resp.status_code == 422

    # 用户名太短
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "valid@example.com", "username": "ab", "password": "Password123"},
    )
    assert resp.status_code == 422

    # 弱密码
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "valid@example.com", "username": "validuser", "password": "weak"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(client):
    """无效 Refresh Token"""
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """登录不存在的用户"""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "Password123"},
    )
    assert resp.status_code == 401
```

**Step 2: 运行全部测试并检查覆盖率**
```bash
cd server && python -m pytest tests/ -v --cov=app --cov-report=term-missing
```
Expected: 全部 PASS，覆盖率 ≥ 91%

**Step 3: 提交**
```bash
git add .
git commit -m "test: add integration tests for complete auth flow with coverage verification"
```

---

## Task 8: 前端 — 初始化 Electron + Vue 3 项目

**Files:**
- Create: 前端项目脚手架（通过 electron-vite）

**Step 1: 使用 electron-vite 创建项目**
```bash
cd d:\colin\ai_coding\Mihits_wangpan
npm config set registry https://registry.npmmirror.com
npm create @quick-start/electron client -- --template vue-ts
```

**Step 2: 安装依赖**
```bash
cd client
npm install element-plus pinia vue-router@4 axios
npm install -D @types/node unplugin-auto-import unplugin-vue-components
```

**Step 3: 验证项目可启动**
```bash
cd client && npm run dev
```
Expected: Electron 窗口打开

**Step 4: 提交**
```bash
git add .
git commit -m "chore: initialize Electron + Vue 3 frontend with electron-vite"
```

---

## Task 9: 前端 — 路由、Pinia Store 和网络层

**Files:**
- Create: `client/src/router/index.ts`
- Create: `client/src/stores/user.ts`
- Create: `client/src/utils/request.ts`
- Create: `client/src/views/auth/LoginView.vue`
- Create: `client/src/views/auth/RegisterView.vue`

**Step 1: 创建路由**

`client/src/router/index.ts`:
```typescript
import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (!to.meta.requiresAuth && token && (to.name === 'Login' || to.name === 'Register')) {
    next('/')
  } else {
    next()
  }
})

export default router
```

**Step 2: 创建 Axios 封装**

`client/src/utils/request.ts`:
```typescript
import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const data = error.response?.data
    if (error.response?.status === 401) {
      const code = data?.code
      if (code === 'TOKEN_EXPIRED') {
        try {
          const refreshToken = localStorage.getItem('refresh_token')
          const res = await axios.post(
            `${request.defaults.baseURL}/api/v1/auth/refresh`,
            { refresh_token: refreshToken }
          )
          const { access_token, refresh_token } = res.data.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
          error.config.headers.Authorization = `Bearer ${access_token}`
          return request(error.config)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.hash = '#/login'
        }
      }
    }
    const message = data?.message || '网络连接异常，请检查网络设置'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
```

**Step 3: 创建用户 Store**

`client/src/stores/user.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'

export const useUserStore = defineStore('user', () => {
  const user = ref<UserInfo | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  const isLoggedIn = computed(() => !!accessToken.value)

  interface UserInfo {
    id: string
    email: string
    username: string
    storage_quota: number
    storage_used: number
  }

  async function login(email: string, password: string) {
    const res: any = await request.post('/api/v1/auth/login', { email, password })
    const { access_token, refresh_token, user: userInfo } = res.data
    accessToken.value = access_token
    refreshToken.value = refresh_token
    user.value = userInfo
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
  }

  async function register(email: string, username: string, password: string) {
    await request.post('/api/v1/auth/register', { email, username, password })
  }

  async function logout() {
    try {
      await request.post('/api/v1/auth/logout')
    } finally {
      accessToken.value = null
      refreshToken.value = null
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) throw new Error('No refresh token')
    const res: any = await request.post('/api/v1/auth/refresh', {
      refresh_token: refreshToken.value
    })
    const { access_token, refresh_token: new_refresh } = res.data
    accessToken.value = access_token
    refreshToken.value = new_refresh
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', new_refresh)
  }

  function loadFromStorage() {
    accessToken.value = localStorage.getItem('access_token')
    refreshToken.value = localStorage.getItem('refresh_token')
  }

  return { user, accessToken, refreshToken, isLoggedIn, login, register, logout, refreshAccessToken, loadFromStorage }
})
```

**Step 4: 创建登录页面**

`client/src/views/auth/LoginView.vue`:
```vue
<template>
  <div class="auth-container">
    <el-card class="auth-card">
      <template #header>
        <div class="auth-header">
          <h2>Mihits 网盘</h2>
          <p>登录你的账号</p>
        </div>
      </template>
      <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleLogin">
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱" size="large" prefix-icon="Message" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" size="large"
            prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleLogin"
            style="width: 100%">登录</el-button>
        </el-form-item>
      </el-form>
      <div class="auth-footer">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({ email: '', password: '' })

const rules = {
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email' as const, message: '请输入有效的邮箱地址', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.login(form.email, form.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.auth-card {
  width: 400px;
  border-radius: 12px;
}
.auth-header {
  text-align: center;
}
.auth-header h2 {
  margin: 0 0 8px;
  color: #303133;
}
.auth-header p {
  margin: 0;
  color: #909399;
}
.auth-footer {
  text-align: center;
  color: #909399;
}
.auth-footer a {
  color: #409eff;
  text-decoration: none;
}
</style>
```

**Step 5: 创建注册页面**

`client/src/views/auth/RegisterView.vue`:
```vue
<template>
  <div class="auth-container">
    <el-card class="auth-card">
      <template #header>
        <div class="auth-header">
          <h2>Mihits 网盘</h2>
          <p>创建新账号</p>
        </div>
      </template>
      <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleRegister">
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱" size="large" prefix-icon="Message" />
        </el-form-item>
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名（3-20位字母数字下划线）" size="large"
            prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码（8-32位，含大小写字母和数字）"
            size="large" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" size="large"
            prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleRegister"
            style="width: 100%">注册</el-button>
        </el-form-item>
      </el-form>
      <div class="auth-footer">
        已有账号？<router-link to="/login">立即登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  email: '',
  username: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email' as const, message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 32, message: '密码长度为8-32个字符', trigger: 'blur' },
    { pattern: /[A-Z]/, message: '密码必须包含至少一个大写字母', trigger: 'blur' },
    { pattern: /[a-z]/, message: '密码必须包含至少一个小写字母', trigger: 'blur' },
    { pattern: /[0-9]/, message: '密码必须包含至少一个数字', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.register(form.email, form.username, form.password)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.auth-card {
  width: 400px;
  border-radius: 12px;
}
.auth-header {
  text-align: center;
}
.auth-header h2 {
  margin: 0 0 8px;
  color: #303133;
}
.auth-header p {
  margin: 0;
  color: #909399;
}
.auth-footer {
  text-align: center;
  color: #909399;
}
.auth-footer a {
  color: #409eff;
  text-decoration: none;
}
</style>
```

**Step 6: 创建 HomeView 占位页面**

`client/src/views/HomeView.vue`:
```vue
<template>
  <div class="home">
    <el-container>
      <el-header>
        <span>Mihits 网盘</span>
        <el-button @click="handleLogout">退出登录</el-button>
      </el-header>
      <el-main>
        <h1>欢迎使用 Mihits 网盘</h1>
        <p>文件管理功能开发中...</p>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

async function handleLogout() {
  await userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.el-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}
.el-main {
  text-align: center;
  padding-top: 80px;
}
</style>
```

**Step 7: 提交**
```bash
git add .
git commit -m "feat: add Vue 3 auth views, router, Pinia user store, and Axios request layer"
```

---

## Task 10: 最终集成与 Git 推送

**Step 1: 验证后端测试覆盖率**
```bash
cd server && python -m pytest tests/ -v --cov=app --cov-report=term-missing
```
Expected: 覆盖率 ≥ 91%

**Step 2: 验证前端可构建**
```bash
cd client && npm run build
```
Expected: 构建成功

**Step 3: 最终提交**
```bash
git add .
git commit -m "chore: finalize M1 auth module implementation"
```

**Step 4: 推送到远程仓库**

需要用户提供远程仓库地址，例如：
```bash
git remote add origin <repository-url>
git branch -M main
git push -u origin main
```
