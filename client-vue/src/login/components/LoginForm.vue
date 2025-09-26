
<template>
  <form key="login" class="form" @submit.prevent="handleLogin">
    <div class="form-group">
      <label for="login-email">邮箱</label>
      <input
        id="login-email"
        v-model="loginForm.email"
        type="email"
        class="form-input"
        :class="{ 'input-error': emailError }"
        placeholder="请输入您的邮箱"
        required
        @blur="triggerEmailValidation"
      />
      <p v-if="emailError" class="error-message">请输入有效的邮箱地址</p>
    </div>

    <div class="form-group">
      <label for="login-password">密码</label>
      <input
        id="login-password"
        v-model="loginForm.password"
        type="password"
        class="form-input"
        placeholder="请输入您的密码"
        required
      />
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

// 登录表单数据
const loginForm = ref({
  email: '',
  password: '',
  rememberMe: false
})

// 使用组合式函数进行邮箱验证
const { isEmailValid, emailError, triggerEmailValidation } = useEmailValidator(toRef(loginForm.value, 'email'))

const handleLogin = () => {
  triggerEmailValidation()
  if (!isEmailValid.value) {
    return
  }
  // 在这里处理登录逻辑
  console.log('正在使用以下信息登录:', loginForm.value)
}
</script>
]]>
