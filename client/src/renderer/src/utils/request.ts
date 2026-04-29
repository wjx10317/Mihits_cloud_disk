import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// 后端 API 基础地址
const BASE_URL = 'http://localhost:8000/api/v1'

const request: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：自动附带 Token
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStr = localStorage.getItem('auth')
    if (authStr) {
      try {
        const auth = JSON.parse(authStr)
        if (auth.access_token) {
          config.headers.Authorization = `Bearer ${auth.access_token}`
        }
      } catch {
        // 忽略解析错误
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const data = response.data
    // 后端返回 { code, message, data } 格式
    if (data.code && data.code !== 'SUCCESS') {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }
    return data
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      const message = data?.message || '请求失败'

      switch (status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          // 清除本地 token，跳转登录
          localStorage.removeItem('auth')
          window.location.hash = '#/login'
          break
        case 422:
          ElMessage.error('请求参数错误')
          break
        default:
          ElMessage.error(message)
      }
    } else if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请检查网络')
    } else {
      ElMessage.error('网络连接失败，请检查后端服务是否启动')
    }
    return Promise.reject(error)
  }
)

export default request
