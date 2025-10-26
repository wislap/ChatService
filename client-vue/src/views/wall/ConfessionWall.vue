<template>
  <div class="confession-wall">
    <!-- Temporary: render full list with v-for to eliminate virtual-scroller measurement issues -->
    <ul class="posts">
      <li v-for="item in confessions" :key="item.id" class="post-item">
        <ConfessionBubble
          :data="item"
          @like="handleLike"
          @delete="handleDelete"
        />
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import ConfessionBubble from './ConfessionBubble.vue'

interface Confession {
  id: number
  user: { avatar: string; username: string }
  content: string
  images?: string[]
  mentions?: { id: number; username: string }[]
  likes: number
  liked: boolean
  isMine: boolean
  isAnonymous: boolean
  createdAt: number
}

const confessions = ref<Confession[]>([])
const loading = ref(false)

import { watch } from 'vue'

onMounted(() => {
  console.log('[ConfessionWall] mounted, initial confessions length:', confessions.value.length)
  loadMore()
})

// watch confessions for debugging
watch(confessions, (newVal) => {
  console.log('[ConfessionWall] confessions changed: new length =', newVal.length)
})

const loadMore = async () => {
  if (loading.value) return
  loading.value = true
  // 调用 API 加载数据
  // const data = await api.getConfessions()
  // confessions.value.push(...data)
  loading.value = false
}

const handleLike = async (id: number) => {
  const item = confessions.value.find(c => c.id === id)
  if (!item) return

  item.liked = !item.liked
  item.likes += item.liked ? 1 : -1
  // await api.toggleLike(id)
}

const handleDelete = async (id: number) => {
  confessions.value = confessions.value.filter(c => c.id !== id)
  // await api.deleteConfession(id)
}

onMounted(() => loadMore())

// expose a method so parent can push a new confession
const scrollerKey = ref(0)

const pushConfession = async (confession: Confession) => {
  console.log('[ConfessionWall] pushConfession called with:', confession)
  confessions.value.unshift(confession)
  console.log('[ConfessionWall] after push, length =', confessions.value.length)

  // bump key to force RecycleScroller to re-render and pick up new items
  scrollerKey.value++
  await nextTick()
  console.log('[ConfessionWall] bumped scrollerKey to', scrollerKey.value)
}

defineExpose({
  pushConfession
})
</script>

<style scoped lang="scss">
.confession-wall {
  /* fill parent's available space; allow internal scrolling */
  flex: 1;
  min-height: 0;
  overflow: auto;
}

/* Posts rendered as normal list for debugging/consistency */
.posts {
  list-style: none;
  margin: 0;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-sizing: border-box;
}

/* Individual item wrapper */
.post-item {
  margin: 0;
  padding: 0;
}

/* Target ConfessionBubble's container to ensure consistent internal padding */
:deep(.bubble-container) {
  padding: 12px 12px; /* align with .posts padding */
  margin: 0;
}

/* Ensure bubble root has no extra margins and consistent spacing inside */
:deep(.bubble-container) :deep(.bubble) {
  margin: 0;
}

/* A small rule to prevent unexpected overflow inside bubble content */
:deep(.bubble .markdown-body) {
  overflow-wrap: anywhere;
}
</style>
