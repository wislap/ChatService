<template>
  <form key="login" class="form" @submit.prevent="handleLogin">
    <div class="form-group">
      <label for="login-email">邮箱</label>
      <input id="login-email" v-model="loginForm.email" type="email" class="form-input"
        :class="{ 'input-error': emailError }" placeholder="请输入您的邮箱" required @blur="triggerEmailValidation" />
      <p v-if="emailError" class="error-message">请输入有效的邮箱地址</p>
    </div>

    <div class="form-group">
      <label for="login-password">密码</label>
      <input id="login-password" v-model="loginForm.password" type="password" class="form-input" placehowlder="请输入您的密码"
        required />
    </div>

    <div class="form-options">
      <label class="checkbox-label">
        <input v-model="loginForm.rememberMe" type="checkbox" />
        <span class="checkmark"></span>
        记住我
      </label>
      <a href="#" class="forgot-link">忘记密码？</a>
    </div>

    <button type="submit" class="auth-button primary">
      登录
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref, toRef } from 'vue'
import { useEmailValidator } from '@/utils/authValidators'
import api from '@/utils/api'
// 登录表单数据

interface LoginForm {
  email: string
  password: string
  rememberMe: boolean
}
interface LoginResponse {
  token: string
  expiresIn?: number // 可选：后端返回有效时间（秒）
  message?: string
}

const loginForm = ref<LoginForm>({
  email: '',
  password: '',
  rememberMe: false
})
// 使用组合式函数进行邮箱验证
const { isEmailValid, emailError, triggerEmailValidation } = useEmailValidator(toRef(loginForm.value, 'email'))

// 辅助函数：检测 localStorage 是否有有效 token
const isLocalTokenValid = (): boolean => {
  const token = localStorage.getItem('token')
  const expiry = localStorage.getItem('token_expiry')

  if (!token || !expiry) return false

  const now = Date.now()
  const expiryTime = Number(expiry)
  return now < expiryTime
}
import { useRouter } from 'vue-router'
// 自动登录逻辑（改为使用 router.push 并延迟，避免同步卸载导致的闪烁）
const router = useRouter()
const autoLogin = (): void => {
  const token = localStorage.getItem('token')
  if (token) {
    sessionStorage.setItem('token', token)
    console.log('✅ 自动登录成功，token 已同步到 sessionStorage')
    // 延迟路由跳转，给 Vue 过渡一帧时间完成渲染，减少白屏闪烁
    setTimeout(() => {
      router.push('/')
    }, 0)
  }
}
const handleLogin = async () => {
  triggerEmailValidation()
  if (!isEmailValid.value) {
    return
  }
  // ① 检查 localStorage 中是否有未过期 token
  if (isLocalTokenValid()) {
    const confirmAutoLogin = window.confirm('检测到有效登录状态，是否自动登录？')
    if (confirmAutoLogin) {
      autoLogin()
      return
    }
  }

  // 在这里处理登录逻辑
  try {
    const res = await api.post<LoginResponse>('/user/login/', {
      email: loginForm.value.email,
      password: loginForm.value.password
    })
    const token = res.data.token
    console.log('Received token:', res)
    if (!token) throw new Error('后端未返回 token')
    // 计算过期时间：默认 7 天
    const expiresIn = res.data.expiresIn ? res.data.expiresIn * 1000 : 7 * 24 * 60 * 60 * 1000
    const expiryTime = Date.now() + expiresIn
    // ✅ 根据“记住我”状态选择存储方式
    if (loginForm.value.rememberMe) {
      localStorage.setItem('token', token)
      localStorage.setItem('token_expiry', expiryTime.toString())
    }
    // ✅ 同步当前会话登录
    sessionStorage.setItem('token', token)

    // 全局设置请求头
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`

    console.log('登录成功，token 已保存')

    // 跳转（改为 router.push 并延迟）
    setTimeout(() => {
      router.push('/')
    }, 0)
  } catch (error) {
    const msg = (error as Error)?.message ?? String(error)
    console.error('登录失败:', msg)
  }
}

</script>
]]
