import Dexie, { type Table } from 'dexie'

/** 传输任务 */
export interface TransferTask {
  id?: number
  taskId: string
  type: 'upload' | 'download'
  fileName: string
  fileSize: number
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed'
  progress: number
  folderId?: string
  storageKey?: string
  createdAt: number
  updatedAt: number
}

/** 文件缓存条目 */
export interface FileCacheEntry {
  id?: number
  fileId: string
  fileName: string
  mimeType?: string
  size: number
  blobKey: string
  accessedAt: number
}

/** 应用 IndexedDB 数据库 */
class AppDB extends Dexie {
  uploadTasks!: Table<TransferTask>
  downloadTasks!: Table<TransferTask>
  fileCache!: Table<FileCacheEntry>

  constructor() {
    super('MihitsCloudDB')
    this.version(1).stores({
      uploadTasks: '++id, taskId, status, createdAt',
      downloadTasks: '++id, taskId, status, createdAt',
      fileCache: '++id, fileId, accessedAt',
    })
  }
}

export const db = new AppDB()

// ===== 传输任务持久化 =====

/** 保存上传任务 */
export async function saveUploadTask(task: TransferTask): Promise<void> {
  await db.uploadTasks.put(task)
}

/** 保存下载任务 */
export async function saveDownloadTask(task: TransferTask): Promise<void> {
  await db.downloadTasks.put(task)
}

/** 获取所有未完成的上传任务 */
export async function getPendingUploadTasks(): Promise<TransferTask[]> {
  return db.uploadTasks.where('status').anyOf(['pending', 'paused', 'failed']).toArray()
}

/** 获取所有未完成的下载任务 */
export async function getPendingDownloadTasks(): Promise<TransferTask[]> {
  return db.downloadTasks.where('status').anyOf(['pending', 'paused', 'failed']).toArray()
}

/** 更新任务状态 */
export async function updateTaskStatus(
  table: 'uploadTasks' | 'downloadTasks',
  taskId: string,
  status: TransferTask['status'],
  progress?: number
): Promise<void> {
  const task = await (table === 'uploadTasks' ? db.uploadTasks : db.downloadTasks)
    .where('taskId').equals(taskId).first()
  if (task?.id) {
    const update: Partial<TransferTask> = { status, updatedAt: Date.now() }
    if (progress !== undefined) update.progress = progress
    await (table === 'uploadTasks' ? db.uploadTasks : db.downloadTasks).update(task.id, update)
  }
}

/** 删除已完成任务 */
export async function cleanCompletedTasks(): Promise<void> {
  await db.uploadTasks.where('status').equals('completed').delete()
  await db.downloadTasks.where('status').equals('completed').delete()
}
