"""MinIO 客户端封装 - 对象存储操作"""
import io
import uuid
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from app.config import settings


def get_minio_client() -> Minio:
    """获取 MinIO 客户端实例"""
    return Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


def get_bucket_name(user_id: str) -> str:
    """获取用户桶名"""
    return f"{settings.MINIO_BUCKET_PREFIX}{user_id.replace('-', '')}"


def ensure_bucket(client: Minio, bucket_name: str) -> None:
    """确保桶存在"""
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)


def generate_storage_key(user_id: str, extension: str = "") -> str:
    """生成唯一存储键"""
    file_id = str(uuid.uuid4())
    if extension:
        return f"{user_id}/{file_id}.{extension}"
    return f"{user_id}/{file_id}"


def upload_object(
    bucket_name: str,
    storage_key: str,
    data: BinaryIO,
    length: int,
    content_type: str = "application/octet-stream",
) -> str:
    """上传对象到 MinIO"""
    client = get_minio_client()
    ensure_bucket(client, bucket_name)
    client.put_object(
        bucket_name=bucket_name,
        object_name=storage_key,
        data=data,
        length=length,
        content_type=content_type,
    )
    return storage_key


def get_presigned_url(bucket_name: str, storage_key: str, expires_hours: int = 1) -> str:
    """生成预签名下载 URL"""
    from datetime import timedelta
    client = get_minio_client()
    return client.presigned_get_object(
        bucket_name=bucket_name,
        object_name=storage_key,
        expires=timedelta(hours=expires_hours),
    )


def delete_object(bucket_name: str, storage_key: str) -> None:
    """删除 MinIO 对象"""
    client = get_minio_client()
    client.remove_object(bucket_name=bucket_name, object_name=storage_key)


def copy_object(source_bucket: str, source_key: str, dest_bucket: str, dest_key: str) -> None:
    """复制 MinIO 对象"""
    from minio.commonconfig import CopySource
    client = get_minio_client()
    client.copy_object(
        dest_bucket,
        dest_key,
        CopySource(source_bucket, source_key),
    )


def init_multipart_upload(bucket_name: str, storage_key: str) -> str:
    """初始化分片上传，返回 upload_id"""
    client = get_minio_client()
    ensure_bucket(client, bucket_name)
    upload_id = client._create_multipart_upload(bucket_name, storage_key)
    return upload_id


def upload_part(
    bucket_name: str,
    storage_key: str,
    upload_id: str,
    part_number: int,
    data: BinaryIO,
    length: int,
) -> str:
    """上传分片，返回 ETag"""
    client = get_minio_client()
    result = client._upload_part(
        bucket_name=bucket_name,
        object_name=storage_key,
        upload_id=upload_id,
        part_number=part_number,
        data=data,
        length=length,
    )
    return result


def complete_multipart_upload(
    bucket_name: str,
    storage_key: str,
    upload_id: str,
    parts: list,
) -> None:
    """合并分片"""
    client = get_minio_client()
    client._complete_multipart_upload(
        bucket_name=bucket_name,
        object_name=storage_key,
        upload_id=upload_id,
        parts=parts,
    )


def list_uploaded_parts(bucket_name: str, storage_key: str, upload_id: str) -> list:
    """查询已上传的分片列表"""
    client = get_minio_client()
    parts = client._list_parts(
        bucket_name=bucket_name,
        object_name=storage_key,
        upload_id=upload_id,
    )
    return [p.part_number for p in parts]
