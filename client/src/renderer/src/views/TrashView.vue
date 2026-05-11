<template>
  <div class="files-container">
    <header class="top-bar">
      <div class="top-bar-left">
        <el-button @click="router.push('/')" text>
          <el-icon><ArrowLeft /></el-icon> 返回文件
        </el-button>
        <h1 class="page-title">回收站</h1>
      </div>
      <div class="top-bar-right">
        <el-button type="danger" size="small" @click="handleEmptyTrash" :disabled="trashItems.length === 0">
          清空回收站
        </el-button>
      </div>
    </header>

    <main class="content-area">
      <el-table v-loading="loading" :data="trashItems" empty-text="回收站为空">
        <el-table-column label="名称" min-width="300">
          <template #default="{ row }">
            <div class="file-name-cell">
              <el-icon :color="row.type === 'folder' ? '#e6a23c' : '#409eff'">
                <component :is="row.type === 'folder' ? Folder : Document" />
              </el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="大小" width="120">
          <template #default="{ row }">{{ row.type === 'folder' ? '-' : formatSize(row.size) }}</template>
        </el-table-column>
        <el-table-column label="删除时间" width="180">
          <template #default="{ row }">{{ formatDate(row.deleted_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link size="small" type="primary" @click="handleRestore(row)">恢复</el-button>
            <el-button link size="small" type="danger" @click="handlePurge(row)">彻底删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTrashList, restoreTrashItems, purgeTrashItems, emptyTrash } from '@/api/file'
import { Folder, Document, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const trashItems = ref<any[]>([])
const loading = ref(false)

onMounted(loadTrash)

async function loadTrash() {
  loading.value = true
  try {
    const res = await getTrashList()
    if (res.code === 'SUCCESS') {
      trashItems.value = res.data
    }
  } finally {
    loading.value = false
  }
}

async function handleRestore(row: any) {
  try {
    const res = await restoreTrashItems([{ id: row.id, type: row.type }])
    if (res.code === 'SUCCESS') {
      ElMessage.success('恢复成功')
      await loadTrash()
    }
  } catch { /* ignore */ }
}

async function handlePurge(row: any) {
  try {
    await ElMessageBox.confirm('彻底删除后将无法恢复，确定继续？', '警告', { type: 'warning' })
    const res = await purgeTrashItems([{ id: row.id, type: row.type }])
    if (res.code === 'SUCCESS') {
      ElMessage.success('已彻底删除')
      await loadTrash()
    }
  } catch { /* ignore */ }
}

async function handleEmptyTrash() {
  try {
    await ElMessageBox.confirm('清空回收站后所有文件将无法恢复，确定继续？', '警告', { type: 'warning' })
    const res = await emptyTrash()
    if (res.code === 'SUCCESS') {
      ElMessage.success(res.message)
      await loadTrash()
    }
  } catch { /* ignore */ }
}

function formatSize(bytes: number): string {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0, size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(i === 0 ? 0 : 1)} ${units[i]}`
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.files-container { height: 100vh; display: flex; flex-direction: column; background: #f5f7fa; }
.top-bar {
  height: 56px; background: white; border-bottom: 1px solid #e8e8ec;
  display: flex; align-items: center; justify-content: space-between; padding: 0 24px;
}
.top-bar-left { display: flex; align-items: center; gap: 12px; }
.page-title { font-size: 18px; font-weight: 600; margin: 0; }
.content-area { flex: 1; padding: 16px; overflow-y: auto; }
.file-name-cell { display: flex; align-items: center; gap: 8px; }
</style>
