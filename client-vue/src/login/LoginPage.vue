
<template>
  <div class="auth-container">
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
          <component :is="isLogin ? LoginForm : RegisterForm" />
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import LoginForm from './components/LoginForm.vue'
import RegisterForm from './components/RegisterForm.vue'

// 控制显示登录还是注册
const isLogin = ref(true)
</script>

<style>
@import './styles/auth-common.css';
@import './styles/auth-forms.css';
</style>

