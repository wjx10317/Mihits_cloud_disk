"""存储空间相关 Schema"""
from typing import Optional
from pydantic import BaseModel, Field


class CategoryBreakdown(BaseModel):
    """按文件类型分类的存储统计"""
    image: int = 0
    video: int = 0
    document: int = 0
    audio: int = 0
    other: int = 0


class StorageUsage(BaseModel):
    """存储空间使用情况"""
    total_quota: int = Field(description="总配额（字节）")
    used_quota: int = Field(description="已用空间（字节）")
    available_quota: int = Field(description="可用空间（字节）")
    usage_percentage: float = Field(description="使用百分比", ge=0, le=100)
    category_breakdown: CategoryBreakdown = Field(description="按类型分类统计")


class StorageQuotaUpdate(BaseModel):
    """更新用户配额"""
    storage_quota: int = Field(gt=0, description="新配额（字节）")
