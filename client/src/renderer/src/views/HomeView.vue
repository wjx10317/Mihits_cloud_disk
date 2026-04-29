<template>
  <div class="home-container">
    <!-- 顶栏 -->
    <header class="top-bar">
      <div class="top-bar-left">
        <h1 class="app-title">Mihits 网盘</h1>
      </div>
      <div class="top-bar-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-avatar :size="32" class="user-avatar">
              {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <span class="user-name">{{ authStore.user?.username }}</span>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="welcome-section">
        <h2>欢迎使用 Mihits 网盘 👋</h2>
        <p>你的文件，随时随地在手</p>
        <el-empty description="文件管理功能开发中，敬请期待..." />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

async function handleCommand(command: string) {
  if (command === 'logout') {
    await authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.home-container {
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

.top-bar-left {
  display: flex;
  align-items: center;
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.top-bar-right {
  -webkit-app-region: no-drag;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-weight: 600;
}

.user-name {
  font-size: 14px;
  color: #333;
}

.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-section {
  text-align: center;
}

.welcome-section h2 {
  font-size: 28px;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.welcome-section p {
  font-size: 16px;
  color: #8c8ca1;
  margin-bottom: 48px;
}
</style>
