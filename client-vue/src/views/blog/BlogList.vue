<template>
  <div class="blog-list">
    <p class="lead">示例文章列表（占位）</p>
    <ul class="items">
      <li v-for="i in 6" :key="i" class="item">
        <h3>示例文章标题 {{ i }}</h3>
        <p>文章摘要示例内容，长度用于占位展示布局效果。</p>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
// 简单占位文章列表
</script>

<style scoped>
.blog-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px;
}

.lead {
  margin: 0 0 8px 0;
  color: #4a5568;
  font-size: 16px;
}

.items {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.item {
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.04);
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 6px 18px rgba(15,23,42,0.04);
}

.item h3 {
  margin: 0 0 6px 0;
  font-size: 16px;
  color: #2d3748;
}

.item p {
  margin: 0;
  color: #656d7a;
  font-size: 14px;
}
</style>
