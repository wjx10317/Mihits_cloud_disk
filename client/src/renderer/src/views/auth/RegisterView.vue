<template>
  <div class="auth-container">
    <!-- 左侧品牌区 -->
    <div class="auth-brand">
      <div class="brand-content">
        <h1 class="brand-title">Mihits</h1>
        <p class="brand-subtitle">开始你的云端之旅</p>
        <div class="brand-features">
          <div class="feature-item">
            <el-icon size="24"><Upload /></el-icon>
            <span>极速上传下载</span>
          </div>
          <div class="feature-item">
            <el-icon size="24"><FolderOpened /></el-icon>
            <span>智能文件管理</span>
          </div>
          <div class="feature-item">
            <el-icon size="24"><Lock /></el-icon>
            <span>安全加密存储</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧表单区 -->
    <div class="auth-form-area">
      <div class="auth-form-wrapper">
        <h2 class="form-title">创建账号</h2>
        <p class="form-desc">注册一个全新的 Mihits 账号</p>

        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          size="large"
          @keyup.enter="handleRegister"
        >
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="请输入用户名"
              prefix-icon="User"
              clearable
            />
          </el-form-item>

          <el-form-item prop="email">
            <el-input
              v-model="registerForm.email"
              placeholder="请输入邮箱"
              prefix-icon="Message"
              clearable
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="请输入密码（至少8位）"
              prefix-icon="Lock"
              show-password
              clearable
            />
          </el-form-item>

          <el-form-item prop="confirm_password">
            <el-input
              v-model="registerForm.confirm_password"
              type="password"
              placeholder="请确认密码"
              prefix-icon="Lock"
              show-password
              clearable
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              class="register-btn"
              :loading="loading"
              @click="handleRegister"
            >
              {{ loading ? '注册中...' : '注 册' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <span>已有账号？</span>
          <el-link type="primary" @click="$router.push('/login')">立即登录</el-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Upload, FolderOpened, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const registerFormRef = ref<FormInstance>()
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirm_password: ''
})

// 自定义确认密码校验
const validateConfirmPassword = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度 2-20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 32, message: '密码长度 8-32 位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

async function handleRegister() {
  if (!registerFormRef.value) return
  const valid = await registerFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const success = await authStore.register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      confirm_password: registerForm.confirm_password
    })
    if (success) {
      router.push('/')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.auth-brand {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.auth-brand::before {
  content: '';
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  top: -200px;
  left: -100px;
}

.auth-brand::after {
  content: '';
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  bottom: -100px;
  right: -50px;
}

.brand-content {
  text-align: center;
  color: white;
  z-index: 1;
  padding: 0 40px;
}

.brand-title {
  font-size: 56px;
  font-weight: 700;
  margin: 0 0 12px 0;
  letter-spacing: -1px;
  text-shadow: 0 2px 20px rgba(0, 0, 0, 0.15);
}

.brand-subtitle {
  font-size: 20px;
  opacity: 0.9;
  margin: 0 0 48px 0;
  font-weight: 300;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: flex-start;
  max-width: 220px;
  margin: 0 auto;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  opacity: 0.85;
}

.auth-form-area {
  width: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  padding: 40px;
}

.auth-form-wrapper {
  width: 100%;
  max-width: 360px;
}

.form-title {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.form-desc {
  font-size: 15px;
  color: #8c8ca1;
  margin: 0 0 28px 0;
}

.register-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.register-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.form-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: #8c8ca1;
}

.form-footer .el-link {
  font-size: 14px;
  margin-left: 4px;
}

@media (max-width: 900px) {
  .auth-brand {
    display: none;
  }
  .auth-form-area {
    width: 100%;
  }
}
</style>
