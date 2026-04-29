import request from '@/utils/request'

/** 注册请求参数 */
export interface RegisterParams {
  username: string
  email: string
  password: string
  confirm_password: string
}

/** 登录请求参数 */
export interface LoginParams {
  email: string
  password: string
}

/** 认证响应数据 */
export interface AuthData {
  access_token: string
  refresh_token: string
  token_type: string
  user: {
    id: number
    username: string
    email: string
  }
}

/** 用户注册 */
export function registerApi(data: RegisterParams) {
  return request.post<any, { code: string; message: string; data: AuthData }>(
    '/auth/register',
    data
  )
}

/** 用户登录 */
export function loginApi(data: LoginParams) {
  return request.post<any, { code: string; message: string; data: AuthData }>(
    '/auth/login',
    data
  )
}

/** 刷新 Token */
export function refreshTokenApi(refresh_token: string) {
  return request.post<any, { code: string; message: string; data: { access_token: string; refresh_token: string } }>(
    '/auth/refresh',
    { refresh_token }
  )
}

/** 退出登录 */
export function logoutApi() {
  return request.post<any, { code: string; message: string }>(
    '/auth/logout'
  )
}
