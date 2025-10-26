<template>
  <div class="blog-page">
    <div class="blog-container">
      <header class="blog-header">
        <h1>Blog</h1>
      </header>

      <section class="blog-content">
        <!-- 占位：主要内容区（文章列表 / 文章详情） -->
        <div class="placeholder">
          <p>这里是 Blog 主内容区。页面占据大部分屏幕，可放文章列表或文章详情。</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
// Blog 页面初始占位组件
</script>

<style scoped>
/* 父容器：保留左右间隙，但让内容几乎占满视口 */
.blog-page {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 32px; /* 更大的外围留白 */
  min-height: 100vh;
  box-sizing: border-box;
  background: transparent;
}

/* 主容器：几乎占满宽度与高度的可视区域 */
.blog-container {
  width: calc(100% - 64px); /* 保证左右各有 32px 的外边距 */
  max-width: 1920px;
  min-height: calc(100vh - 64px); /* 保证上下各留 32px */
  background: #ffffff;
  border: 1px solid rgba(76,81,191,0.10); /* 细边框，若不需要可设置为 none */
  border-radius: 10px;
  padding: 28px;
  box-sizing: border-box;
  box-shadow: 0 8px 24px rgba(76,81,191,0.06);
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* 标题区 */
.blog-header h1 {
  margin: 0;
  font-size: 28px;
  color: #2d3748;
}

/* 主内容区 */
.blog-content {
  flex: 1;
  background: #ffffff;
  padding: 12px;
  border-radius: 8px;
  overflow: auto;
  box-sizing: border-box;
}

/* 占位样式 */
.placeholder {
  min-height: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4a5568;
  font-size: 16px;
}

/* 响应式调整：在小屏上减少左右间距，保持几乎填满 */
@media (max-width: 1200px) {
  .blog-page {
    padding: 20px;
  }
  .blog-container {
    width: calc(100% - 40px);
    min-height: calc(100vh - 40px);
    padding: 20px;
  }
}

@media (max-width: 640px) {
  .blog-page {
    padding: 12px;
  }
  .blog-container {
    width: 100%;
    min-height: calc(100vh - 24px);
    border-radius: 8px;
    padding: 16px;
  }
}
</style>
