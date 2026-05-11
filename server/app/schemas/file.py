"""文件和文件夹相关的 Pydantic Schema"""
import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ===== 文件夹 Schema =====

class FolderCreate(BaseModel):
    parent_id: Optional[UUID] = None
    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if re.search(r'[\\/:*?"<>|]', v):
            raise ValueError("文件夹名不能包含特殊字符 \\ / : * ? \" < > |")
        v = v.strip()
        if not v:
            raise ValueError("文件夹名不能为空")
        return v


class FolderRename(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if re.search(r'[\\/:*?"<>|]', v):
            raise ValueError("文件夹名不能包含特殊字符 \\ / : * ? \" < > |")
        v = v.strip()
        if not v:
            raise ValueError("文件夹名不能为空")
        return v


class FolderInfo(BaseModel):
    id: UUID
    user_id: UUID
    parent_id: Optional[UUID] = None
    name: str
    path: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FolderTreeNode(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[UUID] = None
    children: list["FolderTreeNode"] = []

    model_config = {"from_attributes": True}


class BreadcrumbItem(BaseModel):
    id: UUID
    name: str


# ===== 文件 Schema =====

class FileCreate(BaseModel):
    folder_id: Optional[UUID] = None
    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if re.search(r'[\\/:*?"<>|]', v):
            raise ValueError("文件名不能包含特殊字符 \\ / : * ? \" < > |")
        v = v.strip()
        if not v:
            raise ValueError("文件名不能为空")
        return v


class FileRename(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if re.search(r'[\\/:*?"<>|]', v):
            raise ValueError("文件名不能包含特殊字符 \\ / : * ? \" < > |")
        v = v.strip()
        if not v:
            raise ValueError("文件名不能为空")
        return v


class FileInfo(BaseModel):
    id: UUID
    user_id: UUID
    folder_id: Optional[UUID] = None
    name: str
    extension: Optional[str] = None
    mime_type: Optional[str] = None
    size: int
    storage_key: str
    file_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FileListResponse(BaseModel):
    folders: list[FolderInfo]
    files: list[FileInfo]
    total: int
    page: int
    page_size: int


# ===== 移动/复制 Schema =====

class FileMoveRequest(BaseModel):
    file_ids: list[UUID] = []
    folder_ids: list[UUID] = []
    target_folder_id: Optional[UUID] = None


class FileCopyRequest(BaseModel):
    file_ids: list[UUID] = []
    folder_ids: list[UUID] = []
    target_folder_id: Optional[UUID] = None


# ===== 删除 Schema =====

class FileDeleteRequest(BaseModel):
    file_ids: list[UUID] = []
    folder_ids: list[UUID] = []


# ===== 回收站 Schema =====

class TrashRestoreRequest(BaseModel):
    items: list[dict]  # [{"id": "uuid", "type": "file|folder"}]


class TrashItemInfo(BaseModel):
    id: UUID
    name: str
    type: str  # file or folder
    size: int = 0
    original_path: str = ""
    deleted_at: Optional[datetime] = None


# ===== 搜索 Schema =====

class SearchResult(BaseModel):
    folders: list[FolderInfo]
    files: list[FileInfo]


# ===== 上传 Schema =====

class UploadInitRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    folder_id: Optional[UUID] = None
    size: int = Field(gt=0)
    file_hash: Optional[str] = None
    total_chunks: int = Field(gt=0, le=10000)


class UploadInitResponse(BaseModel):
    upload_id: str
    storage_key: str
    chunk_size: int = 5 * 1024 * 1024  # 5MB


class UploadCompleteRequest(BaseModel):
    upload_id: str
    name: str
    folder_id: Optional[UUID] = None
    size: int = Field(gt=0)
    file_hash: Optional[str] = None


class ChunkStatusResponse(BaseModel):
    upload_id: str
    completed_chunks: list[int]
    total_chunks: int
    status: str  # uploading/completed/expired


class DownloadResponse(BaseModel):
    download_url: str
    expires_in: int = 3600
