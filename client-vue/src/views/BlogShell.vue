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
  min-height: calc(100vh - 64px);
  max-height: calc(100vh - 64px);
  box-sizing: border-box;
  background: transparent;
  overflow: hidden;
}

.blog-container {
  width: calc(100% - 64px);
  max-width: 1920px;
  height: calc(100vh - 128px);
  max-height: calc(100vh - 128px);
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

.blog-header {
  flex-shrink: 0;
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
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
  min-height: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .blog-page {
    padding: 16px;
    min-height: calc(100vh - 32px);
    max-height: calc(100vh - 32px);
  }

  .blog-container {
    width: calc(100% - 32px);
    height: calc(100vh - 64px);
    max-height: calc(100vh - 64px);
    padding: 20px;
  }

  .blog-header h1 {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .blog-page {
    padding: 8px;
    min-height: calc(100vh - 16px);
    max-height: calc(100vh - 16px);
  }

  .blog-container {
    width: calc(100% - 16px);
    height: calc(100vh - 32px);
    max-height: calc(100vh - 32px);
    padding: 16px;
  }

  .blog-header h1 {
    font-size: 20px;
  }

  .blog-content {
    padding: 8px;
  }
}
</style>
