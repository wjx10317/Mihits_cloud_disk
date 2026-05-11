import request from '@/utils/request'

/** 文件夹信息 */
export interface FolderInfo {
  id: string
  user_id: string
  parent_id: string | null
  name: string
  path: string
  created_at: string
  updated_at: string
}

/** 文件信息 */
export interface FileInfo {
  id: string
  user_id: string
  folder_id: string | null
  name: string
  extension: string | null
  mime_type: string | null
  size: number
  storage_key: string
  file_hash: string | null
  created_at: string
  updated_at: string
}

/** 文件列表响应 */
export interface FileListData {
  folders: FolderInfo[]
  files: FileInfo[]
  total: number
  page: number
  page_size: number
}

/** 获取文件列表 */
export function getFileList(params: {
  folder_id?: string
  page?: number
  page_size?: number
  sort?: string
  order?: string
  type?: string
}) {
  return request.get<any, { code: string; message: string; data: FileListData }>('/files', { params })
}

/** 创建文件夹 */
export function createFolder(data: { parent_id?: string; name: string }) {
  return request.post<any, { code: string; message: string; data: { id: string; name: string; path: string } }>('/folders', data)
}

/** 重命名文件夹 */
export function renameFolder(folderId: string, name: string) {
  return request.put<any, { code: string; message: string; data: { id: string; name: string } }>(`/folders/${folderId}/rename`, { name })
}

/** 获取目录树 */
export function getFolderTree() {
  return request.get<any, { code: string; message: string; data: any[] }>('/folders/tree')
}

/** 面包屑项 */
export interface BreadcrumbItem {
  id: string
  name: string
}

/** 获取面包屑路径 */
export function getFolderPath(folderId: string) {
  return request.get<any, { code: string; message: string; data: BreadcrumbItem[] }>(`/folders/${folderId}/path`)
}

/** 创建空文件 */
export function createFile(data: { folder_id?: string; name: string }) {
  return request.post<any, { code: string; message: string; data: { id: string; name: string } }>('/files', data)
}

/** 重命名文件 */
export function renameFile(fileId: string, name: string) {
  return request.put<any, { code: string; message: string; data: { id: string; name: string } }>(`/files/${fileId}/rename`, { name })
}

/** 移动文件 */
export function moveFiles(data: { file_ids: string[]; folder_ids: string[]; target_folder_id?: string }) {
  return request.post<any, { code: string; message: string; data: { count: number } }>('/files/move', data)
}

/** 复制文件 */
export function copyFiles(data: { file_ids: string[]; target_folder_id?: string }) {
  return request.post<any, { code: string; message: string; data: { count: number } }>('/files/copy', data)
}

/** 删除文件（软删除） */
export function deleteFiles(data: { file_ids: string[]; folder_ids: string[] }) {
  return request.delete<any, { code: string; message: string; data: { count: number } }>('/files', { data })
}

/** 搜索结果 */
export interface SearchResult {
  folders: FolderInfo[]
  files: FileInfo[]
}

/** 搜索文件 */
export function searchFiles(params: { keyword: string; type?: string; limit?: number }) {
  return request.get<any, { code: string; message: string; data: SearchResult }>('/files/search', { params })
}

/** 普通上传（小文件） */
export function uploadSmallFile(formData: FormData) {
  return request.post<any, { code: string; message: string; data: { id: string; name: string; size: number } }>('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000, // 5 分钟超时
  })
}

/** 初始化分片上传 */
export function initChunkUpload(data: { name: string; folder_id?: string; size: number; file_hash?: string; total_chunks: number }) {
  return request.post<any, { code: string; message: string; data: { upload_id: string; storage_key: string; chunk_size: number } }>('/files/upload/init', data)
}

/** 上传分片 */
export function uploadChunk(formData: FormData) {
  return request.put<any, { code: string; message: string }>('/files/upload/chunk', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  })
}

/** 合并分片 */
export function completeChunkUpload(data: { upload_id: string; name: string; folder_id?: string; size: number; file_hash?: string }) {
  return request.post<any, { code: string; message: string; data: { id: string; name: string; size: number } }>('/files/upload/complete', data)
}

/** 已上传分片信息 */
export interface ChunkStatus {
  upload_id: string
  completed_chunks: number[]
  total_chunks: number
  status: string
}

/** 查询已上传分片 */
export function getUploadedChunks(uploadId: string) {
  return request.get<any, { code: string; message: string; data: ChunkStatus }>(`/files/upload/${uploadId}/chunks`)
}

/** 获取下载链接 */
export function getDownloadUrl(fileId: string) {
  return request.get<any, { code: string; message: string; data: { download_url: string; expires_in: number } }>(`/files/${fileId}/download`)
}

/** 获取回收站列表 */
export function getTrashList() {
  return request.get<any, { code: string; message: string; data: any[] }>('/trash')
}

/** 恢复回收站项目 */
export function restoreTrashItems(items: { id: string; type: string }[]) {
  return request.post<any, { code: string; message: string; data: { count: number } }>('/trash/restore', { items })
}

/** 彻底删除 */
export function purgeTrashItems(items: { id: string; type: string }[]) {
  return request.delete<any, { code: string; message: string; data: { count: number } }>('/trash/purge', { data: { items } })
}

/** 清空回收站 */
export function emptyTrash() {
  return request.delete<any, { code: string; message: string; data: { count: number } }>('/trash/empty')
}
