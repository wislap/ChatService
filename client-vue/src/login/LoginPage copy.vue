<template>

  <div class="auth-container" appear>
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
    <div class="auth-card">
      <!-- 标题栏 -->
      <div class="auth-header">
        <h1 class="auth-title">{{ isLogin ? '登录' : '注册' }}</h1>
        <p class="auth-subtitle">
          {{ isLogin ? '欢迎回来！请登录您的账户' : '创建新账户，开始您的旅程' }}
        </p>
      </div>

      <!-- 切换按钮 -->
      <div class="auth-tabs">
        <button
          :class="['tab-button', { active: isLogin }]"
          @click="isLogin = true"
        >
          登录
        </button>
        <button
          :class="['tab-button', { active: !isLogin }]"
          @click="isLogin = false"
        >
          注册
        </button>
      </div>

      <!-- 表单内容 -->
      <div class="auth-form">
        <transition name="fade" mode="out-in">
          <!-- 登录表单 -->
          <form v-if="isLogin" key="login" class="form">
            <div class="form-group">
              <label for="login-email">邮箱</label>
              <input
                id="login-email"
                v-model="loginForm.email"
                type="email"
                class="form-input"
                placeholder="请输入您的邮箱"
                required
              />
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

          <!-- 注册表单 -->
          <form v-else key="register" class="form">
            <div class="form-row">
              <div class="form-group">
                <label for="register-firstname">姓</label>
                <input
                  id="register-firstname"
                  v-model="registerForm.firstName"
                  type="text"
                  class="form-input"
                  placeholder="姓"
                  required
                />
              </div>
              <div class="form-group">
                <label for="register-lastname">名</label>
                <input
                  id="register-lastname"
                  v-model="registerForm.lastName"
                  type="text"
                  class="form-input"
                  placeholder="名"
                  required
                />
              </div>
            </div>

            <div class="form-group">
              <label for="register-email">邮箱</label>
              <input
                id="register-email"
                v-model="registerForm.email"
                type="email"
                class="form-input"
                placeholder="请输入您的邮箱"
                required
              />
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

              <!-- 密码强度指示器 -->
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

                <!-- 密码建议 -->
                <div v-if="passwordStrength.feedback.suggestions.length > 0" class="strength-suggestions">
                  <p class="suggestions-title">建议:</p>
                  <ul class="suggestions-list">
                    <li v-for="suggestion in passwordStrength.feedback.suggestions" :key="suggestion">
                      {{ translateSuggestion(suggestion) }}
                    </li>
                  </ul>
                </div>

                <!-- 警告信息 -->
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
              <!-- 密码匹配提示 -->
              <div v-if="registerForm.confirmPassword && passwordMatchStatus" class="password-match">
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

            <button
              type="submit"
              class="auth-button primary"
              :disabled="!isFormValid"
              :class="{ disabled: !isFormValid }"
              @click="handleSubmit"
            >
              注册
            </button>

          </form>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import zxcvbn from 'zxcvbn'

// 控制显示登录还是注册
const isLogin = ref(true)

// 登录表单数据
const loginForm = ref({
  email: '',
  password: '',
  rememberMe: false
})

// 注册表单数据
const registerForm = ref({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false
})

// 计算密码强度
const passwordStrength = computed(() => {
  if (!registerForm.value.password) return null
  return zxcvbn(registerForm.value.password)
})

// 密码强度文本
const strengthText = computed(() => {
  if (!passwordStrength.value) return ''
  const levels = ['非常弱', '弱', '一般', '强', '非常强']
  return levels[passwordStrength.value.score]
})

// 密码强度颜色
const strengthColor = computed(() => {
  if (!passwordStrength.value) return '#e2e8f0'
  const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#16a34a']
  return colors[passwordStrength.value.score]
})

