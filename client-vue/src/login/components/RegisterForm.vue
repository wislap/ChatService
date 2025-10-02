<template>
  <div>
    <!-- 密码强度不足提示框 -->
    <transition name="modal">
      <div v-if="showPasswordAlert" class="password-alert-overlay" @click="closePasswordAlert">
        <div class="password-alert-modal" @click.stop>
          <div class="modal-content">
            <div class="alert-header">
              <h3>密码强度不足</h3>
              <button class="close-button" @click="closePasswordAlert">×</button>
            </div>
            <div class="alert-content">
              <div class="alert-icon">⚠️</div>
              <p class="alert-message">您当前的密码强度为：<strong>{{ strengthText }}</strong></p>
              <p class="alert-requirement">为了您的账户安全，密码强度需要达到"一般"级别或以上。</p>
              <div v-if="passwordStrength && passwordStrength.feedback.suggestions.length > 0" class="alert-suggestions">
                <h4>改进建议：</h4>
                <ul>
                  <li v-for="suggestion in passwordStrength.feedback.suggestions" :key="suggestion">
                    {{ translateSuggestion(suggestion) }}
                  </li>
                </ul>
              </div>
              <div v-if="passwordStrength && passwordStrength.feedback.warning" class="alert-warning">
                <strong>注意：</strong>{{ translateWarning(passwordStrength.feedback.warning) }}
              </div>
            </div>
            <div class="alert-actions">
              <button class="alert-button primary" @click="closePasswordAlert">我知道了</button>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 验证码发送确认框 -->
    <transition name="modal">
      <div v-if="showVerificationModal" class="password-alert-overlay" @click="closeVerificationModal">
        <div class="password-alert-modal" @click.stop>
          <div class="modal-content">
            <div class="alert-header">
              <h3>确认邮箱</h3>
              <button class="close-button" @click="closeVerificationModal">×</button>
            </div>
            <div class="alert-content">
              <div class="alert-icon">✉️</div>
              <p class="alert-message">我们将发送验证码到您的邮箱：</p>
              <p class="email-display">{{ registerForm.email }}</p>
            </div>
            <div class="alert-actions">
              <button class="alert-button primary" @click="sendVerificationCode">发送验证码</button>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <form key="register" class="form" @submit.prevent="handleSubmit">
      <div class="form-row">
        <div class="form-group">
          <label for="register-lastname">名字</label>
          <input id="register-lastname" v-model="registerForm.lastName" type="text" class="form-input" placeholder="名字" required />
        </div>
      </div>

      <div class="form-group">
        <label for="register-email">邮箱</label>
        <input
          id="register-email"
          v-model="registerForm.email"
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
        <label for="register-password">密码</label>
        <input
          id="register-password"
          v-model="registerForm.password"
          type="password"
          class="form-input"
          placeholder="请输入密码（至少6位）"
          required
          @blur="checkPasswordStrength"
        />
        <div v-if="registerForm.password && passwordStrength" class="password-strength">
          <div class="strength-header">
            <span class="strength-label">密码强度: {{ strengthText }}</span>
            <div class="strength-score">
              <div
                v-for="i in 5"
                :key="i"
                :class="['strength-dot', { active: i <= passwordStrength.score + 1 }]"
                :style="{ backgroundColor: i <= passwordStrength.score + 1 ? strengthColor : '#e2e8f0' }"
              ></div>
            </div>
          </div>
          <div v-if="passwordStrength.feedback.suggestions.length > 0" class="strength-suggestions">
            <p class="suggestions-title">建议:</p>
            <ul class="suggestions-list">
              <li v-for="suggestion in passwordStrength.feedback.suggestions" :key="suggestion">
                {{ translateSuggestion(suggestion) }}
              </li>
            </ul>
          </div>
          <div v-if="passwordStrength.feedback.warning" class="strength-warning">
            {{ translateWarning(passwordStrength.feedback.warning) }}
          </div>
        </div>
      </div>

      <div class="form-group">
        <label for="register-confirm">确认密码</label>
        <input
          id="register-confirm"
          v-model="registerForm.confirmPassword"
          type="password"
          class="form-input"
          placeholder="请再次输入密码"
          required
        />
        <div v-if="passwordMatchStatus" class="password-match">
          <span :class="['match-status', passwordsMatch ? 'match' : 'no-match']">
            {{ passwordsMatch ? '✓ 密码匹配' : '✗ 密码不匹配' }}
          </span>
        </div>
      </div>

      <div class="form-options">
        <label class="checkbox-label">
          <input v-model="registerForm.acceptTerms" type="checkbox" required />
          <span class="checkmark"></span>
          我同意<a href="#" class="terms-link">服务条款</a>和<a href="#" class="terms-link">隐私政策</a>
        </label>
      </div>

      <button type="submit" class="auth-button primary" :disabled="!isFormValid" :class="{ disabled: !isFormValid }" >
        注册
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">

import { ref, computed, toRef } from 'vue'
import { useEmailValidator, usePasswordValidator } from '@/utils/authValidators'
import api from '@/utils/api'


// 注册表单数据
const registerForm = ref({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false
})

const showPasswordAlert = ref(false)
const showVerificationModal = ref(false)

// 使用组合式函数进行验证
const { isEmailValid, emailError, triggerEmailValidation } = useEmailValidator(toRef(registerForm.value, 'email'))
const {
  passwordStrength,
  strengthText,
  strengthColor,
  isPasswordSecure,
  passwordsMatch,
  passwordMatchStatus,
  translateSuggestion,
  translateWarning
} = usePasswordValidator(toRef(registerForm.value, 'password'), toRef(registerForm.value, 'confirmPassword'))

// 检查表单整体是否有效
const isFormValid = computed(() => {
  return (
    registerForm.value.lastName &&
    registerForm.value.email &&
    isEmailValid.value &&
    registerForm.value.password &&
    registerForm.value.confirmPassword &&
    passwordsMatch.value &&
    isPasswordSecure.value &&
    registerForm.value.acceptTerms
  )
})

// 检查密码强度（失去焦点时触发）
const checkPasswordStrength = () => {
  if (registerForm.value.password && !isPasswordSecure.value) {
    showPasswordAlert.value = true
  }
}

const closePasswordAlert = () => {
  showPasswordAlert.value = false
}

const handleSubmit = () => {
  triggerEmailValidation()
  if (!isFormValid.value) {
    if (!isPasswordSecure.value) {
      showPasswordAlert.value = true
    }
    return
  }
  showVerificationModal.value = true
}

const closeVerificationModal = () => {
  showVerificationModal.value = false
}

const sendVerificationCode = async () => {
  console.log(`正在向 ${registerForm.value.email} 发送验证码...`)
  try {
    await api.post('/user/register1', {
      username: registerForm.value.lastName,
      password: registerForm.value.password,
      email: registerForm.value.email
    })
    closeVerificationModal()
  } catch (error) {
    console.error('注册失败:', error)
    // 在这里可以添加错误处理逻辑，例如显示一个错误提示
    closeVerificationModal()
  }
}
</script>

<style scoped>
.email-display {
  font-weight: bold;
  color: #2d3748;
  background-color: #f7fafc;
  padding: 8px 12px;
  border-radius: 8px;
  text-align: center;
  margin-top: 8px;
}
</style>
]]>
