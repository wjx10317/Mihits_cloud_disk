<template>
  <div class="main-layout">
    <!-- 侧边栏 -->
    <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <!-- Logo -->
      <div class="sidebar-logo">
        <span class="logo-icon">☁️</span>
        <span v-if="!sidebarCollapsed" class="logo-text">Mihits 网盘</span>
      </div>

      <!-- 导航菜单 -->
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        :collapse="sidebarCollapsed"
        :collapse-transition="false"
        router
      >
        <el-menu-item index="/">
          <el-icon><Folder /></el-icon>
          <template #title>全部文件</template>
        </el-menu-item>
        <el-menu-item index="/trash">
          <el-icon><Delete /></el-icon>
          <template #title>回收站</template>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>设置</template>
        </el-menu-item>
      </el-menu>

      <!-- 存储空间信息 -->
      <div v-if="!sidebarCollapsed" class="storage-info">
        <div class="storage-ring" @click="handleStorageClick">
          <el-progress
            type="circle"
            :percentage="storageStore.usagePercentage"
            :width="80"
            :stroke-width="6"
            :color="progressColor"
          >
            <template #default>
              <span class="storage-percent">{{ storageStore.usagePercentage }}%</span>
            </template>
          </el-progress>
        </div>
        <div class="storage-text">
          <span>已用 {{ storageStore.formatSize(storageStore.usedQuota) }}</span>
          <span class="storage-total">/ 共 {{ storageStore.formatSize(storageStore.totalQuota) }}</span>
        </div>
        <!-- 预警提示 -->
        <el-alert
          v-if="storageStore.warningLevel === 'danger'"
          type="error"
          :closable="false"
          show-icon
          class="storage-alert"
        >
          存储空间严重不足
        </el-alert>
        <el-alert
          v-else-if="storageStore.warningLevel === 'warning'"
          type="warning"
          :closable="false"
          show-icon
          class="storage-alert"
        >
          存储空间即将不足
        </el-alert>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶部栏 -->
      <div class="topbar">
        <el-button text @click="sidebarCollapsed = !sidebarCollapsed">
          <el-icon :size="20"><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
        </el-button>
        <div class="topbar-right">
          <el-dropdown @command="handleUserCommand">
            <span class="user-info">
              <el-avatar :size="28" class="user-avatar">{{ userInitial }}</el-avatar>
              <span class="user-name">{{ authStore.user?.username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="settings">设置</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 页面内容 -->
      <div class="page-content">
        <router-view />
      </div>
    </div>

    <!-- 传输面板 -->
    <TransferPanel />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Folder, Delete, Setting, Fold, Expand } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useStorageStore } from '@/stores/storage'
import TransferPanel from '@/components/TransferPanel.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const storageStore = useStorageStore()

const sidebarCollapsed = ref(false)

const activeMenu = computed(() => route.path)

const userInitial = computed(() => authStore.user?.username?.charAt(0)?.toUpperCase() ?? 'U')

const progressColor = computed(() => {
  const level = storageStore.warningLevel
  if (level === 'danger') return '#F56C6C'
  if (level === 'warning') return '#E6A23C'
  return '#6C5CE7'
})

function handleStorageClick() {
  router.push('/settings')
}

async function handleUserCommand(command: string) {
  if (command === 'settings') {
    router.push('/settings')
  } else if (command === 'logout') {
    try {
      await authStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
    } catch {
      ElMessage.error('退出失败')
    }
  }
}

onMounted(() => {
  storageStore.fetchUsage()
})
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #f5f6fa;
}

.sidebar {
  width: 220px;
  background: #fff;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  transition: width 0.2s;
  flex-shrink: 0;
}
.sidebar.collapsed {
  width: 64px;
}

.sidebar-logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-bottom: 1px solid #e8e8e8;
  padding: 0 16px;
}
.logo-icon { font-size: 24px; }
.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: #6C5CE7;
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
}

.storage-info {
  padding: 16px;
  border-top: 1px solid #e8e8e8;
  text-align: center;
}
.storage-ring { cursor: pointer; }
.storage-percent { font-size: 14px; font-weight: 600; color: #333; }
.storage-text {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}
.storage-total { color: #ccc; }
.storage-alert { margin-top: 8px; font-size: 12px; }

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.topbar {
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}

.topbar-right { display: flex; align-items: center; gap: 12px; }

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.user-avatar { background: #6C5CE7; color: #fff; font-size: 14px; }
.user-name { font-size: 14px; color: #333; }

.page-content {
  flex: 1;
  overflow: auto;
  padding: 16px;
}
</style>
