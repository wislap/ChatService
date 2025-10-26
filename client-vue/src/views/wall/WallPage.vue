<template>
  <div class="wall-page">
    <div class="wall-container">
      <header class="wall-header">
        <h1>表白墙</h1>
        <p class="subtitle">留下你想说的话（示例本地数据）</p>
      </header>

      <section class="wall-post">
        <form @submit.prevent="addPost" class="post-form">
          <textarea v-model="newPost" placeholder="写下你的心里话..." rows="4"></textarea>
          <div class="form-actions">
            <input v-model="author" placeholder="署名 (可选)" />
            <button type="submit" class="btn primary" :disabled="!newPost.trim()">发布</button>
          </div>
        </form>
      </section>

      <section class="wall-list">
        <p class="lead">最新评论</p>
        <ul class="posts">
          <li v-for="p in posts" :key="p.id" class="post">
            <div class="post-body">{{ p.text }}</div>
            <div class="post-meta">
              <span class="author">{{ p.author || '匿名' }}</span>
              <span class="time">{{ p.time }}</span>
            </div>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

const newPost = ref('')
const author = ref('')

const posts = reactive([
  { id: 1, text: '你是我见过最温柔的人。', author: '匿名', time: '2025-10-01 12:00' },
  { id: 2, text: '愿你每天都开心。', author: '小明', time: '2025-10-05 09:21' }
])

const addPost = () => {
  const text = newPost.value.trim()
  if (!text) return
  posts.unshift({
    id: Date.now(),
    text,
    author: author.value.trim(),
    time: new Date().toLocaleString()
  })
  newPost.value = ''
  author.value = ''
}
</script>

<style scoped>
.wall-page {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 32px;
  min-height: 100vh;
  box-sizing: border-box;
  background: transparent;
}

.wall-container {
  width: calc(100% - 64px);
  max-width: 1200px;
  min-height: calc(100vh - 64px);
  background: #ffffff;
  border: 1px solid rgba(76,81,191,0.08);
  border-radius: 10px;
  padding: 28px;
  box-sizing: border-box;
  box-shadow: 0 8px 24px rgba(76,81,191,0.04);
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* header */
.wall-header h1 {
  margin: 0;
  font-size: 28px;
  color: #2d3748;
}
.subtitle {
  margin: 4px 0 0 0;
  color: #6b7280;
  font-size: 14px;
}

/* post form */
.post-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.post-form textarea {
  width: 100%;
  padding: 12px;
  box-sizing: border-box;
  border: 1px solid #e6e9f2;
  border-radius: 8px;
  resize: vertical;
  font-size: 14px;
}
.post-form input {
  padding: 8px 10px;
  border: 1px solid #e6e9f2;
  border-radius: 8px;
  font-size: 14px;
  width: 40%;
}
.form-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* buttons */
.btn {
  padding: 10px 14px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 600;
}
.btn.primary {
  background: #4c51bf;
  color: white;
}
.btn[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}

/* list */
.wall-list .lead {
  margin: 0 0 8px 0;
  color: #4a5568;
  font-size: 16px;
}
.posts {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.post {
  padding: 12px;
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.03);
  border-radius: 8px;
  box-shadow: 0 6px 18px rgba(15,23,42,0.03);
}
.post-body {
  color: #2d3748;
  font-size: 15px;
  margin-bottom: 8px;
}
.post-meta {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: #6b7280;
  justify-content: space-between;
}

/* responsive */
@media (max-width: 900px) {
  .wall-container {
    width: calc(100% - 40px);
    padding: 20px;
    min-height: calc(100vh - 40px);
  }
  .post-form input {
    width: 100%;
  }
}
</style>
