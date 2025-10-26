<template>
  <div class="blog-page">
    <div class="blog-container">
      <header class="blog-header">
        <h1>{{ title }}</h1>
      </header>

      <section class="blog-content">
        <!-- 子路由内容将在此渲染 -->
        <router-view />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => route.meta.title || 'Blog')
</script>

<style scoped>
.blog-page {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 32px;
  min-height: 100vh;
  box-sizing: border-box;
  background: transparent;
}

.blog-container {
  width: calc(100% - 64px);
  max-width: 1920px;
  min-height: calc(100vh - 64px);
  background: #ffffff;
  border: 1px solid rgba(76,81,191,0.10);
  border-radius: 10px;
  padding: 28px;
  box-sizing: border-box;
  box-shadow: 0 8px 24px rgba(76,81,191,0.06);
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.blog-header h1 {
  margin: 0;
  font-size: 28px;
  color: #2d3748;
}

.blog-content {
  flex: 1;
  background: #ffffff;
  padding: 12px;
  border-radius: 8px;
  overflow: auto;
  box-sizing: border-box;
}
</style>
