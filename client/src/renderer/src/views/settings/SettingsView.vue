<template>
  <div class="settings-page">
    <h2 class="page-title">设置</h2>

    <!-- 存储空间 -->
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>存储空间</span>
        </div>
      </template>

      <div class="storage-detail" v-if="storageStore.usage">
        <div class="storage-overview">
          <el-progress
            type="circle"
            :percentage="storageStore.usagePercentage"
            :width="120"
            :stroke-width="8"
            :color="progressColor"
          >
            <template #default>
              <div class="storage-center">
                <div class="storage-used">{{ storageStore.formatSize(storageStore.usedQuota) }}</div>
                <div class="storage-label">已使用</div>
              </div>
            </template>
          </el-progress>
          <div class="storage-meta">
            <div class="meta-item">
              <span class="meta-label">总容量</span>
              <span class="meta-value">{{ storageStore.formatSize(storageStore.totalQuota) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">可用空间</span>
              <span class="meta-value">{{ storageStore.formatSize(storageStore.availableQuota) }}</span>
            </div>
          </div>
        </div>

        <!-- 分类统计 -->
        <div class="category-breakdown">
          <h4>分类统计</h4>
          <div class="category-list">
            <div class="category-item" v-for="item in categoryItems" :key="item.key">
              <span class="category-icon">{{ item.icon }}</span>
              <span class="category-name">{{ item.label }}</span>
              <span class="category-size">{{ storageStore.formatSize(item.size) }}</span>
              <el-progress
                :percentage="categoryPercentage(item.size)"
                :show-text="false"
                :stroke-width="4"
                :color="item.color"
                class="category-bar"
              />
            </div>
          </div>
        </div>
      </div>

      <el-empty v-else description="加载中..." />
    </el-card>

    <!-- 应用信息 -->
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>关于</span>
        </div>
      </template>
      <div class="about-info">
        <div class="about-item">
          <span class="about-label">应用名称</span>
          <span class="about-value">Mihits 网盘</span>
        </div>
        <div class="about-item">
          <span class="about-label">版本</span>
          <span class="about-value">0.1.0</span>
        </div>
        <div class="about-item">
          <span class="about-label">技术栈</span>
          <span class="about-value">Electron + Vue 3 + FastAPI</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useStorageStore } from '@/stores/storage'

const storageStore = useStorageStore()

const progressColor = computed(() => {
  const level = storageStore.warningLevel
  if (level === 'danger') return '#F56C6C'
  if (level === 'warning') return '#E6A23C'
  return '#6C5CE7'
})

const categoryItems = computed(() => [
  { key: 'image', label: '图片', icon: '🖼️', color: '#6C5CE7', size: storageStore.breakdown.image },
  { key: 'video', label: '视频', icon: '🎬', color: '#E17055', size: storageStore.breakdown.video },
  { key: 'document', label: '文档', icon: '📄', color: '#00B894', size: storageStore.breakdown.document },
  { key: 'audio', label: '音频', icon: '🎵', color: '#FDCB6E', size: storageStore.breakdown.audio },
  { key: 'other', label: '其他', icon: '📦', color: '#B2BEC3', size: storageStore.breakdown.other },
])

function categoryPercentage(size: number): number {
  if (storageStore.totalQuota === 0) return 0
  return Math.round((size / storageStore.totalQuota) * 100)
}

onMounted(() => {
  storageStore.fetchUsage()
})
</script>

<style scoped>
.settings-page {
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 20px 0;
}

.settings-card {
  margin-bottom: 16px;
}

.card-header {
  font-weight: 600;
  font-size: 15px;
}

.storage-overview {
  display: flex;
  align-items: center;
  gap: 40px;
  margin-bottom: 24px;
}

.storage-center {
  text-align: center;
}
.storage-used { font-size: 16px; font-weight: 600; color: #333; }
.storage-label { font-size: 12px; color: #999; margin-top: 4px; }

.storage-meta { display: flex; flex-direction: column; gap: 12px; }
.meta-item { display: flex; gap: 16px; }
.meta-label { font-size: 14px; color: #999; min-width: 60px; }
.meta-value { font-size: 14px; color: #333; font-weight: 500; }

.category-breakdown h4 {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px 0;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-item {
  display: grid;
  grid-template-columns: 24px 50px auto 100px;
  align-items: center;
  gap: 8px;
}
.category-icon { font-size: 16px; text-align: center; }
.category-name { font-size: 13px; color: #666; }
.category-size { font-size: 13px; color: #333; text-align: right; }
.category-bar { width: 100px; }

.about-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.about-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
}
.about-label { font-size: 14px; color: #999; }
.about-value { font-size: 14px; color: #333; }
</style>
