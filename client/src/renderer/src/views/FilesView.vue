<template>
  <div class="files-container">
    <!-- 顶栏 -->
    <header class="top-bar">
      <div class="top-bar-left">
        <h1 class="app-title">Mihits 网盘</h1>
      </div>
      <div class="top-bar-center">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文件..."
          prefix-icon="Search"
          clearable
          class="search-input"
          @keyup.enter="handleSearch"
          @clear="handleClearSearch"
        />
      </div>
      <div class="top-bar-right">
        <el-dropdown @command="handleUserCommand">
          <span class="user-info">
            <el-avatar :size="32" class="user-avatar">
              {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <span class="user-name">{{ authStore.user?.username }}</span>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon> 退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <div class="main-layout">
      <!-- 左侧目录树 -->
      <aside class="sidebar">
        <div class="sidebar-section">
          <div class="sidebar-title">文件管理</div>
          <el-tree
            :data="folderTree"
            node-key="id"
            :props="{ label: 'name', children: 'children' }"
            highlight-current
            default-expand-all
            @node-click="handleTreeNodeClick"
          >
            <template #default="{ node }">
              <span class="tree-node">
                <el-icon size="16"><Folder /></el-icon>
                <span>{{ node.label }}</span>
              </span>
            </template>
          </el-tree>
        </div>
        <div class="sidebar-section">
          <el-menu @select="handleSidebarSelect">
            <el-menu-item index="files">
              <el-icon><FolderOpened /></el-icon>
              <span>全部文件</span>
            </el-menu-item>
            <el-menu-item index="trash">
              <el-icon><Delete /></el-icon>
              <span>回收站</span>
            </el-menu-item>
          </el-menu>
        </div>
      </aside>

      <!-- 右侧内容区 -->
      <main class="content-area">
        <!-- 工具栏 -->
        <div class="toolbar">
          <div class="toolbar-left">
            <!-- 面包屑 -->
            <el-breadcrumb separator="/">
              <el-breadcrumb-item
                v-for="(item, index) in fileStore.breadcrumb"
                :key="index"
                @click="fileStore.navigateTo(index)"
              >
                <span class="breadcrumb-link">{{ item.name }}</span>
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="toolbar-right">
            <el-button-group>
              <el-button :type="fileStore.viewMode === 'table' ? 'primary' : 'default'" @click="fileStore.viewMode = 'table'" size="small">
                <el-icon><List /></el-icon>
              </el-button>
              <el-button :type="fileStore.viewMode === 'grid' ? 'primary' : 'default'" @click="fileStore.viewMode = 'grid'" size="small">
                <el-icon><Grid /></el-icon>
              </el-button>
            </el-button-group>

            <el-dropdown trigger="click" @command="handleNewCommand">
              <el-button type="primary" size="small">
                <el-icon><Plus /></el-icon> 新建
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="folder">新建文件夹</el-dropdown-item>
                  <el-dropdown-item command="file">新建文本文件</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>

            <el-button size="small" :disabled="!fileStore.hasSelection" @click="fileStore.handleDelete()">
              <el-icon><Delete /></el-icon> 删除
            </el-button>

            <el-upload
              :show-file-list="false"
              :before-upload="handleUpload"
              multiple
              :action="''"
            >
              <el-button type="primary" size="small">
                <el-icon><Upload /></el-icon> 上传
              </el-button>
            </el-upload>
          </div>
        </div>

        <!-- 文件列表 - 表格视图 -->
        <el-table
          v-if="fileStore.viewMode === 'table'"
          v-loading="fileStore.loading"
          :data="[...fileStore.folders.map(f => ({...f, _type: 'folder'})), ...fileStore.files.map(f => ({...f, _type: 'file'}))]"
          @selection-change="handleSelectionChange"
          class="file-table"
          empty-text="空文件夹"
        >
          <el-table-column type="selection" width="40" />
          <el-table-column label="名称" min-width="300">
            <template #default="{ row }">
              <div class="file-name-cell" @click="handleItemClick(row)">
                <el-icon size="22" :color="row._type === 'folder' ? '#e6a23c' : '#409eff'">
                  <component :is="row._type === 'folder' ? Folder : Document" />
                </el-icon>
                <span class="file-name">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="大小" width="120">
            <template #default="{ row }">
              {{ row._type === 'folder' ? '-' : formatSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column label="修改时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.updated_at || row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button link size="small" @click="handleRenameClick(row)">重命名</el-button>
              <el-button link size="small" @click="handleDownload(row)" v-if="row._type === 'file'">下载</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 文件列表 - 网格视图 -->
        <div v-else class="grid-view" v-loading="fileStore.loading">
          <div v-if="fileStore.folders.length === 0 && fileStore.files.length === 0" class="empty-grid">
            <el-empty description="空文件夹" />
          </div>
          <div
            v-for="folder in fileStore.folders"
            :key="'f-'+folder.id"
            class="grid-item"
            @click="fileStore.enterFolder(folder.id, folder.name)"
          >
            <el-icon size="48" color="#e6a23c"><Folder /></el-icon>
            <div class="grid-item-name">{{ folder.name }}</div>
          </div>
          <div v-for="file in fileStore.files" :key="file.id" class="grid-item" @contextmenu.prevent>
            <el-icon size="48" color="#409eff"><Document /></el-icon>
            <div class="grid-item-name">{{ file.name }}</div>
            <div class="grid-item-size">{{ formatSize(file.size) }}</div>
          </div>
        </div>
      </main>
    </div>

    <!-- 传输面板 -->
    <TransferPanel />

    <!-- 新建文件夹对话框 -->
    <el-dialog v-model="newFolderDialogVisible" title="新建文件夹" width="400px">
      <el-input v-model="newFolderName" placeholder="请输入文件夹名称" @keyup.enter="confirmNewFolder" />
      <template #footer>
        <el-button @click="newFolderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmNewFolder">确定</el-button>
      </template>
    </el-dialog>

    <!-- 重命名对话框 -->
    <el-dialog v-model="renameDialogVisible" title="重命名" width="400px">
      <el-input v-model="renameName" placeholder="请输入新名称" @keyup.enter="confirmRename" />
      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRename">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFileStore } from '@/stores/file'
import { useTransferStore } from '@/stores/transfer'
import { uploadSmallFile, getDownloadUrl, getFolderTree } from '@/api/file'
import {
  SwitchButton, Folder, FolderOpened, Delete, List, Grid,
  Plus, Upload, Document, Search,
} from '@element-plus/icons-vue'
import TransferPanel from '@/components/TransferPanel.vue'

const router = useRouter()
const authStore = useAuthStore()
const fileStore = useFileStore()
const transferStore = useTransferStore()

const searchKeyword = ref('')
const folderTree = ref<any[]>([])
const newFolderDialogVisible = ref(false)
const newFolderName = ref('')
const renameDialogVisible = ref(false)
const renameName = ref('')
const renameTarget = ref<{ type: string; id: string } | null>(null)

onMounted(async () => {
  await fileStore.loadFiles()
  await loadFolderTree()
})

async function loadFolderTree() {
  try {
    const res = await getFolderTree()
    if (res.code === 'SUCCESS') {
      folderTree.value = res.data
    }
  } catch { /* ignore */ }
}

function handleUserCommand(cmd: string) {
  if (cmd === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}

function handleSidebarSelect(index: string) {
  if (index === 'files') {
    fileStore.navigateTo(0)
  } else if (index === 'trash') {
    router.push('/trash')
  }
}

function handleTreeNodeClick(data: any) {
  fileStore.enterFolder(data.id, data.name)
}

function handleItemClick(row: any) {
  if (row._type === 'folder') {
    fileStore.enterFolder(row.id, row.name)
  }
}

function handleNewCommand(cmd: string) {
  if (cmd === 'folder') {
    newFolderName.value = '新建文件夹'
    newFolderDialogVisible.value = true
  } else if (cmd === 'file') {
    fileStore.handleCreateFolder('新建文本文件.txt') // 复用：创建空文件
  }
}

async function confirmNewFolder() {
  if (!newFolderName.value.trim()) return
  await fileStore.handleCreateFolder(newFolderName.value.trim())
  newFolderDialogVisible.value = false
  await loadFolderTree()
}

function handleRenameClick(row: any) {
  renameTarget.value = { type: row._type, id: row.id }
  renameName.value = row.name
  renameDialogVisible.value = true
}

async function confirmRename() {
  if (!renameTarget.value || !renameName.value.trim()) return
  await fileStore.handleRename(
    renameTarget.value.type as 'file' | 'folder',
    renameTarget.value.id,
    renameName.value.trim()
  )
  renameDialogVisible.value = false
  await loadFolderTree()
}

function handleSelectionChange(selection: any[]) {
  fileStore.selectedFiles = selection.filter(s => s._type === 'file').map(s => s.id)
  fileStore.selectedFolders = selection.filter(s => s._type === 'folder').map(s => s.id)
}

async function handleUpload(file: File) {
  const taskId = Date.now().toString()
  transferStore.addTask({
    id: taskId, type: 'upload', fileName: file.name, fileSize: file.size,
    progress: 0, speed: 0, status: 'active', createdAt: Date.now(),
  })

  const formData = new FormData()
  formData.append('file', file)
  if (fileStore.currentFolderId) {
    formData.append('folder_id', fileStore.currentFolderId)
  }

  try {
    const res = await uploadSmallFile(formData)
    if (res.code === 'SUCCESS') {
      transferStore.updateTask(taskId, { progress: 100, status: 'completed', completedAt: Date.now() })
      await fileStore.loadFiles()
    } else {
      transferStore.updateTask(taskId, { status: 'failed', error: '上传失败' })
    }
  } catch (e: any) {
    transferStore.updateTask(taskId, { status: 'failed', error: e.message || '上传失败' })
  }
  return false // 阻止默认上传
}

async function handleDownload(row: any) {
  try {
    const res = await getDownloadUrl(row.id)
    if (res.code === 'SUCCESS') {
      window.open(res.data.download_url, '_blank')
    }
  } catch { /* ignore */ }
}

async function handleSearch() {
  if (searchKeyword.value.trim()) {
    await fileStore.handleSearch(searchKeyword.value)
  } else {
    await fileStore.loadFiles()
  }
}

async function handleClearSearch() {
  searchKeyword.value = ''
  await fileStore.loadFiles()
}

function formatSize(bytes: number): string {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(i === 0 ? 0 : 1)} ${units[i]}`
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.files-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.top-bar {
  height: 56px;
  background: white;
  border-bottom: 1px solid #e8e8ec;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  -webkit-app-region: drag;
}

.top-bar-left { display: flex; align-items: center; }
.top-bar-center { -webkit-app-region: no-drag; flex: 1; max-width: 400px; margin: 0 24px; }
.top-bar-right { -webkit-app-region: no-drag; }

.app-title {
  font-size: 20px; font-weight: 600; color: #1a1a2e; margin: 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

.search-input { width: 100%; }

.user-info { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.user-avatar { background: linear-gradient(135deg, #667eea, #764ba2); color: white; font-weight: 600; }
.user-name { font-size: 14px; color: #333; }

.main-layout { flex: 1; display: flex; overflow: hidden; }

.sidebar {
  width: 220px; background: white; border-right: 1px solid #e8e8ec;
  overflow-y: auto; padding: 12px 0;
  -webkit-app-region: no-drag;
}

.sidebar-title { font-size: 12px; color: #909399; padding: 8px 16px; text-transform: uppercase; }

.tree-node { display: flex; align-items: center; gap: 6px; font-size: 13px; }

.content-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.toolbar {
  height: 48px; background: white; border-bottom: 1px solid #e8e8ec;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 16px;
}

.toolbar-left { display: flex; align-items: center; }
.toolbar-right { display: flex; align-items: center; gap: 8px; }

.breadcrumb-link { cursor: pointer; }
.breadcrumb-link:hover { color: #667eea; }

.file-table { flex: 1; }

.file-name-cell {
  display: flex; align-items: center; gap: 8px; cursor: pointer;
}
.file-name-cell:hover .file-name { color: #667eea; }
.file-name { font-size: 14px; }

.grid-view {
  flex: 1; overflow-y: auto; padding: 16px;
  display: flex; flex-wrap: wrap; gap: 16px; align-content: flex-start;
}

.grid-item {
  width: 120px; height: 130px; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 8px;
  border-radius: 8px; cursor: pointer; transition: all 0.2s;
  border: 1px solid transparent;
}
.grid-item:hover { background: #f0f2ff; border-color: #d0d5ff; }
.grid-item-name { font-size: 12px; text-align: center; word-break: break-all; max-width: 110px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.grid-item-size { font-size: 11px; color: #909399; }

.empty-grid { width: 100%; padding: 80px 0; }
</style>
