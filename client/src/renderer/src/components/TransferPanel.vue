<template>
  <div class="transfer-panel" :class="{ expanded: transferStore.panelVisible }">
    <div class="panel-header" @click="transferStore.togglePanel">
      <span class="panel-title">
        <el-icon><Upload /></el-icon>
        传输列表
        <el-badge :value="activeCount" :max="99" v-if="activeCount > 0" />
      </span>
      <el-icon class="toggle-icon">
        <component :is="transferStore.panelVisible ? ArrowDown : ArrowUp" />
      </el-icon>
    </div>

    <div v-if="transferStore.panelVisible" class="panel-body">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="上传" name="upload">
          <div v-if="transferStore.uploadTasks.length === 0" class="empty-tip">暂无上传任务</div>
          <div v-for="task in transferStore.uploadTasks" :key="task.id" class="task-item">
            <div class="task-info">
              <span class="task-name">{{ task.fileName }}</span>
              <span class="task-status" :class="task.status">{{ statusText(task.status) }}</span>
            </div>
            <el-progress :percentage="task.progress" :status="task.status === 'failed' ? 'exception' : task.status === 'completed' ? 'success' : undefined" :stroke-width="4" />
          </div>
        </el-tab-pane>
        <el-tab-pane label="下载" name="download">
          <div v-if="transferStore.downloadTasks.length === 0" class="empty-tip">暂无下载任务</div>
          <div v-for="task in transferStore.downloadTasks" :key="task.id" class="task-item">
            <div class="task-info">
              <span class="task-name">{{ task.fileName }}</span>
              <span class="task-status" :class="task.status">{{ statusText(task.status) }}</span>
            </div>
            <el-progress :percentage="task.progress" :status="task.status === 'failed' ? 'exception' : task.status === 'completed' ? 'success' : undefined" :stroke-width="4" />
          </div>
        </el-tab-pane>
      </el-tabs>

      <div class="panel-footer" v-if="hasCompleted">
        <el-button size="small" @click="transferStore.clearCompleted()">清除已完成</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTransferStore } from '@/stores/transfer'
import { Upload, ArrowDown, ArrowUp } from '@element-plus/icons-vue'

const transferStore = useTransferStore()
const activeTab = ref('upload')

const activeCount = computed(() =>
  transferStore.tasks.filter(t => t.status === 'active' || t.status === 'pending').length
)

const hasCompleted = computed(() =>
  transferStore.tasks.some(t => t.status === 'completed')
)

function statusText(status: string): string {
  const map: Record<string, string> = {
    pending: '等待中', active: '传输中', paused: '已暂停',
    completed: '已完成', failed: '失败', cancelled: '已取消',
  }
  return map[status] || status
}
</script>

<style scoped>
.transfer-panel {
  position: fixed; bottom: 0; left: 220px; right: 0;
  background: white; border-top: 1px solid #e8e8ec;
  z-index: 100; transition: all 0.3s;
}
.transfer-panel.expanded { height: 280px; }

.panel-header {
  height: 40px; display: flex; align-items: center; justify-content: space-between;
  padding: 0 16px; cursor: pointer; border-bottom: 1px solid #f0f0f0;
}
.panel-header:hover { background: #fafafa; }

.panel-title { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 500; }
.toggle-icon { font-size: 14px; color: #909399; }

.panel-body { padding: 0 16px; overflow-y: auto; height: 240px; }

.empty-tip { text-align: center; color: #909399; padding: 24px 0; font-size: 13px; }

.task-item { padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.task-info { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.task-name { font-size: 12px; max-width: 70%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.task-status { font-size: 11px; }
.task-status.completed { color: #67c23a; }
.task-status.failed { color: #f56c6c; }
.task-status.active { color: #409eff; }

.panel-footer { padding: 8px 0; text-align: right; }
</style>
