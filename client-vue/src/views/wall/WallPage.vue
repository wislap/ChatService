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
        <!-- 使用复用的 ConfessionWall 组件渲染滚动列表 -->
        <ConfessionWall ref="confessionWall" />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ConfessionWall from './ConfessionWall.vue'
import type { Ref } from 'vue'
import { GetSpecificMessages } from '../../idb'


const newPost = ref('')
const author = ref('')

const confessionWall = ref<{ pushConfession?: (c: unknown) => void } | null>(null) as Ref<{ pushConfession?: (c: unknown) => void } | null>

const addPost = () => {
  const text = newPost.value.trim()
  if (!text) return

  const newConf = {
    id: Date.now(),
    user: { avatar: '/favicon.ico', username: author.value.trim() || '匿名' },
    content: text,
    images: [],
    mentions: [],
    likes: 0,
    liked: false,
    isMine: true,
    isAnonymous: !author.value.trim(),
    createdAt: Date.now()
  }

  // 调用 ConfessionWall 暴露的方法将新条目插入列表
  if (confessionWall.value && typeof confessionWall.value.pushConfession === 'function') {
    confessionWall.value.pushConfession(newConf)
  }

  newPost.value = ''
  author.value = ''
}

onMounted(async () => {
  try {
    const res = await GetSpecificMessages('GaMessages')
    console.log('[WallPage] GetSpecificMessages result:', res)
    const msgs = (res && res.message ? res.message : []) as unknown[]
    console.log('[WallPage] messages count:', msgs.length)

    // push messages into ConfessionWall. pushConfession uses unshift, so iterate from end to start to preserve original order
    if (confessionWall.value && typeof confessionWall.value.pushConfession === 'function') {
      for (let i = msgs.length - 1; i >= 0; i--) {
        const m = msgs[i] as Record<string, unknown>
        const content = typeof m['content'] === 'string' ? (m['content'] as string) : String(m ?? '')
        const timestamp = typeof m['timestamp'] === 'number' ? (m['timestamp'] as number) : Date.now() + i
        const username = typeof m['username'] === 'string' ? (m['username'] as string) : '本地'

        const conf = {
          id: timestamp,
          user: { avatar: '/favicon.ico', username },
          content,
          images: [],
          mentions: [],
          likes: 0,
          liked: false,
          isMine: false,
          isAnonymous: true,
          createdAt: timestamp
        }
        console.log('[WallPage] pushing confession:', conf)
        confessionWall.value.pushConfession(conf)
      }
      console.log('[WallPage] finished pushing messages to ConfessionWall')
    } else {
      console.warn('[WallPage] confessionWall not ready or pushConfession not available')
    }
  } catch (e) {
    console.error('Failed to load local messages', e)
  }
})
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
.wall-list {
  /* ensure the virtual scroller has height to render into */
  flex: 1;
  min-height: 300px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
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
