import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getFileList, createFolder, renameFolder, renameFile,
  deleteFiles, searchFiles, getFolderPath,
  moveFiles, copyFiles,
} from '@/api/file'
import type { FolderInfo, FileInfo, FileListData } from '@/api/file'
import { ElMessage, ElMessageBox } from 'element-plus'

export const useFileStore = defineStore('file', () => {
  // ===== State =====
  const currentFolderId = ref<string | null>(null) // null = 根目录
  const folders = ref<FolderInfo[]>([])
  const files = ref<FileInfo[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(50)
  const sort = ref('name')
  const order = ref('asc')
  const breadcrumb = ref<{ id: string; name: string }[]>([{ id: '', name: '全部文件' }])
  const loading = ref(false)
  const selectedFiles = ref<string[]>([])
  const selectedFolders = ref<string[]>([])
  const viewMode = ref<'table' | 'grid'>('table')
  const searchKeyword = ref('')

  // ===== Getters =====
  const hasSelection = computed(() => selectedFiles.value.length > 0 || selectedFolders.value.length > 0)

  // ===== Actions =====

  /** 加载文件列表 */
  async function loadFiles() {
    loading.value = true
    try {
      const res = await getFileList({
        folder_id: currentFolderId.value || undefined,
        page: page.value,
        page_size: pageSize.value,
        sort: sort.value,
        order: order.value,
      })
      if (res.code === 'SUCCESS') {
        folders.value = res.data.folders
        files.value = res.data.files
        total.value = res.data.total
      }
    } catch {
      // 错误已由拦截器处理
    } finally {
      loading.value = false
    }
  }

  /** 进入文件夹 */
  async function enterFolder(folderId: string, folderName: string) {
    currentFolderId.value = folderId
    selectedFiles.value = []
    selectedFolders.value = []
    page.value = 1

    // 更新面包屑
    try {
      const res = await getFolderPath(folderId)
      if (res.code === 'SUCCESS') {
        breadcrumb.value = [{ id: '', name: '全部文件' }, ...res.data]
      }
    } catch {
      breadcrumb.value = [...breadcrumb.value, { id: folderId, name: folderName }]
    }

    await loadFiles()
  }

  /** 导航到面包屑某层 */
  async function navigateTo(index: number) {
    if (index === 0) {
      currentFolderId.value = null
      breadcrumb.value = [{ id: '', name: '全部文件' }]
    } else {
      const target = breadcrumb.value[index]
      currentFolderId.value = target.id
      breadcrumb.value = breadcrumb.value.slice(0, index + 1)
    }
    selectedFiles.value = []
    selectedFolders.value = []
    page.value = 1
    await loadFiles()
  }

  /** 新建文件夹 */
  async function handleCreateFolder(name: string) {
    try {
      const res = await createFolder({
        parent_id: currentFolderId.value || undefined,
        name,
      })
      if (res.code === 'SUCCESS') {
        ElMessage.success('文件夹创建成功')
        await loadFiles()
      }
    } catch {
      // 错误已处理
    }
  }

  /** 重命名 */
  async function handleRename(type: 'file' | 'folder', id: string, name: string) {
    try {
      if (type === 'folder') {
        await renameFolder(id, name)
      } else {
        await renameFile(id, name)
      }
      ElMessage.success('重命名成功')
      await loadFiles()
    } catch {
      // 错误已处理
    }
  }

  /** 删除选中项目 */
  async function handleDelete() {
    if (!hasSelection.value) return

    try {
      await ElMessageBox.confirm(
        `确定将 ${selectedFiles.value.length + selectedFolders.value.length} 个项目移至回收站？`,
        '删除确认',
        { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
      )

      const res = await deleteFiles({
        file_ids: selectedFiles.value,
        folder_ids: selectedFolders.value,
      })
      if (res.code === 'SUCCESS') {
        ElMessage.success(res.message)
        selectedFiles.value = []
        selectedFolders.value = []
        await loadFiles()
      }
    } catch {
      // 用户取消或错误已处理
    }
  }

  /** 移动文件 */
  async function handleMove(targetFolderId: string | null) {
    try {
      const res = await moveFiles({
        file_ids: selectedFiles.value,
        folder_ids: selectedFolders.value,
        target_folder_id: targetFolderId || undefined,
      })
      if (res.code === 'SUCCESS') {
        ElMessage.success(res.message)
        selectedFiles.value = []
        selectedFolders.value = []
        await loadFiles()
      }
    } catch {
      // 错误已处理
    }
  }

  /** 搜索文件 */
  async function handleSearch(keyword: string) {
    if (!keyword.trim()) {
      await loadFiles()
      return
    }
    loading.value = true
    try {
      const res = await searchFiles({ keyword: keyword.trim() })
      if (res.code === 'SUCCESS') {
        folders.value = res.data.folders
        files.value = res.data.files
        total.value = res.data.folders.length + res.data.files.length
      }
    } catch {
      // 错误已处理
    } finally {
      loading.value = false
    }
  }

  /** 切换排序 */
  async function changeSort(newSort: string, newOrder: string) {
    sort.value = newSort
    order.value = newOrder
    await loadFiles()
  }

  return {
    currentFolderId, folders, files, total, page, pageSize,
    sort, order, breadcrumb, loading, selectedFiles, selectedFolders,
    viewMode, searchKeyword, hasSelection,
    loadFiles, enterFolder, navigateTo, handleCreateFolder,
    handleRename, handleDelete, handleMove, handleSearch, changeSort,
  }
})
