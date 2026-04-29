import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginApi, registerApi, refreshTokenApi, logoutApi } from '@/api/auth'
import type { LoginParams, RegisterParams, AuthData } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', () => {
  // ===== State =====
  const user = ref<{ id: number; username: string; email: string } | null>(null)
  const accessToken = ref<string>('')
  const refreshToken = ref<string>('')

  // 从 localStorage 恢复会话
  function restoreSession() {
    const authStr = localStorage.getItem('auth')
    if (authStr) {
      try {
        const auth: AuthData = JSON.parse(authStr)
        user.value = auth.user
        accessToken.value = auth.access_token
        refreshToken.value = auth.refresh_token
      } catch {
        localStorage.removeItem('auth')
      }
    }
  }

  // 初始化时恢复
  restoreSession()

  // ===== Getters =====
  const isLoggedIn = computed(() => !!accessToken.value)

  // ===== Actions =====

  /** 保存认证数据到本地 */
  function saveAuthData(data: AuthData) {
    user.value = data.user
    accessToken.value = data.access_token
    refreshToken.value = data.refresh_token
    localStorage.setItem('auth', JSON.stringify(data))
  }

  /** 清除认证数据 */
  function clearAuthData() {
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''
    localStorage.removeItem('auth')
  }

  /** 用户登录 */
  async function login(params: LoginParams): Promise<boolean> {
    try {
      const res = await loginApi(params)
      if (res.code === 'SUCCESS') {
        saveAuthData(res.data)
        ElMessage.success('登录成功')
        return true
      }
      return false
    } catch {
      return false
    }
  }

  /** 用户注册 */
  async function register(params: RegisterParams): Promise<boolean> {
    try {
      const res = await registerApi(params)
      if (res.code === 'SUCCESS') {
        saveAuthData(res.data)
        ElMessage.success('注册成功')
        return true
      }
      return false
    } catch {
      return false
    }
  }

  /** 刷新 Token */
  async function refresh(): Promise<boolean> {
    if (!refreshToken.value) return false
    try {
      const res = await refreshTokenApi(refreshToken.value)
      if (res.code === 'SUCCESS') {
        accessToken.value = res.data.access_token
        refreshToken.value = res.data.refresh_token
        // 更新 localStorage
        const authStr = localStorage.getItem('auth')
        if (authStr) {
          const auth = JSON.parse(authStr)
          auth.access_token = res.data.access_token
          auth.refresh_token = res.data.refresh_token
          localStorage.setItem('auth', JSON.stringify(auth))
        }
        return true
      }
      return false
    } catch {
      clearAuthData()
      return false
    }
  }

  /** 退出登录 */
  async function logout() {
    try {
      await logoutApi()
    } catch {
      // 即使后端退出失败也清除本地状态
    }
    clearAuthData()
    ElMessage.success('已退出登录')
  }

  return {
    user,
    accessToken,
    refreshToken,
    isLoggedIn,
    login,
    register,
    refresh,
    logout,
    restoreSession,
    saveAuthData,
    clearAuthData
  }
})