// 密码匹配状态
const passwordMatchStatus = computed(() => {
  return registerForm.value.confirmPassword.length > 0
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

const passwordsMatch = computed(() => {
  return registerForm.value.password === registerForm.value.confirmPassword
})
const isPasswordSecure = computed(() => {
  return passwordStrength.value && passwordStrength.value.score >= 2
})
const isFormValid = computed(() => {
  return registerForm.value.firstName &&
         registerForm.value.lastName &&
         registerForm.value.email &&
         registerForm.value.password &&
         registerForm.value.confirmPassword &&
         passwordsMatch.value &&
         isPasswordSecure.value &&
         registerForm.value.acceptTerms
})
const showPasswordError = ref(false)
const showPasswordAlert = ref(false)
const handleSubmit = (event: Event) => {
  event.preventDefault()

  if (!isPasswordSecure.value) {
    showPasswordAlert.value = true
    showPasswordError.value = true
    return
  }

  if (!isFormValid.value) {
    return
  }

  showPasswordError.value = false
  // 处理表单提交逻辑
  console.log('表单提交成功')
}

// 当密码改变时隐藏错误提示
watch(() => registerForm.value.password, () => {
  showPasswordError.value = false
})
// 翻译建议
const translateSuggestion = (suggestion: string): string => {
  const translations: { [key: string]: string } = {
    'Add another word or two. Uncommon words are better.': '添加一两个单词。不常见的单词更好。',
    'Use a longer keyboard pattern with more turns.': '使用更长的键盘模式，包含更多转向。',
    'Avoid repeated words and characters.': '避免重复的单词和字符。',
    'Avoid sequences.': '避免使用序列。',
    'Avoid recent years.': '避免使用近期年份。',
    'Avoid years that are associated with you.': '避免使用与你相关的年份。',
    'Avoid dates and years that are associated with you.': '避免使用与你相关的日期和年份。',
    'Capitalization doesn\'t help very much.': '大写化并不能提供很大帮助。',
    'All-uppercase is almost as easy to guess as all-lowercase.': '全大写几乎和全小写一样容易猜测。',
    'Reversed words aren\'t much harder to guess.': '倒写的单词不会更难猜测。',
    'Predictable substitutions like \'@\' instead of \'a\' don\'t help very much.': '像用\'@\'代替\'a\'这样的可预测替换帮助不大。'
  }
  return translations[suggestion] || suggestion
}

// 翻译警告
const translateWarning = (warning: string): string => {
  const translations: { [key: string]: string } = {
    'This is a top-10 common password.': '这是一个非常常见的密码。',
    'This is a top-100 common password.': '这是一个常见密码。',
    'This is a very common password.': '这是一个很常见的密码。',
    'This is similar to a commonly used password.': '这与常用密码相似。',
    'A word by itself is easy to guess.': '单独的单词很容易被猜到。',
    'Names and surnames by themselves are easy to guess.': '单独的姓名很容易被猜到。',
    'Common names and surnames are easy to guess.': '常见的姓名很容易被猜到。',
    'Straight rows of keys are easy to guess.': '键盘上的直行按键很容易被猜到。',
    'Short keyboard patterns are easy to guess.': '短的键盘模式很容易被猜到。',
    'Repeats like "aaa" are easy to guess.': '像"aaa"这样的重复很容易被猜到。',
    'Repeats like "abcabcabc" are only slightly harder to guess than "abc".': '像"abcabcabc"这样的重复比"abc"只是稍微难猜一点。',
    'Sequences like abc or 6543 are easy to guess.': '像abc或6543这样的序列很容易被猜到。',
    'Recent years are easy to guess.': '近期年份很容易被猜到。',
    'Dates are often easy to guess.': '日期通常很容易被猜到。'
  }
  return translations[warning] || warning
}
</script>

<style scoped>
.input-error {
  border-color: #dc2626 !important;
}

.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.auth-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 440px;
  min-height: 600px;
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-title {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 8px 0;
}

.auth-subtitle {
  color: #718096;
  margin: 0;
  font-size: 14px;
}

.auth-tabs {
  display: flex;
  background: #f7fafc;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 30px;
}

.tab-button {
  flex: 1;
  padding: 12px 16px;
  border: none;
  background: transparent;
  color: #718096;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-button.active {
  background: white;
  color: #4c51bf;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form {
  width: 100%;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-group {
  margin-bottom: 20px;
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #2d3748;
  font-size: 14px;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #4c51bf;
}

/* 密码强度样式 */
.password-strength {
  margin-top: 8px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}
.password-requirements {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}
.requirement-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}
.requirement-status.met {
  color: #16a34a;
  font-weight: bold;
}

.requirement-status.not-met {
  color: #dc2626;
  font-weight: bold;
}

.requirement-text {
  color: #4b5563;
}
.strength-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.strength-label {
  font-size: 12px;
  font-weight: 500;
  color: #4a5568;
}

.strength-score {
  display: flex;
  gap: 4px;
}

.strength-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.strength-suggestions {
  margin-top: 8px;
}

.suggestions-title {
  font-size: 12px;
  font-weight: 500;
  color: #4a5568;
  margin: 0 0 4px 0;
}

.suggestions-list {
  margin: 0;
  padding-left: 16px;
  font-size: 12px;
  color: #718096;
}

.suggestions-list li {
  margin-bottom: 2px;
}

.strength-warning {
  margin-top: 8px;
  padding: 8px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  font-size: 12px;
  color: #dc2626;
}

/* 密码匹配样式 */
.password-match {
  margin-top: 4px;
}

.match-status {
  font-size: 12px;
  font-weight: 500;
}

.match-status.match {
  color: #16a34a;
}

.match-status.no-match {
  color: #dc2626;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #4a5568;
}

.checkbox-label input[type="checkbox"] {
  margin-right: 8px;
}

.checkmark {
  margin-left: 4px;
}

.forgot-link,
.terms-link {
  color: #4c51bf;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.forgot-link:hover,
.terms-link:hover {
  text-decoration: underline;
}

.auth-button {
  width: 100%;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.auth-button.primary {
  background: #4c51bf;
  color: white;
  margin-bottom: 20px;
}

.auth-button.primary:hover {
  background: #4338ca;
  transform: translateY(-1px);
}

.auth-button.secondary {
  background: #f7fafc;
  color: #4a5568;
  border: 2px solid #e2e8f0;
}

.auth-button.secondary:hover {
  background: #edf2f7;
  border-color: #cbd5e0;
}

.icon {
  flex-shrink: 0;
}

.divider {
  text-align: center;
  margin: 20px 0;
  position: relative;
  color: #a0aec0;
  font-size: 14px;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #e2e8f0;
}

.divider span {
  background: white;
  padding: 0 16px;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .auth-card {
    padding: 24px;
    margin: 10px;
  }

  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-options {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}

.modal-enter-active {
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
}

.modal-leave-active {
  transition: all 0.3s cubic-bezier(0.755, 0.05, 0.855, 0.06);
}

.modal-enter-from {
  opacity: 0;
}

.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .password-alert-modal {
  transform: scale(0.8) translateY(-50px);
  opacity: 0;
}

.modal-leave-to .password-alert-modal {
  transform: scale(0.95) translateY(20px);
  opacity: 0;
}
/* 弹窗遮罩层 */
.password-alert-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(31, 41, 55, 0.5);
  backdrop-filter: blur(8px) saturate(120%);
  -webkit-backdrop-filter: blur(8px) saturate(120%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

/* 弹窗主体 */
.password-alert-modal {
  width: 100%;
  max-width: 420px;
  max-height: 85vh;
  border-radius: 20px;
  background: linear-gradient(135deg,
      rgba(255, 255, 255, 0.85) 0%,
      rgba(255, 255, 255, 0.75) 100%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow:
    0 20px 40px rgba(0, 0, 0, 0.15),
    0 10px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

/* 内容容器 */
.modal-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: transparent;
}
/* 其他样式保持不变，但确保所有内容元素都有适当的z-index */
.alert-header {
  position: relative;
  z-index: 3;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 16px;
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
}

.alert-header h3 {
  margin: 0;
  color: #dc2626;
  font-size: 18px;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-button:hover {
  background: #f3f4f6;
}


.alert-content {
  position: relative;
  z-index: 3;
  padding: 20px 24px;
  flex: 1;
  overflow-y: auto;
}

.alert-icon {
  font-size: 32px;
  text-align: center;
  margin-bottom: 16px;
}

.alert-message {
  font-size: 16px;
  color: #374151;
  margin-bottom: 12px;
  text-align: center;
}

.alert-requirement {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 20px;
  text-align: center;
}

.alert-suggestions {
  margin-bottom: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.alert-suggestions h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.alert-suggestions ul {
  margin: 0;
  padding-left: 16px;
}

.alert-suggestions li {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 6px;
  line-height: 1.4;
}

.alert-warning {
  padding: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  font-size: 13px;
  color: #dc2626;
  line-height: 1.4;
}


.alert-actions {
  position: relative;
  z-index: 3;
  padding: 16px 24px 24px;
  display: flex;
  gap: 12px;
  flex-direction: column;
  border-top: 1px solid rgba(229, 231, 235, 0.5);
}

.alert-button {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  z-index: 4;
}

.alert-button.primary {
  background: #dc2626;
  color: white;
}

.alert-button.primary:hover {
  background: #b91c1c;
}

.alert-button.secondary {
  background: #f9fafb;
  color: #374151;
  border: 1px solid #d1d5db;
}

.alert-button.secondary:hover {
  background: #f3f4f6;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .password-alert-overlay {
    padding: 15px;
  }

  .password-alert-modal {
    max-width: 100%;
    border-radius: 16px;
  }

  .modal-backdrop {
    border-radius: 16px;
  }

  .alert-header {
    padding: 20px 20px 16px;
  }

  .alert-body {
    padding: 0 20px 16px;
  }

  .alert-actions {
    padding: 16px 20px 20px;
    flex-direction: column;
  }

  .close-button {
    top: 16px;
    right: 16px;
  }
}
</style>
