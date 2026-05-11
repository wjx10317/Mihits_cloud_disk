import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getStorageUsage, type StorageUsage, type CategoryBreakdown } from '@/api/storage'

export const useStorageStore = defineStore('storage', () => {
  const usage = ref<StorageUsage | null>(null)
  const loading = ref(false)

  const usagePercentage = computed(() => usage.value?.usage_percentage ?? 0)
  const totalQuota = computed(() => usage.value?.total_quota ?? 0)
  const usedQuota = computed(() => usage.value?.used_quota ?? 0)
  const availableQuota = computed(() => usage.value?.available_quota ?? 0)
  const breakdown = computed<CategoryBreakdown>(() => usage.value?.category_breakdown ?? {
    image: 0, video: 0, document: 0, audio: 0, other: 0
  })

  // 预警等级
  const warningLevel = computed<'normal' | 'warning' | 'danger'>(() => {
    const pct = usagePercentage.value
    if (pct >= 95) return 'danger'
    if (pct >= 80) return 'warning'
    return 'normal'
  })

  async function fetchUsage() {
    loading.value = true
    try {
      const res = await getStorageUsage()
      usage.value = res.data
    } catch (e) {
      console.error('获取存储空间信息失败', e)
    } finally {
      loading.value = false
    }
  }

  function formatSize(bytes: number): string {
    if (bytes === 0) return '0 B'
    const units = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`
  }

  return {
    usage, loading, usagePercentage, totalQuota, usedQuota,
    availableQuota, breakdown, warningLevel,
    fetchUsage, formatSize,
  }
})
