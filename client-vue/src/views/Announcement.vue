<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="auth-title">公告栏</h1>
        <p class="auth-subtitle">登录后显示的主页公告，配色与登录页一致。</p>
      </div>

      <div class="announcement-list">
        <article class="announcement">
          <h3>版本更新</h3>
          <p>已移除旧的独立聊天界面，聊天功能已迁移为可选模块。如需恢复，请联系管理员。</p>
        </article>

        <article class="announcement">
          <h3>维护通知</h3>
          <p>系统将在下周二 02:00—04:00 进行维护，期间服务可能中断。</p>
        </article>

        <article class="announcement">
          <h3>使用提示</h3>
          <p>使用左下角菜单可以展开功能侧边栏，快速导航到聊天、Blog 或登录页面。</p>
        </article>
      </div>

      <div class="auth-actions" style="margin-top:24px; display:flex; gap:12px;">
        <button class="auth-button" @click="goLogin">登录</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import '../login/styles/auth-common.css'

const router = useRouter()


const goLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.announcement {
  background: #f7fafc;
  border-radius: 10px;
  padding: 12px 14px;
  border: 1px solid #edf2f7;
}

.announcement h3 {
  margin: 0 0 6px 0;
  color: #2d3748;
  font-size: 16px;
}

.announcement p {
  margin: 0;
  color: #4a5568;
  font-size: 14px;
}
</style>
