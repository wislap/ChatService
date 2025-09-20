<template>
  <div>
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

    <form key="register" class="form" @submit.prevent="handleSubmit">
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
      >
        注册
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import zxcvbn from 'zxcvbn'

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

const checkPasswordStrength = () => {
  if (registerForm.value.password && !isPasswordSecure.value) {
    showPasswordAlert.value = true
  }
}

const closePasswordAlert = () => {
  showPasswordAlert.value = false
}

const handleSubmit = () => {
  if (!isFormValid.value) {
    if (!isPasswordSecure.value) {
      showPasswordAlert.value = true
    }
    // 可以添加其他验证失败的提示
    return
  }
  // 处理表单提交逻辑
  console.log('注册表单提交成功:', registerForm.value)
}

// 翻译函数
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
  };
  return translations[suggestion] || suggestion;
};

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
  };
  return translations[warning] || warning;
};
</script>
]]>
