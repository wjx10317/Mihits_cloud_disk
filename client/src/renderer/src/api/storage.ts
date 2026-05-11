import request from '@/utils/request'

/** 分类统计 */
export interface CategoryBreakdown {
  image: number
  video: number
  document: number
  audio: number
  other: number
}

/** 存储使用情况 */
export interface StorageUsage {
  total_quota: number
  used_quota: number
  available_quota: number
  usage_percentage: number
  category_breakdown: CategoryBreakdown
}

/** 获取存储空间使用情况 */
export function getStorageUsage() {
  return request.get<any, { code: string; message: string; data: StorageUsage }>('/storage/usage')
}

/** 更新存储配额 */
export function updateStorageQuota(storageQuota: number) {
  return request.put<any, { code: string; message: string; data: { storage_quota: number; storage_used: number } }>('/storage/quota', { storage_quota: storageQuota })
}
