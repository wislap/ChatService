
import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import zxcvbn from 'zxcvbn'

/**
 * 组合式函数：用于验证邮箱格式
 * @param email - 一个包含邮箱字符串的 Ref
 */
export function useEmailValidator(email: Ref<string>) {
  const showEmailError = ref(false)

  const isEmailValid = computed(() => {
    // 只有在有输入时才开始验证
    if (!email.value) return true
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email.value)
  })

  const emailError = computed(() => {
    return showEmailError.value && !isEmailValid.value
  })

  const triggerEmailValidation = () => {
    showEmailError.value = true
  }

  return {
    isEmailValid,
    emailError,
    triggerEmailValidation,
    showEmailError
  }
}

/**
 * 组合式函数：用于验证密码强度和匹配
 * @param password - 包含密码的 Ref
 * @param confirmPassword - 包含确认密码的 Ref
 */
export function usePasswordValidator(password: Ref<string>, confirmPassword?: Ref<string>) {
  const passwordStrength = computed(() => {
    if (!password.value) return null
    return zxcvbn(password.value)
  })

  const strengthText = computed(() => {
    if (!passwordStrength.value) return ''
    const levels = ['非常弱', '弱', '一般', '强', '非常强']
    return levels[passwordStrength.value.score]
  })

  const strengthColor = computed(() => {
    if (!passwordStrength.value) return '#e2e8f0'
    const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#16a34a']
    return colors[passwordStrength.value.score]
  })

  const isPasswordSecure = computed(() => {
    return passwordStrength.value && passwordStrength.value.score >= 2
  })

  const passwordsMatch = computed(() => {
    if (confirmPassword === undefined) return true
    // 只有在确认密码框有输入时才开始比较
    if (!confirmPassword.value) return true
    return password.value === confirmPassword.value
  })

  const passwordMatchStatus = computed(() => {
    return confirmPassword && confirmPassword.value.length > 0
  })

  // 翻译建议和警告
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

  return {
    passwordStrength,
    strengthText,
    strengthColor,
    isPasswordSecure,
    passwordsMatch,
    passwordMatchStatus,
    translateSuggestion,
    translateWarning
  }
}

