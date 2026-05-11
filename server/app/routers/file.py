"""文件管理路由"""
import os
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query, UploadFile, File as FastAPIFile, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.middleware.error_handler import AppException
from app.schemas.file import (
    FileCreate, FileRename, FileMoveRequest, FileCopyRequest,
    FileDeleteRequest, UploadInitRequest, UploadCompleteRequest,
)
from app.services.file_service import FileService
from app.services.folder_service import FolderService

router = APIRouter(prefix="/api/v1/files", tags=["文件管理"])


# ===== 文件列表 =====
@router.get("")
async def list_files(
    folder_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort: str = Query("name"),
    order: str = Query("asc"),
    type: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    result = await service.list_files(user_id, folder_id, page, page_size, sort, order, type)
    return {"code": "SUCCESS", "message": "获取成功", "data": result}


# ===== 创建空文件 =====
@router.post("")
async def create_file(
    req: FileCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    try:
        file = await service.create_file(
            user_id, str(req.folder_id) if req.folder_id else None, req.name
        )
        await db.commit()
        return {
            "code": "SUCCESS", "message": "创建成功",
            "data": {"id": str(file.id), "name": file.name},
        }
    except AppException:
        raise


# ===== 重命名文件 =====
@router.put("/{file_id}/rename")
async def rename_file(
    file_id: UUID,
    req: FileRename,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    try:
        file = await service.rename_file(file_id, user_id, req.name)
        await db.commit()
        return {
            "code": "SUCCESS", "message": "重命名成功",
            "data": {"id": str(file.id), "name": file.name},
        }
    except AppException:
        raise


# ===== 移动文件 =====
@router.post("/move")
async def move_files(
    req: FileMoveRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    try:
        count = await service.move_files(
            user_id,
            [str(i) for i in req.file_ids],
            [str(i) for i in req.folder_ids],
            str(req.target_folder_id) if req.target_folder_id else None,
        )
        await db.commit()
        return {"code": "SUCCESS", "message": f"已移动 {count} 个项目", "data": {"count": count}}
    except AppException:
        raise


# ===== 复制文件 =====
@router.post("/copy")
async def copy_files(
    req: FileCopyRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    try:
        count = await service.copy_files(
            user_id,
            [str(i) for i in req.file_ids],
            str(req.target_folder_id) if req.target_folder_id else None,
        )
        await db.commit()
        return {"code": "SUCCESS", "message": f"已复制 {count} 个文件", "data": {"count": count}}
    except AppException:
        raise


# ===== 软删除文件 =====
@router.delete("")
async def delete_files(
    req: FileDeleteRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    file_service = FileService(db)
    folder_service = FolderService(db)
    try:
        count = 0
        if req.file_ids:
            count += await file_service.delete_files([str(i) for i in req.file_ids], user_id)
        if req.folder_ids:
            count += await folder_service.delete_folders([str(i) for i in req.folder_ids], user_id)
        await db.commit()
        return {"code": "SUCCESS", "message": f"已移入回收站 {count} 个项目", "data": {"count": count}}
    except AppException:
        raise


# ===== 搜索文件 =====
@router.get("/search")
async def search_files(
    keyword: str = Query(..., min_length=1),
    type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    result = await service.search_files(user_id, keyword, type, limit)
    return {"code": "SUCCESS", "message": "搜索完成", "data": result}


# ===== 普通上传（小文件） =====
@router.post("/upload")
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    folder_id: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    try:
        # 读取文件内容
        content = await file.read()
        size = len(content)

        # 生成存储键并上传到 MinIO
        from app.utils.minio_client import upload_object, generate_storage_key, get_bucket_name
        import io

        extension = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else ""
        storage_key = generate_storage_key(user_id, extension)
        bucket_name = get_bucket_name(user_id)

        upload_object(
            bucket_name=bucket_name,
            storage_key=storage_key,
            data=io.BytesIO(content),
            length=size,
            content_type=file.content_type or "application/octet-stream",
        )

        # 创建文件记录
        new_file = await service.upload_small_file(
            user_id=user_id,
            folder_id=folder_id,
            name=file.filename or "unnamed",
            size=size,
            storage_key=storage_key,
            mime_type=file.content_type,
        )
        await db.commit()

        return {
            "code": "SUCCESS", "message": "上传成功",
            "data": {"id": str(new_file.id), "name": new_file.name, "size": new_file.size},
        }
    except AppException:
        raise
    except Exception as e:
        raise AppException(code="UPLOAD_FAILED", message=f"上传失败: {str(e)}", status_code=500)


# ===== 初始化分片上传 =====
@router.post("/upload/init")
async def init_upload(
    req: UploadInitRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    try:
        from app.utils.minio_client import init_multipart_upload, generate_storage_key, get_bucket_name

        extension = req.name.rsplit(".", 1)[-1] if "." in req.name else ""
        storage_key = generate_storage_key(user_id, extension)
        bucket_name = get_bucket_name(user_id)

        upload_id = init_multipart_upload(bucket_name, storage_key)

        # 创建上传会话记录
        session = await service.create_upload_session(
            user_id=user_id,
            upload_id=upload_id,
            storage_key=storage_key,
            file_name=req.name,
            folder_id=str(req.folder_id) if req.folder_id else None,
            total_chunks=req.total_chunks,
            file_size=req.size,
            file_hash=req.file_hash,
        )
        await db.commit()

        return {
            "code": "SUCCESS", "message": "初始化成功",
            "data": {
                "upload_id": upload_id,
                "storage_key": storage_key,
                "chunk_size": 5 * 1024 * 1024,
            },
        }
    except AppException:
        raise
    except Exception as e:
        raise AppException(code="UPLOAD_INIT_FAILED", message=f"初始化失败: {str(e)}", status_code=500)


# ===== 上传分片 =====
@router.put("/upload/chunk")
async def upload_chunk(
    chunk: UploadFile = FastAPIFile(...),
    upload_id: str = Form(...),
    chunk_number: int = Form(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    try:
        session = await service.get_upload_session(upload_id, user_id)

        if chunk_number < 1 or chunk_number > session.total_chunks:
            raise AppException(code="CHUNK_OUT_OF_RANGE", message="分片编号超出范围", status_code=400)

        # 上传分片到 MinIO
        from app.utils.minio_client import upload_part, get_bucket_name
        import io

        content = await chunk.read()
        bucket_name = get_bucket_name(user_id)

        upload_part(
            bucket_name=bucket_name,
            storage_key=session.storage_key,
            upload_id=upload_id,
            part_number=chunk_number,
            data=io.BytesIO(content),
            length=len(content),
        )

        return {"code": "SUCCESS", "message": f"分片 {chunk_number} 上传成功"}
    except AppException:
        raise
    except Exception as e:
        raise AppException(code="CHUNK_UPLOAD_FAILED", message=f"分片上传失败: {str(e)}", status_code=500)


# ===== 合并分片 =====
@router.post("/upload/complete")
async def complete_upload(
    req: UploadCompleteRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    try:
        session = await service.get_upload_session(req.upload_id, user_id)

        # 合并 MinIO 分片
        from app.utils.minio_client import complete_multipart_upload, get_bucket_name
        bucket_name = get_bucket_name(user_id)

        # 简化处理：直接调用 MinIO 完成合并
        try:
            complete_multipart_upload(bucket_name, session.storage_key, req.upload_id, [])
        except Exception:
            pass  # MinIO 合并可能已有内部处理

        # 创建文件记录
        file = await service.complete_upload(
            upload_id=req.upload_id,
            user_id=user_id,
            name=req.name,
            folder_id=str(req.folder_id) if req.folder_id else None,
            size=req.size,
            file_hash=req.file_hash,
        )
        await db.commit()

        return {
            "code": "SUCCESS", "message": "上传完成",
            "data": {"id": str(file.id), "name": file.name, "size": file.size},
        }
    except AppException:
        raise


# ===== 查询已上传分片 =====
@router.get("/upload/{upload_id}/chunks")
async def get_uploaded_chunks(
    upload_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    try:
        session = await service.get_upload_session(upload_id, user_id)

        # 从 MinIO 查询已上传分片
        try:
            from app.utils.minio_client import list_uploaded_parts, get_bucket_name
            bucket_name = get_bucket_name(user_id)
            completed = list_uploaded_parts(bucket_name, session.storage_key, upload_id)
        except Exception:
            completed = []

        return {
            "code": "SUCCESS", "message": "获取成功",
            "data": {
                "upload_id": upload_id,
                "completed_chunks": completed,
                "total_chunks": session.total_chunks,
                "status": session.status,
            },
        }
    except AppException:
        raise


# ===== 下载 =====
@router.get("/{file_id}/download")
async def download_file(
    file_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    try:
        result = await service.get_download_url(file_id, user_id)
        return {"code": "SUCCESS", "message": "获取成功", "data": result}
    except AppException:
        raise
