import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/** 传输任务 */
export interface TransferTask {
  id: string
  type: 'upload' | 'download'
  fileName: string
  fileSize: number
  progress: number       // 0-100
  speed: number          // bytes/s
  status: 'pending' | 'active' | 'paused' | 'completed' | 'failed' | 'cancelled'
  error?: string
  createdAt: number
  completedAt?: number
  // 分片上传额外字段
  uploadId?: string
  totalChunks?: number
  completedChunks?: number[]
}

export const useTransferStore = defineStore('transfer', () => {
  const tasks = ref<TransferTask[]>([])
  const panelVisible = ref(false)

  const uploadTasks = computed(() => tasks.value.filter(t => t.type === 'upload'))
  const downloadTasks = computed(() => tasks.value.filter(t => t.type === 'download'))
  const activeUploads = computed(() => uploadTasks.value.filter(t => t.status === 'active'))
  const activeDownloads = computed(() => downloadTasks.value.filter(t => t.status === 'active'))

  /** 添加任务 */
  function addTask(task: TransferTask) {
    tasks.value.unshift(task)
    panelVisible.value = true
  }

  /** 更新任务进度 */
  function updateTask(id: string, updates: Partial<TransferTask>) {
    const task = tasks.value.find(t => t.id === id)
    if (task) {
      Object.assign(task, updates)
    }
  }

  /** 移除任务 */
  function removeTask(id: string) {
    tasks.value = tasks.value.filter(t => t.id !== id)
  }

  /** 清除已完成任务 */
  function clearCompleted() {
    tasks.value = tasks.value.filter(t => t.status !== 'completed')
  }

  /** 切换面板显示 */
  function togglePanel() {
    panelVisible.value = !panelVisible.value
  }

  return {
    tasks, panelVisible, uploadTasks, downloadTasks, activeUploads, activeDownloads,
    addTask, updateTask, removeTask, clearCompleted, togglePanel,
  }
})
